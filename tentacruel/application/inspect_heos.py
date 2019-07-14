import asyncio

from inflection import singularize, pluralize
from tentacruel import HeosClientProtocol, RECEIVER_IP, HEOS_PORT


def inflect(that,word):
    """

    :param that: some object;  if it has a length,  we use that
    :param word: this word will be made singular or plural depending on the singularity or plurarlity of that
    :return: inflected word
    """

    try:
        cnt = len(that)
    except TypeError:
        cnt = 1

    inflected_word = singularize(word) if cnt == 1 else pluralize(word)
    return f"{cnt} {inflected_word}"


async def application(that:HeosClientProtocol):
    that.system
    playerz = inflect(that._players,"players")
    print(f"Found {playerz}:")
    for (number, player) in enumerate(that._players):
        index = number + 1
        print()
        print(f"Player {index}:")
        if "serial" in player:
            print(f"   Serial Number: {player['serial']}")
        if player["name"] != player["model"]:
            print(f"   Name: {player['name']}")
        print(f"   Model: {player['model']}   Version: {player['version']}")
        print(f"   IP: {player['ip']} ({player['network']})")


loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: HeosClientProtocol(loop,start_action=application),
    RECEIVER_IP, HEOS_PORT
)

loop.run_until_complete(coro)
loop.run_forever()
loop.close()
