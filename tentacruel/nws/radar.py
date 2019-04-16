"""
Command line program to create movies for radar

"""
import datetime
import re
from logging import getLogger, StreamHandler
from os import environ

from tentacruel.config import get_config
from tentacruel.nws import RadarFetch, register


@register
def radar_file_date(name: str) -> datetime.datetime:
    """
    Compute date based on pattern on name of radar file

    :param name:
    :return:
    """
    file_pattern = re.compile(r"_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(?:_N0R|_N1P)?.gif$")
    match = file_pattern.search(name)
    if not match:
        return None

    (year, month, day, hour, minute) = map(int, match.groups())
    return datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)

def main():
    """
    Main method of radar fetcher program

    :return:
    """
    if "LOGGING_LEVEL" in environ:
        getLogger(None).setLevel(environ["LOGGING_LEVEL"])

    getLogger(None).addHandler(StreamHandler())

    server_config = get_config("wx-paths.yaml")
    product_config = get_config("radar_config.yaml", package="tentacruel.nws")
    config = {**server_config, **product_config}

    fetcher = RadarFetch(config)
    fetcher.refresh()
    fetcher.make_video()

if __name__ == '__main__':
    main()
