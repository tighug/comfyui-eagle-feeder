from comfy.comfy_types.node_typing import IO
from comfy_api.input import VideoInput
from comfy_api.util.video_types import VideoCodec, VideoContainer

from ..api.eagle_api import EagleAPI
from .eagle_feeder_base import EagleFeederBase


class EagleFeederMp4(EagleFeederBase):
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, any]:
        return {
            "required": {
                "video": (IO.VIDEO,),
                "tags": ("STRING", {"default": "", "forceInput": True}),
                "folder_name": ("STRING", {"default": ""}),
                "eagle_host": ("STRING", {"default": "http://localhost:41595"}),
                "eagle_token": ("STRING", {"default": ""}),
                "embed_workflow": ("BOOLEAN", {"default": True}),
                "format": (VideoContainer.as_input(), {"default": "auto"}),
                "codec": (VideoCodec.as_input(), {"default": "auto"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def send_to_eagle(
        self,
        video: VideoInput,
        tags: str,
        folder_name: str,
        eagle_host: str,
        eagle_token: str,
        embed_workflow: bool,
        format: str,
        codec: str,
        prompt=None,
        extra_pnginfo=None,
    ) -> dict:
        self.eagle_api = EagleAPI(eagle_host, eagle_token)
        folder_list = self.eagle_api.list_folder()
        folder_id = self.find_id_by_name(folder_list, folder_name)
        file_name = self.get_file_name("MP4")
        file_path = self.img_dir + "/" + file_name

        metadata = None
        if embed_workflow:
            metadata = {}
            if extra_pnginfo is not None:
                metadata.update(extra_pnginfo)
            if prompt is not None:
                metadata["prompt"] = prompt

        video.save_to(file_path, format=format, codec=codec, metadata=metadata)

        tag_list = tags.split(",")
        self.eagle_api.add_from_url(file_name, tag_list, folder_id)

        return {}
