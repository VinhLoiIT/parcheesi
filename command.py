from board import Board
from objects import Piece, Player


class Command:
    def execute(self):
        pass


class MoveCommand(Command):
    def __init__(self, board: Board, piece: Piece, steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps

    def execute(self):
        pass


class MoveHomeCommand(Command):
    def __init__(self, board: Board, piece: Piece, steps: int) -> None:
        self.board = board
        self.piece = piece
        self.steps = steps

    def execute(self):
        pass


class PassCommand(Command):
    def __init__(self, player: Player) -> None:
        super(PassCommand, player).__init__()
        self.player = player

    def execute(self):
        print(f'Player {self.player.name} passed.')


class ShowHelpCommand(Command):
    def __init__(self, help_str) -> None:
        super().__init__()
        self.help_str = help_str

    def execute(self):
        print(self.help_str)
        input('Press any key to continue.')


class UnknowCommandException(BaseException):
    def __init__(self, command_str) -> None:
        super().__init__()
        self.command_str = command_str

    def __str__(self) -> str:
        return self.command_str


class InvalidCommandException(BaseException):
    def __init__(self, command_str) -> None:
        super().__init__()
        self.command_str = command_str

    def __str__(self) -> str:
        return self.command_str
