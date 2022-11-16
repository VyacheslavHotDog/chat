from plugins.common.base import BaseCommand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('client')


class OutputCommand(BaseCommand):

    action = 'output'

    def __init__(self, room, rooms, user, jwt_token, msg = None):
        self.room = room
        self.rooms = rooms
        self.user_name = user
        self.jwt_token = jwt_token
        self.msg = msg


class LeftRoomOutputCommand(OutputCommand):
    action = 'left_output'

    async def command(self):
        self.message = f'User {self.user_name} left the room {self.room}'
        await BroadcastCommand(self).execute()


class JoinRoomCommand(OutputCommand):

    action = 'join'

    async def command(self):
        self.message = f'User {self.user_name} joined the room {self.room}'
        await BroadcastCommand(self, self.jwt_token).execute()


class ChatCommand(OutputCommand):

    action = 'chat'

    async def command(self):
        logger.info(self.msg)
        self.message = f'{self.user_name}: {self.msg}'
        await BroadcastCommand(self, self.jwt_token).execute()
        return self.message


class BroadcastCommand(OutputCommand):

    action = 'broadcast'

    def __init__(self, execute_command, ignore_user = None):
        self.execute_command = execute_command
        self.ignore_user = ignore_user

    async def command(self):
        logger.info(self.execute_command.room)
        for user, ws in self.execute_command.rooms[self.execute_command.room].users.items():
            if self.ignore_user and user == self.ignore_user:
                pass
            else:
                await ws.send_json(self.execute_command.message)
