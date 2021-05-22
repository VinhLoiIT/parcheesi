from typing import List
from error import InvalidCommandError, IsInRoomError, IsPlayingError, NoError, Status
from exception import InvalidCommandException
from command import CommandFactory
from gameroom import GameRoom, GameRoomDB
from player import Player, SocketIOPlayer
from socketio import Server, WSGIApp
import eventlet


class GameConnection:

    def send_status(self, player_recv, status):
        pass

    def create_room(self, players) -> GameRoom:
        pass


class SocketGameConnection(GameConnection):

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

        self._players: List[Player] = []

    def send_status(self, player_recv, status: Status):
        sid = player_recv.sid
        data = (status.code, status.desc)
        self.sio.emit('status', data=data, to=sid)

    def connect(self, sid, env, auth):
        print('connect', sid, auth)
        if auth is None:
            return False

        if 'username' not in auth.keys():
            return False

        instance = SocketIOPlayer(auth['username'], self.sio, sid)
        self.sio.save_session(sid, {
            'instance': instance,
            'room_name': None,
        })

        if len(self._players) < self.MAX_CAPACITY:
            self._players.append(instance)
            return True

        return False

    def disconnect(self, sid):
        print('disconnect ', sid)
        session = self.sio.get_session(sid)
        instance = session['instance']
        room_name = session['room_name']
        self._players.remove(instance)
        if room_name is not None:
            GameRoomDB.leave(instance, room_name)

    def list_room(self, sid):
        data = list(GameRoomDB.rooms.keys())
        return data

    def join_room(self, sid, room_name):
        # Check room available
        room = GameRoomDB.rooms.get(room_name, GameRoom(self))
        if room.is_playing:
            status = IsPlayingError()
            return status.code, status.desc

        session = self.sio.get_session(sid)
        player = session['instance']

        # is in room
        if session['room_name'] is not None:
            status = IsInRoomError(session['room_name'])
            return status.code, status.desc

        # join new room
        room.enter(player)
        session['room_name'] = room_name
        GameRoomDB.rooms[room_name] = room

        status = NoError()
        return status.code, status.desc

    def leave_room(self, sid):
        session = self.sio.get_session(sid)
        player = session['instance']
        joined_room = session['room_name']
        if joined_room is None:
            return -1, 'Not in a room'

        GameRoomDB.leave(player, joined_room)

        session['room_name'] = None

        status = NoError()
        return status.code, status.desc

    def ready(self, sid):
        session = self.sio.get_session(sid)
        player = session['instance']
        joined_room = GameRoomDB.rooms.get(session['room_name'], None)
        if joined_room is None:
            return -1, 'Not in a room'

        if joined_room.is_playing:
            status = IsPlayingError()
            return status.code, status.desc

        joined_room.ready(player)

        if joined_room.is_able_to_start():
            self.sio.start_background_task(joined_room.start)

        status = NoError()
        return status.code, status.desc

    def command(self, sid, command_str):
        session = self.sio.get_session(sid)
        player = session['instance']
        game = GameRoomDB.rooms.get(session['room_name'], None)
        if game is None:
            return -1, 'Game is None'

        if not game.is_playing:
            return -1, 'Game has not started yet'

        try:
            command = CommandFactory.parse(player, game.state, command_str)
        except InvalidCommandException:
            error = InvalidCommandError(command_str)
            return error.code, error.desc

        game.receive_command(player, command)

        status = NoError()
        return status.code, status.desc

    def listen(self, host='localhost', port=5050):
        app = WSGIApp(self.sio)
        eventlet.wsgi.server(eventlet.listen((host, port)), app)
