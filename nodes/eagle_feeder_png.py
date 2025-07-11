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

    INPUT_IS_LIST = True

    def send_to_eagle(
        self,
        images: list[torch.Tensor],
        tags: list[str],
        folder_name: list[str],
        eagle_host: list[str],
        eagle_token: list[str],
        embed_workflow: list[bool],
        prompt: list,
        extra_pnginfo: list,
    ) -> dict:
        images = images[0]
        folder_name = folder_name[0]
        eagle_host = eagle_host[0]
        eagle_token = eagle_token[0]
        embed_workflow = embed_workflow[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]

        self.eagle_api = EagleAPI(eagle_host, eagle_token)

        folder_list = self.eagle_api.list_folder()
        folder_id = self.find_id_by_name(folder_list, folder_name)

        for idx, image in enumerate(images):
            image = tensor_to_pil(image)
            file_name = f'{idx:03}_{self.get_file_name("PNG")}'
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

            tag_list = tags[idx].split(",")
            self.eagle_api.add_from_url(file_name, tag_list, folder_id)

        return {}
