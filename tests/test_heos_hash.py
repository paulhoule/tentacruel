from tentacruel import MessageKeyGenerator


def test_one_message():
    that = MessageKeyGenerator()
    k1 = that.generate("player/get_play_state",{'pid': -2223})
    k2 = that.generate("player/get_play_state",{'pid': -2224})
    k3 = that.generate("player/get_play_state","pid=-2223")
    assert(k1 != k2)
    assert(k1 == k3)