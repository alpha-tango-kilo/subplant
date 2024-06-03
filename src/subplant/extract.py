import re
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

import pyron
from pymkv import MKVFile, MKVTrack

from subplant import SubtitleMetadata, VideoMetadata

SEASON_EPISODE_REGEX = re.compile(r"S(\d{2,})E(\d{2,})")
SUBTITLE_CODEC_EXTENSIONS = {
    "SubStationAlpha": ".ass",
}


def guess_season_episode_from(file_name: str) -> tuple[int, int] | None:
    if match := SEASON_EPISODE_REGEX.search(file_name):
        season_str, episode_str = match.group(1, 2)
        return int(season_str), int(episode_str)


def process(mkv_path: Path, root_output_dir: Path):
    mkv = MKVFile(mkv_path)
    # TODO: handle no season/episode info
    season, episode = guess_season_episode_from(mkv_path.stem)
    output_dir = root_output_dir / f"S{season:02}E{episode:02}"
    if output_dir.is_dir():
        shutil.rmtree(str(output_dir))
    output_dir.mkdir(parents=True, exist_ok=False)

    # Get subtitle tracks, build map {Path => (file_name, SubtitleMetadata)}
    sub_map = {}
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
        extracted_sub_path = output_dir / f"{sub_metadata.lang}{sub_extension}"
        print(f"Extracting {extracted_sub_path.relative_to(root_output_dir)}")
        mkvextract_tracks(
            mkv_path,
            sub_track.track_id,
            extracted_sub_path,
        )
        sub_map[extracted_sub_path] = (extracted_sub_path.name, sub_metadata)

    # Build VideoMetadata
    video_metadata = VideoMetadata(season, episode, subs=dict(sub_map.values()))
    metadata_file = output_dir / "metadata.ron"
    metadata_file.write_text(pyron.to_string(video_metadata) + "\n")

    # TODO: extract attachments


def name_for_file(mkv_path: Path, sub_track: MKVTrack) -> Path:
    assert sub_track.track_type == "subtitles"
    mkv_path.with_suffix(SUBTITLE_CODEC_EXTENSIONS[sub_track.track_codec])


def mkvextract_tracks(mkv_path: Path, track_id: int, destination: Path):
    subprocess.check_call(
        [
            "mkvextract",
            "tracks",
            "--quiet",
            str(mkv_path),
            f"{track_id}:{destination}",
        ]
    )


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
