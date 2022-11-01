from plugins.common.base import BaseCommand
import logging

from utils import broadcast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatMessageCommand(BaseCommand):

    action = 'chat_message'

    async def command(self):
        logger.info('%s: Message: %s', self.room, self.message_json.get('message'))
        await self.current_websocket.send_json(
            {'action': 'chat_message', 'success': True, 'message': self.message_json.get('message')}
        )
        await broadcast(
            app=self.request.app,
            room=self.room,
            message={'action': 'chat_message', 'message': self.message_json.get('message'), 'user': self.user},
            ignore_user=self.user,
        )
        return {'user': self.user, 'room':self.room}

