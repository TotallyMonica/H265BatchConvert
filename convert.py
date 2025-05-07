#!/usr/bin/env python3
import click
from pathlib import Path
from subprocess import call, check_output, CalledProcessError, run
from tqdm import tqdm
import sys
import find
import json

def encoders(codec: str="hevc"):
    if codec.lower() == "hevc" or codec.lower() == "h265" or codec.lower() == "h.265" or codec.lower() == "x265":
        return ("hevc_nvenc", "hevc_amf", "hevc_qsv", "hevc_vaapi", "hevc_v4l2m2m", "hevc_mf", "libx265")
    elif codec.lower() == "av1":
        return ("libsvtav1", "av1_nvenc", "av1_qsv", "av1_amf", "av1_vaapi", "libaom-av1")
    elif codec.lower() == "h.264" or codec.lower() == "h264" or codec.lower() == "x264":
        return ("h264_nvenc", "h264_amf", "h264_qsv", "h264_vaapi", "h264_v4l2m2m", "libx264")

def decoders(codec: str="hevc"):
    if codec.lower() == "hevc" or codec.lower() == "h265" or codec.lower() == "h.265":
        return ("hevc_cuvid", "hevc_qsv", "hevc_v4l2m2m", "hevc")
    elif codec.lower() == "av1":
        return ("libaom-av1", "av1_cuvid", "av1_qsv", "av1", "libdav1d")

def check_dependencies():
    dependencies = ("ffmpeg", "ffprobe")
    windows_dependencies = ("powershell",)

def delete_file(target: str, dry_run: bool=False):
    command = ''
    if sys.platform.startswith("linux"):
        command = f'rm "{target}"'
    elif sys.platform.startswith("win32"):
        command = f"""powershell -Command "Delete-File '{target}'" """

    return command

# OS agnostic way to create files
def create_file(reference: str, new_file: str, dry_run: bool=False):
    command = ''
    if sys.platform.startswith("linux"):
        command = f'touch -r "{reference}" "{new_file}"'
    elif sys.platform.startswith("win32"):
        command = f"""powershell -Command "(Get-ChildItem '{new_file}').CreationTime = (Get-ChildItem '{reference}').CreationTime; (Get-ChildItem '{new_file}').LastAccessTime = (Get-ChildItem '{reference}').LastAccessTime; (Get-ChildItem '{new_file}').LastWriteTime = (Get-ChildItem '{reference}').LastWriteTime" """

    return command

# OS agnostic move command
def move_file(source: str, dest: str, dry_run: bool=False):
    command = ''
    if sys.platform.startswith("linux"):
        command = f'mv "{source}" "{dest}"'
    elif sys.platform.startswith("win32"):
        command = f"""powershell -Command "Move-Item '{source}' '{dest}'" """

    return command

def convert(files, destructive, target_codec="hevc"):
    known_good = ""
    text_subtitles = ("ssa", "ass", "hdmv_text_subtitle", "mov_text", "srt", "subrip", "dvb_teletext")
    for file_path in tqdm(files, desc='Converting files', unit='videos'):
        file = Path(file_path)

        # Probe media information from source file
        probe_cmd = ["ffprobe", "-v", "error", "-of", "json", file, "-of", "json", "-show_format", "-show_streams"]
        probe_cmd_output = run(probe_cmd, capture_output=True)
        video_streams = []
        audio_streams = []
        subtitle_streams = []

        if probe_cmd_output.returncode == 0:
            parsed_output = json.loads(probe_cmd_output.stdout)
            for stream in parsed_output['streams']:
                if stream['codec_type'].lower() == 'subtitle':
                    subtitle_streams.append(stream)
                elif stream['codec_type'].lower() == 'audio':
                    audio_streams.append(stream)
                elif stream['codec_type'].lower() == 'video':
                    video_streams.append(stream)

        src_ext = file_path.split(".")[-1]
        temp_file = file.parent / f'temp_ffmpeg.mp4'

        # Right now, we're relying on the user having extensions that match the container.
        # We do have a hard dependency for `ffmpeg` and `ffprobe`, this likely could be mod
        is_source_mp4 = src_ext == 'mp4'
        if not is_source_mp4:
            new_file_name = str(file).replace(src_ext, "mp4")
        else:
            new_file_name = str(file)

        if known_good:
            convert_cmd = ['ffmpeg', '-i', file, '-vcodec', known_good, '-acodec', 'copy', '-map_metadata', '0', '-strict', '-2', temp_file]

            conversion_return_code = run(convert_cmd, capture_output=True)
        else:
            for codec in encoders(target_codec):
                convert_cmd = ['ffmpeg', '-i', file, '-vcodec', codec, '-acodec', 'copy', '-map_metadata', '0', '-strict', '-2', temp_file]

                conversion_return_code = run(convert_cmd, capture_output=True)

                if conversion_return_code.returncode == 0:
                    known_good = codec
                    break

        # Ensure the conversion succeeded
        if conversion_return_code.returncode == 0:
            call(create_file(file, temp_file), shell=True)

            # Ultimately, extension doesn't matter if we're destructive
            if destructive:
                call(delete_file(file), shell=True)
                call(move_file(temp_file, file), shell=True)

            # We know we're not destructive, are we mp4?
            elif is_source_mp4:
                mp4_extension = '.mp4'
                nondestructive_extension = f'_{target_codec}.mp4'
                call(move_file(temp_file, f"{new_file_name.replace(mp4_extension, nondestructive_extension)}"), shell=True)

            # We aren't mp4 and we aren't destructive, move temporary file to final file name as MP4 extension
            else:
                call(move_file(temp_file, new_file_name), shell=True)

def simulate(files, destructive, target_codec="hevc"):
    known_good = ""
    for file_path in tqdm(files, desc='Converting files', unit='videos'):
        file = Path(file_path)
        src_ext = file_path.split(".")[-1]
        temp_file = file.parent / f'temp_ffmpeg.mp4'

        # Right now, we're relying on the user having extensions that match the container.
        # We do have a hard dependency for `ffmpeg` and `ffprobe`, this likely could be mod
        is_source_mp4 = src_ext == 'mp4'
        if not is_source_mp4:
            new_file_name = str(file).replace(src_ext, "mp4")
        else:
            new_file_name = str(file)

        if known_good:
            convert_cmd = f'ffmpeg -i "{file}" -map 0 -vcodec {known_good} -acodec copy -map_metadata 0 -strict -2 "{temp_file}"'
            print(convert_cmd)
            create_file(file, temp_file, dry_run=True)
        else:
            for codec in encoders(target_codec):
                convert_cmd = f'ffmpeg -i "{file}" -map 0 -vcodec {codec} -acodec copy -map_metadata 0 -strict -2 "{temp_file}"'
                print(convert_cmd)

        # Ultimately, extension doesn't matter if we're destructive
        if destructive:
            print(delete_file(file, dry_run=True))
            print(move_file(temp_file, new_file_name, dry_run=True))

        # We know we're not destructive, are we mp4?
        elif is_source_mp4:
            mp4_extension = '.mp4'
            nondestructive_extension = '_h265.mp4'
            print(move_file(temp_file, f"{new_file_name.replace(mp4_extension, nondestructive_extension)}", dry_run=True))

        # We aren't mp4 and we aren't destructive, move temporary file to final file name as MP4 extension
        else:
            print(move_file(temp_file, new_file_name, dry_run=True))

@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', is_flag=True, help='Recursive')
@click.option('--file-ext', help='File format to process')
@click.option('--dry-run', is_flag=True, help='Simulate running')
@click.option('--nondestructive', is_flag=True, help='Save the original files')
@click.option('--all-exts', is_flag=True, help='Use all of the extensions in the provided directory')
@click.option('--trust-extensions', is_flag=True, help='Trust the file extensions')
@click.option('--target-codec', default='hevc', help="Use a specific codec (default: hevc)")
def main(directory, file_ext='mp4,m4a,mkv,ts,avi', recursive=False, dry_run=False, nondestructive=False, all_exts=False, trust_extensions=False, target_codec="hevc"):
    """ Compress h264 video files in a directory using libx265 codec with crf=24
    Args:
         nondestructive: whether to convert the files nondestructively
         dry_run: perform a dry run of the script rather than running. Helpful for checking for expected behavior
         directory: the directory to scan for video files
         file_ext: the file extensions to consider for conversion, comma delimited
         recursive: whether to search directory or all its contents
         all_exts: get all files in the directory given
         trust_extensions: Skip detecting the type of file
         codec: Specify codec to use (default: hevc)
    """

    print(f"Directory:        {directory}")
    print(f"File Extension:   {file_ext}")
    print(f"Recursive:        {recursive}")
    print(f"Dry run:          {dry_run}")
    print(f"Nondestructive:   {nondestructive}")
    print(f"All Extensions:   {all_exts}")
    print(f"Trust Extensions: {trust_extensions}")
    print(f"Target Codec:     {target_codec}")

    if all_exts:
        exts = find.FileExtensions(directory, recursive=recursive)
        file_exts=[ext for ext in tqdm(exts, desc='Getting extensions', unit='files')]
    else:
        file_exts = file_ext.split(",")

    files = find.VideoFileIterator(directory, extensions=file_exts, trust_extensions=trust_extensions)

    video_files = [file for file in tqdm(files, desc='Getting video files', unit='files')]

    check_codec_cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "{fp}"'
    codecs = []
    for fp in tqdm(files, desc='Checking metadata', unit='videos'):
        try:
            codecs.append(check_output(check_codec_cmd.format(fp=fp), shell=True).strip().decode('UTF-8'))
        except CalledProcessError:
            pass

    print(codecs)
    print(video_files)
    files_to_process = [fp for fp, codec in zip(video_files, codecs) if codec != target_codec.lower()]

    print(f'\nTOTAL FILES FOUND ({len(video_files)})')
    print(f'FILES TO PROCESS ({len(files_to_process)}):', [fp for fp in files_to_process], '\n')

    if len(files_to_process) == 0:
        raise click.Abort
    else:
        click.confirm('Do you want to continue?', abort=True)

    if dry_run:
        simulate(files_to_process, not nondestructive, target_codec)
    else:
        convert(files_to_process, not nondestructive, target_codec)

if __name__ == '__main__':
    main()
