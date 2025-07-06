import requests
from loguru import logger

FILE_SERVER_PORT = 8000


class EagleAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url + "/api"
        self.token = token

    def list_folder(self) -> list:
        url = self.base_url + "/folder/list"
        params = {"token": self.token}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logger.error("[EagleFeeder] Getting folder list is failed.")
            logger.error(response.text)
        return response.json()["data"]

    def add_from_url(self, file_name: str, tag_list: list[str], folder_id: str) -> None:
        url = self.base_url + "/item/addFromURL"
        headers = {"Content-Type": "application/json"}
        src_url = f"http://localhost:{FILE_SERVER_PORT}/{file_name}"
        json = {
            "url": src_url,
            "name": file_name,
            "tags": tag_list,
            "folderId": folder_id,
            "token": self.token,
        }
        response = requests.post(url, headers=headers, json=json)
        if response.status_code != 200:
            logger.error("[EagleFeeder] Uploading to eagle is failed.")
            logger.error(response.text)
        return
