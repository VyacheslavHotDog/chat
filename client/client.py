import asyncio
import logging

from aioconsole import ainput
from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage
from aiohttp.web import WSMsgType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('client')


async def ping(websocket: ClientWebSocketResponse) -> None:
    """
    A function that sends a PING every minute to keep the connection alive.

    Note that you can do this automatically by simply using `autoping=True` and `heartbeat`.
    This is implemented as an example.

    :param websocket: Websocket connection
    :return: None, forever living task
    """
    while True:
        logger.debug('< PING')
        await websocket.ping()
        await asyncio.sleep(60)


class Client:

    async def subscribe_to_messages(self, websocket: ClientWebSocketResponse) -> None:
        """
        A subscription handler to subscribe to messages. Simply logs them.

        :param websocket: Websocket connection
        :return: None, forever living task
        """
        test_messages = ['User dimon joined the room test', 'dimon: t123']
        async for message in websocket:
            if isinstance(message, WSMessage):
                if message.type == WSMsgType.text:
                    message_json = message.json()
                    logger.info('> Message from server received: %s', message_json)
                    assert message_json == test_messages.pop(0)

    async def handler(self, jwt_token, room: str = None ) -> None:
        async with ClientSession() as session:
            async with session.ws_connect(f'ws://127.0.0.1:8080/chat?jwt_token={jwt_token}', ssl=False) as ws:
                read_message_task = asyncio.create_task(self.subscribe_to_messages(websocket=ws))
                await ws.send_json({'action': 'join_room', 'room': room})

                await ws.send_json({'action': 'chat_message', "message": "t123"})

                ping_task = asyncio.create_task(ping(websocket=ws))
                await asyncio.wait(
                    [read_message_task, ping_task], return_when=asyncio.FIRST_COMPLETED,
                )

