#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path

from subplant import __version__ as VERSION
from subplant.extract import extract
from subplant.implant import implant

"""
TODO: can I see which attachments are used by which subtitle lang?
TODO: aligning timing...
TODO: rescaling subtitle size if resolution changes
"""


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
        help="the folder to create all the loose files in",
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

    args = parser.parse_args()
    match args.subcommand:
        case None:
            print("not yet supported")
        case "extract":
            extract(args)
        case "implant":
            implant(args)


if __name__ == "__main__":
    clap()
