"""
Time handling to meet tentacruel's needs.

In particular,  we receive dates from Smartthings in the format::

   yyyy-mm-ddThh:mm:ssZ

(namely,  with "Z" as a timecode indicator)

so we also store dates like that in the arangodb database.  This is a good
convention because ISO8601 dates sort correctly in ascii order if they are all
in the same timezone.

Also the organization of the datetime package,  where most of the methods
that we use are static methods of the datetime object is annoying to so this
package defines aliases so you can write::

   from tentacruel.time import now

for civilized coding.
"""
import datetime as dt
from numbers import Number

UTC = dt.timezone.utc

fromisoformat = dt.datetime.fromisoformat   # pylint: disable=invalid-name
Datetime = dt.datetime                      # pylint: disable=invalid-name
now = Datetime.now                          # pylint: disable=invalid-name
utcnow = lambda: now(UTC)                   # pylint: disable=invalid-name

def from_zulu_string(when: str):
    """
    Convert dates stored the way we do in Arangodb (GMT with "Z" as a timezone marker)
    to datetime.

    :param when: "2019-01-04T02:12:55Z"
    :return: corresponding Datetime
    """
    return fromisoformat(when.replace("Z", "")).replace(tzinfo=UTC)


def to_zulu_string(when: Datetime):
    """
    Convert datetime to the format we use to store dates in Arangodb,  specifically
    in GMT time with the "Z" character to specify timezone

    :param when: a datetime
    :return: "2019-01-04T02:12:55Z"
    """
    return when.isoformat().replace("+00:00", "Z")

def timestamp_to_zulu(posixMilliseconds: Number):
    return to_zulu_string(Datetime.fromtimestamp(float(posixMilliseconds)/1000,tz=UTC))