from socketio import Server


class Connection:

    def send_data(self, channel, data) -> bool:
        pass


class PlayerConnection(Connection):

    CHANNEL_TURN = 'turn'
    CHANNEL_STATUS = 'status'

    def __init__(self, sio: Server, sid, username) -> None:
        self.sio = sio
        self.sid = sid
        self.username = username

    def send_data(self, channel, data):
        self.sio.emit(channel, data, to=self.sid)
        return True


class NoConnection(Connection):

    def send_data(self, channel, data):
        return False
