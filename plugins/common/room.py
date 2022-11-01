from plugins.common.base import BaseCommand
import logging
from typing import Dict,  Tuple, Union
from aiohttp import web

from utils import broadcast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class JoinRoomCommand(BaseCommand):

    action = 'join_room'

    async def command (self):
        return_body, success = await self.change_room(
            app=self.request.app, new_room=self.message_json.get('room'), old_room=self.room, nick=self.user
        )
        if not success:
            logger.info(
                '%s: Unable to change room for %s to %s, reason: %s',
                self.room,
                self.user,
                self.message_json.get('room'),
                return_body['message'],
            )
            await self.current_websocket.send_json(return_body)
        else:
            logger.info('%s: User %s joined the room', self.user, self.message_json.get('room'))
            await broadcast(
                app=self.request.app,
                room=self.room,
                message={'action': 'left', 'room': self.room, 'user': self.user, 'shame': False},
            )
            await broadcast(
                app=self.request.app,
                room=self.message_json.get('room'),
                message={'action': 'joined', 'room': self.room, 'user': self.user},
                ignore_user=self.user,
            )
            self.room = self.message_json.get('room')
        return {'user': self.user, 'room':self.room}

    async def change_room(self,
            app: web.Application, new_room: str, old_room: str, nick: str
    ) -> Tuple[Dict[str, Union[str, bool]], bool]:

        if not isinstance(new_room, str) or not 3 <= len(new_room) <= 20:
            return (
                {'action': 'join_room', 'success': False,
                 'message': 'Room name must be a string and between 3-20 chars.'},
                False,
            )
        if nick in app['websockets'][new_room].keys():
            return (
                {'action': 'join_room', 'success': False, 'message': 'Name already in use in this room.'},
                False,
            )
        app['websockets'][new_room][nick] = app['websockets'][old_room].pop(nick)
        return {'action': 'join_room', 'success': True, 'message': ''}, True