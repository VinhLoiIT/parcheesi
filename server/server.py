from connection import PlayerConnection
from typing import List
from error import IsInRoomError, IsPlayingError, NoError, Status
from gamedb import GameRoomDB
from socketio import Server, WSGIApp
import eventlet


class ParcheesiServer:

    MAX_CAPACITY = 100

    def __init__(self):
        self.sio = Server(logger=False)
        self.sio.on('connect', self.connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('list_room', self.list_room)
        self.sio.on('join_room', self.join_room)
        self.sio.on('leave_room', self.leave_room)
        self.sio.on('ready', self.ready)
        self.sio.on('command', self.command)

        self.connections: List[PlayerConnection] = []

    def connect(self, sid, env, auth):
        print('connect', sid, auth)
        if auth is None:
            return False

        if 'username' not in auth.keys():
            return False

        if len(self.connections) < self.MAX_CAPACITY:
            connection = PlayerConnection(self.sio, sid, auth['username'])
            self.connections.append(connection)
            self.sio.save_session(sid, {
                'connection': connection,
                'room_name': None,
            })
            return True

        return False

    def disconnect(self, sid):
        print('disconnect ', sid)
        session = self.sio.get_session(sid)
        connection = session['connection']
        room_name = session['room_name']
        self.connections.remove(connection)
        if room_name is not None:
            GameRoomDB.leave(connection, room_name)

    def list_room(self, sid):
        data = list(GameRoomDB.rooms.keys())
        return data

    def join_room(self, sid, room_name):
        session = self.sio.get_session(sid)
        if session['room_name'] is not None:
            return _ack(IsInRoomError(session['room_name']))

        connection = session['connection']
        status = GameRoomDB.join(connection, room_name)
        if status:
            session['room_name'] = room_name
        return _ack(status)

    def leave_room(self, sid):
        session = self.sio.get_session(sid)
        connection = session['connection']
        room_name = session['room_name']
        if room_name is None:
            return _ack(Status(-1, 'Not in a room'))

        GameRoomDB.leave(connection, room_name)
        session['room_name'] = None
        return _ack(NoError())

    def ready(self, sid):
        session = self.sio.get_session(sid)
        room_name = session['room_name']
        if room_name is None:
            return _ack(Status(-1, 'Not in a room'))

        room = GameRoomDB.rooms[room_name]
        if room.is_playing:
            return _ack(IsPlayingError())

        room.ready(session['connection'])

        if room.is_able_to_start():
            self.sio.start_background_task(room.start)

        return _ack(NoError())

    def command(self, sid, command_str):
        session = self.sio.get_session(sid)
        connection = session['connection']
        game = GameRoomDB.rooms.get(session['room_name'], None)
        if game is None:
            return _ack(Status(-1, 'Game is None'))

        status = game.receive_command(connection, command_str)
        return _ack(status)

    def listen(self, host='localhost', port=5050):
        app = WSGIApp(self.sio)
        eventlet.wsgi.server(eventlet.listen((host, port)), app)


def _ack(status: Status):
    return status.code, status.desc


if __name__ == '__main__':
    server = ParcheesiServer()
    server.listen()
