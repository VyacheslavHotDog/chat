import logging
import random
from collections import defaultdict
from settings import PLUGINS
from utils import to_jwt, from_jwt
import sys, inspect
from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request
from plugins.models import UserSession
from serializers.common_serializer import MessageSerializer
from plugins.common.output import LeftRoomOutputCommand, BroadcastCommand
from plugins.models import Room
from plugins.common.handle_error import HandleErrorCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
COMMANDS_LIST = dict()


class Chat:
    rooms = defaultdict(dict)

    async def ws_chat(self, request: Request) -> web.WebSocketResponse:

        current_websocket = web.WebSocketResponse(autoping=True, heartbeat=60)  # Create a websocket response object
        ready = current_websocket.can_prepare(request=request)
        if not ready:
            await current_websocket.close(code=WSCloseCode.PROTOCOL_ERROR)
        await current_websocket.prepare(request)  # Load it with the request object
        request_data = request.rel_url.query

        jwt_token = request_data['jwt_token']

        user_session = UserSession(current_websocket, jwt_token, self.rooms)
        try:

            async for message in user_session.session:
                data = await on_message(message, user_session)
        finally:
            pass

        return user_session.session


async def init_app() -> web.Application:

    app = web.Application()
    app.on_shutdown.append(shutdown)  # Shut down connections before shutting down the app entirely
    chat = Chat()
    app.add_routes([web.get('/chat', handler=chat.ws_chat)])  # `ws_chat` handles this request

    return app


async def on_message(message, user_session):
    if isinstance(message, WSMessage):
        if message.type == web.WSMsgType.text:
            serializer_data = MessageSerializer().serialize(message)
            action = serializer_data.get('action')
            if action not in COMMANDS_LIST:
                await HandleErrorCommand(action, 'Not allowed.').execute()

            command = COMMANDS_LIST[action](user_session, serializer_data)
            data = await command.execute()
            return data


async def shutdown(rooms):
    for room in rooms:
        for ws in room.users.values():
            ws.close()
    rooms.clear()


def init_plugins(COMMANDS_LIST):
    from os import listdir
    from os.path import isfile, join
    import importlib
    for plugin in PLUGINS:
        onlyfiles = [f for f in listdir(plugin.replace('.', '/')) if isfile(join(plugin.replace('.', '/'), f))]
        for x in onlyfiles:
            module = plugin + '.' + x[:-3]
            importlib.import_module(module)
            clsmembers = inspect.getmembers(sys.modules[module], inspect.isclass)
            for cls in clsmembers:
                COMMANDS_LIST[cls[1].action] = cls[1]
    return COMMANDS_LIST

def main():
    init_plugins(COMMANDS_LIST)
    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
