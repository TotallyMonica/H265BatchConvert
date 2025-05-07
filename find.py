from tqdm import tqdm
import os
from pathlib import Path
import magic

class FileIterator:
    def __init__(self, path=os.getcwd(), exclude_prefixes=("$RECYCLE.BIN", ".Trash-1000"), recursive=True):
        self.path = path
        self.exclude_prefixes = exclude_prefixes
        self.recursive = recursive

    def __iter__(self):
        return self._file_generator()

    def _file_generator(self):
        if self.recursive:
            for root, dirs, files in os.walk(self.path, topdown=True):
                dirs[:] = [d for d in dirs if d not in self.exclude_prefixes]

                for name in files:
                    yield os.path.join(root, name)

        else:
            for file in os.listdir(self.path):
                if os.path.isfile(os.path.join(self.path, file)):
                    yield file

class VideoFileIterator:
    def __init__(self, path=os.getcwd(), exclude_prefixes=("$RECYCLE.BIN", ".Trash-1000"), recursive=True, extensions=(), trust_extensions=False):
        self.path = path
        self.exclude_prefixes = exclude_prefixes
        self.recursive = recursive
        self.trust_extensions = trust_extensions
        if extensions:
            self.extensions = tuple(extensions)
        else:
            self.extensions = ('.flv', '.f4v', '.f4p', '.f4a', '.f4b', '.nsv', '.roq', '.mxf', '.3g2', '.3gp', '.svi',
                               '.m4v', '.mpg', '.mpeg', '.m2v', '.mp2', '.mpe', '.mpv', '.mp4', '.m4p', '.amv', '.asf',
                               '.viv', '.rm', '.rmvb', '.yuv', '.wmv', '.mov', '.qt', '.mts', '.m2ts', '.ts', '.avi',
                               '.mng', '.gifv', '.gif', '.drc', '.ogv', '.ogg', '.vob', '.mkv', '.webm')

    def __iter__(self):
        return self._file_generator()

    def _file_generator(self):
        file_iter = FileIterator(self.path, self.exclude_prefixes, self.recursive)

        def can_access(f):
            return os.access(f, os.R_OK)

        if self.trust_extensions:
            for file in file_iter:
                f = magic.Magic(mime=True)
                if can_access(file) and file.endswith(self.extensions):
                    yield file
        else:
            for file in file_iter:
                f = magic.Magic(mime=True)
                if can_access(file) and file.endswith(self.extensions) and "video/" in f.from_file(file):
                    yield file

class FileExtensions:
    def __init__(self, path=os.getcwd(), recursive=True):
        self.path = path
        self.recursive = recursive

    def __iter__(self):
        return self._get_exts()

    def _get_exts(self):
        exclude_prefixes = ['$RECYCLE.BIN', '.Trash-1000']
        types = []

        if self.recursive:
            for root, dirs, files in os.walk(self.path, topdown=True):
                dirs[:] = [d for d in dirs if d not in exclude_prefixes]

                for name in files:
                    ext = name.split('.')[-1]
                    if ext not in types:
                        types.append(ext)
                        yield ext
        else:
            for file in os.listdir(os.path.join(self.path)):
                if os.path.isfile(file) and file.split('.')[-1] not in types:
                    types.append(file.split('.')[-1])
                    yield file.split('.')[-1]

if __name__ == "__main__":
    PATH = os.getcwd()
    exts = FileExtensions(PATH)
    files = FileIterator(PATH)
    video_files = VideoFileIterator(PATH)
    for ext in tqdm(exts, desc="Getting extensions", unit=" files"):
        # print(ext)
        pass
    print(list(exts))
    for file in tqdm(files, desc="Getting files", unit=" files"):
        # print(ext)
        pass
    print(list(files))
    for file in tqdm(video_files, desc="Getting video files", unit=" files"):
        # print(file)
        pass
    print(list(video_files))
