from plugins.common.base import BaseCommand
from plugins.common.output import ChatCommand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatMessageCommand(BaseCommand):

    action = 'chat_message'

    async def command(self):
        msg = self.message_json.get('message')
        message = await ChatCommand(self.room, self.rooms, self.user, self.jwt_token, msg).command()
        return {'user': self.user, 'room': self.room, 'message': message}

