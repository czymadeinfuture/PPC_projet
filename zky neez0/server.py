import socket
import threading

class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.client_id = 0
        self.game_can_start = False

    def handle_client(self, client_socket, client_id):
        client_socket.sendall(str(client_id).encode())
        while True:
            data = client_socket.recv(1024).decode()
            if data == "start_game":
                self.game_can_start = True
                print("Let's start!")
                break
            # 其他通信处理...

    def run(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            self.client_id += 1
            print(f"Client {self.client_id} connected from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, self.client_id)).start()
        
        # 等待开始游戏的确认
        while not self.game_can_start:
            pass
        print("Game starting...")

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345
    server = GameServer(HOST, PORT)
    server.run()
