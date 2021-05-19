from objects import Piece


class Board:
    EMPTY = -1

    def is_able_to_move(self):
        raise NotImplementedError()

    def move(self, piece, steps):
        raise NotImplementedError()


class Chessboard(Board):

    def __init__(self, player_lane_size: int, max_num_players: int) -> None:
        self.state = [self.EMPTY] * (player_lane_size * max_num_players)

    def __repr__(self) -> str:
        return ' '.join(['**' if step == self.EMPTY else str(step) for step in self.state])

    def is_able_to_move(self, piece, steps):
        try:
            piece_location = self.state.index(piece)
        except ValueError:
            if steps == 6 or steps == 1:
                return True
            return False

        if piece_location + steps + 1 > len(self.state):
            first = self.state[piece_location + 1:]
            second = self.state[:(piece_location + steps) % len(self.state)]
            return all([step == self.EMPTY for step in first + second])

        if all([step == self.EMPTY for step in self.state[piece_location + 1:piece_location + steps]]):
            return True

        # TODO: check round

        return False

    def move(self, piece: Piece, steps: int):
        try:
            piece_location = self.state.index(piece)
        except ValueError:
            if steps == 6 or steps == 1:
                self.state[piece.player.offset] = piece
                return
            raise ValueError()

        self.state[piece_location] = self.EMPTY

        if piece_location + steps + 1 > len(self.state):
            self.state[(piece_location + steps) % len(self.state)] = piece
            return

        if all([step == self.EMPTY for step in self.state[piece_location + 1:piece_location + steps]]):
            self.state[piece_location + steps] = piece
            return

        # TODO: check round

        return False


class Home(Board):

    def __init__(self) -> None:
        super(Home, self).__init__()
        self.state = [self.EMPTY] * 6

    def __repr__(self) -> str:
        return ' '.join(['**' if step == self.EMPTY else str(step) for step in self.state])

    def is_able_to_move(self, piece, steps):
        try:
            piece_location = self.state.index(piece)
        except IndexError:
            return False

        new_location = piece_location + steps

        if not 1 <= new_location <= 6:
            return False

        if all([step == self.EMPTY for step in self.state[piece_location + 1:new_location]]):
            return True

        return False

    def move(self, piece: Piece, steps: int):
        try:
            piece_location = self.state.index(piece)
        except IndexError:
            raise ValueError()

        new_location = piece_location + steps

        if piece_location == 0 and all([step == self.EMPTY for step in self.state[piece_location + 1:new_location]]):
            self.state[piece_location] = self.EMPTY
            self.state[new_location] = piece
            return

        if piece_location > 0:
            if steps == piece_location + 1 and self.state[piece_location + 1] == self.EMPTY:
                self.state[piece_location] = self.EMPTY
                self.state[new_location] = piece

        raise ValueError()
