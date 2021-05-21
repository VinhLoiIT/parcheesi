class Status:
    pass


class NoError(Status):
    code = 0

    def __init__(self) -> None:
        self.desc = 'OK'

    def __str__(self) -> str:
        return self.desc


class CannotMoveError(Status):
    code = -1

    def __init__(self, piece_name, steps) -> None:
        self.desc = f'Could not move {piece_name} {steps} steps'

    def __str__(self) -> str:
        return self.desc


class InvalidDiceError(Status):
    code = -2

    def __init__(self, dice_value, correct_values) -> None:
        self.desc = f'Could not move {dice_value} steps. Available steps = {correct_values}'

    def __str__(self) -> str:
        return self.desc
