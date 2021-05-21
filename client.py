from socketio import Client
from argparse import ArgumentParser

HOST = 'localhost'
PORT = 5050

sio = Client(logger=True)


@sio.on('turn')
def get_turn(data):
    print('Receive turn data:', data)
    # command_str = 'pass'
    # sio.emit('command', data=command_str, callback=on_command_status)
    dice_values = data['dice_values']
    board_state = data['state']
    print('Dices:', dice_values)
    print(board_state)

    command_str = input('Enter command: ')
    sio.emit('command', data=command_str, callback=on_command_status)


def on_command_status():
    pass


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('username', type=str)
    args = parser.parse_args()

    url = f'http://{HOST}:{PORT}'
    sid = sio.connect(url, auth={
        'username': args.username
    })

    sio.wait()
