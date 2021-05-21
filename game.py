from error import NoError
from typing import List, Optional
from player import Player
from gamestate import GameState
import queue
import eventlet


class GameRoom:

    PLAYER_WAIT_TIMEOUT = 10  # seconds
    COMMAND_FULL_TIMEOUT = 5

    def __init__(self) -> None:
        self.state: Optional[GameState] = None
        self._player_queue: List[Player] = []
        self._command_queue = queue.Queue(100)
        self.is_playing = False

    def is_able_to_start(self):
        return (not self.is_playing) and len(self._player_queue) == 2

    def player_join(self, player) -> bool:
        if len(self._player_queue) >= GameState.MAX_NUM_PLAYER or self.is_playing:
            return False

        self._player_queue.append(player)
        return True

    def player_leave(self, player):
        if self.is_playing:
            player.set_disconnected(True)
            self._player_queue.remove(player)
        else:
            self._player_queue.remove(player)

    def add_command(self, player, command):
        self._command_queue.put((player, command), block=True, timeout=GameRoom.COMMAND_FULL_TIMEOUT)

    def start(self):
        self.state = GameState()
        for player in self._player_queue:
            self.state.add_player(player)
        self.state.start()

        while True:
            self.state.roll_dice()
            self.state.send_turn()
            current_player = self.state.players[self.state.current_player_index]
            print(f'Waiting for command from {current_player.name}...')
            while True:
                try:
                    eventlet.sleep()
                    player, command = self._command_queue.get(block=False)
                except queue.Empty:
                    continue
                    # TODO: generate pass command here
                    pass
                print(f'Receive command from player: {player.name}')
                if player != current_player:
                    # TODO: send error status (NOT_YOUR_TURN) back to player
                    print(f'Not {player.name}\'s turn. Discard command')
                    continue

                status = self.state.receive_command(command)
                if not isinstance(status, NoError):
                    # TODO: send error status back to player
                    continue

                self.state.next_player()
                break

            if self.state.is_done():
                break

        print('Game Over!')
