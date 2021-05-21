from error import NoError
from typing import Dict, Optional
from player import Player
from gamestate import GameState
import queue
import eventlet


class GameRoom:

    PLAYER_WAIT_TIMEOUT = 10  # seconds
    COMMAND_FULL_TIMEOUT = 5
    MAX_NUM_PLAYER = 4
    MIN_NUM_PLAYER = 2

    def __init__(self, connection) -> None:
        self.state: Optional[GameState] = None
        self._command_queue = queue.Queue(100)
        self.is_playing = False
        self.players_ready: Dict[Player, bool] = {}
        self.connection = connection

    def enter(self, player):
        if self.is_playing:
            return
        self.players_ready[player] = False

    def leave(self, player):
        self.players_ready.pop(player)

    def ready(self, player):
        self.players_ready[player] = not self.players_ready[player]

    def empty(self) -> bool:
        return len(self.players_ready) == 0

    def is_able_to_start(self):
        return not self.is_playing and all(list(self.players_ready.values())) and \
             self.MAX_NUM_PLAYER >= len(self.players_ready) >= self.MIN_NUM_PLAYER

    def start(self):
        if self.is_playing:
            return

        self.is_playing = True
        self.state = GameState()
        self.state.start(list(self.players_ready.keys()))
        while True:
            try:
                eventlet.sleep()
                player, command = self._command_queue.get(block=False)
            except queue.Empty:
                continue

            status = self.state.receive_command(player, command)
            self.connection.send_status(player, status)
            if isinstance(status, NoError):
                self.state.next_turn()

            if self.state.is_done():
                break

    def receive_command(self, player, command):
        self._command_queue.put((player, command), block=True)


class GameRoomDB:
    rooms: Dict[str, GameRoom] = {}
