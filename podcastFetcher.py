import os
import requests
import feedparser

# Create the folder if it doesn't exist
folder_name = "latentspacepodcast/descriptions/"
os.makedirs(folder_name, exist_ok=True)

# Fetch the feed
response = requests.get(
    "https://api.substack.com/feed/podcast/1084089/private/83ac408d-3179-402f-a981-ebaf0c166953.rss"
)
feed = feedparser.parse(response.content)

# Iterate over each entry (episode) in the feed
for entry in feed.entries:
    # Get the description
    description = entry.description

    # Get the GUID
    guid = entry.guid

    # Write the description to a file in the specified folder
    with open(os.path.join(folder_name, f"description_{guid}.txt"), "w") as f:
        f.write(description)
