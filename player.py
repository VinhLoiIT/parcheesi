from exception import InvalidCommandException
from gamestate import GameState
from command import Command, CommandFactory
import re

from board import Home
from piece import Piece


class Player:

    MAX_NUM_PIECE = 4

    def __init__(self, name: str) -> None:
        self.name = name
        self.pieces = [Piece(self, i) for i in range(self.MAX_NUM_PIECE)]
        self.home: Home = Home()

    def turn(self, gamestate: GameState) -> Command:
        raise NotImplementedError()


class ConsolePlayer(Player):

    def turn(self, gamestate: GameState):
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

            return command
