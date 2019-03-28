import re

from pytest import raises
from tentacruel.avr.powerctl import parse_argv

def test_none():
    result = parse_argv([])
    assert(result == {})

def test_z1():
    result1 = parse_argv(["zone1","off"])
    assert(result1 == {1: False})
    result2 = parse_argv(["main", "on"])
    assert(result2 == {1: True})

def test_z2():
    result1 = parse_argv(["z2","off"])
    assert(result1 == {2: False})
    result2 = parse_argv(["2", "on"])
    assert(result2 == {2: True})

def test_both():
    result1 = parse_argv(["z1","zone2","off"])
    assert(result1 == {1: False, 2: False})

def test_split():
    result1 = parse_argv(["hallway","on","Room23","off"])
    assert(result1 == {1: False, 2: True})

def test_all_on():
    result = parse_argv(["all","on"])
    assert(result == {1: True, 2: True})

def test_cannot_just_say_on():
    with raises(ValueError):
        parse_argv(["on"])

def test_cannot_just_say_off():
    with raises(ValueError,match=re.compile("not preceded by.*zone")):
        parse_argv(["off"])

def test_no_double_state():
    with raises(ValueError,match=re.compile("two power")):
        parse_argv(["z1","z2","off","on"])

def test_cant_do_it_again():
    with raises(ValueError,match=re.compile("state.*zone more than once$")):
        parse_argv(["z1","off","z1","on"])

if __name__ == "__main__":
    import pytest
    pytest.main()