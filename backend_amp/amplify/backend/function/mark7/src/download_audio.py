from urllib.parse import urlparse
import requests


def download_audio(data, filename):
    call_uuid = data["callId"]
    url = data["recording_url"]
    if not url.startswith("http"):
        return None
    url = urlparse(url)
    url = url.scheme + "://" + url.netloc + url.path
    params = {"callid": call_uuid}
    response = requests.get(url, params=params)
    with open(filename, "wb") as f:
        f.write(response.content)
