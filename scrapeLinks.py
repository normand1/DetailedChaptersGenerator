from bs4 import BeautifulSoup
import json
import os, re


def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


desc_dir = "latentspacepodcast/descriptions/"
links_dir = "latentspacepodcast/links/"

files = os.listdir(desc_dir)
sorted_files = sorted(files, key=extract_number, reverse=True)

for filename in sorted_files[0:1]:
    with open(desc_dir + filename, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Identify the start and end of the actual content
    # content_start = "<![CDATA["
    # content_end = "]]>"

    # # Extract the HTML content
    # start_index = content.find(content_start)
    # end_index = content.find(content_end)

    # if start_index == -1 or end_index == -1:
    #     print("No content found.")
    #     exit()

    # html_content = content[start_index + len(content_start) : end_index]

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(content, "html.parser")

    # Find all 'a' tags (which define hyperlinks in HTML)
    links = soup.find_all("a")

    # Extract the link text and the URL and store them in a dictionary
    link_dict = {link.text.strip(): link.get("href") for link in links}

    if not os.path.exists(links_dir):
        os.makedirs(links_dir)

    number = extract_number(filename)

    # Write the results into a JSON file
    with open(
        links_dir + "/" + str(number) + "_links.json", "w", encoding="utf-8"
    ) as f:
        json.dump(link_dict, f)
