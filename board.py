from objects import Piece, Player


class Board:
    EMPTY = -1
    LOC_OUT_BOARD = -2


class Chessboard(Board):

    def __init__(self, player_lane_size: int, max_num_players: int, players) -> None:
        self.state = [self.EMPTY] * (player_lane_size * max_num_players)
        self.players = players
        self.player_lane_size = player_lane_size
        self.max_num_players = max_num_players

    def __repr__(self) -> str:
        steps = []
        entrances = {self.home_entrance_location(player): player.name[0] for player in self.players}
        print(' '.join([f'{x:02d}' for x in range(len(self.state))]))
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

    def is_pass_home_entrance(self, piece: Piece, steps: int):
        home_location = self.home_entrance_location(piece.player)
        piece_location = self.location(piece)

        # Norm piece location to 0->len(state)
        if piece_location < piece.player.offset:
            piece_location += piece.player.offset
        else:
            piece_location -= piece.player.offset

        if piece.player.offset > home_location:
            home_location += len(self.state) - piece.player.offset

        return piece_location + steps > home_location

    def is_able_to_move(self, piece: Piece, steps: int):
        def is_clear_rollback(piece_location, piece_player, steps):
            first = self.state[piece_location + 1:]
            second = self.state[:(piece_location + steps) % len(self.state)]
            clear_mid = all([step == self.EMPTY for step in first + second])
            new_location = (piece_location + steps) % len(self.state)
            same_player = self.state[new_location] != self.EMPTY and self.state[new_location].player == piece_player
            return clear_mid and not same_player

        def is_clear_forward(piece_location, piece_player, steps):
            new_location = piece_location + steps
            clear_mid = all([step == self.EMPTY for step in self.state[piece_location + 1:new_location]])
            same_player = self.state[new_location] != self.EMPTY and self.state[new_location].player == piece_player
            return clear_mid and not same_player

        piece_location = self.location(piece)

        if piece_location == self.LOC_OUT_BOARD:
            if piece.player.home.location(piece) == piece.player.home.EMPTY:
                return self.is_able_kickstart(piece.player, steps)
            return False

        if self.is_pass_home_entrance(piece, steps):
            return False

        if piece_location + steps + 1 > len(self.state):
            return is_clear_rollback(piece_location, piece.player, steps)

        return is_clear_forward(piece_location, piece.player, steps)

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

    def location(self, piece: Piece):
        try:
            return self.state.index(piece)
        except ValueError:
            return self.LOC_OUT_BOARD
