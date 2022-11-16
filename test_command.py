from server import on_message, init_plugins
from plugins.models import Room, UserSession
from collections import defaultdict
import pytest
import logging
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from plugins.common.output import BroadcastCommand
LOGGER = logging.getLogger(__name__)


class TestCommands(IsolatedAsyncioTestCase):

    def setUp(self):
        self.COMMANDS_LIST = dict()
        self.COMMANDS_LIST = init_plugins(self.COMMANDS_LIST)
        self.jwt1 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTIzLCJuYW1lIjoibGF2b24ifQ.1yV_Lv2DK6slQ94WTuNIOBTQWjIRtHFN3WDYgv4T_aA'
        self.jwt2 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzIxLCJuYW1lIjoiZGltb24ifQ.eBvt0HKJJo7sWCfBm1yYyY8IF44YhuboWikmNmeTfGA'

    @patch.object(BroadcastCommand, 'execute')
    async def test_rooms(self, mock_execute):
        mock_execute.return_value = None
        rooms = defaultdict(dict)
        user_one = UserSession(None, self.jwt1, rooms)
        
        serializer_data = {'action': 'join_room', 'room': 'test'}
        command = self.COMMANDS_LIST['join_room'](user_one, serializer_data)
        data = await command.execute()

        user_two = UserSession(None, self.jwt2, data['rooms'])
        command = self.COMMANDS_LIST['join_room'](user_two, serializer_data)
        data = await command.execute()

        expected_join = {self.jwt1: None, self.jwt2: None}

        self.assertEqual(data['rooms']['test'].users, expected_join)
        mock_execute.assert_called()
        serializer_data = {'action': 'left', 'room': 'test'}
        command = self.COMMANDS_LIST['left'](user_two, serializer_data)
        data = await command.execute()
        expected_left = {self.jwt1: None}

        self.assertEqual(data['rooms']['test'].users, expected_left)
        mock_execute.assert_called()

    @patch.object(BroadcastCommand, 'execute')
    async def test_message(self, mock_execute):
        mock_execute.return_value = None
        rooms = defaultdict(dict)
        user_one = UserSession(None, self.jwt1, rooms)

        serializer_data = {'action': 'join_room', 'room': 'test'}
        command = self.COMMANDS_LIST['join_room'](user_one, serializer_data)
        data = await command.execute()

        serializer_data = {'action': 'chat_message', 'message': 'test message'}
        command = self.COMMANDS_LIST['chat_message'](user_one, serializer_data)
        data = await command.execute()
        expected_result = 'lavon: test message'
        self.assertEqual(data['message'], expected_result)
        mock_execute.assert_called()


if __name__ == '__main__':
    unittest.main()

