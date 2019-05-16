"""
Run module for TC web application.

"""
import json

from aiohttp.web import Application, Response, run_app, get
from tentacruel import keep
from tentacruel.config import get_config
from tentacruel.sqs import SqsQueue

class WebApp():
    """
    This design is slightly confused but to avoid any baggage involving
    initialization it does not inherit from the Application class in aiohttp.web
    """

    def __init__(self, config):
        """
        Constructor

        :param config: application configuration dictionary
        """
        self.sqs = SqsQueue(config)
        web_config = config["web"]
        self.prefix = web_config["prefix"]

    def attach_to(self, app: Application) -> None:
        """
        Attach this fully initialzed application to the ``Application`` object so we
        can run

        :param app:
        :return:
        """
        app.add_routes([get(self.prefix+"sqs/count/", self.sqs_count)])

    async def sqs_count(self, _) -> Response:
        """
        Return the message count in the SQS queue

        :param _: Request Parameter that we ignore because we do the same regardless
        :return: the Response
        """
        message = {
            "message_count": self.sqs.count()
        }
        return Response(text=json.dumps(message))

def main() -> None:
    """
    Main method of application

    :return: nothing
    """
    config = get_config()
    app = Application()
    web_config = config["web"]
    webapp = WebApp(config)
    webapp.attach_to(app)

    run_config = keep(web_config, {"host", "port"})
    run_app(app, **run_config)

if __name__ == "__main__":
    main()
