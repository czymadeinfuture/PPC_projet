import os
import socket
import threading
import pickle
from sysv_ipc import SharedMemory, IPC_CREAT
import signal

from gameH import Game

class GameServer:
    def __init__(self, host, port, num_players):
        self.host = host
        self.port = port
        self.num_players = num_players
        self.players = []  # 存储玩家的套接字连接
        self.game = Game(num_players)  # 初始化游戏逻辑
        key = 119
        self.shm = SharedMemory(key, IPC_CREAT, size=4096)  # 创建共享内存
        self.update_shared_memory()  # 初始化共享内存中的游戏状态

        # 创建套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(num_players)
        print(f"Game server listening on {host}:{port}")

    def update_shared_memory(self):
        # 更新共享内存中的游戏状态
        game_state = {
            'played_cards': self.game.played_cards,
            'info_tokens': self.game.info_tokens,
            'fuse_tokens': self.game.fuse_tokens
        }
        serialized_state = pickle.dumps(game_state)
        self.shm.write(serialized_state)

    def accept_connections(self):
        # 接受玩家的连接
        for _ in range(self.num_players):
            client_socket, _ = self.server_socket.accept()
            self.players.append(client_socket)
            print("Accepted a new connection.")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # 处理来自客户端的数据
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    action = pickle.loads(data)
                    if action['type'] == 'end':  # 检测到结束信号
                        print("Ending game...")
                        for player in self.players:  # 关闭所有客户端连接
                            player.close()
                        self.server_socket.close()  # 关闭服务器套接字
                        os._exit(0)  # 立即结束程序
                    self.process_action(action, client_socket)
                    self.update_shared_memory()  # 更新共享内存中的游戏状态
                    self.broadcast_game_state()  # 广播游戏状态
            except Exception as e:
                print(f"Error handling client data: {e}")
                break

    def process_action(self, action, client_socket):
        # 根据接收到的动作更新游戏状态
        print(f"Received action: {action}")
        # 此处添加处理动作的逻辑
        # 例如，self.game.play_card(player_index, card_index) 等

    def broadcast_game_state(self):
        # 广播游戏状态给所有玩家
        game_state = self.game.get_game_state()
        serialized_state = pickle.dumps(game_state)
        for player in self.players:
            player.sendall(serialized_state)

    def run(self):
        # 启动游戏服务器
        self.accept_connections()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 2003
    NUM_PLAYERS = 3

    game_server = GameServer(HOST, PORT, NUM_PLAYERS)
    game_server.run()
