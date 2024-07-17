from bs4 import BeautifulSoup
import json
import os
import re
import sys


class LinkScraper:
    def __init__(self, desc_dir, links_dir):
        self.desc_dir = desc_dir
        self.links_dir = links_dir
        os.makedirs(self.links_dir, exist_ok=True)
        print(f"Initialized LinkScraper")

    def extract_guid(self, filename):
        match = re.search(r"description_(.*)\.txt", filename)
        return match.group(1) if match else None

    def scrape(self, description_file_path, guid):
        print(f"Starting to scrape links for podcast episode {guid}.")

        with open(description_file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            print(f"Failed to read {description_file_path} with utf-8 encoding.")

            # Extract links from the content
            link_dict = self.extract_links(content)
            print(f"Found {len(link_dict)} links in the file.")

            # Write the results into a JSON file
            output_filepath = os.path.join(self.links_dir, f"{guid}_links.json")
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(link_dict, f)
            print(f"Saved links to {output_filepath}")

            print("Finished scraping links.")

    def extract_links(self, content):
        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(content, "html.parser")

        # Find all 'a' tags (which define hyperlinks in HTML)
        links = soup.find_all("a")

        # Extract the link text and the URL and store them in a dictionary
        link_dict = {link.text.strip(): link.get("href") for link in links}

        # Find URLs in text
        urls_in_text = re.findall(r"(https?://\S+)", content)
        for url in urls_in_text:
            # Extract surrounding text to use as the link text
            start = content.find(url) - 50 if content.find(url) > 50 else 0
            end = content.find(url) + len(url) + 50
            surrounding_text = content[start:end]
            link_text = surrounding_text.replace(url, "").strip()
            link_dict[link_text] = url

        return link_dict


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        guid = sys.argv[2]
        descriptions_folder = f"{name}/descriptions/"
        description_path = os.path.join(descriptions_folder, f"description_{guid}.txt")
        links_folder: str = f"{name}/links/"
        scraper = LinkScraper(descriptions_folder, links_folder)
        scraper.scrape(description_path, guid)
    else:
        print("Please provide a podcast name as an argument.")
