from pathlib import Path
from typing import List

import yaml
from tentacruel.watch_gui import extract_sensor_list


def test_extract_sensor_list():
    there = Path(__file__).parent / "independent_config.yaml"
    with open(there) as from_there:
        zone_config = yaml.load(from_there)

    config = {
        "zones" : [zone_config]
    }

    out = extract_sensor_list(config)
    assert(isinstance(out, List))
    assert(len(out)==4)
    assert(out[0]["name"] == "upstairs-south")
    assert(out[3]["sensor_id"] == "a20bab2e-a7d0-4c93-8723-27a7bf3299b6")





if __name__ == "__main__":
    import pytest
    pytest.main()