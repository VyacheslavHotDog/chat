
import logging
import asyncio
from aiohttp import ClientSession, ClientWebSocketResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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