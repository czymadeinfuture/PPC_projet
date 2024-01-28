import socket
import threading
import pickle
from sysv_ipc import MessageQueue, IPC_CREAT
import os

class PlayerClient:
    def __init__(self, server_host, server_port, player_id):
        self.server_host = server_host
        self.server_port = server_port
        self.player_id = player_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接到游戏服务器
        self.socket.connect((self.server_host, self.server_port))
        print(f"Player {self.player_id} connected to the game server at {self.server_host}:{self.server_port}.")

        # 初始化消息队列
        self.mq_key = 119 # 示例键，实际项目中应使用唯一键
        self.mq = MessageQueue(self.mq_key, IPC_CREAT)

    def listen_for_server_messages(self):
        while True:
            # 监听来自服务器的消息
            message = self.socket.recv(1024)
            if message:
                game_state = pickle.loads(message)
                self.display_game_state(game_state)

    def display_game_state(self, game_state):
        print("\n--- Game State Update ---")
        print(f"Played Cards: {game_state['played_cards']}")
        print(f"Info Tokens: {game_state['info_tokens']}, Fuse Tokens: {game_state['fuse_tokens']}")

    def listen_for_player_messages(self):
        while True:
            # 监听来自其他玩家的消息
            message, _ = self.mq.receive()
            print(f"\n--- Message from another player ---\n{message.decode()}")

    def send_action(self, action):
        # 序列化并发送动作到服务器
        message = pickle.dumps(action)
        self.socket.sendall(message)

    def run(self):
        # 启动线程监听服务器和其他玩家的消息
        threading.Thread(target=self.listen_for_server_messages).start()
        threading.Thread(target=self.listen_for_player_messages).start()

        # 等待并处理用户输入
        while True:
            action_type = input("\nEnter action type (play/give_info/end): ")
            if action_type.lower() == 'end':
                print("Ending game...")
                self.socket.close()  # 关闭与服务器的连接
                break  # 退出循环，结束程序
            action_details = input("Enter action details: ")
            self.send_action({'type': action_type, 'details': action_details, 'player_id': self.player_id})
            
if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 2003
    PLAYER_ID = int(input("Enter your player ID (e.g., 1, 2, 3...): "))

    player_client = PlayerClient(SERVER_HOST, SERVER_PORT, PLAYER_ID)
    player_client.run()
