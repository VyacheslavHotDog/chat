import logging
import random
from collections import defaultdict
from settings import PLUGINS
from utils import broadcast
import sys, inspect
from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request


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

        room = 'Default'
        user = f'User{random.randint(0, 999999)}'
        logger.info('%s connected to room %s', user, room)

        # Inform current WS subscription that he's connecting:
        await current_websocket.send_json({'action': 'connecting', 'room': room, 'user': user})

        # Check that the user does not exist in the room already
        if request.app['websockets'][room].get(user):
            logger.warning('User already connected. Disconnecting.')
            await current_websocket.close(code=WSCloseCode.TRY_AGAIN_LATER, message=b'Username already in use')
            return current_websocket
        else:
            # {'websockets': {'<room>': {'<user>': 'obj', '<user2>': 'obj'}}}
            request.app['websockets'][room][user] = current_websocket
            # Inform everyone that user has joined
            for ws in request.app['websockets'][room].values():
                await ws.send_json({'action': 'join', 'user': user, 'room': room})
        # Send out messages whenever they are received

        try:
            async for message in current_websocket:  # for each message in the websocket connection
                if isinstance(message, WSMessage):
                    if message.type == web.WSMsgType.text:  # If it's a text, process it as a message
                        # Parse incoming data
                        message_json = message.json()
                        action = message_json.get('action')
                        if action not in COMMANDS_LIST:
                            await current_websocket.send_json(
                                {'action': action, 'success': False, 'message': 'Not allowed.'}
                            )

                        command = COMMANDS_LIST[action](request, room, message_json, user, current_websocket)
                        data = await command.execute()
                        user = data['user']
                        room = data['room']
        finally:
            # When a connection is stopped, remove the connection
            request.app['websockets'][room].pop(user)
        if current_websocket.closed:
            # This only happens if a close signal is received.
            await broadcast(
                app=request.app, room=room, message={'action': 'left', 'room': room, 'user': user, 'shame': False}
            )
        else:
            # Abrupt disconnect without close signal (e.g. `ctrl`+`c`)
            await broadcast(
                app=request.app, room=room, message={'action': 'left', 'room': room, 'user': user, 'shame': True}
            )
        return current_websocket


async def init_app() -> web.Application:
    """
    Creates an backend app object with a 'websockets' dict on it, where we can store open websocket connections.
    :return: The app
    """
    app = web.Application()
    app['websockets'] = defaultdict(dict)

    app.on_shutdown.append(shutdown)  # Shut down connections before shutting down the app entirely
    chat = Chat()
    app.add_routes([web.get('/chat', handler=chat.ws_chat)])  # `ws_chat` handles this request

    return app


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
    print(COMMANDS_LIST)
    app = init_app()
    web.run_app(app)



if __name__ == '__main__':
    main()
