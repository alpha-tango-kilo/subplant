import itertools
import re
from pathlib import Path

from fontTools.ttLib import TTFont

from subplant import VideoMetadata

FONT_REGEX = re.compile(r"\\fn(?P<font_name>[^\\]+)\\")


def get_font_names(attachments_dir: Path) -> set[str]:
    return {
        next(
            record.toStr()
            for record in TTFont(font_file)["name"].names  # type: ignore
            if record.nameID == 1
        )
        for font_file in itertools.chain(
            attachments_dir.glob("*.ttf"),
            attachments_dir.glob("*.TTF"),
            attachments_dir.glob("*.otf"),
            attachments_dir.glob("*.OTF"),
        )
    }


def process_one(subplant_path: Path) -> None:
    subplant = VideoMetadata.loads((subplant_path / "metadata.ron").read_text())
    attachments = get_font_names(subplant_path / "attachments")
    if len(attachments) > 0:
        print(f"{subplant_path.stem}: has {sorted(attachments)}")
    uses = set()
    missing = set()
    for sub in subplant.subs.keys():
        sub_path = Path(subplant_path, sub)
        ass = sub_path.read_text()
        for re_match in FONT_REGEX.finditer(ass):
            font_name: str = re_match.group("font_name")
            uses.add(font_name)
            if font_name not in attachments and "Arial" not in font_name:
                missing.add(font_name)
    uses -= missing
    # if len(uses) > 0:
    #     print(f"{subplant_path.stem}: uses {sorted(uses)}")
    if len(missing) > 0:
        print(f"{subplant_path.stem}: is missing {sorted(missing)}")


def check(args) -> None:
    if args.subplant_package.suffix == ".subplant":
        process_one(args.subplant_package)
    else:
        for subplant in sorted(args.subplant_package.glob("*.subplant")):
            process_one(subplant)
