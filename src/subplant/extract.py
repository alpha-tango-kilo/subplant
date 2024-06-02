import subprocess
from pathlib import Path
from typing import Protocol

import cattrs
import pyron
from pymkv import MKVFile, MKVTrack

from subplant import SubtitleMetadata, VideoMetadata

SUBTITLE_CODEC_EXTENSIONS = {
    "SubStationAlpha": ".ass",
}


def process(mkv_path: Path):
    mkv = MKVFile(mkv_path)
    # Guess season & episode
    # Get subtitle tracks, build map {Path => (file_name, SubtitleMetadata)}
    # Build VideoMetadata
    # Build directory structure
    # Extract attachments
    # Extract subs


def name_for_file(mkv_path: Path, sub_track: MKVTrack) -> Path:
    assert sub_track.track_type == "subtitles"
    mkv_path.with_suffix(SUBTITLE_CODEC_EXTENSIONS[sub_track.track_codec])


def mkvextract_tracks(mkv_path: Path, track_id: int, destination: Path):
    subprocess.check_call(
        ["mkvextract", "tracks", str(mkv_path), f"{track_id}:{destination}"]
    )


class ExtractArgs(Protocol):
    mkv_file: Path


def extract(args: ExtractArgs) -> None:
    # mkv = MKVFile(args.mkv_file)
    # TODO: do something sensible with multiple sub tracks
    # (sub_track,) = [
    #     track for track in mkv.tracks if track.track_type == "subtitles"
    # ]
    # mkvextract_tracks(
    #     args.mkv_file,
    #     sub_track.track_id,
    #     args.mkv_file.with_suffix(
    #         SUBTITLE_CODEC_EXTENSIONS[sub_track.track_codec]
    #     ),
    # )
    sub_file = SubtitleMetadata("und", "Commie", False)
    sub_file_2 = cattrs.structure(
        pyron.loads(pyron.to_string(sub_file)), SubtitleMetadata
    )
    assert sub_file == sub_file_2
    vid_file = VideoMetadata(1, 1, {".": sub_file})
    stringified = pyron.to_string(vid_file)
    print(stringified)
    vid_file_2 = cattrs.structure(pyron.loads(stringified), VideoMetadata)
    print(pyron.to_string(vid_file_2))
    assert vid_file == vid_file_2
