#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path

from subplant import __version__ as VERSION
from subplant.bitrate import bitrate
from subplant.check import check
from subplant.extract import extract
from subplant.implant import implant
from subplant.sidecar import sidecar


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

    # Note: keep in sync with extract.ExtractArgs
    extract_subcommand = subparsers.add_parser(
        "extract", help="get subs out of a movie/series"
    )
    extract_subcommand.add_argument(
        "work_path",
        type=Path,
        help="the file or folder to get stuff from",
    )
    extract_subcommand.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("."),
        metavar="DIR",
        help="the folder to create subplant packages in",
    )

    # Note: keep in sync with implant.ImplantArgs
    implant_subcommand = subparsers.add_parser(
        "implant",
        help="put a .subplant package into summink",
    )
    implant_subcommand.add_argument(
        "work_path",
        type=Path,
        help="the file or folder with the video files",
    )
    implant_subcommand.add_argument(
        "subplant_package",
        type=Path,
        help="the .subplant directory, or a directory containing them",
    )

    # Note: keep in sync with bitrate.BitrateArgs
    bitrate_subcommand = subparsers.add_parser(
        "bitrate",
        help="print bitrate information for video & audio tracks",
    )
    bitrate_subcommand.add_argument(
        "work_path",
        type=Path,
        help="the file or folder with the video files",
    )

    # Note: keep in sync with sidecar.SidecarArgs
    sidecar_subcommand = subparsers.add_parser(
        "sidecar",
        help="map a .subplant package into sidecar files",
    )
    sidecar_subcommand.add_argument(
        "work_path",
        type=Path,
        help="the file or folder with the video files",
    )
    sidecar_subcommand.add_argument(
        "subplant_package",
        type=Path,
        help="the .subplant directory, or a directory containing them",
    )
    mode_group = sidecar_subcommand.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-s",
        "--symlink",
        action="store_true",
        help="symlink files from .subplant next to target",
    )
    mode_group.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="copy files from .subplant next to target (default)",
    )

    check_subcommand = subparsers.add_parser(
        "check",
        help="check for missing attachments",
    )
    check_subcommand.add_argument(
        "subplant_package",
        type=Path,
        help="the .subplant directory, or a directory containing them",
    )

    args = parser.parse_args()
    match args.subcommand:
        case "extract":
            extract(args)
        case "implant":
            implant(args)
        case "sidecar":
            sidecar(args)
        case "bitrate":
            bitrate(args)
        case "check":
            check(args)
        case _:
            parser.print_usage()


if __name__ == "__main__":
    clap()
