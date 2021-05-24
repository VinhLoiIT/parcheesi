import re
from argparse import ArgumentParser

import eventlet
from socketio import Client

HOST = 'localhost'
PORT = 5050

sio = Client(logger=True)


def norm_cmd(command_str: str):
    return re.sub(' +', ' ', command_str.strip())


@sio.on('turn')
def get_turn(data):
    print('Dices:', data['dice_values'])
    print('Homes:', data['homes'])
    print('Nests:', data['nests'])
    print('Route:', data['route'])


@sio.on('status')
def on_status(code, desc):
    print(f'Status: {code}: {desc}')


def on_list_room_result(room_names):
    print('ROOMS:', room_names)


def cli(username):
    while True:
        eventlet.sleep()
        command_str = input(f'{username}> ')
        command_str = norm_cmd(command_str)
        if command_str == '':
            continue

        parts = command_str.split(' ')

        command_name = parts[0]
        if command_name == 'list-room':
            sio.emit('list_room', callback=on_list_room_result)
        elif command_name == 'join-room':
            room_name = parts[-1]
            sio.emit('join_room', data=room_name, callback=on_status)
        elif command_name == 'leave-room':
            sio.emit('leave_room', callback=on_status)
        elif command_name == 'ready':
            sio.emit('ready', callback=on_status)
        elif command_name == 'quit' or command_name == 'exit':
            break
        else:
            sio.emit('command', data=command_str, callback=on_status)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('username', type=str)
    args = parser.parse_args()

    url = f'http://{HOST}:{PORT}'
    sid = sio.connect(url, auth={
        'username': args.username
    })

    sio.start_background_task(cli, args.username)
    sio.wait()
