from unittest.mock import MagicMock

from tentacruel.cli import LightZone

def test_independent_mode():
    now = 0
    effector = MagicMock()
    zone = LightZone(effector)
    zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "moe",
        "value": 11.2,
    },now)
    effector.assert_not_called()
    now += 10
    zone.on_event({
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

    now += 10
    zone.on_event({
        "deviceId": "a76876ab-6ded-4fb5-9955-76dd0cbb6525",
        "attribute": "motion",
        "value": "inactive",
    },now)
    effector.assert_not_called()

    zone.on_tick(now+100)
    effector.assert_not_called()

    zone.on_event({
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

    zone.on_tick(now+499)
    effector.assert_not_called()

    zone.on_tick(now+500)
    effector.assert_called_once()

    commands = effector.call_args[0][0]
    assert(len(commands) == 2)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {2,3})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()

    zone.on_tick(now+510)
    effector.assert_not_called()

    zone.on_tick(now+660)
    effector.assert_not_called()

    zone.on_event({
        "deviceId": "a20bab2e-a7d0-4c93-8723-27a7bf3299b6",
        "attribute": "motion",
        "value": "inactive",
    },now+700)
    effector.assert_not_called()

    zone.on_tick(now+899)
    effector.assert_not_called()

    zone.on_tick(now+905)
    effector.assert_called_once()

    commands = effector.call_args[0][0]
    assert(len(commands) == 1)
    assert({x[0] for x in commands} == {'l'})
    assert({x[1] for x in commands} == {6})
    assert({x[2] for x in commands} == {'on'})
    assert({x[3] for x in commands} == {False})
    effector.reset_mock()