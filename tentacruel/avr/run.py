"""
Script for AVR application
"""

from asyncio import get_event_loop

from tentacruel.avr import avr_status

if __name__ == "__main__":
    # pylint: disable=invalid-name
    loop = get_event_loop()
    loop.run_until_complete(avr_status())
    loop.close()
