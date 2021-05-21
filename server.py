from error import InvalidCommandError
from exception import InvalidCommandException
from command import CommandFactory
from game import GameRoom
from player import SocketIOPlayer
from socketio import Server, WSGIApp

HOST = 'localhost'
PORT = 5050

sio = Server(logger=False)
game = GameRoom()


@sio.event
def connect(sid, env, auth):
    print('connect', sid, auth)
    if auth is None:
        return False

    if 'username' not in auth.keys():
        return False

    instance = SocketIOPlayer(auth['username'], sio, sid)
    sio.save_session(sid, {
        'instance': instance
    })

    if not game.player_join(instance):
        return False

    if game.is_able_to_start():
        sio.start_background_task(game.start)
    return True


@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    session = sio.get_session(sid)
    instance = session['instance']
    game.player_leave(instance)


@sio.on('command')
def on_command(sid, command_str):
    session = sio.get_session(sid)
    player = session['instance']
    try:
        command = CommandFactory.parse(player, game.state, command_str)
    except InvalidCommandException:
        error = InvalidCommandError(command_str)
        return error.code, error.desc

    game.add_command(player, command)


if __name__ == '__main__':
    import eventlet
    app = WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen((HOST, PORT)), app)
