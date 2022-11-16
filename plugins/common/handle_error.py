from plugins.common.base import BaseCommand
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HandleErrorCommand(BaseCommand):
    action = 'handle_error'

    def __init__(self, action, message):
        self.message = message
        self.action = action

    async def command(self):
        return {"action": self.action, "success": False, "message": self.message}

