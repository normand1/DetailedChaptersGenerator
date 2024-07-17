from datetime import datetime, timedelta
import os
import re


def parse_srt_time(time_string):
    """Converts an SRT time string into a datetime object."""
    return datetime.strptime(time_string, "%H:%M:%S,%f")


def format_srt_time(dt):
    """Formats a datetime object into an SRT time string."""
    return datetime.strftime(dt, "%H:%M:%S,%f")[:-3]


def combine_srt_entries(input_filename, output_filename, max_duration):
    with open(input_filename, "r") as input_file:
        data = input_file.read().strip().split("\n\n")
        if data == [""]:
            return
        srt_entries = [entry.split("\n", 2) for entry in data]

    combined_entries = []
    current_entry = srt_entries[0]
    current_start_time = parse_srt_time(current_entry[1].split(" --> ")[0])
    current_end_time = parse_srt_time(current_entry[1].split(" --> ")[1])
    current_duration = current_end_time - current_start_time

    for entry in srt_entries[1:]:
        start_time, end_time = map(parse_srt_time, entry[1].split(" --> "))
        entry_duration = end_time - start_time

        if current_duration + entry_duration <= max_duration:
            current_entry[2] += "\n" + entry[2]
            current_end_time = end_time
            current_duration += entry_duration
        else:
            current_entry[1] = (
                format_srt_time(current_start_time)
                + " --> "
                + format_srt_time(current_end_time)
            )
            combined_entries.append(current_entry)
            current_entry = entry
            current_start_time = start_time
            current_end_time = end_time
            current_duration = entry_duration

    # Add last entry
    current_entry[1] = (
        format_srt_time(current_start_time)
        + " --> "
        + format_srt_time(current_end_time)
    )
    combined_entries.append(current_entry)

    with open(output_filename, "w") as output_file:
        for index, entry in enumerate(combined_entries, start=1):
            print(f"{index}\n{entry[1]}\n{entry[2]}\n", file=output_file)


srt_dir = "latentspacepodcast/srt/"
files = os.listdir(srt_dir)
max_duration = timedelta(seconds=300)


def extract_number(filename):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


files = os.listdir(srt_dir)
sorted_files = sorted(files, key=extract_number, reverse=True)

for filename in sorted_files[0:1]:
    combine_srt_entries(srt_dir + filename, srt_dir + filename, max_duration)
