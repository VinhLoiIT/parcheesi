from connection import PlayerConnection
from error import IsPlayingError, NoError, Status
from typing import Dict, Optional
from gamestate import GameState
import queue
import eventlet


class GameRoom:

    PLAYER_WAIT_TIMEOUT = 10  # seconds
    COMMAND_FULL_TIMEOUT = 5
    MAX_NUM_PLAYER = 4
    MIN_NUM_PLAYER = 2

    def __init__(self) -> None:
        self.state: Optional[GameState] = None
        self._command_queue = queue.Queue(100)
        self.is_playing = False
        self.connection_ready: Dict[PlayerConnection, bool] = {}

    def enter(self, connection) -> Status:
        if self.is_playing or connection in self.connection_ready.keys():
            return IsPlayingError()
        # TODO: Check room full
        self.connection_ready[connection] = False
        return NoError()

    def leave(self, connection):
        self.connection_ready.pop(connection)
        if self.is_playing:
            self.state.disconnect(connection)

    def ready(self, connection):
        self.connection_ready[connection] = not self.connection_ready[connection]

    def empty(self) -> bool:
        return len(self.connection_ready) == 0

    def is_able_to_start(self):
        return not self.is_playing and all(list(self.connection_ready.values())) and \
             self.MAX_NUM_PLAYER >= len(self.connection_ready) >= self.MIN_NUM_PLAYER

    def start(self):
        if self.is_playing:
            return

        self.is_playing = True
        self.state = GameState()
        self.state.start(list(self.connection_ready.keys()))
        while True:
            try:
                eventlet.sleep()
                connection: PlayerConnection
                command_str: str
                connection, command_str = self._command_queue.get(block=False)
            except queue.Empty:
                continue

            status = self.state.receive_command(connection, command_str)
            connection.send_data(PlayerConnection.CHANNEL_STATUS, status)
            if isinstance(status, NoError):
                self.state.next_turn()

            if self.state.is_done():
                break
        print('Game done')

    def receive_command(self, connection: PlayerConnection, command_str: str) -> Status:

        if not self.is_playing:
            return Status(-1, 'Game has not started yet')

        self._command_queue.put((connection, command_str), block=True)
