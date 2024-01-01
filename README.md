# H.265 Batch Convert

A simple python script to batch convert videos to H.265

## Requirements:

 - tqdm
 - click
 - ffmpeg

## Usage:

```
python3 convert.py <path> [--recursive] [--file-extension <extension>] [--dry-run] [--nondescructive] [--all-exts] [--trust-extensions]
```

Defaults:
 - File extensions: mp4, m4a, mkv, ts, avi
 - Not recursive
 - Not a dry run
 - Destructive
 - Validates scanned files

Equivalent command to defaults:

```
python3 convert.py <path> --file-extension "mp4,m4a,mkv,ts,avi"
```

## To-do:

 - [x] ~~Support multiple extensions~~ Validated as of 12/29/2023
 - [ ] Add in support for AV1
 - [ ] Better HW acceleration support
 - [x] ~~Validate Windows support~~ Cautiously saying its implemented as of 12/29/2023
 - [ ] Validate macOS support
 - [ ] Ensure support on non-Nvidia GPUs

## Sources

Original script from [asdfgeoff](https://gist.github.com/asdfgeoff/62b155ee4ea6b81c9175c39ec2d22e9a)
