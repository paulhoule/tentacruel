"""
Manage modes that are temporary (leases) so that resources are unlocked
if and when processes go down.
"""
import datetime
from uuid import UUID

from arango.database import StandardDatabase

class LeaseManager:
    """
    Class to manage leases by manipulating the database directly
    """

    def __init__(self, adb: StandardDatabase):
        """
        :param adb: connection to arangodb
        """
        self.adb = adb
        self.collection = adb.collection("leases")

    def create_device(self, device_id: UUID):
        """
        Create lease record for device

        :param device_id: device id
        :return:
        """
        document = {
            "_key": str(device_id),
            "stack": [],
            "mode": {},
        }
        self.collection.insert(document)

    def push_lease(self, device_id: UUID, mode: str, duration: datetime.timedelta):
        """
        For a given device,  push a new lease onto the stack,  this becomes the current mode

        :param device_id: UUID
        :param mode: the mode the device is transitioning to
        :param duration: how long until the lease expires
        :return: True if we got the lease,  False otherwise (say "mode" is already in use)
        """
        now = datetime.datetime.utcnow()
        expires = (now + duration).isoformat("T", "seconds")+"Z"
        lease_data = {
            mode: {"expires": expires}
        }
        cursor = self.adb.aql.execute("""
            FOR lease IN leases
               FILTER lease._key == @device_id
               FILTER @mode NOT IN lease.stack
               UPDATE lease WITH { 
                  _key: lease._key,
                  stack: UNSHIFT(lease.stack,@mode,TRUE),
                  mode: MERGE(lease.mode,@lease_data)
               } IN leases
               RETURN True
        """, bind_vars={
            "device_id": str(device_id),
            "mode": mode,
            "lease_data": lease_data,
        })

        return bool(list(cursor))

    def pop_lease(self, device_id: UUID, mode: str):
        """

        :param device_id: The affected device
        :param mode: a mode we intend to end
        :return: True if ``mode`` was at the top of the stack,  False otherwise
        """
        cursor = self.adb.aql.execute("""
            FOR lease IN leases
               FILTER lease._key == @device_id
               FILTER @mode == lease.stack[0]
               UPDATE lease WITH { 
                  _key: lease._key,
                  stack: SHIFT(lease.stack),
                  mode: UNSET(lease.mode,@mode)
               } IN leases OPTIONS { mergeObjects: false}
               RETURN UNSET(lease.mode,@mode)
        """, bind_vars={
            "device_id": str(device_id),
            "mode": mode,
        })

        return bool(list(cursor))

    def expire(self, now=None):
        """
        Expire old leases.

        This returns a list of expired device/mode combinations,  but it also
        deletes the mode leases from the leases table.

        This does NOT send any messages to the MQ about expired leases.

        :param now: time to expire at,  if left blank it will be this moment
        :return: list of deviceId(s) and expiredModes [ modes ]
        """
        if not now:
            now = datetime.datetime.utcnow()
        when = now.isoformat("T", "seconds")+"Z"
        cursor = self.adb.aql.execute("""
            LET expired = (
                FOR lease IN leases
                    FOR mode IN ATTRIBUTES(lease.mode)
                    FILTER lease.mode[mode].expires < @now
                    COLLECT deviceId = lease._key INTO modes = mode
                    RETURN {deviceId: deviceId,expiredModes: modes}
            )
            RETURN expired
        """, bind_vars={"now": when})

        expired = list(cursor)[0]
        self.adb.aql.execute("""
            FOR expired in @expired
                FOR lease in leases
                    FILTER lease._key == expired.deviceId
                    UPDATE {
                        _key: expired.deviceId,
                        stack: REMOVE_VALUES(lease.stack,expired.expiredModes),
                        mode: UNSET(lease.mode,expired.expiredModes) 
                    } IN leases OPTIONS { mergeObjects: false}
        """, bind_vars={"expired": expired})

        return expired
