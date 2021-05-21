from error import Status
from socketio.server import Server
from exception import InvalidCommandException
from gamestate import GameState
from command import Command, CommandFactory, PassCommand
import re

from board import Home
from piece import Piece


class Player:

    MAX_NUM_PIECE = 4

    def __init__(self, name: str) -> None:
        self.name = name
        self.pieces = [Piece(self, i) for i in range(self.MAX_NUM_PIECE)]
        self.home: Home = Home()
        self.is_disconnected = False

    def set_disconnected(self, is_disconnected: bool):
        self.is_disconnected = is_disconnected

    def take_turn(self, gamestate: GameState) -> Command:
        raise NotImplementedError()

    def receive_status(self, status: Status):
        raise NotImplementedError()


class ConsolePlayer(Player):

    def take_turn(self, gamestate: GameState):
        if self.is_disconnected:
            return PassCommand(self)

        print('Dices:', gamestate.current_dices)

        while True:
            command_str = input(f'{self.name}> ')
            command_str = re.sub(' +', ' ', command_str.strip())
            if len(command_str) == 0:
                continue

            try:
                command = CommandFactory.parse(self, gamestate, command_str)
            except InvalidCommandException as e:
                print(f'Unknow command: {e}')
                continue

            gamestate.receive_command(command)


class SocketIOPlayer(Player):
    def __init__(self, name: str, sio, sid) -> None:
        super().__init__(name)
        self.sid = sid
        self.sio: Server = sio

    def take_turn(self, gamestate: GameState) -> Command:
        data = gamestate.to_dict()
        print(data)
        self.sio.emit('turn', data=data, room=self.sid)
