"""
Command to generate movie from GOES EAST satellite

"""
import datetime
import re

from tentacruel.nws import RadarFetch

def sat_file_date(name: str) -> datetime.datetime:
    """
    Compute date/time for satelliteimage file based on parsing pattern

    :param name:
    :return:
    """
    file_pattern = re.compile(r"^(\d{4})(\d{3})(\d{2})(\d{2})_")
    match = file_pattern.search(name)
    if not match:
        return None

    (year, day_in_year, hour, minute) = map(int, match.groups())
    first_day = datetime.datetime(year, 1, 1, hour, minute, tzinfo=datetime.timezone.utc)
    return first_day + datetime.timedelta(day_in_year)


# pylint: disable=too-many-function-args
# pylint: disable=invalid-name
g = RadarFetch(
    "https://cdn.star.nesdis.noaa.gov/",
    [dict(
        pattern=r"GOES16/ABI/SECTOR/ne/GEOCOLOR/\d{11}_GOES16-ABI-ne-GEOCOLOR-1200x1200.jpg",
        date_fn=sat_file_date,
        video="northeast-color.mp4"
    )]
)
g.refresh()
g.make_video()
