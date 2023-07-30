from bs4 import BeautifulSoup
import re
import os


def transcript_to_srt(transcript_text):
    soup = BeautifulSoup(transcript_text, "html.parser")
    paragraphs = soup.find_all("p")

    srt_text = ""
    for i, paragraph in enumerate(paragraphs, start=1):
        timecode = re.search("\[\d\d:\d\d:\d\d\]", paragraph.text)
        if not timecode:
            continue
        start_time = timecode.group(0)[1:-1] + ",000"
        if i < len(paragraphs):
            end_time = re.search("\[\d\d:\d\d:\d\d\]", paragraphs[i].text)
            if end_time:
                end_time = end_time.group(0)[1:-1] + ",000"
            else:
                end_time = "00:00:00,000"
        else:
            end_time = "00:00:00,000"

        srt_text += f"{i}\n"
        srt_text += f"{start_time} --> {end_time}\n"
        srt_text += re.sub("<[^>]*>|\\[.*\\]", "", paragraph.text) + "\n\n"

    return srt_text


description_dir = "latentspacepodcast/descriptions/"
srt_dir = "latentspacepodcast/srt/"

# Check if srt_dir exists and create it if not
if not os.path.exists(srt_dir):
    os.makedirs(srt_dir)

for filename in os.listdir(description_dir):
    with open(description_dir + filename, "r") as f:
        transcript_text = f.read()

    srt_text = transcript_to_srt(transcript_text)

    # Sanitize filename by replacing colons with underscores
    sanitized_filename = filename.replace(":", "_")

    # Assuming the filename has the structure 'description_<i>.txt', we strip off 'description_' and '.txt'
    # to get '<i>', then we use that to name the new file.
    new_filename = (
        "transcript_"
        + sanitized_filename.replace("description_", "").replace(".txt", "")
        + ".srt"
    )

    with open(srt_dir + new_filename, "w") as f:
        f.write(srt_text)
