from typing import Dict, Optional
from connection import Connection, PlayerConnection, NoConnection


__all__ = [
    'Player'
]


class Player:

    def __init__(self) -> None:
        self.connection: Connection = NoConnection()
        self.offset: Optional[int] = None
        self.__name = 'NONAME'

    def init(self, connection: PlayerConnection, offset: int):
        # type: (Connection, int) -> None
        self.offset = offset
        self.connection = connection
        self.name = connection.username  # save in case lose connection

    def take_turn(self, turn_info: Dict) -> bool:
        return self.connection.send_data(PlayerConnection.CHANNEL_TURN, data=turn_info)

    def set_connection(self, connection: Connection):
        self.connection = connection

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value
