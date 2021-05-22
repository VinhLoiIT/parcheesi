from typing import List
from piece import EmptyPiece, Piece


class Board:
    LOC_OUT_BOARD = -2

    def to_dict(self):
        pass


class Chessboard(Board):

    def __init__(self, player_lane_size: int, players) -> None:
        self.state: List[Piece] = [EmptyPiece() for _ in range(player_lane_size * len(players))]
        self.players = players
        self.offset = {player.name: i * player_lane_size for i, player in enumerate(players)}
        self.player_lane_size = player_lane_size

    def __repr__(self) -> str:
        steps = []
        entrances = {self.home_entrance_location(player): player.name[0] for player in self.players}
        print(' '.join([f'{x:02d}' for x in range(len(self.state))]))
        for index, step in enumerate(self.state):
            if isinstance(step, EmptyPiece) and index in entrances.keys():
                representation = f'{entrances[index]}H'
            else:
                representation = step.name
            steps.append(representation)
        return ' '.join(steps)

    def is_able_kickstart(self, player, steps: int):
        player_offset = self.offset[player.name]
        return (steps == 6 or steps == 1) and self.state[player_offset].player != player

    def is_pass_home_entrance(self, piece: Piece, steps: int):
        home_location = self.home_entrance_location(piece.player)
        piece_location = self.location(piece)
        player_offset = self.offset[piece.player.name]

        # Norm piece location to 0->len(state)
        if piece_location < player_offset:
            piece_location += player_offset
        else:
            piece_location -= player_offset

        if player_offset > home_location:
            home_location += len(self.state) - player_offset

        return piece_location + steps > home_location

    def is_able_to_move(self, piece: Piece, steps: int):
        def is_clear_rollback(piece_location, piece_player, steps):
            first = self.state[piece_location + 1:]
            second = self.state[:(piece_location + steps) % len(self.state)]
            clear_mid = all([isinstance(step, EmptyPiece) for step in first + second])
            new_location = (piece_location + steps) % len(self.state)
            same_player = self.state[new_location].player == piece_player
            return clear_mid and not same_player

        def is_clear_forward(piece_location, piece_player, steps):
            new_location = piece_location + steps
            clear_mid = all([isinstance(step, EmptyPiece) for step in self.state[piece_location + 1:new_location]])
            same_player = self.state[new_location].player == piece_player
            return clear_mid and not same_player

        piece_location = self.location(piece)
        home_location = piece.player.home.location(piece)

        if piece_location == self.LOC_OUT_BOARD:
            if home_location == Home.LOC_OUT_BOARD:
                return self.is_able_kickstart(piece.player, steps)
            return False

        if self.is_pass_home_entrance(piece, steps):
            return False

        if piece_location + steps + 1 > len(self.state):
            return is_clear_rollback(piece_location, piece.player, steps)

        return is_clear_forward(piece_location, piece.player, steps)

    def home_entrance_location(self, player):
        home_location = (self.offset[player.name] + len(self.state) - 1) % len(self.state)
        return home_location

    def is_at_home_entrance(self, piece: Piece, location: int):
        home_location = self.home_entrance_location(piece.player)
        return home_location == location

    def location(self, piece: Piece):
        try:
            return self.state.index(piece)
        except ValueError:
            return self.LOC_OUT_BOARD

    def set_location(self, piece: Piece, location: int):
        piece_location = self.location(piece)

        if piece_location == self.LOC_OUT_BOARD and location != self.LOC_OUT_BOARD:
            self.state[location] = piece
            return

        if piece_location != self.LOC_OUT_BOARD:
            self.state[piece_location] = EmptyPiece()
            if location != self.LOC_OUT_BOARD:
                self.state[location] = piece

    def to_dict(self):
        output = {}
        output['homes'] = {
            player.name: player.home.to_dict() for player in self.players
        }
        output['board'] = [piece.to_dict() for piece in self.state]
        output['metadata'] = {
            'LANE_SIZE': self.player_lane_size
        }
        return output


class Home(Board):

    def __init__(self) -> None:
        super(Home, self).__init__()
        self.state: List[Piece] = [EmptyPiece() for _ in range(6)]

    def __repr__(self) -> str:
        return ' '.join([step.name for step in self.state])

    def location(self, piece: Piece):
        try:
            return self.state.index(piece)
        except ValueError:
            return self.LOC_OUT_BOARD

    def is_finished(self):
        if any([isinstance(step, EmptyPiece) for step in self.state[-4:]]):
            return False
        return True

    def to_dict(self):
        return [piece.to_dict() for piece in self.state]
