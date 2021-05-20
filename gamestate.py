from os import name, system
import numpy as np
from board import Chessboard
from typing import Optional
from error import NoError


class GameState:

    CLEAR_SCREEN_EACH_RUN = False
    PLAYER_LANE_SIZE = 14
    MAX_NUM_PLAYER = 4
    MAX_NUM_PIECE_PER_PLAYER = 4
    COLORS = ['red', 'green', 'blue', 'yellow']

    def __init__(self, printer: Optional['GameStatePrinter'] = None) -> None:
        self.players = []
        self.current_player_index = 0
        self.printer = printer or TerminalPrinter(self.CLEAR_SCREEN_EACH_RUN)
        self.current_dices = None
        self.chessboard: Optional[Chessboard] = None

    def start(self):
        self.chessboard = Chessboard(self.PLAYER_LANE_SIZE, self.players)

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)

    def remove_player(self, player):
        try:
            self.players.remove(player)
        except ValueError:
            return

    def roll_dice(self):
        return np.random.randint(1, 7, size=2)

    def update(self):
        self.current_dices = self.roll_dice()
        current_player = self.players[self.current_player_index]

        while True:
            self.printer.print(self)
            command = current_player.turn(self)

            status = command.execute()
            print('Status:', status)
            if not isinstance(status, NoError):
                command.undo()
                continue

            break

        self.next_player()

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0


class GameStatePrinter:

    def print(self):
        pass


class TerminalPrinter(GameStatePrinter):
    def __init__(self, clear_screen: bool) -> None:
        super().__init__()
        self.clear_screen = clear_screen

    def print(self, state: GameState):
        if self.clear_screen:
            _clear_screen()

        print('-' * 10)
        self._print_board(state)
        print('-' * 10)

        current_player = state.players[state.current_player_index]
        print(f'Current player: {current_player.name}')
        print('-' * 10)

    def _print_board(self, state: GameState):
        chessboard = str(state.chessboard)
        homes = [player.home for player in state.players[1:] + [state.players[0]]]
        homes = list(zip(*[str(home).split(' ') for home in homes]))
        print(chessboard)
        spaces = '  ' * (GameState.PLAYER_LANE_SIZE - 1) + ' ' * GameState.PLAYER_LANE_SIZE
        for home in homes:
            home_str = spaces[:-1] + spaces.join(home)
            print(home_str)


# define our clear function
def _clear_screen():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
