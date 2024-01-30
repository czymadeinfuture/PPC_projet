import socket

class PlayerClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.server_host, self.server_port))
        print(f"Connected to server at {self.server_host}:{self.server_port}")

    def run(self):
    # 后续接收和处理服务器数据的代码
        pass

if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345

    player_client = PlayerClient(SERVER_HOST, SERVER_PORT)
    player_client.run()
