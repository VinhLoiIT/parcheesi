from typing import List

from error import CannotMoveError, NoError, Status
from player import Player

from objects.piece import EmptyPiece, Piece


class Board:
    LOC_OUT_BOARD = -2

    def __init__(self, route_size: int) -> None:
        self.route_size = route_size
        self.state: List[Piece] = [EmptyPiece() for _ in range(route_size)]

    def to_dict(self):
        return [piece.to_dict() for piece in self.state]

    def piece_at(self, location: int) -> Piece:
        return self.state[location]

    def __len__(self):
        return len(self.state)

    def __repr__(self) -> str:
        return ' '.join([piece.name for piece in self.state])

    def location(self, piece: Piece):
        try:
            return self.state.index(piece)
        except ValueError:
            return self.LOC_OUT_BOARD

    def set_location(self, piece: Piece, new_location: int):
        self.state[new_location] = piece

    def clear_location(self, location: int):
        self.set_location(EmptyPiece(), location)

    def is_clear(self, from_location: int, to_location: int) -> bool:
        '''
        [from_location, to_location]
        '''
        pass


class Route(Board):

    def norm_location(self, location: int):
        if location < 0:
            return location + len(self.state) - 1

        if location >= len(self.state):
            return location % len(self.state)

        return location

    def is_clear(self, from_location: int, to_location: int) -> bool:
        '''
        [from_location, to_location]
        '''
        from_location = self.norm_location(from_location)
        to_location = self.norm_location(to_location)

        if from_location <= to_location:
            range_check = self.state[from_location:to_location + 1]
        else:
            range_check = self.state[from_location:] + self.state[:to_location + 1]
        return all([isinstance(piece, EmptyPiece) for piece in range_check])

    def home_entrance_location(self, player: Player):
        home_location = self.norm_location(player.offset - 1)
        return home_location

    def is_pass_home_entrance(self, piece: Piece, steps: int):
        home_location = self.home_entrance_location(piece.player)
        piece_location = self.location(piece)
        player_offset = piece.player.offset

        # Norm piece location to 0->len(state)
        if piece_location < player_offset:
            piece_location += player_offset
        else:
            piece_location -= player_offset

        if player_offset > home_location:
            home_location += len(self) - player_offset

        return piece_location + steps > home_location

    def is_at_home_entrance(self, piece: Piece):
        return self.location(piece) == self.home_entrance_location(piece.player)

    def move(self, piece: Piece, steps: int) -> Status:
        old_location = self.location(piece)
        new_location = self.norm_location(old_location + steps)

        # conditions
        is_clear = self.is_clear(self.norm_location(old_location + 1), self.norm_location(new_location - 1))
        is_not_same_player = piece.player != self.piece_at(new_location).player
        is_not_pass_home = not self.is_pass_home_entrance(piece, steps)

        if is_clear and is_not_same_player and is_not_pass_home:
            self.clear_location(old_location)
            self.set_location(piece, new_location)
            return NoError()

        return CannotMoveError(piece.name, steps)

    def undo_move(self, piece: Piece, steps: int):
        location = self.location(piece)
        self.clear_location(location)
        self.set_location(piece, self.norm_location(location - steps))


class Home(Board):

    def __init__(self, player: Player, route_size: int = 6) -> None:
        super().__init__(route_size)
        self.player = player

    def is_clear(self, from_location: int, to_location: int) -> bool:
        '''
        [from_location, to_location]
        '''
        if from_location > to_location:
            return False

        range_check = self.state[from_location:to_location + 1]
        return all([isinstance(piece, EmptyPiece) for piece in range_check])

    def move(self, piece: Piece, steps: int) -> Status:
        piece_location = self.location(piece)
        if piece_location == self.LOC_OUT_BOARD:
            return CannotMoveError(piece.name, steps)

        if self.is_clear(steps - 1, steps - 1) and piece_location == steps - 2:
            self.clear_location(piece_location)
            self.set_location(piece, steps - 1)
            return NoError()
        return CannotMoveError(piece.name, steps)

    def undo_move(self, piece: Piece, steps: int):
        self.clear_location(steps - 1)
        self.set_location(piece, steps - 2)

    def is_finished(self):
        # TODO: change to NUM_PIECE_PER_PLAYER
        if any([isinstance(piece, EmptyPiece) for piece in self.state[-4:]]):
            return False
        return True
