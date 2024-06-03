from pathlib import Path
import subprocess
from typing import Protocol

from subplant import FONT_MIME_TYPE, METADATA_FILE_NAME, VideoMetadata


class ImplantArgs(Protocol):
    work_path: Path
    subplant_package: Path


def process(mkv_path: Path, subplant_package: Path) -> None:
    # Incredible name, I know (shut up)
    output_file = mkv_path.with_stem(f"{mkv_path.stem}+")
    output_file.unlink(missing_ok=True)
    metadata_txt = (subplant_package / METADATA_FILE_NAME).read_text()
    metadata = VideoMetadata.loads(metadata_txt)

    # Generate args to implant attachments
    attachment_args = []
    for attachment in (subplant_package / "attachments").glob("*"):
        attachment_args.extend(
            [
                "--attachment-mime-type",
                FONT_MIME_TYPE,
                "--attach-file",
                str(attachment),
            ]
        )

    # Generate args to implant subs

    subprocess.check_call(
        [
            "mkvmerge",
            "--quiet",
            "-o",
            str(output_file),
            mkv_path,
            *attachment_args,
        ]
    )


def implant(args: ImplantArgs) -> None:
    if (
        args.work_path.is_dir()
        and args.subplant_package.is_dir()
        and args.subplant_package.suffix != ".subplant"
    ):
        # Multi mode
        pass
    elif (
        args.work_path.is_file()
        and args.subplant_package.is_dir()
        and args.subplant_package.suffix == ".subplant"
    ):
        # Single mode
        process(args.work_path, args.subplant_package)
    else:
        raise ValueError(
            "couldn't work out if you want to operate on one file or many files"
        )
