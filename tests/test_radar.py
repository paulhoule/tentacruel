from datetime import timedelta

from pytest import raises
from tentacruel.nws import parse_duration

def test_parse_hours():
    duration = parse_duration("17 hours")
    assert(duration  == timedelta(hours=17))

def test_parse_days():
    duration = parse_duration("4 days")
    assert(duration  == timedelta(days=4))

def test_minutes():
    duration = parse_duration("127 minutes")
    assert (duration == timedelta(minutes=127))

def test_b0rked_01():
    with raises(ValueError):
        parse_duration("weeks")

def test_b0rked_02():
    with raises(ValueError):
        parse_duration("35")

def test_b0rked_03():
    """
    Maybe it should support centuries,  but it doesn't...

    :return:
    """
    with raises(ValueError):
        parse_duration("11 centuries")

def test_b0rked_04():
    with raises(ValueError):
        parse_duration("3minutes")


def test_b0rked_05():
    with raises(ValueError):
        parse_duration("3.2 seconds")

def test_x_date_from_file():
    "CCX_20190418_1617_N0R.gif"

if __name__ == "__main__":
    import pytest
    pytest.main()