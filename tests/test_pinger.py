from asyncio import run
from tentacruel.pinger import ping, ensure_proactor, iso_zulu_now

ensure_proactor()

def test_ping_localhost():
    assert(run(ping("127.0.0.1")))

def test_ping_elsewhere():
    """
    The following is a private network that you probably aren't on.  Unless you are!

    Should always fail to route because you can't route to this address via the public
    internet.

    :return:
    """
    assert(not run(ping("10.254.254.254")))

def test_iso_zulu_now():
    """
    Check that this function returns a date string with the right length (20 chars)
    :return:
    """
    sample_date = "2019-03-15T16:01:12Z"
    zulu = iso_zulu_now()
    assert(len(sample_date) == len(zulu))
    assert(len(sample_date) == 20)
    assert(zulu[4] == "-")
    assert(zulu[7] == "-")
    assert(zulu[10] == "T")
    assert(zulu[13] == ":")
    assert(zulu[16] == ":")
    assert(zulu[19] == "Z")


if __name__ == "__main__":
    import pytest
    pytest.main()