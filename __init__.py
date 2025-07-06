from .nodes.eagle_feeder_animated_webp import EagleFeederAnimatedWebp
from .nodes.eagle_feeder_mp4 import EagleFeederMp4
from .nodes.eagle_feeder_png import EagleFeederPng

NODE_CLASS_MAPPINGS = {
    "EagleFeederPng": EagleFeederPng,
    "EagleFeederAnimatedWebp": EagleFeederAnimatedWebp,
    "EagleFeederMp4": EagleFeederMp4,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EagleFeederPng": "EagleFeeder (PNG)",
    "EagleFeederAnimatedWebp": "EagleFeeder (AnimatedWEBP)",
    "EagleFeederMp4": "EagleFeeder (MP4)",
}
