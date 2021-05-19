from error import CannotMoveError, NoError, Status
from typing import Iterable
from board import Chessboard
from objects import Piece, Player


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
    def __init__(self, board: Chessboard, piece: Piece, steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps

    def execute(self):

        piece_location = self.board.location(self.piece)
        if piece_location == self.board.LOC_OUT_BOARD:
            new_location = self.piece.player.offset
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
        return NoError()

    def undo(self):
        self.board.set_location(self.piece, self.old_location)


class MoveHomeCommand(Command):
    def __init__(self, board: Chessboard, piece: Piece, steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps

    def execute(self):
        pass


class PassCommand(Command):
    def __init__(self, player: Player) -> None:
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
