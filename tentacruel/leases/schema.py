"""

Structure of collection:

      _key: caf89ac6-4c19-11e9-b4a5-9eb6d06a70c5
      stack:
         - pink
         - blue
      modes:
         pink:
            expires: 2019-08-01T14:22:11Z
         blue:
            expires: 2019-08-01T15:25:11Z

Note that the key is a UUID which would be a deviceId if the thing that has a mode is device,  otherwise
it would be a locationId or a zoneId,  or a personId or whatever.

The stack and the modes are separated because I believe the queries would be simple and natural to
handle both changes to the stack (push and pop) as well as updates to the expiration date in an
atomic way.

In principle modes could have some more dictionary keys added that could be used for data
structures having to do with a node (e.g. what color is the light supposed to be?) but then it
gets tempting to let modes nest (eg. two kinds of "blue")

"""

from pathlib import Path

import yaml
from tentacruel.leases import get_config, connect_to_adb

if __name__ == "__main__":
    config = get_config()
    adb = connect_to_adb(config)
    print(type(adb))
    adb.create_collection("leases")