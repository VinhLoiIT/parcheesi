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

    def to_dict(self):
        return {
            'index': self.index,
            'player': self.player
        }


class EmptyPiece(Piece):
    def __init__(self) -> None:
        self.index = -1
        self.player = None

    @property
    def name(self):
        return '**'

    def __eq__(self, o: object) -> bool:
        if isinstance(o, EmptyPiece):
            return True
        return super().__eq__(o)
