from dotenv import load_dotenv
import json
import os
import re
import anthropic
from datetime import datetime
import sys

load_dotenv()


class DescriptionChapterGenerator:
    def __init__(
        self,
        podcast_name,
        links_folder,
        srt_folder,
        chapters_folder,
    ):
        self.podcast_name = podcast_name
        self.links_folder = links_folder
        self.srt_folder = srt_folder
        self.chapters_folder = chapters_folder
        os.makedirs(self.chapters_folder, exist_ok=True)
        self.client = anthropic.Anthropic()

    def extract_guid(self, filename):
        if filename.endswith("_links.json"):
            return filename.split("_links.json")[0]
        return None

    def find_files_with_specific_guid(self, directory, number):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if str(number) in file:
                    return file

    def convert_time_str_to_seconds(self, time_str):
        try:
            time_format = "%H:%M:%S"
            time_object = datetime.strptime(time_str, time_format)
            total_seconds = (
                time_object.hour * 3600 + time_object.minute * 60 + time_object.second
            )
            return int(total_seconds)
        except ValueError as e:
            print(f"Error converting timestamp '{time_str}': {e}")
            return None

    def generate_chapters(self, guid):

        links_file = self.find_files_with_specific_guid(self.links_folder, guid)
        links_file_path = os.path.join(self.links_folder, links_file)
        with open(links_file_path, "r") as links_file_path_data:
            links = json.load(links_file_path_data)

        srt_file = self.find_files_with_specific_guid(self.srt_folder, guid)
        srt_file_path = os.path.join(self.srt_folder, srt_file)

        if not os.path.exists(links_file_path):
            print(f"Links file not found: {links_file}")
            return
        if not os.path.exists(srt_file_path):
            print(f"SRT file not found: {srt_file}")
            return

        with open(os.path.join(self.srt_folder, srt_file), "r", encoding="utf-8") as f:
            transcript = f.read().strip()

        links_str = "\n".join([f"{link}: {url}" for link, url in links.items()])
        print(f"Links string for GPT-3.5:\n{links_str}")

        message = f"""You will be given an SRT transcript of a podcast and a list of links discussed during the podcast. Your task is to create a mapping between each link and the timestamp when it was discussed in the podcast.

        Here is the SRT transcript of the podcast:
        <transcript>
        {transcript}
        </transcript>

        Here are the links discussed during the podcast:
        <links>
        {links_str}
        </links>

        Follow these steps to complete the task:

        1. Parse the SRT transcript, paying attention to the timestamps and the content of each subtitle.

        2. For each link in the provided list, search for mentions or discussions of that link in the transcript. Look for exact matches, partial matches, or contextual clues that indicate the link is being discussed.

        3. When you find a mention of a link, note the timestamp associated with that part of the transcript.

        4. Create a mapping between each link and the earliest timestamp when it was mentioned or discussed.

        5. If a link is not mentioned in the transcript, map it to "Not mentioned".

        Provide your output in the following format:
        <link_timestamp_mapping>
        [Link 1]: [Timestamp]
        [Link 2]: [Timestamp]
        ...
        </link_timestamp_mapping>

        Note: Timestamps should be in the format used in the SRT transcript (typically HH:MM:SS,mmm)."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",  # claude-3-5-sonnet-20240620
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": message}],
            extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"},
        )

        result = response.content[0].text
        print("Received mapping response:")
        print(result)

        pattern = r"<link_timestamp_mapping>(.*?)</link_timestamp_mapping>"
        match = re.search(pattern, result, re.DOTALL)

        if match:
            mapping_str = match.group(1).strip()
            mapping_lines = mapping_str.split("\n")

            new_chapters_file = os.path.join(
                self.chapters_folder, f"episode_{guid}_chapters.json"
            )
            os.makedirs(os.path.dirname(new_chapters_file), exist_ok=True)

            new_chapters_data = {"chapters": []}
            seen_timestamps = set()

            for line in mapping_lines:
                parts = line.split(": ")
                if len(parts) == 2:
                    link = parts[0].strip()
                    timestamp = parts[1].strip()

                    if timestamp != "Not mentioned":
                        start_time = self.convert_time_str_to_seconds(
                            timestamp.split(",")[0]
                        )

                        if start_time is not None and start_time not in seen_timestamps:
                            seen_timestamps.add(start_time)

                            chapter = {
                                "startTime": start_time,
                                "url": links.get(link, link),
                                "title": link,
                            }
                            new_chapters_data["chapters"].append(chapter)

            new_chapters_data["chapters"].sort(key=lambda x: x["startTime"])

            print(f"Created new chapters file: {new_chapters_file}")
            with open(new_chapters_file, "w") as f:
                json.dump(new_chapters_data, f, indent=2)
        else:
            print(f"No valid mapping found for file: {links_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        podcast_name = sys.argv[1]
        outer_guid = sys.argv[2]
        srt_folder = f"{podcast_name}/srt/"
        links_folder: str = f"{podcast_name}/links/"
        chapters_folder = f"{podcast_name}/chapters/"
        generator = DescriptionChapterGenerator(
            podcast_name, links_folder, srt_folder, chapters_folder
        )
        generator.generate_chapters(outer_guid)
    else:
        print("Please provide a podcast name as an argument.")
