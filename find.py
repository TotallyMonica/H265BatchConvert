import os

def locate(path: str=os.getcwd()):
    files = os.walk(path)
    types = []
    for file in files:
        for name in file[-1]:
            ext = name.split('.')[-1]
            if ext not in types:
                types.append(name.split('.')[-1])
    return types

if __name__ == "__main__":
    print(locate("/mnt/media/TV Shows"))