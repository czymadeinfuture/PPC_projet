import socket
import threading

class GameServer:
    def __init__(self, host, port, max_clients):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.clients = []
        self.client_id = 0

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print(f"Server listening on {self.host}:{self.port}")

    def handle_client(self, client_socket, client_id):
        print(f"Client {client_id} connected")
        # 后续处理客户端数据的代码

    def accept_connections(self):
        while len(self.clients) < self.max_clients:
            client_socket, addr = self.server_socket.accept()
            self.client_id += 1
            self.clients.append((client_socket, self.client_id))
            threading.Thread(target=self.handle_client, args=(client_socket, self.client_id)).start()

    def run(self):
        print("Waiting for clients to connect...")
        self.accept_connections()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345
    MAX_CLIENTS = 5

    game_server = GameServer(HOST, PORT, MAX_CLIENTS)
    game_server.run()
