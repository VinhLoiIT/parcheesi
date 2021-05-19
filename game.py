from os import name, system
from typing import List

import numpy as np

from board import Chessboard, Home
from command import (Command, InvalidCommandException, MoveCommand,
                     MoveHomeCommand, PassCommand, ShowHelpCommand,
                     UnknowCommandException)
from objects import ConsolePlayer, Piece, Player


class Game:

    CLEAR_SCREEN_EACH_RUN = False
    PLAYER_LANE_SIZE = 14
    MAX_NUM_PLAYER = 4
    MAX_NUM_PIECE_PER_PLAYER = 4

    def __init__(self) -> None:
        self.chessboard = Chessboard(self.PLAYER_LANE_SIZE, self.MAX_NUM_PLAYER)
        self.players: List[Player] = []
        self.homes: List[Home] = []
        self.pieces: List[Piece] = []
        for i, color in enumerate(['red', 'green', 'blue', 'yellow']):
            offset = i * self.PLAYER_LANE_SIZE
            player = ConsolePlayer(color, offset)
            self.players.append(player)
            self.homes.append(Home())
            self.pieces.extend([Piece(player, f'{color[0]}{index}') for index in range(self.MAX_NUM_PIECE_PER_PLAYER)])

        self.current_player_index = 0

    def print_state(self):
        # TODO: move to a Printer class which could be derived later.
        chessboard = str(self.chessboard)
        homes = list(zip(*[str(home).split(' ') for home in self.homes]))
        print(chessboard)
        spaces = '  ' * (self.PLAYER_LANE_SIZE - 1) + ' ' * self.PLAYER_LANE_SIZE
        for home in homes:
            home_str = spaces[:-1] + spaces.join(home)
            print(home_str)

    def run_loop(self):
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                ans = input('Are you sure want to quit? [y/n]: ')
                if ans.upper() == 'Y':
                    break

        print('Game Over!')

    def run(self):
        if self.CLEAR_SCREEN_EACH_RUN:
            _clear_screen()

        print('-' * 10)
        self.print_state()
        print('-' * 10)

        dice_values = self.roll_dice()
        current_player = self.players[self.current_player_index]

        print(f'Current player: {current_player.name}')
        print('-' * 10)

        command_str = current_player.turn(dice_values)

        try:
            command = self.parse_command(command_str)
        except UnknowCommandException as e:
            print(f'Unknow command: {e}')
            if self.CLEAR_SCREEN_EACH_RUN:
                input('Press any key to continue')
            else:
                print('Press any key to continue')
            return
        except InvalidCommandException as e:
            print(f'Invalid command {e}')
            if self.CLEAR_SCREEN_EACH_RUN:
                input('Press "help" or "h" to show help')
            else:
                print('Press "help" or "h" to show help')
            return

        command.execute()

        self.current_player_index = self.current_player_index + 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0

    def roll_dice(self):
        return np.random.randint(1, 7, size=2)

    def piece_from_name(self, name):
        for piece in self.pieces:
            if piece.name == name:
                return piece
        raise ValueError()

    def parse_command(self, command_str: str) -> Command:
        parts = command_str.split(' ')
        command_key = parts[0]

        if command_key == 'move':
            try:
                piece = self.piece_from_name(parts[1])
            except ValueError:
                raise InvalidCommandException(command_str)

            steps = int(parts[2])
            command = MoveCommand(self.chessboard, piece, steps)
            return command

        if command_key == 'move-home':
            piece,  = parts[1], int(parts[2])
            command = MoveHomeCommand()
            return command

        if command_key == 'help' or command_key == 'h':
            help_str = 'HELP!!!!!!!!!!!!!!'
            command = ShowHelpCommand(help_str)
            return command

        if command_key == 'pass' or command_key == 'p':
            command = PassCommand(self)
            return command

        raise UnknowCommandException(command_str)


# define our clear function
def _clear_screen():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


if __name__ == '__main__':
    game = Game()
    game.run_loop()
