import os
import requests
import feedparser
import whisper
import time
import json
import re
from datetime import datetime
from whisper.utils import get_writer
from dotenv import load_dotenv
import anthropic
import sys
from utils import sanitize_guid

load_dotenv()


class PodcastFetcher:
    def __init__(
        self,
        description_folder,
        srt_folder,
        links_folder,
        chapters_folder,
        processed_episodes_file,
        description_path,
        audio_filepath,
        srt_filepath,
    ):
        self.description_folder = description_folder
        self.srt_folder = srt_folder
        self.links_folder = links_folder
        self.chapters_folder = chapters_folder
        self.processed_episodes_file = processed_episodes_file
        self.description_path = description_path
        self.audio_filepath = audio_filepath
        self.srt_filepath = srt_filepath
        self.model = whisper.load_model("base")
        self.processed_episodes = self._get_processed_episodes()
        self.client = anthropic.Anthropic()

    def extract_guid(self, filename):
        match = re.search(r"description_(.*)\.txt", filename)
        return match.group(1) if match else None

    def find_files_with_specific_guid(self, directory, number):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if str(number) in file:
                    return file

    def _get_processed_episodes(self):
        if os.path.exists(self.processed_episodes_file):
            with open(self.processed_episodes_file, "r") as file:
                return json.load(file)
        return []

    def _update_processed_episodes(self, guid):
        self.processed_episodes.append(guid)
        with open(self.processed_episodes_file, "w") as file:
            json.dump(self.processed_episodes, file)

    def download_audio(self, url, filepath):
        print(f"Downloading audio from {url} to {filepath}...")
        response = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print("Audio downloaded.")

    def convert_time_str_to_seconds(self, time_str):
        time_format = "%H:%M:%S"
        time_object = datetime.strptime(time_str, time_format)
        total_seconds = (
            time_object.hour * 3600 + time_object.minute * 60 + time_object.second
        )
        return int(total_seconds)

    def fetch(self, entry, guid):

        # Get the audio URL (assuming it's available in the feed)
        if "enclosures" not in entry or not entry.enclosures:
            print("No enclosures found, skipping entry.")
            return  # Skip if there are no enclosures

        # save the feed description to a file
        description_file_path = os.path.join(
            self.description_folder, f"description_{guid}.txt"
        )
        with open(description_file_path, "w") as f:
            f.write(entry.description)
        print(f"Description saved to {description_file_path}")

        audio_url = entry.enclosures[0].href

        # Download the audio file
        self.download_audio(audio_url, self.audio_filepath)

        # Transcribe the audio file using Whisper
        print(f"Transcribing audio file {self.audio_filepath}...")
        start_time = time.time()
        result = self.model.transcribe(self.audio_filepath, verbose=True)
        end_time = time.time()
        print(f"Transcription completed in {end_time - start_time:.2f} seconds.")

        # Save the transcription to an SRT file

        srt_writer = get_writer("srt", self.srt_folder)
        srt_writer(result, self.srt_filepath)
        print(f"Transcription saved to {self.srt_filepath}")

        # # Process links and generate chapters
        # self.process_links_and_generate_chapters(guid)

        # # Update the processed episodes
        # self._update_processed_episodes(guid)

    print("Processing completed.")


#     def process_links_and_generate_chapters(self, guid):
#         links_file = self.find_files_with_specific_guid(self.links_folder, guid)
#         links = json.load(links_file)
#         links_file_path = os.path.join(self.links_folder, links_file)

#         srt_file = self.find_files_with_specific_guid(self.srt_folder, guid)
#         srt_file_path = os.path.join(self.srt_folder, srt_file)

#         if not os.path.exists(links_file_path):
#             print(f"Links file not found: {links_file}")
#             return
#         if not os.path.exists(srt_file_path):
#             print(f"SRT file not found: {srt_file}")
#             return

#         with open(os.path.join(self.srt_folder, srt_file), "r", encoding="utf-8") as f:
#             transcript = f.read().strip()

#         links_str = "\n".join([f"{link}: {url}" for link, url in links.items()])

#         message = f"""You will be given an SRT transcript of a podcast and a list of links discussed during the podcast. Your task is to create a mapping between each link and the timestamp when it was discussed in the podcast.

# Here is the SRT transcript of the podcast:
# <transcript>
# {transcript}
# </transcript>

# Here are the links discussed during the podcast:
# <links>
# {links_str}
# </links>

# Follow these steps to complete the task:

# 1. Parse the SRT transcript, paying attention to the timestamps and the content of each subtitle.

# 2. For each link in the provided list, search for mentions or discussions of that link in the transcript. Look for exact matches, partial matches, or contextual clues that indicate the link is being discussed.

# 3. When you find a mention of a link, note the timestamp associated with that part of the transcript.

# 4. Create a mapping between each link and the earliest timestamp when it was mentioned or discussed.

# 5. If a link is not mentioned in the transcript, map it to "Not mentioned".

# Provide your output in the following format:
# <link_timestamp_mapping>
# [Link 1]: [Timestamp]
# [Link 2]: [Timestamp]
# ...
# </link_timestamp_mapping>

# Note: Timestamps should be in the format used in the SRT transcript (typically HH:MM:SS,mmm)."""

#         response = self.client.messages.create(
#             model="claude-3-sonnet-20240229",  # claude-3-5-sonnet-20240620
#             max_tokens=2000,
#             temperature=0,
#             messages=[{"role": "user", "content": message}],
#         )

#         result = response.content[0].text
#         print("Received mapping response:")
#         print(result)

#         pattern = r"<link_timestamp_mapping>(.*?)</link_timestamp_mapping>"
#         match = re.search(pattern, result, re.DOTALL)

#         if match:
#             mapping_str = match.group(1).strip()
#             mapping_lines = mapping_str.split("\n")

#             new_chapters_file = os.path.join(
#                 self.chapters_folder, f"episode_{guid}_chapters.json"
#             )
#             os.makedirs(os.path.dirname(new_chapters_file), exist_ok=True)

#             new_chapters_data = {"chapters": []}
#             seen_timestamps = set()

#             for line in mapping_lines:
#                 parts = line.split(": ")
#                 if len(parts) == 2:
#                     link = parts[0].strip()
#                     timestamp = parts[1].strip()

#                     if timestamp != "Not mentioned":
#                         try:
#                             start_time = self.convert_time_str_to_seconds(
#                                 timestamp.split(",")[0]
#                             )
#                         except ValueError as e:
#                             print(f"Error converting timestamp '{timestamp}': {e}")
#                             continue

#                         if start_time not in seen_timestamps:
#                             seen_timestamps.add(start_time)

#                             chapter = {
#                                 "startTime": start_time,
#                                 "url": links.get(link, link),
#                                 "title": link,
#                             }
#                             new_chapters_data["chapters"].append(chapter)

#             new_chapters_data["chapters"].sort(key=lambda x: x["startTime"])

#             with open(new_chapters_file, "w") as f:
#                 json.dump(new_chapters_data, f, indent=2)

#             print(f"Created new chapters file: {new_chapters_file}")
#         else:
#             print(f"No valid mapping found for file: {link_file}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        podcast_name = sys.argv[1]
        rss_url = sys.argv[2]
        guid = sys.argv[3]
        description_folder = f"{podcast_name}/descriptions/"
        srt_folder = f"{podcast_name}/srt/"
        links_folder = f"{podcast_name}/links/"
        chapters_folder = f"{podcast_name}/chapters/"
        processed_episodes_file = f"{podcast_name}/processed_episodes.json"
        audio_filepath = os.path.join(description_folder, f"audio_{guid}.mp3")
        srt_filepath = os.path.join(srt_folder, f"transcription_{guid}.srt")
        description_path = os.path.join(description_folder, f"description_{guid}.txt")
        os.makedirs(description_folder, exist_ok=True)
        os.makedirs(srt_folder, exist_ok=True)
        os.makedirs(links_folder, exist_ok=True)
        os.makedirs(chapters_folder, exist_ok=True)

        response = requests.get(rss_url)
        feed = feedparser.parse(response.content)

        for entry in feed.entries:

            rawGuid = getattr(entry, "guid", None)
            current_guid = sanitize_guid(rawGuid)
            if not current_guid or current_guid != guid:
                print("guid doesn't match the one we're looking for, skipping entry.")
                continue  # Skip if there's no GUID

            fetcher = PodcastFetcher(
                description_folder,
                srt_folder,
                links_folder,
                chapters_folder,
                processed_episodes_file,
                description_path,
                audio_filepath,
                srt_filepath,
            )
            fetcher.fetch(entry)
    else:
        print("Please provide a podcast name and RSS URL as arguments.")
