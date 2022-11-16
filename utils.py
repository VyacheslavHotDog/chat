import logging
from aiohttp import web
import jwt
from settings import JWT_SECRET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def to_jwt(data: dict):
    return jwt.encode(data, JWT_SECRET, algorithm="HS256")


def from_jwt(encoded_jwt):
    return jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
