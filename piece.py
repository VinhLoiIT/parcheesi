class Piece:
    def __init__(self, player, index: int) -> None:
        self.index = index
        self.player = player

    @property
    def name(self):
        return f'{self.player.name[0]}{self.index}'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
