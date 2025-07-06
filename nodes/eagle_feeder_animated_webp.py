import json

import torch

from ..api.eagle_api import EagleAPI
from ..utils.image_utils import tensor_to_pil
from .eagle_feeder_base import EagleFeederBase


class EagleFeederAnimatedWebp(EagleFeederBase):
    methods = {"default": 4, "fastest": 0, "slowest": 6}

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
                "fps": (
                    "FLOAT",
                    {"default": 6.0, "min": 0.01, "max": 1000.0, "step": 0.01},
                ),
                "lossless": ("BOOLEAN", {"default": True}),
                "quality": ("INT", {"default": 80, "min": 0, "max": 100}),
                "method": (list(cls.methods.keys()),),
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
        fps: float,
        lossless: bool,
        quality: int,
        method: str,
        prompt=None,
        extra_pnginfo=None,
    ) -> dict:
        self.eagle_api = EagleAPI(eagle_host, eagle_token)
        folder_list = self.eagle_api.list_folder()
        folder_id = self.find_id_by_name(folder_list, folder_name)
        method = self.methods.get(method)

        pil_images = [tensor_to_pil(image) for image in images]
        file_name = self.get_file_name("WEBP")
        file_path = self.img_dir + "/" + file_name

        metadata = pil_images[0].getexif()
        if embed_workflow:
            if prompt is not None:
                metadata[0x0110] = "prompt:{}".format(json.dumps(prompt))
            if extra_pnginfo is not None:
                inital_exif = 0x010F
                for x in extra_pnginfo:
                    metadata[inital_exif] = "{}:{}".format(
                        x, json.dumps(extra_pnginfo[x])
                    )
                    inital_exif -= 1

        num_frames = len(pil_images)
        for i in range(0, num_frames, num_frames):
            start = i + 1
            end = i + num_frames
            pil_images[i].save(
                file_path,
                save_all=True,
                duration=int(1000.0 / fps),
                append_images=pil_images[start:end],
                exif=metadata,
                lossless=lossless,
                quality=quality,
                method=method,
            )

        tag_list = tags.split(",")
        self.eagle_api.add_from_url(file_name, tag_list, folder_id)

        return {}
