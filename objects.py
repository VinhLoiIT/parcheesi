import re


class Player:

    def __init__(self, name: str) -> None:
        self.name = name

    def turn(self, dice_values):
        raise NotImplementedError()


class ConsolePlayer(Player):

    def turn(self, dice_values):
        print('Dices:', dice_values)
        while True:
            command_str = input(f'{self.name}> ')
            command_str = re.sub(' +', ' ', command_str.strip())
            if len(command_str) == 0:
                continue

            return command_str


class SocketIOPlayer(Player):
    def __init__(self, name: str, sid) -> None:
        super().__init__(name)
        self.sid = sid

    def turn(self, dice_values):
        pass


class Piece:
    def __init__(self, player: 'Player', name: str) -> None:
        self.name = name
        self.player = player

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
