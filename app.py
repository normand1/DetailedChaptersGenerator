import json
from podcastFetcher import PodcastFetcher
from scrapeLinks import LinkScraper
from generateDescriptionChaptersV2 import DescriptionChapterGenerator
import os
import re
import requests
import feedparser
from utils import sanitize_guid


def _get_processed_episodes(podcast_name):
    processed_episodes_file = f"{podcast_name}/processed_episodes.json"
    if os.path.exists(processed_episodes_file):
        with open(processed_episodes_file, "r") as file:
            return json.load(file)
    return []


def _save_processed_episode(podcast_name, guid):
    processed_episodes_file = f"{podcast_name}/processed_episodes.json"
    processed_episodes = _get_processed_episodes(podcast_name)
    if guid not in processed_episodes:
        processed_episodes.append(guid)
        with open(processed_episodes_file, "w") as file:
            json.dump(processed_episodes, file)


def find_files_with_specific_guid(directory, number):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if str(number) in file:
                return file


# Load podcasts from JSON file
with open("output/allMappedChapterPodcasts.json", "r") as f:
    data = json.load(f)
    podcasts = data.get("podcasts", {})

# iterate over all podcasts in allMappedChapterPodcasts.json
for podcastGuid, podcast in podcasts.items():
    description_folder = f"output/{podcast['name']}/descriptions/"
    srt_folder = f"output/{podcast['name']}/srt/"
    links_folder = f"output/{podcast['name']}/links/"
    chapters_folder = f"output/{podcast['name']}/chapters/"
    descriptions_folder = f"output/{podcast['name']}/descriptions/"

    os.makedirs(description_folder, exist_ok=True)
    os.makedirs(srt_folder, exist_ok=True)
    os.makedirs(links_folder, exist_ok=True)
    os.makedirs(chapters_folder, exist_ok=True)

    response = requests.get(podcast["feedUrl"])
    feed = feedparser.parse(response.content)

    for entry in feed.entries:
        if not entry.guid:
            print("No GUID found, skipping entry.")
            continue  # Skip if there's no GUID

        rawGuid = getattr(entry, "guid", None)
        guid = sanitize_guid(rawGuid)

        processed_episodes = _get_processed_episodes(podcast["name"])

        if guid in processed_episodes:
            print(f"Already processed episode with GUID: {guid}, skipping.")
            continue

        print(f"Processing entry with GUID: {guid}")

        audio_filepath = os.path.join(description_folder, f"audio_{guid}.mp3")
        srt_filepath = os.path.join(srt_folder, f"transcription_{guid}.srt")
        description_filepath = os.path.join(
            description_folder, f"description_{guid}.txt"
        )
        description_path = os.path.join(descriptions_folder, f"description_{guid}.txt")

        # Process podcast episodes
        processor = PodcastFetcher(
            description_folder,
            srt_folder,
            links_folder,
            chapters_folder,
            f"output/{podcast['name']}/processed_episodes.json",
            description_path,
            audio_filepath,
            srt_filepath,
        )

        processor.fetch(entry, guid)

        # Scrape links from descriptions
        scraper = LinkScraper(description_path, links_folder)
        scraper.scrape(description_filepath, guid)

        link_files = os.listdir(links_folder)
        print(f"Found link files: {link_files}")

        srt_file = find_files_with_specific_guid(srt_folder, guid)

        # Generate chapters from descriptions and links
        generator = DescriptionChapterGenerator(
            podcast["name"], links_folder, srt_folder, chapters_folder
        )
        generator.generate_chapters(guid)

        # Save the processed GUID
        _save_processed_episode(podcast["name"], guid)

        print(f"Finished processing episode with GUID: {guid}")
