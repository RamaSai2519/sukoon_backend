import requests


def download_txt_file(url):
    """
    Downloads a text file from the given URL and returns its contents.

    :param url: URL of the text file to download
    :return: Contents of the downloaded text file as a string
    """
    response = requests.get(url)
    return response.text if response.status_code == 200 else None
