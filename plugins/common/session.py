from plugins.common.base import BaseCommand
import logging
from typing import Dict, Tuple, List, Union
from aiohttp import web

from utils import broadcast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InitSessionCommand(BaseCommand):

    action = 'set_nick'

    async def command(self):
        return_body, success = await self.change_nick(
            app=self.request.app, room=self.room, new_nick=self.message_json.get('nick'), old_nick=self.user
        )
        if not success:
            logger.warning(
                'Failed to set nick %s for %s. Reason %s',
                self.message_json.get('nick'),
                self.user,
                return_body['message'],
            )
            await self.current_websocket.send_json(return_body)
        else:
            logger.info('%s: %s is now known as %s', self.room, self.user, self.message_json.get('nick'))
            await self.current_websocket.send_json(return_body)
            await broadcast(
                app=self.request.app,
                room=self.room,
                message={
                    'action': 'nick_changed',
                    'room': self.room,
                    'from_user': self.user,
                    'to_user': self.message_json.get('nick'),
                },
                ignore_user=self.message_json.get('nick'),
            )
            self.user = self.message_json.get('nick')
        return {'user': self.user, 'room':self.room}

    async def change_nick(self,
            app: web.Application, room: str, new_nick: str, old_nick: str
    ) -> Tuple[Dict[str, Union[str, bool]], bool]:
        if not isinstance(new_nick, str) or not 3 <= len(new_nick) <= 20:
            return (
                {'action': 'set_nick', 'success': False, 'message': 'Name must be a string and between 3-20 chars.'},
                False,
            )
        if new_nick in app['websockets'][room].keys():
            return (
                {'action': 'set_nick', 'success': False, 'message': 'Name already in use.'},
                False,
            )
        else:
            app['websockets'][room][new_nick] = app['websockets'][room].pop(old_nick)
            return {'action': 'set_nick', 'success': True, 'message': ''}, True

class UserListCommand(BaseCommand):

    action = 'user_list'

    async def command(self):
        logger.info('%s: %s requested user list', self.room, self.user)
        user_list = await self.retrieve_users(app=self.request.app, room=self.message_json['room'])
        await self.current_websocket.send_json(user_list)
        return {'user': self.user, 'room': self.room}

    async def retrieve_users(self, app: web.Application, room: str) -> Dict[str, Union[str, bool, List[str]]]:
        return {'action': 'user_list', 'success': True, 'room': room, 'users': list(app['websockets'][room].keys())}