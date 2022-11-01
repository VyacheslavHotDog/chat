
import logging

from settings import MIDDLEWARE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCommand:
    action = 'base'

    def preprocess_middleware(self):
        for middleware in MIDDLEWARE:
            middleware().preProcess(self)

    def postrocess_middleware(self):
        for middleware in MIDDLEWARE:
            middleware().postProcess(self)


    def command(self):
        pass

    async def execute(self):
        self.preprocess_middleware()
        res = await self.command()
        self.postrocess_middleware()
        return res

    def __init__(self, request, room, message_json, user, current_websocket):
        self.request = request
        self.room = room
        self.message_json = message_json
        self.user = user
        self.current_websocket = current_websocket
        logger.info(self.__class__.__name__)

