import torch
from PIL import Image
from torchvision.transforms import ToPILImage, ToTensor


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    image = image.convert("RGB")
    to_tensor = ToTensor()
    image_tensor = to_tensor(image)  # [3, H, W]
    image_comfy_tensor = image_tensor.permute(1, 2, 0).unsqueeze(0)  # [1, H, W, 3]
    return image_comfy_tensor


def tensor_to_pil(images: torch.Tensor) -> list[Image.Image] | Image.Image:
    if images.ndim == 3:
        image = images
        to_pil = ToPILImage()
        image_pil = to_pil(image.permute(2, 0, 1))
        return image_pil
    elif images.ndim == 4:
        images_pil = [tensor_to_pil(image) for image in images]
        return images_pil

    return None
