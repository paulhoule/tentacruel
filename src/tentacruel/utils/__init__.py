import re
from pathlib import Path
from urllib.parse import unquote
from shutil import copy

in_dir = Path.home() / "danganronpa_ost.in"
out_dir = Path.home() / "danganronpa_ost"

#
# Reserved characters on VFAT,  NTFS,  HFS+ and common Unix filesystems
#
# see https://en.wikipedia.org/wiki/Filename#Comparison_of_filename_limitations
#

def generate_reserved_chars():
    reserved_chars_src = list(range(0,20)) + [127, '"*/:<>?\\|']
    def convert(x):
        if type(x) is int:
            return {chr(x)}
        elif type(x) is str:
            return set(x)
    reserved_chars = set()
    for x in reserved_chars_src:
        reserved_chars.update(convert(x))
    return reserved_chars

reserved_chars=generate_reserved_chars()

def ok_filename(filename):
    global reserved_chars
    file_chars=set(filename)
    return not(file_chars.intersection(reserved_chars))

percent_code = re.compile("%[0-9]{2}")

def translate_filename():
    global percent_code

files = [(path,unquote(path.name)) for path in in_dir.iterdir()]
out_dir.mkdir()
for f in files:
    if not ok_filename(f[1]):
        raise ValueError(f"Filename {f[1]} contains reserved characters for common filesystems")
    copy(f[0],out_dir / f[1])
