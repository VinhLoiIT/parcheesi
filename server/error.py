class Status:
    def __init__(self, code, desc):
        self.code = code
        self.desc = desc

    def __str__(self) -> str:
        return f'{self.code}: {self.desc}'

    def __repr__(self) -> str:
        return str(self)

    def ok(self):
        return self.code == NoError.code


class NoError(Status):

    code = 0

    def __init__(self) -> None:
        super().__init__(0, 'OK')


class CannotMoveError(Status):

    def __init__(self, piece_name, steps) -> None:
        code = -1
        desc = f'Could not move {piece_name} {steps} steps'
        super().__init__(code, desc)


class InvalidDiceError(Status):

    def __init__(self, dice_value, correct_values) -> None:
        code = -2
        desc = f'Could not move {dice_value} steps. Available steps = {correct_values}'
        super().__init__(code, desc)


class InvalidCommandError(Status):

    def __init__(self, command_str) -> None:
        code = -3
        desc = f'Invalid command "{command_str}"'
        super().__init__(code, desc)


class InvalidTurnError(Status):

    def __init__(self) -> None:
        code = -4
        desc = 'This is not your turn'
        super().__init__(code, desc)


class IsPlayingError(Status):

    def __init__(self) -> None:
        code = -5
        desc = 'Game is current playing'
        super().__init__(code, desc)


class IsInRoomError(Status):

    def __init__(self, room_name) -> None:
        code = -6
        desc = f'You are already in room "{room_name}"'
        super().__init__(code, desc)
