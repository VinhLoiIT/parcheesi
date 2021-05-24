from objects.nest import Nest
from objects.board import Home, Route
from error import CannotMoveError, InvalidDiceError, NoError, Status
from typing import Iterable, List
from objects.piece import Piece


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
            if not status.ok():
                return status
            self.max_success_index = i
        return NoError()

    def undo(self):
        for command in reversed(list(self.commands[:self.max_success_index + 1])):
            command.undo()


class DiceConsumedCommand(Command):
    def __init__(self, dices: List[int], steps: int) -> None:
        self.steps = steps
        self.dices = dices

    def execute(self) -> Status:
        if self.steps not in self.dices:
            return InvalidDiceError(self.steps, self.dices)

        self.index = self.dices.index(self.steps)
        self.dices.pop(self.index)
        return NoError()

    def undo(self):
        self.dices.insert(self.index, self.steps)


class MoveRouteCommand(DiceConsumedCommand):
    def __init__(self, route: Route, piece: Piece, dices: List[int], steps: int) -> None:
        super().__init__(dices, steps)
        self.route = route
        self.piece = piece

    def execute(self) -> Status:
        status = super().execute()
        if not status.ok():
            return status

        self.status = self.route.move(self.piece, self.steps)
        return self.status

    def undo(self):
        super().undo()
        self.route.undo_move(self.piece, self.steps)


class MoveToHomeCommand(DiceConsumedCommand):
    def __init__(self, route: Route, home: Home, piece: Piece, dices: List[int], steps: int) -> None:
        super().__init__(dices, steps)
        self.route = route
        self.home = home
        self.piece = piece

    def execute(self) -> Status:
        status = super().execute()
        if not status.ok():
            return status

        piece_location = self.route.location(self.piece)
        if self.route.is_at_home_entrance(self.piece):
            if self.home.is_clear(0, self.steps - 1):
                self.route.clear_location(piece_location)
                self.home.set_location(self.piece, self.steps - 1)
                self.piece.set_place(Piece.PLACE_HOME)
                return NoError()

        return CannotMoveError(self.piece.name, self.steps)

    def undo(self):
        super().undo()
        piece_location = self.home.location(self.piece)
        self.home.clear_location(piece_location)
        self.route.set_location(self.piece, self.route.home_entrance_location(self.piece.player))
        self.piece.set_place(Piece.PLACE_ROUTE)


class MoveInHomeCommand(DiceConsumedCommand):
    def __init__(self, home: Home, piece: Piece, dices: List[int], steps: int) -> None:
        super().__init__(dices, steps)
        self.home = home
        self.piece = piece

    def execute(self):
        status = super().execute()
        if not status.ok():
            return status

        status = self.home.move(self.piece, self.steps)
        return status

    def undo(self):
        super().undo()
        self.home.undo_move(self.piece, self.steps)


class StartCommand(DiceConsumedCommand):
    def __init__(self, nest: Nest, route: Route, dices: List[int], steps: int) -> None:
        super().__init__(dices, steps)
        self.nest = nest
        self.route = route

    def execute(self):
        status = super().execute()
        if not status.ok():
            return status

        status = self.nest.move(self.route, self.steps)
        return status

    def undo(self):
        super().undo()
        self.nest.undo_move(self.route)


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
