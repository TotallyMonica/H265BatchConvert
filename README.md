# H.265 Batch Convert

A simple python script to batch convert videos to H.265

## Requirements:

 - tqdm
 - click
 - ffmpeg

## Usage:

```
python3 convert.py <path> [--recursive] [--file-extension <extension>] [--dry-run] [--nondescructive]
```

Defaults:
 - File extension: mp4
 - Not recursive
 - Not a dry run
 - Destructive

Equivalent command to defaults:

```
python3 convert.py <path> --file-extension "mp4"
```

## To-do:

 - [ ] Support multiple extensions
 - [ ] Add in support for AV1
 - [ ] Better HW acceleration support

## Sources

Original script from [asdfgeoff](https://gist.github.com/asdfgeoff/62b155ee4ea6b81c9175c39ec2d22e9a)
