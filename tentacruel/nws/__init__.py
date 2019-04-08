# pylint: disable=missing-docstring
import datetime

import os
import re
import sys
from logging import getLogger, basicConfig
from math import floor
from operator import itemgetter
from pathlib import Path
from typing import Dict

import imageio
import numpy as np
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape

JINJA = Environment(
    loader=PackageLoader('tentacruel.nws', 'jj2'),
    autoescape=select_autoescape(['html', 'xml'])
)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")
LOGGER = getLogger(__package__)
basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=LOG_LEVEL)

# 600 x 576
# to install ffmepg: imageio.plugins.ffmpeg.download()

DATE_FUNCTIONS = {}

def register(function):
    DATE_FUNCTIONS[function.__name__] = function
    return function

RE_DURATION = re.compile(r"(\d+) (days|seconds|microseconds|milliseconds|minutes|hours|weeks)")
def parse_duration(duration):
    match = RE_DURATION.fullmatch(duration)
    if not match:
        raise ValueError(f"duration {duration} is not an integer followed by a time unit")
    amount = int(match[1])
    unit = match[2]
    return datetime.timedelta(**{unit: amount})


class RadarFetch:
    def __init__(self, config: Dict):
        """

        :param config:
           Configuration dictionary.  The first key is "paths" and represents paths,
           the second is "products" which represents products that this system can
           generate.  This is not the general 'tentacruel' configuration dictionary.

        """
        self._session = requests.Session()
        self._source_base = config["paths"]["source_base"]
        self._cache = Path.home() / "radar"
        self._patterns = config["products"]
        self._output = Path(config["paths"]["output"])

    def copy_template(self):
        for pattern in self._patterns:
            template_name = pattern["template"]
            template = JINJA.get_template(template_name)
            index_out = self._output / template_name
            index_out.write_text(template.render(), encoding="utf-8")

    def refresh(self):
        self._session = requests.Session()
        for pattern in self._patterns:
            self._refresh(pattern)

    def _refresh(self, pattern: dict):
        self._fetch_overlays(pattern)
        product_dir = "/".join(pattern["pattern"].split("/")[:-1])
        regex = re.compile(pattern["pattern"].split("/")[-1])
        target_dir = self._cache / product_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        url_directory = self._source_base + product_dir + "/"
        LOGGER.warning("Checking %s", url_directory)
        target = self._session.get(url_directory).text
        soup = BeautifulSoup(target, features="lxml")
        links = soup.find_all("a")
        crawl = []
        for link in links:
            href = link["href"]
            if regex.match(href):
                crawl.append(href)

        for href in crawl:
            target_file = self._cache / product_dir / href
            source_url = url_directory + href
            self._fetch_file(source_url, target_file)

    def _fetch_overlays(self, pattern: dict):
        if "overlays" in pattern:
            for overlay in pattern["overlays"]:
                source_url = self._source_base + overlay
                target_file = self._cache / overlay
                self._fetch_file(source_url, target_file)


    def _fetch_file(self, source_url, target_file: Path):
        if target_file.exists():
            LOGGER.debug(
                "File %s already exists -- no need to download %s",
                target_file, source_url)
            return

        gif_data = self._session.get(source_url)
        if gif_data.ok and gif_data.content:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, "wb") as that:
                that.write(gif_data.content)


    def make_video(self):
        for pattern in self._patterns:
            self._make_video(pattern)
            self._make_still(pattern)

    # pylint: disable=too-many-locals
    def _make_video(self, pattern):
        LOGGER.info("Creating video %s", pattern['video'])
        start = datetime.datetime.now()
        infiles = self._lookup_matching(pattern)
        date_fn = DATE_FUNCTIONS[pattern["date_fn"]]
        dated = [{"path": file, "timestamp": date_fn(file.name)} for file in infiles]
        dated.sort(key=itemgetter("timestamp"))

        now = datetime.datetime.now(datetime.timezone.utc)
        window = parse_duration(pattern.get("window", "1 days"))

        dated = [{**row, "age": now - row["timestamp"]} for row in dated if row["timestamp"]]
        dated = [row for row in dated if row["age"] < window]

        self._output.mkdir(parents=True, exist_ok=True)
        movie_out = str(self._output / pattern["video"])
        movie_temp = movie_out[:-4] + "-temp.mp4"
        overlays = self._load_overlays(pattern)
        overlays = self._merge_overlays(overlays)

        with imageio.get_writer(
                movie_temp,
                mode='I', fps=10) as writer:
            for item in dated:
                file = item["path"]
                try:
                    content = self._compose_frame(file, overlays)
                except ValueError as err:
                    print(str(type(err)) + ":" + str(err))
                    print("Could not read image from " + str(file) + " deleting")
                    try:
                        # if the file is corrupt ignore it and get rid of it
                        file.unlink()
                        # on Windows the file might not have been released by imageio and we might
                        # not be able to delete it
                    except PermissionError:
                        pass
                    continue

                if len(content.shape) == 2:
                    content = np.moveaxis(
                        np.array([
                            content, content, content, np.zeros_like(content)
                        ]), 0, -1)

                # the image should be divisible for 16x16 macroblocks;  crop away the from the left
                # and the top because my judgement is that for the northeast case this is best.
                (width, height, _) = content.shape

                legal_width = 16 * floor(width / 16)
                legal_height = 16 * floor(height / 16)
                cropped = content[-legal_width:, -legal_height:]

                writer.append_data(cropped)

        if not sys.platform.startswith('linux'):
            if os.path.exists(movie_out):
                os.unlink(movie_out)
        os.rename(movie_temp, movie_out)
        end = datetime.datetime.now()
        LOGGER.info("Completed video %s in time %s", pattern['video'], end - start)

    def _lookup_matching(self, pattern):
        product_dir = "/".join(pattern["pattern"].split("/")[:-1])
        src = self._cache / product_dir
        ext = pattern["pattern"][-3:]
        infiles = sorted(src.glob(f"*.{ext}"))
        return infiles



    def _make_still(self, pattern):
        if "still" not in pattern:
            return

        last_shot = self._lookup_matching(pattern)[-1]
        overlays = self._load_overlays(pattern)
        content = self._compose_frame(last_shot, overlays)
        imageio.imwrite(self._output / pattern["still"], content, "PNG-FI")

    def _load_overlays(self, pattern):
        output = []
        if "overlays" in pattern:
            for file_name in pattern["overlays"]:
                overlay = load_masked_image(self._cache / file_name)
                output.append(overlay)
        return output

    # pylint: disable=no-self-use
    def _merge_overlays(self, overlays):
        if len(overlays) < 2:
            return overlays

        output = overlays[0]
        for overlay in overlays[1:]:
            output = fast_composite(output, overlay)

        return [output]

    def _compose_frame(self, path, overlays):
        content = load_masked_image(self._cache / path)
        content = black_background(content)

        for overlay in overlays:
            content = fast_composite(content, overlay)
        return content[0].astype(np.uint8)

def load_masked_image(path):
    img = imageio.imread(path)
    if len(img.shape) == 2:
        rgb = np.broadcast_to(np.expand_dims(img, axis=-1), img.shape + (3,))
        alpha = np.expand_dims(img.astype(bool), axis=-1)
        return (rgb, alpha)
    rgb = img[:, :, 0:3]
    alpha = img[:, :, 3:].astype(bool)
    return (rgb, alpha)

def fast_composite(below, above):
    rgb = above[0] * above[1] + below[0] * (1-above[1])
    alpha = above[1] | below[1]
    return (rgb, alpha)

def black_background(above):
    if (above[0] == 255).all() and above[1].all():
        return (above[0]*0, above[1] | True)

    rgb = above[0] * above[1]
    alpha = above[1] | True
    return (rgb, alpha)

def floatify(img):
    return img.astype("f8")/255.0

def byteify(img):
    clipped = np.clip(img, 0.0, 1.0)
    return (clipped*255.0).astype('B')

def alpha_composite(below, above):
    b_color = below[:, :, 0:3]
    a_color = above[:, :, 0:3]
    b_alpha = below[:, :, 3:]
    a_alpha = above[:, :, 3:]

    c_alpha = a_alpha + b_alpha * (1.0 - a_alpha)
    c_color = np.nan_to_num(
        (a_color * a_alpha + b_color * b_alpha * (1.0 - a_alpha)) / c_alpha,
        copy=False
    )

    return np.concatenate((c_color, c_alpha), axis=2)
