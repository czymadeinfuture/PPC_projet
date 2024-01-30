import socket

class PlayerClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

    def run(self):
        data = self.socket.recv(1024).decode()
        if not data:
            print("Error: Received empty data from server.")
            return  # 或者进行其他错误处理

        client_id = int(data)
        print(f"Connected to server at {self.server_host}:{self.server_port} as Player {client_id}")

        if client_id > 1:
            # 确认是否是最后一个玩家
            is_last_player = input("Are you the last player? (Yes/No): ").strip().lower()
            if is_last_player == 'yes':
                print("OK, the game will start soon.")
                self.socket.sendall(b"start_game")
            else:
                print("Waiting for other players...")
        else:
            print("Waiting for other players...")

        while True:
            pass


if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345
    client = PlayerClient(SERVER_HOST, SERVER_PORT)
    client.run()
