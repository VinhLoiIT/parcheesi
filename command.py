from error import CannotMoveError, NoError, Status
from typing import Iterable, List
from board import Chessboard
import re
from exception import InvalidCommandException
from piece import EmptyPiece, Piece
from copy import deepcopy


class Command:
    def execute(self) -> Status:
        pass

    def undo(self):
        pass


class CommandSequence(Command):
    def __init__(self, cmds: Iterable[Command]) -> None:
        self.commands = cmds
        self.max_success_index = -1

    def execute(self):
        for i, command in enumerate(self.commands):
            status = command.execute()
            if not isinstance(status, NoError):
                return status
            self.max_success_index = i
        return NoError()

    def undo(self):
        for command in reversed(list(self.commands[:self.max_success_index + 1])):
            command.undo()


class MoveCommand(Command):
    def __init__(self, board: Chessboard, piece: Piece, dices: List[int], steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps
        self.dices = dices

    def execute(self):

        if self.steps not in self.dices:
            return CannotMoveError(self.piece.name, self.steps)

        piece_location = self.board.location(self.piece)
        if piece_location == self.board.LOC_OUT_BOARD:
            new_location = self.board.offset[self.piece.player]
        elif piece_location + self.steps + 1 > len(self.board.state):
            new_location = (piece_location + self.steps) % len(self.board.state)
        elif piece_location + self.steps < 0:
            new_location = piece_location + self.steps - 1 + len(self.board.state)
        else:
            new_location = piece_location + self.steps

        self.old_location = piece_location
        self.new_location = new_location

        if not self.board.is_able_to_move(self.piece, self.steps):
            return CannotMoveError(self.piece.name, self.steps)

        self.board.set_location(self.piece, self.new_location)
        self.index = self.dices.index(self.steps)
        self.dices.pop(self.index)
        return NoError()

    def undo(self):
        self.board.set_location(self.piece, self.old_location)
        self.dices.insert(self.index, self.steps)


class MoveHomeCommand(Command):
    def __init__(self, board: Chessboard, piece: Piece, dices: List[int], steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps
        self.dices = dices
        self.home = board.homes[piece.player]

    def is_able_to_move(self, entrance_location, home_location, board_location):
        entrance_location = self.board.home_entrance_location(self.piece.player)
        home_location = self.home.location(self.piece)
        board_location = self.board.location(self.piece)
        if board_location == entrance_location:
            if all([isinstance(step, EmptyPiece) for step in self.home.state[:self.steps]]):
                return True
            return False

        if home_location != self.home.LOC_OUT_BOARD:
            if isinstance(self.home.state[self.steps - 1], EmptyPiece) and home_location == self.steps - 2:
                return True
            return False

        return False

    def execute(self):

        if self.steps not in self.dices:
            return CannotMoveError(self.piece.name, self.steps)

        entrance_location = self.board.home_entrance_location(self.piece.player)
        home_location = self.home.location(self.piece)
        board_location = self.board.location(self.piece)

        self.old_home_location = home_location
        self.old_board_location = board_location

        if not self.is_able_to_move(entrance_location, home_location, board_location):
            return CannotMoveError(self.piece.name, self.steps)

        if board_location == entrance_location:
            if all([isinstance(step, EmptyPiece) for step in self.home.state[:self.steps]]):
                self.board.state[entrance_location] = EmptyPiece()
                self.home.state[self.steps - 1] = self.piece
                self.index = self.dices.index(self.steps)
                self.dices.pop(self.index)
                return NoError()

        if home_location != self.home.LOC_OUT_BOARD:
            if isinstance(self.home.state[self.steps - 1], EmptyPiece) and home_location == self.steps - 2:
                self.home.state[home_location] = EmptyPiece()
                self.home.state[self.steps - 1] = self.piece
                self.index = self.dices.index(self.steps)
                self.dices.pop(self.index)
                return NoError()

        return CannotMoveError(self.piece.name, self.steps)

    def undo(self):
        entrance_location = self.board.home_entrance_location(self.piece.player)

        if self.old_board_location == entrance_location:
            self.board.state[entrance_location] = self.piece
            self.home.state[self.steps - 1] = EmptyPiece()
            self.dices.insert(self.index, self.steps)

        if self.old_home_location != self.home.LOC_OUT_BOARD:
            self.home.state[self.old_home_location] = self.piece
            self.home.state[self.steps - 1] = EmptyPiece()
            self.dices.insert(self.index, self.steps)


class PassCommand(Command):
    def __init__(self, player) -> None:
        super(PassCommand, self).__init__()
        self.player = player

    def execute(self):
        print(f'Player {self.player.name} passed.')
        return NoError()


class ShowHelpCommand(Command):
    def __init__(self, help_str) -> None:
        super().__init__()
        self.help_str = help_str

    def execute(self):
        print(self.help_str)
        input('Press any key to continue.')
        return NoError()


class CommandFactory:

    @staticmethod
    def parse(player, chessboard, dices, command_str: str):
        def norm(cmd_str: str):
            cmd_str = re.sub(' +', ' ', cmd_str.strip())
            return cmd_str

        def piece_from_index(player, index: int):
            for piece in player.pieces:
                if piece.index == index:
                    return piece
            raise InvalidCommandException(command_str)

        def parse_single_command(cmd: str):
            parts = cmd.split(' ')
            command_key = parts[0]

            if command_key == 'move':
                piece = piece_from_index(player, int(parts[1]))
                steps = int(parts[2])
                command = MoveCommand(chessboard, piece, dices, steps)
                return command

            if command_key == 'move-home':
                piece = piece_from_index(player, int(parts[1]))
                steps = int(parts[2])
                command = MoveHomeCommand(chessboard, piece, dices, steps)
                return command

            if command_key == 'help' or command_key == 'h':
                help_str = 'HELP!!!!!!!!!!!!!!'
                command = ShowHelpCommand(help_str)
                return command

            if command_key == 'pass' or command_key == 'p':
                command = PassCommand(player)
                return command

            raise InvalidCommandException(command_str)

        dices = deepcopy(dices)
        commands = CommandSequence([parse_single_command(norm(cmd)) for cmd in command_str.split(';')])
        return commands
