import os
from datetime import datetime, timedelta
from pathlib import Path

import torch
from loguru import logger

from ..api.eagle_api import EagleAPI
from ..utils.file_server import FileServer
from ..utils.image_utils import tensor_to_pil

FILE_SERVER_PORT = 8000


class EagleFeeder:
    file_server = None

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, any]:
        return {
            "required": {
                "images": ("IMAGE",),
                "tags": ("STRING", {"default": "", "forceInput": True}),
                "folder_name": ("STRING", {"default": ""}),
                "eagle_host": ("STRING", {"default": "http://localhost:41595"}),
                "eagle_token": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "send_to_eagle"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def __init__(self):
        self.img_dir = str(Path(__file__).parents[1] / "images")
        self.remove_old_files(self.img_dir)
        if EagleFeeder.file_server is None:
            self.start_file_server(self.img_dir, FILE_SERVER_PORT)

    def send_to_eagle(
        self,
        images: torch.Tensor,
        tags: str,
        folder_name: str,
        eagle_host: str,
        eagle_token: str,
    ) -> dict:
        self.eagle_api = EagleAPI(eagle_host, eagle_token)

        folder_list = self.eagle_api.list_folder()
        folder_id_list = [
            item["id"] for item in folder_list if item["name"] == folder_name
        ]
        folder_id = folder_id_list[0]

        for image in images:
            image = tensor_to_pil(image)
            # 画像をローカルに保存
            file_name = self.get_file_name()
            file_path = self.img_dir + "/" + file_name
            image.save(file_path, format="PNG")

            # EagleAPI addFromURL 呼び出し
            src_url = f"http://localhost:{FILE_SERVER_PORT}/{file_name}"
            tag_list = tags.split(",")
            self.eagle_api.add_from_url(src_url, file_name, tag_list, folder_id)

        return {}

    def start_file_server(self, directory: str, port: int):
        if not Path(directory).exists():
            os.mkdir(directory)
        EagleFeeder.file_server = FileServer(directory, port)
        EagleFeeder.file_server.start()
        logger.info(f"[EagleFeeder] File server started as {directory}")

    def get_file_name(self) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        ext = "png"
        file_name = f"{timestamp}.{ext}"
        return file_name

    def remove_old_files(self, dir_path: str) -> None:
        if not Path(dir_path).exists():
            return

        now = datetime.now()
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_mtime > timedelta(days=2):
                    os.remove(file_path)
