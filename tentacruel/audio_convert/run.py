"""
Command:  convert all .wma files in target directory to .flac
"""

from pathlib import Path
from subprocess import Popen
from sys import argv, platform


def main():
    """
    main() method of command

    :return:
    """
    destination = Path(argv[1])
    source_files = destination.glob("**/*.wma")
    for file in source_files:
        new_name = file.name.rsplit(".", maxsplit=1)[0] + ".flac"
        dest = str(file.parent / new_name)
        cmd = list(map(str, ["avconv", "-i", file, dest]))
        if platform == "win32":
            print("Running on windows...  on Unix I'd run the following command:")
            print(cmd)
        else:
            that = Popen(cmd)
            that.wait()

if __name__ == "__main__":
    main()
