"""
HEOS API call (just one) that works on the HEOS system as a whole.\
"""
from . service import _HeosService

# pylint: disable=too-few-public-methods
class _HeosSystem(_HeosService):
    """
    HEOS API calls prefixed with ``system/``.
    """
    prefix = "system"

    async def register_for_change_events(self, enable: bool = True):
        """
        Register this client to receive events from the HEOS server

        :param enable:
        :return:
        """
        await self._run(
            "register_for_change_events",
            enable="on" if enable else "off"
        )
