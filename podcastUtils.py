import re


def create_gcs_bucket_safe_name(url):
    # Remove 'https://', 'http://', 'www.'
    url = re.sub(r"^https?://(www\.)?", "", url)

    # Replace invalid characters with dashes
    bucket_name = re.sub(r"[^a-z0-9-_.]", "-", url.lower())

    # Ensure the name starts and ends with a letter or number
    bucket_name = re.sub(r"^[^a-z0-9]+", "", bucket_name)
    bucket_name = re.sub(r"[^a-z0-9]+$", "", bucket_name)

    # Ensure the name is within the valid length
    bucket_name = bucket_name[:63]

    return bucket_name


url = "https://allinchamathjason.libsyn.com/rss"
bucket_name = create_gcs_bucket_safe_name(url)
print(bucket_name)
