# pylint: disable=missing-docstring
# pylint: disable=invalid-name
import concurrent
from asyncio import open_connection, StreamReader, wait_for, shield, StreamWriter
from decimal import Decimal
from logging import getLogger
import re
from re import fullmatch
from typing import Pattern, Dict

from multidict import MultiDict
from tentacruel import HeosClientProtocol

#pylint: disable=invalid-name
logger = getLogger(__name__)

# pylint: disable=pointless-string-statement
"""
Notes about audio sources
-------------------------

A bit of a disorganized mess.

My understanding is as follows.  Zone 1 can play any source.  Zone 2 can play
NET, TUNER and I believe any of the other channels if these are assigned to
an analog input.  For instance if you connect "Game" to an analog audio input
you can play it on Zone 2 and it will show up as GAME.  However,  if you get audio through
the HDMI or through the TOSLINK inputs,  then you cannot play it on Zone 2.
Thus which labels you see in Zone 2 depend on how your receiver is configured.

NET is anything from the HEOS system and also Bluetooth.  There are four total
buttons on the remote control (USB,  funny H,  Bluetooth,  and Internet Radio)
that all select NET.

For the time being,  I figured I would add to this chaos by hard-coding names for the
devices I have
plugged in.  (I do have these named in my receiver's configuration and these
names appear in the receiver's UI but I don't think I can find out about
that configuration from here!)

Other Denon receivers could have different codes for sources.  In particular,  some
receivers use names like USB and IPOD in cases where the AVR-S730H uses NET.

I've seen SOURCE in Zone 2 in cases where the reciever configuration was changed
in such a way to make the source invalid (e.g. it was a channel with an analog
audio input that got changed back to the digital)

"""

SOURCES = {
    "SAT/CBL": "XBOX One",
    "DVD": "Playstation 3",
    "NET": "Network",
    "BD": "Blu-Ray",
    "GAME": "Game Console",
    "AUX1": "Front Panel Input",
    "MPLAY": "Media Player",
    "TV": "TV Audio",
    "SOURCE": "None",
}

async def read_lines_until(reader: StreamReader, timeout: float):
    lines = []
    while not reader.at_eof():
        try:
            line = await shield(wait_for(reader.readuntil(b'\r'), timeout))
            lines.append(line.decode("ascii"))
        # pylint: disable=protected-access
        except concurrent.futures._base.TimeoutError:
            break
    return lines

async def read_lines_matching(reader: StreamReader, *patterns: Pattern):
    waiting_for = {}
    for (index, pattern) in enumerate(patterns):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        waiting_for[pattern] = index

    values = [None] * len(waiting_for)
    while not reader.at_eof():
        if all(values):
            break
        line = await reader.readuntil(b'\r')
        line = line.decode("ascii").strip()
        logger.debug("got line: %s", line)
        for pattern in waiting_for:
            index = waiting_for[pattern]
            if not values[index]:
                match = pattern.fullmatch(line)
                if match:
                    values[index] = match[1]

    return values

def pop_fact(facts, prefix):
    matching = set()
    for fact in facts:
        if fact.startswith(prefix):
            matching.add(fact)

    for fact in matching:
        facts.remove(fact)

    return {match[len(prefix):] for match in matching}

def pop_numeric(facts, prefix=""):
    matching = set()
    for fact in facts:
        if fact.startswith(prefix):
            suffix = fact[len(prefix):]
            if fullmatch(r"\d+", suffix):
                matching.add(fact)

    for fact in matching:
        facts.remove(fact)

        suffix = fact[len(prefix):]
        if (len(suffix)) <= 2:
            return Decimal(int(suffix)).quantize(Decimal("0.1"))

        return (Decimal(int(suffix))/Decimal(10)).quantize(Decimal("0.1"))

def only(facts):
    if len(facts) != 1:
        raise ValueError(f"Facts {facts} can contain only one matching fact")
    return list(facts)[0]


class AvrControl:
    def __init__(self, host):
        self.host = host
        self.reader: StreamReader = None
        self.writer: StreamWriter = None

    async def setup(self):
        (self.reader, self.writer) = await open_connection(self.host, 23)

    async def shutdown(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def is_heos_on(self):
        """

        Some notes on power system behavior:  with the remote control you can put the
        receiver in and out of standby by turning off both Z1 and Z2.   There is no
        PWOFF state because in PWOFF it would not be listening on the net.

        :return:
        """
        status = {}
        #
        # this returns Z2ON if Z2 is ON.  If we didn't get Z2ON by the time we got
        # ZM back then we could probably save a millisecond or two by not asking
        # for Z2?
        #
        self.writer.write(b"PW?\r")
        await(self.writer.drain())
        (power, ) = await read_lines_matching(self.reader, "^PW(ON|STANDBY)$")
        status["power"] = (power == "ON")

        self.writer.write(b"ZM?\r")
        await(self.writer.drain())
        (z1_power, ) = await read_lines_matching(self.reader, "^ZM(ON|OFF)$")
        status["zone1"] = {}
        status["zone1"]["power"] = (z1_power == "ON")

        self.writer.write(b"SI?\r")
        await(self.writer.drain())
        (z1_source, ) = await read_lines_matching(self.reader, "^SI(.*)$")
        status["zone1"]["source"] = z1_source

        self.writer.write(b"Z2?\r")
        await(self.writer.drain())

        z2_source_pattern = "^Z2(" + "|".join(SOURCES.keys()) +")$"
        (z2_power, z2_source) = \
            await read_lines_matching(self.reader, "^Z2(ON|OFF)$", z2_source_pattern)
        status["zone2"] = {}
        status["zone2"]["power"] = z2_power
        status["zone2"]["source"] = None if z2_source == "SOURCE" else z2_source
        return status

    async def set_power_status(self, power_status: Dict[int, bool]) -> None:
        """
        Sets the power status of the speakers.  Key value pairs are set one at a
        time.  ex.::

            that.set_power_status({1: True,2: False})

        :param power_status: dictionary,  key is zone number,  value is power state as a booleab
        :return: None
        """

        for (zone, state) in power_status.items():
            try:
                if zone == 1:
                    if state:
                        self.writer.write(b"ZMON\rSINET\r")
                    else:
                        self.writer.write(b"ZMOFF\r")
                elif zone == 2:
                    if state:
                        self.writer.write(b"Z2ON\rZ2NET\r")
                    else:
                        self.writer.write(b"Z2OFF\r")
                else:
                    raise ValueError("Only Zones 1 and 2 are supported")
            finally:
                await self.writer.drain()

async def avr_status():
    """
    Show report on the AVR system status,  primarily based on the telnet API but
    getting some version information from HEOS.

    """
    host = '192.168.0.10'
    await heos_report(host)
    reader, writer = await open_connection(host, 23)
    reified_facts = await ask_queries(reader, writer)
    facts = set(reified_facts.keys())
    z2_facts = await zone1_report(facts)
    await zone2_report(z2_facts)
    writer.close()
    await writer.wait_closed()


async def zone1_report(facts):
    print("Zone 1 =========================")
    #
    # The "excess facts" that I am seeing when analog inputs are enabled come up as
    # {'SSALSVAL 000', 'SSALSSET ON', 'SSALSDSP OFF'}
    #
    # I don't see these written down in the docs I am looking at.  One obnoxious thing
    # is that these come up when we are running HEOS/Tuner audio with a video channel
    #
    await z1_main_report(facts)
    await tuner_report(facts)
    await ps_report(facts)
    await cv_report(facts)
    z2_facts = pop_fact(facts, "Z2")
    if facts:
        print("Stray facts in Zone 1:")
        print(facts)
    print()
    return z2_facts


async def z1_main_report(facts):
    power = only(pop_fact(facts, "PW")).capitalize()
    z1_power = only(pop_fact(facts, "ZM")).capitalize()
    slp = only(pop_fact(facts, "SLP")).capitalize()
    pop_fact(facts, "MSQUICK")  # dont' care if a quick select has been pressed (for now)
    ms_mode = only(pop_fact(facts, "MS")).capitalize()
    print(f"Main Power: {power}   Zone 1 Power: {z1_power}   Sleep: {slp}")
    main_volume = pop_numeric(facts, "MV")
    max_volume = pop_numeric(facts, "MVMAX ")
    sd_mode = only(pop_fact(facts, "SD"))
    dc_mode = only(pop_fact(facts, "DC"))
    print(f"Main Volume: {main_volume} / {max_volume}  Digital Input: {sd_mode}/{dc_mode}")
    source = only(pop_fact(facts, "SI"))
    mute = only(pop_fact(facts, "MU")).capitalize()
    print(f"Source: {source}   Mute: {mute}   Mode: {ms_mode}")
    pop_fact(facts, "SVON")
    sv = only(pop_fact(facts, "SV"))
    if sv != "OFF":
        print(f"Video Source: {sv}")


async def tuner_report(facts):
    is_am = bool(pop_fact(facts, "TMANAM"))
    bool(pop_fact(facts, "TMANFM"))
    is_auto = bool(pop_fact(facts, "TMANAUTO"))
    bool(pop_fact(facts, "TMANMANUAL"))
    tfan = only(pop_fact(facts, "TFAN"))
    tpan = only(pop_fact(facts, "TPAN"))
    tpan = "Off" if tpan == "OFF" else int(tpan)
    band = "AM" if is_am else "FM"
    tuner_mode = "Auto" if is_auto else "Manual"
    #
    # known bug:  if the tuner is in auto mode and moving at the time
    # we scan,  we might get multiple numbers for the frequency which causes
    # a crash
    #
    if band == "AM":
        frequency = tfan[0:4]
        if frequency[0] == "0":
            frequency = frequency[1:]
        frequency += "kHz"
    else:
        frequency = tfan[1:4] + "." + tfan[4:6]
        if frequency[0] == "0":
            frequency = frequency[1:]
        frequency += "MHz"
    print(f"Band: {band}   Frequency:  {frequency}  Tuner Mode: {tuner_mode}")
    if tpan != "Off":
        print(f"Tuner Preset: Channel {tpan}")
    print()


async def ps_report(facts):
    reflev = pop_numeric(facts, "PSREFLEV ")
    delay = int(only(pop_fact(facts, "PSDEL ")))
    ps_drc = only(pop_fact(facts, "PSDRC ")).capitalize()
    ps_swr = only(pop_fact(facts, "PSSWR ")).capitalize()
    ps_lfe = pop_numeric(facts, "PSLFE ")
    ps_eff = pop_numeric(facts, "PSEFF ")
    ps_tre = pop_numeric(facts, "PSTRE ")
    ps_bas = pop_numeric(facts, "PSBAS ")
    ps_dynamic_eq = only(pop_fact(facts, "PSDYNEQ ")).capitalize()
    ps_dynamic_vol = only(pop_fact(facts, "PSDYNVOL ")).capitalize()
    ps_rstr = only(pop_fact(facts, "PSRSTR ")).capitalize()
    ps_lom = only(pop_fact(facts, "PSLOM ")).capitalize()
    ps_tone = only(pop_fact(facts, "PSTONE CTRL ")).capitalize()
    ps_multeq = only(pop_fact(facts, "PSMULTEQ:")).capitalize()
    print(f"Reference Level: {reflev} dB    Delay: {delay} ms   Dynamic Range Control: {ps_drc}")
    print(f"LFE Level: {ps_lfe} dB  Effect level: {ps_eff} dB  Multichannel EQ: {ps_multeq}")
    print(f"SWR: {ps_swr}   Dynamic EQ: {ps_dynamic_eq}   Dynamic Volume: {ps_dynamic_vol}")
    print(f"Audio Restorer: {ps_rstr}  Loudness Management: {ps_lom}  Tone Control: {ps_tone}")
    print(f"Tone Control: {ps_tone}  Bass: {ps_bas} dB  Treble: {ps_tre} dB")
    print()


async def cv_report(facts):
    #
    # yes,  this is my particular speaker configuration:  even with the same receiver it
    # should be possible to add other channels
    #
    # SW == subwoofer (what if there is a right and a left?)
    # SBL/SBR == surround Back Left/Right
    # SB == surround Back
    # FHL/FHR == front height left and right
    #
    # logically I think we could check to see if certain channels exist and print more
    # lines,  height at top,  back on the bottom,  not sure where to put the sub(s)
    cv_front_right = pop_numeric(facts, "CVFR ")
    cv_surround_right = pop_numeric(facts, "CVSR ")
    cv_surround_left = pop_numeric(facts, "CVSL ")
    cv_center = pop_numeric(facts, "CVC ")
    cv_front_left = pop_numeric(facts, "CVFL ")
    pop_fact(facts, "CVEND")  # appears at end of CV presumable so we know it is done
    print(f"Front Left: {cv_front_left} Center: {cv_center}  Front Right: {cv_front_right}")
    print(f"Surround Left: {cv_surround_left}             Surround Right: {cv_surround_right}")


async def zone2_report(z2_facts):
    print("Zone 2 =========================")
    sleep_mode = only(pop_fact(z2_facts, "SLP")).capitalize()
    mute_mode = only(pop_fact(z2_facts, "MU")).capitalize()
    is_on = bool(pop_fact(z2_facts, "ON"))
    bool(pop_fact(z2_facts, "OFF"))
    z2_power = "On" if is_on else "Off"
    _ = pop_fact(z2_facts, "QUICK")
    z2_volume = pop_numeric(z2_facts)
    source_ids = []
    sources = []
    for fact in z2_facts:
        if fact in SOURCES:
            source_ids.append(fact)
            sources.append(SOURCES[fact])
    for source in source_ids:
        z2_facts.remove(source)
    print(f"Zone Power: {z2_power}   Volume: {z2_volume}")
    print(f"Sleep: {sleep_mode}  Mute: {mute_mode}")
    if not sources:
        print(f"Could not find recognized input source for Zone2")
    elif len(sources) == 1:
        print(f"Input Source: {sources[0]}")
    else:
        print(f"Error:  more than one source observed in Zone2!")
    if z2_facts:
        print("Stray facts found for Zone2:")
        print(z2_facts)


async def heos_report(host):
    heos = HeosClientProtocol(host)
    await heos.setup()
    players = heos.get_players()
    await heos.shutdown()
    for player in players:
        if player["ip"] == host:
            print(f"Model: {player['model']}   Serial: {player['serial']}")
            print(f"Name: {player['name']}   Player Id: {player['pid']}   SW: {player['version']}")
            print(f"IP address: {player['ip']} on {player['network']} network")
            print("")
    await heos.shutdown()


async def ask_queries(reader, writer):
    """
    This set of commands seems to elicit all of the unique information I can get out of
    my receiver.  (Denon AVR-S730H)

    :param reader:
    :param writer:
    :return:
    """

    commands = ["PW?", "MV?", "CV?", "MU?", "SI?"]
    commands += ["ZM?", "SV?", "SD?", "SLP?", "MS?"]
    commands += ["MSQUICK ?", "PSLOM ?"]
    commands += ["PSMULTEQ: ?", "PSDYNEQ ?", "PSREFLEV ?", "PSDYNVOL ?"]
    commands += ["PSEFF ?", "PSDEL ?", "PSSWR ?", "PSRSTR ?"]
    commands += ["Z2?", "Z2MU?", "Z2SLP?", "Z2QUICK ?", "TMAN?"]

    # commands = [b"Z2ON", b"SINET"]
    facts = MultiDict()
    for command in commands:
        writer.write(command.encode("ascii") + b"\r")
        lines = await read_lines_until(reader, 0.1)
        for line in lines:
            facts.add(line.strip(), command)
    return facts
