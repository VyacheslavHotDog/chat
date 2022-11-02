import logging
import random
from collections import defaultdict
from settings import PLUGINS
from utils import broadcast, to_jwt, from_jwt
import sys, inspect
from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request
from plugins.models import UserSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
COMMANDS_LIST = dict()


class Chat:

    async def ws_chat(self, request: Request) -> web.WebSocketResponse:

        current_websocket = web.WebSocketResponse(autoping=True, heartbeat=60)  # Create a websocket response object
        ready = current_websocket.can_prepare(request=request)
        if not ready:
            await current_websocket.close(code=WSCloseCode.PROTOCOL_ERROR)
        await current_websocket.prepare(request)  # Load it with the request object
        request_data = request.rel_url.query

        jwt_token = request_data['jwt_token']
        jwt_data = from_jwt(jwt_token)
        user_session = UserSession(current_websocket, jwt_data)

        # Check that the user does not exist in the room already
        if request.app['websockets'][user_session.room].get(user_session.name):
            logger.warning('User already connected. Disconnecting.')
            await current_websocket.close(code=WSCloseCode.TRY_AGAIN_LATER, message=b'Username already in use')
            return current_websocket
        else:
            request.app['websockets'][user_session.room][user_session.name] = current_websocket
            # Inform everyone that user has joined
            for ws in request.app['websockets'][user_session.room].values():
                await ws.send_json({'action': 'join', 'user': user_session.name, 'room': user_session.room})

        try:
            async for message in current_websocket:
                data = await on_message(message, current_websocket)
                user_session.name = data['user']
                user_session.room = data['room']
        finally:

            request.app['websockets'][user_session.room].pop(user_session.name)
        if current_websocket.closed:

            await broadcast(
                app=request.app, room=user_session.room, message={'action': 'left', 'room': user_session.room, 'user': user_session.name, 'shame': False}
            )
        else:

            await broadcast(
                app=request.app, room=user_session.room, message={'action': 'left', 'room': user_session.room, 'user': user_session.name, 'shame': True}
            )
        return current_websocket


async def init_app() -> web.Application:

    app = web.Application()
    app['websockets'] = defaultdict(dict)

    app.on_shutdown.append(shutdown)  # Shut down connections before shutting down the app entirely
    chat = Chat()
    app.add_routes([web.get('/chat', handler=chat.ws_chat)])  # `ws_chat` handles this request

    return app

async def on_message(message,current_websocket):
    if isinstance(message, WSMessage):
        if message.type == web.WSMsgType.text:
            message_json = message.json()
            action = message_json.get('action')
            if action not in COMMANDS_LIST:
                await current_websocket.send_json(
                    {'action': action, 'success': False, 'message': 'Not allowed.'}
                )

            command = COMMANDS_LIST[action](request, user_session.room, message_json, user_session.name,
                                            current_websocket)
            data = await command.execute()
            return data

async def shutdown(app):
    for room in app['websockets']:
        for ws in app['websockets'][room].values():
            ws.close()
    app['websockets'].clear()

def init_plugins():
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


def main():
    init_plugins()
    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
