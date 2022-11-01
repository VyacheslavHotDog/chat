import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def broadcast( app: web.Application, room: str, message: dict, ignore_user: str = None) -> None:
    for user, ws in app['websockets'][room].items():
        if ignore_user and user == ignore_user:
            pass
        else:
            logger.info('> Sending message %s to %s', message, user)
            await ws.send_json(message)