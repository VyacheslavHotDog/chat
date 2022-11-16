import random
from utils import to_jwt, from_jwt


class UserSession:

    def __init__(self, session, jwt_token, rooms):
        jwt_data = from_jwt(jwt_token)
        self.jwt_token = jwt_token
        self.id = jwt_data.get('id', random.randint(0, 999999))
        self.name = jwt_data.get('name', f'User{random.randint(0, 999999)}')
        self.rooms = rooms
        self.session = session

class Room:
    action = 'None'

    def __init__(self, name):
        self.name = name
        self.users = dict()
