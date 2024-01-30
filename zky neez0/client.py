import socket

class PlayerClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

    def run(self):
        # 接收从服务器发送的客户端ID
        client_id = int(self.socket.recv(1024).decode())
        print(f"Connected to server at {self.server_host}:{self.server_port} as Player {client_id}")

        if client_id > 1:
            # 确认是否是最后一个玩家
            is_last_player = input("Are you the last player? (Yes/No): ").strip().lower()
            if is_last_player == 'yes':
                print("OK, the game will start soon.")
                # 发送消息给服务器，通知可以开始游戏
                self.socket.sendall(b"start_game")
            else:
                print("Waiting for other players...")
        else:
            print("Waiting for other players...")

        # 保持客户端运行，以便接收后续的服务器消息
        while True:
            pass

if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345
    client = PlayerClient(SERVER_HOST, SERVER_PORT)
    client.run()
