import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

import pyron
from pymkv import MKVFile

from subplant import (
    FONT_MIME_TYPE,
    METADATA_FILE_NAME,
    AttachmentMetadata,
    SubtitleMetadata,
    VideoMetadata,
    get_video_resolution,
)

SEASON_EPISODE_REGEX = re.compile(r"S(\d{2,})E(\d{2,})")
SUBTITLE_CODEC_EXTENSIONS = {
    "SubStationAlpha": ".ass",
}


def guess_season_episode_from(file_name: str) -> tuple[int, int] | None:
    if match := SEASON_EPISODE_REGEX.search(file_name):
        season_str, episode_str = match.group(1, 2)
        return int(season_str), int(episode_str)


def process(mkv_path: Path, root_output_dir: Path) -> None:
    mkv = MKVFile(mkv_path)
    if tup := guess_season_episode_from(mkv_path.stem):
        season, episode = tup
    else:
        season = None
        episode = None

    output_dir = root_output_dir / f"S{season:02}E{episode:02}.subplant"
    if output_dir.is_dir():
        shutil.rmtree(str(output_dir))
    output_dir.mkdir(parents=True, exist_ok=False)

    # Get subtitle tracks
    sub_map = {}
    sub_extract_args = []
    for sub_track in mkv.tracks:
        if sub_track.track_type != "subtitles":
            continue
        sub_metadata = SubtitleMetadata(
            lang=sub_track.language,
            track_name=sub_track.track_name,
            default=sub_track.default_track or False,
            forced=sub_track.forced_track or False,
        )
        sub_extension = SUBTITLE_CODEC_EXTENSIONS.get(sub_track.track_codec, "")
        extracted_sub_path = (
            output_dir
            / f"{sub_track.track_id}-{sub_metadata.lang}{sub_extension}"
        )
        sub_map[extracted_sub_path.name] = sub_metadata
        sub_extract_args.append(f"{sub_track.track_id}:{extracted_sub_path}")

    # Extract subtitles
    print(f"Extracting {len(sub_map)} subtitle(s)")
    subprocess.check_call(
        [
            "mkvextract",
            "tracks",
            "--quiet",
            str(mkv_path),
            *sub_extract_args,
        ]
    )

    # Extract attachments
    attachments_dir = output_dir / "attachments"
    # Build args for mkvextract, pulling all the fonts out in one go
    args = [
        f"{attachment['id']}:{attachments_dir / attachment['file_name']}"
        for attachment in get_attachments(mkv_path)
        if attachment["content_type"] == FONT_MIME_TYPE
    ]
    print(f"Extracting {len(args)} attachment(s)")
    subprocess.check_call(
        ["mkvextract", "attachments", "--quiet", str(mkv_path), *args]
    )

    # Build VideoMetadata
    video_metadata = VideoMetadata(
        season, episode, get_video_resolution(mkv_path), sub_map
    )
    metadata_file = output_dir / METADATA_FILE_NAME
    metadata_file.write_text(pyron.to_string(video_metadata) + "\n")


def get_attachments(mkv_path: Path) -> list[AttachmentMetadata]:
    json_info = subprocess.check_output(["mkvmerge", "-J", mkv_path])
    all_metadata = json.loads(json_info)
    assert isinstance(all_metadata, dict)
    return all_metadata.get("attachments", [])


class ExtractArgs(Protocol):
    work_path: Path
    output_dir: Path


def extract(args: ExtractArgs) -> None:
    if args.work_path.is_file():
        print(f"Processing {args.work_path.name}")
        process(args.work_path, args.output_dir)
    elif args.work_path.is_dir():
        for mkv_path in args.work_path.glob("*.mkv"):
            print(f"Processing {mkv_path.name}")
            process(mkv_path, args.output_dir)
    else:
        raise IOError("expected file/dir for work_path")
