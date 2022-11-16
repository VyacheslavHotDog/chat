from plugins.common.base import BaseCommand
import logging
from typing import Dict,  Tuple, Union
from aiohttp import web
from plugins.common.handle_error import HandleErrorCommand
from plugins.common.output import LeftRoomOutputCommand, JoinRoomCommand
from plugins.models import Room
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChangeRoomCommand(BaseCommand):

    action = 'join_room'

    async def command(self):
        rooms, success = await self.change_room(
            rooms=self.rooms, new_room=self.message_json.get('room'), nick=self.jwt_token
        )
        if success:
            self.rooms = rooms
            logger.info('\n rooms %s \n', self.rooms)
            await JoinRoomCommand(self.message_json.get('room'), self.rooms, self.user, self.jwt_token).command()
            self.room = self.message_json.get('room')
        return {'user': self.user, 'room': self.room, 'rooms':self.rooms}

    async def change_room(self,
            rooms, new_room: str, nick: str
    ) -> Tuple[Dict[str, Union[str, bool]], bool]:

        if not isinstance(new_room, str) or not 3 <= len(new_room) <= 20:
            return HandleErrorCommand(self.action, 'Room name must be a string and between 3-20 chars.').execute()
        if new_room not in rooms:
            rooms[new_room] = Room(new_room)
        rooms[new_room].users[nick] = self.current_websocket
        return rooms, True


class LeftRoomCommand(BaseCommand):

    action = 'left'

    async def command(self):
        self.room = self.message_json.get('room')
        if self.jwt_token in self.rooms[self.room].users:
            self.rooms[self.room].users.pop(self.jwt_token)
            await LeftRoomOutputCommand(self.room, self.rooms, self.user, self.jwt_token).command()
        return {'user': self.user, 'room': self.room, 'rooms': self.rooms}