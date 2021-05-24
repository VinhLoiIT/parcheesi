from gameroom import GameRoom
from typing import Dict
from error import Status


class GameRoomDB:
    rooms: Dict[str, GameRoom] = {}

    @staticmethod
    def leave(connection, room_name):
        if room_name not in GameRoomDB.rooms.keys():
            return

        room = GameRoomDB.rooms[room_name]
        room.leave(connection)
        if room.empty():
            GameRoomDB.rooms.pop(room_name)

    @staticmethod
    def join(connection, room_name) -> Status:
        room = GameRoomDB.rooms.get(room_name, GameRoom())
        status = room.enter(connection)
        if status.ok():
            GameRoomDB.rooms[room_name] = room
        return status
