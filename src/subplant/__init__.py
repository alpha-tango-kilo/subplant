from dataclasses import dataclass
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
