from dotenv import load_dotenv
import json, os, re
from langchain.chat_models import ChatAnthropic
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from datetime import datetime

load_dotenv()

chat = ChatAnthropic()


def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


def find_files_with_specific_number(directory, number):
    # Walk through directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # If the file name contains the specific number, print its path
            if str(number) in file:
                return file


def convert_time_str_to_seconds(time_str):
    time_format = "%H:%M:%S"
    time_object = datetime.strptime(time_str, time_format)
    total_seconds = (
        time_object.hour * 3600 + time_object.minute * 60 + time_object.second
    )
    return int(total_seconds)


links_dir = "latentspacepodcast/links/"

# Get list of files in directory
linkFiles = os.listdir(links_dir)

for linkFile in linkFiles:
    with open(links_dir + linkFile, "r", encoding="utf-8") as f:
        links = json.load(f)

    number = extract_number(links_dir + linkFile)

    srt_file = find_files_with_specific_number("latentspacepodcast/srt/", number)
    chaps_file = find_files_with_specific_number("latentspacepodcast/chapters/", number)

    if not os.path.exists(
        "latentspacepodcast/srt/" + (srt_file or "null")
    ) or not os.path.exists("latentspacepodcast/chapters/" + (chaps_file or "null")):
        continue

    with open("latentspacepodcast/srt/" + srt_file, "r", encoding="utf-8") as f:
        transcript = f.read().strip()
    chapters = []
    for link, linkVal in links.items():
        humanTemplate = '<transcript>{transcript}</transcript> \n\n When is the following discussed in this transcript? <discussedContent>{link}</discussedContent> Return an answer in this format ```{{"<start>", "<end>"}}```. If it\'s not discussed please just return "<result>undefined</result>". Now act as a XML code outputter. Please, Do not add any additional context or introduction in your response, make sure your entire response is parseable by xml'
        humanMessagePrompt = HumanMessagePromptTemplate.from_template(humanTemplate)

        chat_prompt = ChatPromptTemplate.from_messages([humanMessagePrompt])
        result = chat(
            chat_prompt.format_prompt(transcript=transcript, link=link).to_messages()
        )

        # Strip unnecessary parts
        # Strip unnecessary parts
        if "undefined" not in result.content:
            s = result.content
            # Regular expression to match time stamps
            time_pattern = re.compile(
                r"(\d{2}:\d{2}:\d{2}(?:,\d{3})?)"
            )  # Modified regular expression to optionally capture milliseconds

            # Find matches
            matches = time_pattern.findall(s)

            # If we found exactly two matches, assign them to start_time and end_time
            if len(matches) == 2:
                start_time, end_time = [
                    time.split(",")[0] for time in matches
                ]  # Splitting the time string at comma to remove milliseconds (if present)
                print("Start time:", start_time)
                print("End time:", end_time)
                chapter = {
                    "startTime": convert_time_str_to_seconds(start_time),
                    "url": linkVal,
                    "title": link,
                }
                # update chapters
                chaps_file = find_files_with_specific_number(
                    "latentspacepodcast/chapters/", number
                )
                # Load existing data from the file
                with open("latentspacepodcast/chapters/" + chaps_file, "r") as f:
                    data = json.load(f)

                data["chapters"].append(chapter)

                # Convert back to json and save to the file
                with open("latentspacepodcast/chapters/" + chaps_file, "w") as f:
                    json.dump(data, f)
            else:
                print("Unexpected number of matches found:", len(matches))
