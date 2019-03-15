import asyncio
from asyncio import get_event_loop
from pathlib import Path
from unittest.mock import MagicMock

import yaml
from tentacruel.cli import LightZone

def test_independent_mode():
    asyncio.run(_test_independent_mode())

def test_vertical_top():
    asyncio.run(_test_vertical_top())

def test_vertical_bottom():
    asyncio.run(_test_vertical_bottom())

async def _test_independent_mode():
    now = 0
    effector = MagicMock()
    there = Path(__file__).parent / "independent_config.yaml"
    with open(there) as from_there:
        zone_config = yaml.load(from_there)

    zone = LightZone(effector, zone_config)
    await zone.setup()
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert(len(commands) == 3)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {2,3,6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()

    await zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "moe",
        "value": 11.2,
    },now)
    effector.assert_not_called()
    now += 10
    #
    # upstairs-south sensor sees motion
    #
    await zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "motion",
        "value": "active",
    },now)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert(len(commands) == 2)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {2,3})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {True})
    effector.reset_mock()

    #
    # motion stops at upstairs-south
    #

    now += 10
    await zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "motion",
        "value": "inactive",
    },now)
    effector.assert_not_called()

    await zone.on_tick(now+100)
    effector.assert_not_called()

    #
    # motion starts downstairs
    #

    await zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "active",
    },now+450)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert(len(commands) == 1)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {True})
    effector.reset_mock()

    await zone.on_tick(now+499)
    effector.assert_not_called()

    await zone.on_tick(now+500)
    effector.assert_called_once()

    commands = effector.call_args[0][0]
    assert(len(commands) == 2)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {2,3})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()

    await zone.on_tick(now+510)
    effector.assert_not_called()

    await zone.on_tick(now+660)
    effector.assert_not_called()

    await zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "inactive",
    },now+700)
    effector.assert_not_called()

    await zone.on_tick(now+899)
    effector.assert_not_called()

    await zone.on_tick(now+905)
    effector.assert_called_once()

    commands = effector.call_args[0][0]
    assert(len(commands) == 1)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()

async def _test_vertical_top():
    now = 0
    effector = MagicMock()
    there = Path(__file__).parent / "independent_config.yaml"
    with open(there) as from_there:
        zone_config = yaml.load(from_there)

    zone = LightZone(effector, zone_config)
    await zone.setup()
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert(len(commands) == 3)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {2, 3, 6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()

    #
    # bottom sensor sees motion
    #
    await zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "active",
    },now)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert(len(commands) == 2)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {3, 6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {True})
    effector.reset_mock()

    await zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "motion",
        "value": "active",
    },now+20)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert([x[0] for x in commands] == 3 * ['l'])
    assert({x[2] for x in commands} == {'on'})
    assert({x[1] for x in commands if x[3]} == {3, 2})
    assert({x[1] for x in commands if not x[3]} == {6})
    effector.reset_mock()

    await zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "motion",
        "value": "inactive",
    },now+100)
    effector.assert_not_called()

    await zone.on_tick(now+500)
    effector.assert_not_called()

    await zone.on_tick(now+600)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert([x[0] for x in commands] == 2 * ['l'])
    assert({x[2] for x in commands} == {'on'})
    assert({x[1] for x in commands} == {3, 2})
    assert(all([not x[3] for x in commands]))
    effector.reset_mock()

    await zone.on_tick(now+10000)
    effector.assert_not_called()


async def _test_vertical_bottom():
    now = 0
    effector = MagicMock()
    there = Path(__file__).parent / "independent_config.yaml"
    with open(there) as from_there:
        zone_config = yaml.load(from_there)

    zone = LightZone(effector, zone_config)
    await zone.setup()
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert (len(commands) == 3)
    assert ({x[0] for x in commands} == {'l'})
    assert ({x[1] for x in commands} == {2, 3, 6})
    assert ({x[2] for x in commands} == {'on'})
    assert ({x[3] for x in commands} == {False})
    effector.reset_mock()

    #
    # bottom sensor sees motion
    #
    await zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "active",
    }, now)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert (len(commands) == 2)
    assert ({x[0] for x in commands} == {'l'})
    assert ({x[1] for x in commands} == {3, 6})
    assert ({x[2] for x in commands} == {'on'})
    assert ({x[3] for x in commands} == {True})
    effector.reset_mock()

    await zone.on_tick(25)
    effector.assert_not_called()

    await zone.on_tick(35)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert (len(commands) == 1)
    assert (commands[0] == ('l',3,'on',False))
    effector.reset_mock()

    await zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "inactive",
    }, 100)
    await zone.on_tick(299)
    effector.assert_not_called()

    await zone.on_tick(301)
    effector.assert_called_once()
    commands = effector.call_args[0][0]
    assert (len(commands) == 1)
    assert (commands[0] == ('l',6,'on',False))
    effector.reset_mock()

if __name__ == "__main__":
    import pytest
    pytest.main()
