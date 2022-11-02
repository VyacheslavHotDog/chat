
class UserSession:

    def __init__(self, session, jwt_data):
        self.id = jwt_data.get('id', random.randint(0, 999999))
        self.name = jwt_data.get('name', f'User{random.randint(0, 999999)}')
        self.room = jwt_data.get('room', 'Default')
        self.session = session