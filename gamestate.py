import copy
import re
from objects.nest import Nest
from objects.board import Home, Route
from command import (Command, CommandSequence, MoveInHomeCommand, MoveRouteCommand,
                     MoveToHomeCommand, PassCommand, StartCommand)
from player import Player
from connection import Connection, NoConnection, PlayerConnection
from os import name, system
import numpy as np
from typing import List, Optional
from error import InvalidCommandError, InvalidTurnError, NoError
from exception import InvalidCommandException


class GameState:

    CLEAR_SCREEN_EACH_RUN = False
    PLAYER_LANE_SIZE = 14
    MAX_NUM_PLAYER = 4
    MAX_NUM_PIECE_PER_PLAYER = 4

    def __init__(self, printer: Optional['GameStatePrinter'] = None) -> None:
        self.players: List[Player] = []
        self.route: Optional[Route] = None
        self.homes: List[Home] = []
        self.nests: List[Nest] = []
        self.current_player_index = 0
        self.printer = printer or TerminalPrinter(self.CLEAR_SCREEN_EACH_RUN)
        self.current_dices = None

    def start(self, connections: List[PlayerConnection]):
        self.route = Route(len(connections) * self.PLAYER_LANE_SIZE)
        for i, connection in enumerate(connections):
            player = Player()
            offset = i * self.PLAYER_LANE_SIZE
            player.init(connection, offset)
            self.players.append(player)
            self.homes.append(Home(player))
            self.nests.append(Nest(player))
        self._roll_dice()
        self.send_turn()

    def disconnect(self, connection: Connection):
        player = self.find_player(connection)
        player.set_connection(NoConnection())

    def find_player(self, connection: Connection):
        for player in self.players:
            if player.connection == connection:  # TODO: Should based on authentication
                return player
        return None

    def find_home(self, current_player: Player):
        for home in self.homes:
            if home.player == current_player:
                return home
        return None

    def find_nest(self, current_player: Player):
        for nest in self.nests:
            if nest.player == current_player:
                return nest
        return None

    def is_done(self):
        if len(self.players) == 1:
            return True

        for home in self.homes:
            if home.is_finished():
                return True
        return False

    def _roll_dice(self):
        self.current_dices = np.random.randint(1, 7, size=2).tolist()

    def send_turn(self):
        self.printer.print(self)
        self.current_player().take_turn(self.get_turn_info())

    def current_player(self):
        return self.players[self.current_player_index]

    def receive_command(self, connection: Connection, command_str: str):
        player = self.find_player(connection)
        current_player = self.current_player()

        if player != current_player:
            print('Invalid Turn Error')
            return InvalidTurnError()

        try:
            command = self.parse_command(current_player, command_str)
        except InvalidCommandException:
            return InvalidCommandError(command_str)

        status = command.execute()
        print('Status:', status)
        if not isinstance(status, NoError):
            command.undo()
        return status

    def piece_from_index(self, player, index: int):
        for nest in self.nests:
            if nest.player == player:
                return nest.piece_from_index(index)
        raise ValueError()

    def next_turn(self):
        self._roll_dice()
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.send_turn()

    def get_turn_info(self):
        out = {}
        out['dice_values'] = self.current_dices
        out['homes'] = [home.to_dict() for home in self.homes]
        out['nests'] = [nest.to_dict() for nest in self.nests]
        out['route'] = self.route.to_dict()
        out['metadata'] = {
            'LANE_SIZE': self.PLAYER_LANE_SIZE
        }
        return out

    def parse_command(self, current_player, command_str) -> Command:
        def norm(cmd_str: str):
            cmd_str = re.sub(' +', ' ', cmd_str.strip())
            return cmd_str

        def parse_single_command(cmd: str):
            parts = cmd.split(' ')
            command_key = parts[0]

            if command_key == 'move':
                try:
                    piece = self.piece_from_index(current_player, int(parts[1]))
                    steps = int(parts[2])
                except (ValueError, IndexError):
                    raise InvalidCommandException(cmd)

                home = self.find_home(current_player)
                if home.location(piece) == home.LOC_OUT_BOARD:
                    command = MoveRouteCommand(self.route, piece, dices, steps)
                else:
                    command = MoveInHomeCommand(home, piece, dices, steps)
                return command

            if command_key == 'start':

                try:
                    steps = int(parts[1])
                except IndexError:
                    raise InvalidCommandException(cmd)

                nest = self.find_nest(current_player)
                command = StartCommand(nest, self.route, dices, steps)
                return command

            if command_key == 'move-home':

                try:
                    piece = self.piece_from_index(current_player, int(parts[1]))
                    steps = int(parts[2])
                except (ValueError, IndexError):
                    raise InvalidCommandException(cmd)

                home = self.find_home(current_player)
                command = MoveToHomeCommand(self.route, home, piece, dices, steps)
                return command

            # if command_key == 'help' or command_key == 'h':
            #     help_str = 'HELP!!!!!!!!!!!!!!'
            #     command = ShowHelpCommand(help_str)
            #     return command

            if command_key == 'pass' or command_key == 'p':
                command = PassCommand(current_player)
                return command

            raise InvalidCommandException(command_str)

        dices = copy.deepcopy(self.current_dices)
        commands = [parse_single_command(norm(cmd)) for cmd in command_str.split(';')]
        if len(commands) == 1:
            return commands[0]
        return CommandSequence(commands)


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

    # def __repr__(self) -> str:
    #     steps = []
    #     entrances = {self.home_entrance_location(player): player.name[0] for player in self.players}
    #     print(' '.join([f'{x:02d}' for x in range(len(self.state))]))
    #     for index, step in enumerate(self.state):
    #         if isinstance(step, EmptyPiece) and index in entrances.keys():
    #             representation = f'{entrances[index]}H'
    #         else:
    #             representation = step.name
    #         steps.append(representation)
    #     return ' '.join(steps)

    def _print_board(self, state: GameState):
        route = str(state.route)
        homes = list(zip(*[str(home).split(' ') for home in state.homes]))
        print(route)
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
