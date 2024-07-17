import re


def sanitize_guid(guid):
    return re.sub(r'[<>:"/\\|?*]', "_", guid)
