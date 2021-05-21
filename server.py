from connection import SocketGameConnection

if __name__ == '__main__':
    server = SocketGameConnection()
    server.listen()
