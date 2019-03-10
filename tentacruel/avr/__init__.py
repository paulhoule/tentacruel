# pylint: disable=missing-docstring
# pylint: disable=invalid-name

from asyncio import open_connection, get_event_loop, create_task

#
#
#
async def get_z2_status():
    reader, writer = await open_connection('192.168.0.10', 23)

    async def read_loop():
        while not reader.at_eof():
            line = await reader.readuntil(b'\r')
            print(line)

    create_task(read_loop())
    commands = [b"Z2ON"]
    for command in commands:
        writer.write(command+b"\r")

if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(get_z2_status())
    loop.run_forever()
    loop.close()
