# `subplant` - extract & implant subtitles

A relatively quick & dirty CLI tool to pull higher quality subtitles from lower quality videos and stick them into higher quality videos.
**This tool is build on top of [MKVToolnix](https://mkvtoolnix.download/) and requires its commandline utilities `mkvmerge` & `mkvextract` to be available in `$PATH`**

Supports:
  - `.mkv` files with `.ass` subtitles, with attachments
  - Processing entire seasons at once (needs file names with S01E23 information in)
  - Customising the following properties on implant:
    - Subtitle track name
    - Subtitle track language
    - Make subtitle track default
    - Mark subtitle track as forced

Does not support:
  - Rescaling subtitles. Resolution of source & target must match, else an error will prevent you implanting
  - Offsetting subtitle timing
  - Anything other than MKV files and ASS subtitles

## How it works

Install `subplant` by running `pip install subplant@git+https://codeberg.org/alpha-tango-kilo/subplant`

To get a specific released version, add `@v0.1.0` (for example) to the end of the URL, without spaces

### Step 1: extract subtitles

```
usage: subplant extract [-h] [-o DIR] work_path

positional arguments:
  work_path             the file or folder to get stuff from

options:
  -h, --help            show this help message and exit
  -o DIR, --output-dir DIR
                        the folder to create subplant packages in
```

First, you find a video you want to extract the subtitles from, and extract them.
If you don't specify an output directory, `.subplant` packages will be created in your current working directory

```shell
subplant extract "JoJo no Kimyou na Bouken - S01E18.mkv"
```

This will create a package (folder) called `S01E18.subplant`, which will have a structure somewhat like this:

```
S01E18.subplant/
    attachments/
        foo.ttf
        bar.otf
    2-und.ass
    3-jp.ass
    metadata.ron
```

⚠ Do not rename or change the locations of any files in the subplant package

The `attachments` subfolder won't be present if there were no font attachments to extract

### Step 2: customisation (optional)

To customise how the subtitles are implanted into your target video, you edit the `metadata.ron` file, which will looking something like this:

```ron
VideoMetadata(
    season: 1,
    episode: 18,
    resolution: (1920, 1080),
    subs: {
        "2-und.ass": SubtitleMetadata(
            lang: "und",
            track_name: None,
            default: true,
            forced: false,
        ),
        "3-jp.ass": SubtitleMetadata(
            lang: "jp",
            track_name: None,
            default: false,
            forced: false,
        ),
    },
)
```

You are allowed to change the fields within each `SubtitleMetadata`: changing the language a subtitle is marked as, giving the tracks a name, and setting a default track.
Setting multiple default tracks will result in implanting failing

### Step 3: implant

```
usage: subplant implant [-h] work_path subplant_package

positional arguments:
  work_path         the file or folder with the video files
  subplant_package  the .subplant directory, or a directory containing them

options:
  -h, --help        show this help message and exit
```

Now it's go time:

```shell
subplant implant "JoJo no Kimyou na Bouken - S01E18 (higher quality version).mkv" S01E18.subplant
```

Currently there's no way to change the name of the produced MKV file, it'll be the name of the original file with "+" added to the end

You'll see the output of `mkvmerge` as it runs to give an indication of progress
