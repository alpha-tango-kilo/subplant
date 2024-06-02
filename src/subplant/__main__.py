#!/usr/bin/env python3

import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Protocol

# https://gitbib.github.io/pymkv2/
from pymkv import MKVFile

from . import __version__ as VERSION


class ExtractArgs(Protocol):
    mkv_file: Path


def mkvextract_tracks(mkv_path: Path, track_id: int, destination: Path):
    subprocess.check_call(
        ["mkvextract", "tracks", str(mkv_path), f"{track_id}:{destination}"]
    )


def extract(args: ExtractArgs) -> None:
    mkv = MKVFile(args.mkv_file)
    # TODO: do something sensible with multiple sub tracks
    (sub_track,) = [track for track in mkv.tracks if track.track_type == "subtitles"]
    mkvextract_tracks(
        args.mkv_file,
        sub_track.track_id,
        args.mkv_file.with_suffix(".ass"),
    )


def clap() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"v{VERSION}",
        help="print the program's version and exit",
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # Note: keep in sync with ExtractArgs
    extract_subcommand = subparsers.add_parser(
        "extract", help="get subs out of a movie/series"
    )
    extract_subcommand.add_argument(
        "mkv_file",
        type=Path,
        help="the file to get stuff from",
    )

    args = parser.parse_args()
    match args.subcommand:
        case None:
            print("not yet supported")
        case "extract":
            extract(args)


if __name__ == "__main__":
    clap()
