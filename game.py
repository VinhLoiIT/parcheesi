from typing import List, Optional
from player import ConsolePlayer, Player
from gamestate import GameState


class Game:

    def __init__(self) -> None:
        self.state: Optional[GameState] = None
        self.players: List[Player] = []

    def wait_for_players(self):
        # TODO: implement with sockets
        # TODO: psuedo players for early development
        p1 = ConsolePlayer('red')
        self.players.append(p1)
        p2 = ConsolePlayer('green')
        self.players.append(p2)
        # p3 = ConsolePlayer('blue')
        # self.players.append(p3)
        # p4 = ConsolePlayer('yellow')
        # self.players.append(p4)

    def start(self):
        self.state = GameState()
        for player in self.players:
            self.state.add_player(player)
        self.state.start()

    def run_loop(self):
        while True:
            try:
                self.state.update()
            except KeyboardInterrupt:
                ans = input('Are you sure want to quit? [y/n]: ')
                if ans.upper() == 'Y':
                    break

        print('Game Over!')


if __name__ == '__main__':
    game = Game()
    game.wait_for_players()
    game.start()
    game.run_loop()
