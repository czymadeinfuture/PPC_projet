import socket
import threading
import pickle
from sysv_ipc import SharedMemory, IPC_CREAT

class GameServer:
    def __init__(self, host, port, num_players):
        self.host = host
        self.port = port
        self.num_players = num_players
        self.players = []
        self.shm = SharedMemory(12345, IPC_CREAT, size=4096)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)
        print(f"Game server listening on {host}:{port}")

    def start_game(self):
        # 游戏初始化逻辑
        game_state = {
            'deck': [],
            'info_tokens': self.num_players + 3,
            'fuse_tokens': 3
            # 其他游戏状态信息
        }
        # 序列化并写入共享内存
        serialized_state = pickle.dumps(game_state)
        self.shm.write(serialized_state)

    def accept_connections(self):
        print("Waiting for players to connect...")
        for _ in range(self.num_players):
            client_socket, _ = self.server_socket.accept()
            self.players.append(client_socket)
            print("Accepted a new connection.")

        # 向客户端发送开始游戏的信号
        for player in self.players:
            player.sendall(b"Game Starting")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    # 处理从客户端接收到的数据
                    print("Received data from client.")
            except Exception as e:
                print(f"Error handling client data: {e}")
                break

    def run(self):
        ready = input("Are you ready? (yes/no): ")
        if ready.lower() == "yes":
            self.start_game()
            self.accept_connections()
            for player in self.players:
                threading.Thread(target=self.handle_client, args=(player,)).start()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 2003
    NUM_PLAYERS = 3

    game_server = GameServer(HOST, PORT, NUM_PLAYERS)
    game_server.run()
