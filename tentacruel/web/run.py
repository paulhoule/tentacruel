# pylint: disable=missing-docstring

from aiohttp.web import Application, Response, run_app, get
from tentacruel import keep
from tentacruel.config import get_config

async def hello(_):
    return Response(text="Hello, world")

def main():
    config = get_config()
    app = Application()
    web_config = config["web"]
    prefix = web_config["prefix"]
    app.add_routes([get(prefix, hello)])

    run_config = keep(web_config, {"host", "port"})
    run_app(app, **run_config)

if __name__ == "__main__":
    main()
