from dataclasses import dataclass
from typing import Any, TypedDict

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"


@dataclass(frozen=True)
class SubtitleMetadata:
    lang: str
    track_name: str
    default: bool
    forced: bool


@dataclass
class VideoMetadata:
    season: int
    episode: int
    # actually 👇 a path, but pyron doesn't support those
    subs: dict[str, SubtitleMetadata]


class AttachmentMetadata(TypedDict):
    content_type: str
    description: str
    file_name: str
    id: int
    properties: dict[str, Any]
    size: int
