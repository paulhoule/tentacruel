from tentacruel.nws import JINJA

def test_001():
    arguments = {
        "failed": False,
        "radar_id": "BGM",
        "latest_wx": {
            "wx_time": "20190411T02:04:22Z",
            "location": "Ithaca Airport",
            "temp": 44.11123,
            "dewpt": 37.23331,
            "humidity": 5.5764,
            "wind_speed": 300.3,
            "wind_alpha": "N",
            "wind_dir": 10.0,
            "pressure": 900.9,
            "sky": "very cloudy",
            "present_weather": "hurricane force winds,  don't try to land"
        },
        "pages": {}
    }

    template = JINJA.get_template("northeast.html")
    html = template.render(**arguments)

    # test that temperature is rounded correctly
    assert("44.1" in html)
    assert("44.11" not in html)

    assert("hurricane" in html)
    assert ('<span class="na">N.A.</span>' not in html)

def test_002():
    arguments = {
        "failed": False,
        "radar_id": "BGM",
        "latest_wx": {
            "wx_time": None,
            "location": None,
            "temp": None,
            "dewpt": None,
            "humidity": None,
            "wind_speed": None,
            "wind_alpha": None,
            "wind_dir": None,
            "pressure": None,
            "sky": None,
            "present_weather": None
        },
        "pages": {}
    }

    template = JINJA.get_template("northeast.html")
    html = template.render(**arguments)
    assert("Pressure" in html)
    assert('<span class="na">N.A.</span>' in html)