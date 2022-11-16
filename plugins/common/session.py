from plugins.common.base import BaseCommand
import logging
from typing import Dict, Tuple, List, Union
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserListCommand(BaseCommand):

    action = 'user_list'

    async def command(self):
        logger.info('%s: %s requested user list', self.room, self.user)
        user_list = await self.retrieve_users(app=self.request.app, room=self.message_json['room'])
        await self.current_websocket.send_json(user_list)
        return {'user': self.user, 'room': self.room}

    async def retrieve_users(self, app: web.Application, room: str) -> Dict[str, Union[str, bool, List[str]]]:
        return {'action': 'user_list', 'success': True, 'room': room, 'users': list(rooms[room].keys())}
