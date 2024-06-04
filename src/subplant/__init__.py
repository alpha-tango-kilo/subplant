import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

import cattrs
import pyron

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"

FONT_MIME_TYPE = "application/x-truetype-font"
METADATA_FILE_NAME = "metadata.ron"


@dataclass(frozen=True)
class SubtitleMetadata:
    lang: str
    track_name: str | None
    default: bool
    forced: bool


@dataclass
class VideoMetadata:
    season: int
    episode: int
    resolution: tuple[int, int]
    # actually 👇 a path, but pyron doesn't support those
    subs: dict[str, SubtitleMetadata]

    @classmethod
    def loads(cls, s: str) -> "VideoMetadata":
        return cattrs.structure(pyron.loads(s), cls)


class AttachmentMetadata(TypedDict):
    content_type: str
    description: str
    file_name: str
    id: int
    properties: dict[str, Any]
    size: int


def get_video_resolution(mkv_path: Path) -> tuple[int, int]:
    json_info = subprocess.check_output(["mkvmerge", "-J", mkv_path])
    all_metadata = json.loads(json_info)
    assert isinstance(all_metadata, dict)
    for track in all_metadata["tracks"]:
        properties = track.get("properties", {})
        resolution = properties.get(
            "display_dimensions", None
        ) or properties.get("pixel_dimensions", None)
        if resolution:
            width, height = resolution.split("x", 1)
            return int(width), int(height)
    raise ValueError(f"unable to find resolution of {mkv_path}")
