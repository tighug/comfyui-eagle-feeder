import os
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from ..utils.file_server import FileServer

FILE_SERVER_PORT = 8000


class EagleFeederBase:
    file_server = None
    RETURN_TYPES = ()
    FUNCTION = "send_to_eagle"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def __init__(self):
        self.img_dir = str(Path(__file__).parents[1] / "images")
        self.remove_old_files(self.img_dir)
        if EagleFeederBase.file_server is None:
            self.start_file_server(self.img_dir, FILE_SERVER_PORT)

    def start_file_server(self, directory: str, port: int):
        if not Path(directory).exists():
            os.mkdir(directory)
        EagleFeederBase.file_server = FileServer(directory, port)
        EagleFeederBase.file_server.start()
        logger.info(f"[EagleFeeder] File server started as {directory}")

    def find_id_by_name(self, data: list, target_name: str) -> str | None:
        for item in data:
            if item.get("name") == target_name:
                return item.get("id")

            if "children" in item and isinstance(item["children"], list):
                result = self.find_id_by_name(item["children"], target_name)
                if result:
                    return result

        return None

    def get_file_name(self, format: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        ext = format.lower()
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
