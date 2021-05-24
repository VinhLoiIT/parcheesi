import player


class Piece:

    PLACE_NEST = 0
    PLACE_ROUTE = 1
    PLACE_HOME = 2

    def __init__(self, player: player.Player, index: int) -> None:
        self.index = index
        self.player = player
        self.place = self.PLACE_NEST

    def set_place(self, place):
        self.place = place

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
            'player': None if self.player is None else self.player.name
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
