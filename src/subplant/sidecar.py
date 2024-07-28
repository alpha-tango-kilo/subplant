from pathlib import Path
from typing import Protocol

from subplant import discover_implant_work


def process_one(mkv_path: Path, subplant_package: Path) -> None:
    pass


class SidecarArgs(Protocol):
    work_path: Path
    subplant_package: Path


def sidecar(args: SidecarArgs) -> None:
    # Note: identical to implant.implant, should I make an abstraction for this?
    if (
        args.work_path.is_dir()
        and args.subplant_package.is_dir()
        and args.subplant_package.suffix != ".subplant"
    ):
        # Multi mode
        for target, subplant in discover_implant_work(
            args.subplant_package, args.work_path
        ):
            process_one(target, subplant)

    elif (
        args.work_path.is_file()
        and args.subplant_package.is_dir()
        and args.subplant_package.suffix == ".subplant"
    ):
        # Single mode
        process_one(args.work_path, args.subplant_package)
    else:
        raise ValueError(
            "couldn't work out if you want to operate on one file or many files"
        )
