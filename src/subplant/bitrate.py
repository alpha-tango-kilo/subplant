from pathlib import Path
from typing import Protocol

from pymediainfo import MediaInfo


class BitrateArgs(Protocol):
    work_path: Path


def process_one(file: Path) -> None:
    def to_kbps(bps: int) -> int:
        return bps // 1024

    media = MediaInfo.parse(file)
    assert isinstance(media, MediaInfo)

    print(f"{file.name}:")
    for index, track in enumerate(media.video_tracks, start=1):
        assert isinstance(track.bit_rate, int)
        print(
            f"  Video #{index}:     "
            f"{to_kbps(track.bit_rate)} kb/s ({track.bit_depth}-bit colour)"
        )
    for index, track in enumerate(media.audio_tracks, start=1):
        assert isinstance(track.bit_rate, int)
        print(
            f"  Audio #{index} ({track.language}): "
            f"{to_kbps(track.bit_rate)} kb/s {track.format}"
        )


def bitrate(args: BitrateArgs) -> None:
    if args.work_path.is_file():
        process_one(args.work_path)
    elif args.work_path.is_dir():
        # Note: pymediainfo does support other extensions, but .glob() doesn't expand {}
        for file in sorted(args.work_path.glob("*.mkv")):
            process_one(file)
    else:
        raise ValueError("work_path must be to file or folder")
