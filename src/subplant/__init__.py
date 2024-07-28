import json
import re
import subprocess
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, TypedDict

import cattrs
import pyron

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"

FONT_MIME_TYPE = "application/x-truetype-font"
METADATA_FILE_NAME = "metadata.ron"
SEASON_EPISODE_REGEX = re.compile(r"S(\d{2,})E(\d{2,})")


@dataclass(frozen=True)
class SubtitleMetadata:
    lang: str
    track_name: str | None
    default: bool
    forced: bool


@dataclass
class VideoMetadata:
    season: int | None
    episode: int | None
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


def guess_season_episode_from(file_name: str) -> tuple[int, int] | None:
    if match := SEASON_EPISODE_REGEX.search(file_name):
        season_str, episode_str = match.group(1, 2)
        return int(season_str), int(episode_str)


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


ImplantWork = namedtuple("ImplantWork", ("target", "subplant"))


def discover_implant_work(
    subplants_dir: Path, target_dir: Path
) -> Generator[ImplantWork]:
    videos = sorted(
        (guess_season_episode_from(path.stem), path)
        for path in target_dir.glob("*.mkv")
    )
    subplants = sorted(
        (guess_season_episode_from(path.stem), path)
        for path in subplants_dir.glob("*.subplant")
    )
    for ((vid_season, vid_epsiode), vid_path), (
        (subs_season, subs_episode),
        sub_path,
    ) in zip(videos, subplants):  # type: ignore
        if vid_season == subs_season and vid_epsiode == subs_episode:
            print(f"Implenting {sub_path} into {vid_path}")
            yield ImplantWork(vid_path, sub_path)
        else:
            raise ValueError("couldn't line up videos and subplant packages")
