import json

import torch
from PIL.PngImagePlugin import PngInfo

from ..api.eagle_api import EagleAPI
from ..utils.image_utils import tensor_to_pil
from .eagle_feeder_base import EagleFeederBase


class EagleFeederPng(EagleFeederBase):
    @classmethod
    def INPUT_TYPES(cls) -> dict[str, any]:
        return {
            "required": {
                "images": ("IMAGE",),
                "tags": ("STRING", {"default": "", "forceInput": True}),
                "folder_name": ("STRING", {"default": ""}),
                "eagle_host": ("STRING", {"default": "http://localhost:41595"}),
                "eagle_token": ("STRING", {"default": ""}),
                "embed_workflow": ("BOOLEAN", {"default": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def send_to_eagle(
        self,
        images: torch.Tensor,
        tags: str,
        folder_name: str,
        eagle_host: str,
        eagle_token: str,
        embed_workflow: bool,
        prompt=None,
        extra_pnginfo=None,
    ) -> dict:
        self.eagle_api = EagleAPI(eagle_host, eagle_token)

        folder_list = self.eagle_api.list_folder()
        folder_id = self.find_id_by_name(folder_list, folder_name)

        for image in images:
            image = tensor_to_pil(image)
            file_name = self.get_file_name("PNG")
            file_path = self.img_dir + "/" + file_name

            metadata = None
            if embed_workflow:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                image.save(file_path, format="PNG", pnginfo=metadata)
            else:
                image.save(file_path, format="PNG")

            tag_list = tags.split(",")
            self.eagle_api.add_from_url(file_name, tag_list, folder_id)

        return {}
