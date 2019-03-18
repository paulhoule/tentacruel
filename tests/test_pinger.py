from asyncio import run
from tentacruel.pinger import ping, ensure_proactor

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

if __name__ == "__main__":
    import pytest
    pytest.main()