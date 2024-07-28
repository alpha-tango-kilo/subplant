import shutil
from enum import StrEnum, auto
from pathlib import Path
from typing import Protocol

from subplant import (
    METADATA_FILE_NAME,
    SubtitleMetadata,
    VideoMetadata,
    discover_implant_work,
)


class SidecarMode(StrEnum):
    COPY = auto()
    SYMLINK = auto()

    @classmethod
    def from_args(cls, args: "SidecarArgs") -> "SidecarMode":
        if args.symlink:
            return SidecarMode.SYMLINK
        elif args.copy:
            return SidecarMode.COPY
        else:
            # Default
            return SidecarMode.COPY


def gen_sidecar_path(
    mkv_path: Path, sub_ext: str, sub_meta: SubtitleMetadata
) -> Path:
    new_suffix = ""
    if sub_meta.forced:
        new_suffix += ".forced"
    if sub_meta.default:
        new_suffix += ".default"
    new_suffix += f".{sub_meta.lang}{sub_ext}"
    assert new_suffix.startswith(".")
    return mkv_path.with_suffix(new_suffix)


def process_one(
    mkv_path: Path, subplant_package: Path, mode: SidecarMode
) -> None:
    if (subplant_package / "attachments").exists():
        print(f"{subplant_package.name} has attachments, skipping")
        return
    subplant_meta = VideoMetadata.loads(
        (subplant_package / METADATA_FILE_NAME).read_text()
    )
    for sub_path, sub_meta in subplant_meta.subs.items():
        sub_path = subplant_package / sub_path
        dest_path = gen_sidecar_path(mkv_path, sub_path.suffix, sub_meta)

        match mode:
            # TODO: remove common prefixes in paths
            case SidecarMode.COPY:
                shutil.copy(sub_path, dest_path)
                print(f"Copied {sub_path} to {dest_path}")
            case SidecarMode.SYMLINK:
                dest_path.symlink_to(sub_path)
                print(f"Symlinked {sub_path} to {dest_path}")
            case _:
                raise NotImplementedError(f"unsupported mode {mode}")


class SidecarArgs(Protocol):
    work_path: Path
    subplant_package: Path
    # Already checked that both aren't set
    copy: bool
    symlink: bool


def sidecar(args: SidecarArgs) -> None:
    mode = SidecarMode.from_args(args)

    # TODO: ✨ print statements
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
            process_one(target, subplant, mode)

    elif (
        args.work_path.is_file()
        and args.subplant_package.is_dir()
        and args.subplant_package.suffix == ".subplant"
    ):
        # Single mode
        process_one(args.work_path, args.subplant_package, mode)
    else:
        raise ValueError(
            "couldn't work out if you want to operate on one file or many files"
        )
