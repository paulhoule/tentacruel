from datetime import timedelta

from pytest import raises
from tentacruel.nws import parse_duration, wind_alpha


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

def test_wind():
    assert(wind_alpha(0) == "N")
    assert(wind_alpha(90) == "E")
    assert(wind_alpha(180) == "S")
    assert(wind_alpha(270) == "W")

    assert(wind_alpha(45) == "NE")
    assert(wind_alpha(135) == "SE")
    assert(wind_alpha(225) == "SW")
    assert(wind_alpha(315) == "NW")

    assert(wind_alpha(10) == "N")
    assert(wind_alpha(20) == "N")
    assert(wind_alpha(30) == "NE")
    assert(wind_alpha(40) == "NE")
    assert(wind_alpha(50) == "NE")
    assert(wind_alpha(60) == "NE")
    assert(wind_alpha(70) == "E")
    assert(wind_alpha(80) == "E")
    assert(wind_alpha(100) == "E")
    assert(wind_alpha(110) == "E")
    assert(wind_alpha(120) == "SE")

if __name__ == "__main__":
    import pytest
    pytest.main()