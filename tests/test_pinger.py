from tentacruel.pinger import ping

def test_ping_localhost():
    assert(ping("127.0.0.1"))

def test_ping_nowhere():
    assert(not ping("0.0.0.0"))

if __name__ == "__main__":
    import pytest
    pytest.main()