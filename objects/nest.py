from error import NoError, Status
from player import Player

from objects.board import Route
from objects.piece import Piece


class Nest:

    MAX_PIECES = 4

    def __init__(self, player: Player) -> None:
        self.pieces = [Piece(player, i) for i in range(self.MAX_PIECES)]
        self.player = player

    def piece_from_index(self, piece_idx) -> Piece:
        return self.pieces[piece_idx]

    def move(self, route: Route, dice: int):
        if not (dice == 1 or dice == 6):
            return Status(-1, 'Could not kickstart due to dice value')

        available_flag = [piece.place == Piece.PLACE_NEST for piece in self.pieces]
        if any(available_flag):
            index = available_flag.index(True)
            piece = self.pieces[index]

            piece_at_nest_door = route.piece_at(self.player.offset)
            is_not_same_player = self.player != piece_at_nest_door.player
            if is_not_same_player:
                piece.set_place(Piece.PLACE_ROUTE)
                route.set_location(piece, self.player.offset)
                return NoError()

        return Status(-1, 'There is no piece left in nest')

    def undo_move(self, route: Route):
        piece = route.piece_at(self.player.offset)
        piece.set_place(Piece.PLACE_NEST)
        route.clear_location(self.player.offset)

    def to_dict(self):
        out = {}
        out['player'] = self.player.name
        out['pieces'] = [piece.to_dict() for piece in self.pieces]
        return out
