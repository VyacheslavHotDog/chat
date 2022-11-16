
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

    def __init__(self, user_session, message_json):
        self.rooms = user_session.rooms
        self.room = message_json.get('room', None)
        self.message_json = message_json
        self.user = user_session.name
        self.current_websocket = user_session.session
        self.jwt_token = user_session.jwt_token



