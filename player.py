from typing import Dict, List, Optional
from connection import PlayerConnection

from board import Home
from piece import Piece


class Player:

    MAX_NUM_PIECE = 4

    def __init__(self, connection: PlayerConnection) -> None:
        self.connection = connection
        self.name = connection.username  # save in case lose connection
        self.init()

    def init(self, pieces=None, home=None):
        # type: (Optional[List[Piece]], Optional[Home]) -> None
        self.pieces = pieces or [Piece(self, i) for i in range(self.MAX_NUM_PIECE)]
        self.home = home or Home()

    def take_turn(self, turn_info: Dict) -> bool:
        return self.connection.send_data(PlayerConnection.CHANNEL_TURN, data=turn_info)

    def set_connection(self, connection: PlayerConnection):
        self.connection = connection
