import click
from pathlib import Path
from subprocess import call, check_output, CalledProcessError
from tqdm import tqdm
import sys
import find
import re

def convert(files):
    exp = re.compile(' - \\d+p')
    for file_path in tqdm(files, desc='Converting files', unit='videos'):
        file = Path(file_path)
        no_extension = file.name.split('.')[0]
        if exp.search(no_extension):
            no_extension = exp.split(no_extension)[0]
        destination = file.parent / (no_extension + " - 1080p" + file.suffix)

        codec_cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=nw=1:nk=1 "{file}"'
        codec = check_output(call(codec_cmd, shell=True))

        convert_cmd = f'ffmpeg -i "{file}" -vf "scale=1920:-2" -map_metadata 0 -c:v "{codec}" -c:a copy -c:s copy "{destination}"'
        conversion_return_code = call(convert_cmd, shell=True)

def simulate(files):
    exp = re.compile(' - \\d+p')
    for file_path in tqdm(files, desc='Converting files', unit='videos'):
        file = Path(file_path)
        no_extension = file.name.split('.')[0]
        if exp.search(no_extension):
            no_extension = exp.split(no_extension)[0]
        destination = file.parent / (no_extension + " - 1080p" + file.suffix)

        codec_command = f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=nw=1:nk=1 "{file}"'
        codec = check_output(call(codec_cmd, shell=True))

        convert_cmd = f'ffmpeg -i "{file}" -vf "scale=1920:-2" -map_metadata 0 -c:v "{codec}" -c:a copy -c:s copy "{destination}"'
        print(convert_cmd)

@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', is_flag=True, help='Recursive')
@click.option('--file-ext', help='File format to process')
@click.option('--dry-run', is_flag=True, help='Simulate running')
@click.option('--all-exts', is_flag=True, help='Use all of the extensions in the provided directory')
@click.option('--trust-extensions', is_flag=True, help='Trust the file extensions')
def main(directory, file_ext='mp4,m4a,mkv,ts,avi', recursive=False, dry_run=False, all_exts=False, trust_extensions=False):
    if all_exts:
        exts = find.FileExtensions(directory, recursive=recursive)
        file_exts=[ext for ext in tqdm(exts, desc='Getting extensions', unit='files')]
    else:
        file_exts = file_ext.split(",")

    files = find.VideoFileIterator(directory, extensions=file_exts, trust_extensions=trust_extensions)

    video_files = [file for file in tqdm(files, desc='Getting video files', unit='files')]

    check_resolution_cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "{fp}"'
    resolutions = []
    files_to_process = []
    for fp in tqdm(files, desc='Checking metadata', unit='videos'):
        try:
            resolution = check_output(check_resolution_cmd.format(fp=fp), shell=True).strip().decode('UTF-8')
            resolutions.append(resolution)
            if int(resolution) > 1920:
                files_to_process.append(fp)
        except CalledProcessError:
            print(f"Warning: Couldn't open video file {fp} for parsing")
        except ValueError:
            print(f"Warning: Couldn't get resolution for video file {fp}")

    print(f'\nTOTAL FILES FOUND ({len(video_files)})')
    print(f'FILES TO PROCESS ({len(files_to_process)}):', [fp for fp in files_to_process], '\n')

    if len(files_to_process) == 0:
        raise click.Abort
    else:
        click.confirm('Do you want to continue?', abort=True)

    if dry_run:
        simulate(files_to_process)
    else:
        convert(files_to_process)

if __name__ == "__main__":
    main()
