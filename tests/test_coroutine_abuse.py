"""
Experiments to unconver the true nature of coroutines.

One goal is to be able to operate coroutines without an event loop (or some kind of stub of an event
loop)

Other goals are to be able to serialize coroutines,  move them between processes and threads,  implement
advanced error handling (could we back one up a step?  could we implement a transaction processing monitor?)
"""
import types
from asyncio import iscoroutine

from pytest import raises

values = []
async def aprint(that: str):
    values.append(that)

async def hello_world():
    await aprint("Hello")
    await aprint("World")

@types.coroutine
def schedule():
    """
    Strange abusive code modeled after async.tasks.__sleep0() that injects a yield point.  It does
    that by embedding a generator into a coroutine with types.coroutine.

    :return:
    """
    yield

async def think_about_it():
    i = 0
    for j in range(0,4):
        i += j
        await aprint(i)

async def with_a_pause():
    await aprint("Hello")
    await schedule()
    await aprint("World")

def test_abuse():
    """
    Note when we run a coroutine that does nothing but await on other coroutines
    that do nothing asynchronous (never yield) the `send` method runs once and
    all of the side effects happen.

    :return:
    """
    a = hello_world()
    assert(iscoroutine(a))
    values.clear()
    with raises(StopIteration):
        a.send(None)

    assert(values == ["Hello", "World"])

def test_more_complex():
    a = think_about_it()
    assert(iscoroutine(a))
    values.clear()
    with raises(StopIteration):
        a.send(None)

    assert(values == [0, 1, 3, 6])

def test_with_pause():
    """
    This code is modeled after the asyncio.tasks.__sleep0() method.  It shows that yield is the operation that
    causes the execution to get frozen.

    :return
    """

    a = with_a_pause()
    values.clear()
    assert(not a.cr_running)
    a.send(None)
    #
    # Note that cr_running did not get by the things that we did,  probably it is
    # if we invoke the normal way through await
    #
    assert(not a.cr_running)
    assert(values == ["Hello"])
    assert(not a.cr_running)
    with raises(StopIteration):
        a.send(None)
    assert(not a.cr_running)
    assert(values == ["Hello", "World"])

