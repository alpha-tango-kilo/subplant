from pathlib import Path
from typing import Protocol

from pymediainfo import MediaInfo


class BitrateArgs(Protocol):
    work_path: Path


def process_one(file: Path) -> None:
    media = MediaInfo.parse(file)
    assert isinstance(media, MediaInfo)

    # TODO: convert bits per second into something human readable
    print(f"{file.name}:")
    for index, track in enumerate(media.video_tracks):
        print(
            f"  Video #{index}: {track.bit_rate} b/s ({track.bit_depth}-bit colour)"
        )
    for index, track in enumerate(media.audio_tracks):
        print(
            f"  Audio #{index} ({track.language}): {track.bit_rate} b/s {track.format}"
        )


def bitrate(args: BitrateArgs) -> None:
    if args.work_path.is_file():
        process_one(args.work_path)
    elif args.work_path.is_dir():
        print("unsupported")
    else:
        raise ValueError("work_path must be to file or folder")
