import asyncio
import logging

from aioconsole import ainput
from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage
from aiohttp.web import WSMsgType

from utils import ping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('client')


class Client:

    async def subscribe_to_messages(self, websocket: ClientWebSocketResponse) -> None:
        """
        A subscription handler to subscribe to messages. Simply logs them.

        :param websocket: Websocket connection
        :return: None, forever living task
        """
        async for message in websocket:
            if isinstance(message, WSMessage):
                if message.type == WSMsgType.text:
                    message_json = message.json()
                    if message_json.get('action') == 'chat_message' and not message_json.get('success'):
                        print(f'>>>{message_json["user"]}: {message_json["message"]}')
                    logger.info('> Message from server received: %s', message_json)


    async def send_input_message(self, websocket: ClientWebSocketResponse) -> None:

        while True:
            message = await ainput('<<<')
            if message == 'command close':
                await websocket.close()
            else:
                logger.info('\n< Sending message: %s', message)
                await websocket.send_json({'action': 'chat_message', 'message': message})


    async def handler(self, nick: str = None, room: str = None) -> None:

        async with ClientSession() as session:
            async with session.ws_connect('ws://127.0.0.1:8080/chat', ssl=False) as ws:
                read_message_task = asyncio.create_task(self.subscribe_to_messages(websocket=ws))
                # Change nick to `Jonas` and change room to `test`
                await ws.send_json({'action': 'join_room', 'room': room})
                await ws.send_json({'action': 'set_nick', 'nick': nick})

                ping_task = asyncio.create_task(ping(websocket=ws))
                send_input_message_task = asyncio.create_task(self.send_input_message(websocket=ws))

                await ws.send_json({'action': 'user_list', 'room': 'test'})


                done, pending = await asyncio.wait(
                    [read_message_task, ping_task, send_input_message_task], return_when=asyncio.FIRST_COMPLETED,
                )

                if not ws.closed:
                    await ws.close()
                # Then, we cancel each task which is pending:
                for task in pending:
                    task.cancel()
                # At this point, everything is shut down. The program will exit.


if __name__ == '__main__':
    input_nick = input('Nick (random if not provided): ')
    input_room = input('Room (`Default` if not provided): ')
    client = Client()
    asyncio.run(client.handler(nick=input_nick, room=input_room))
