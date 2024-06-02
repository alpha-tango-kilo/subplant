#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path

from subplant import __version__ as VERSION
from subplant.extract import extract

"""
TODO: dir structure
TODO: can I see which attachments are used by which subtitle lang?

file_stem/
    info.ron
    sub_lang.ext
    attachments/
        blah.ttf

TODO: info file
Episode {
    season: int
    episode: int
    subs: {
        sub_file: {
            // NOTE: you can change anything here
            lang: str
            track_name: str
            default: bool
            etc.
        }
    }
}
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
