from objects import Piece, Player


class Board:
    EMPTY = -1

    def is_able_to_move(self):
        raise NotImplementedError()

    def set_location(self, piece: Piece, location: int):
        raise NotImplementedError()


class Chessboard(Board):

    LOC_OUT_BOARD = -2

    def __init__(self, player_lane_size: int, max_num_players: int, players) -> None:
        self.state = [self.EMPTY] * (player_lane_size * max_num_players)
        self.players = players

    def __repr__(self) -> str:
        steps = []
        entrances = {self.home_entrance_location(player): player.name[0] for player in self.players}
        for index, step in enumerate(self.state):
            if step == self.EMPTY:
                if index in entrances.keys():
                    representation = f'{entrances[index]}H'
                else:
                    representation = '**'
            else:
                representation = str(step)
            steps.append(representation)
        return ' '.join(steps)

    def is_able_kickstart(self, player, steps: int):
        if steps == 6 or steps == 1:
            if self.state[player.offset] == self.EMPTY:
                return True
            if self.state[player.offset].player != player:
                return True
        return False

    def is_able_to_move(self, piece: Piece, steps: int):
        piece_location = self.location(piece)

        if piece_location == self.LOC_OUT_BOARD:
            return self.is_able_kickstart(piece.player, steps)

        if piece_location + steps + 1 > len(self.state):
            first = self.state[piece_location + 1:]
            second = self.state[:(piece_location + steps) % len(self.state)]
            return all([step == self.EMPTY for step in first + second])

        if all([step == self.EMPTY for step in self.state[piece_location + 1:piece_location + steps]]):
            return True

        # TODO: check round

        return False

    def home_entrance_location(self, player: Player):
        home_location = (player.offset + len(self.state) - 1) % len(self.state)
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
            self.state[piece_location] = self.EMPTY
            if location != self.LOC_OUT_BOARD:
                self.state[location] = piece


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
