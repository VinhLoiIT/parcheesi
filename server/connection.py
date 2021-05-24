from error import Status
from socketio import Server


class Connection:

    CHANNEL_TURN = 'turn'
    CHANNEL_STATUS = 'status'

    def send_data(self, channel, data) -> bool:
        pass

    def send_status(self, status: Status) -> bool:
        return self.send_data(self.CHANNEL_STATUS, (status.code, status.desc))


class PlayerConnection(Connection):

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
