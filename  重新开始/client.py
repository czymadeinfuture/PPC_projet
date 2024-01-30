import socket
import pickle
from sysv_ipc import SharedMemory, IPC_CREAT

class PlayerClient:
    def __init__(self, server_host, server_port, player_id):
        self.server_host = server_host
        self.server_port = server_port
        self.player_id = player_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接到游戏服务器
        self.socket.connect((self.server_host, self.server_port))
        print(f"Player {self.player_id} connected to the game server at {self.server_host}:{self.server_port}.")

        # 初始化共享内存
        self.shm = SharedMemory(12345, IPC_CREAT, size=4096)

    def listen_for_server_messages(self):
        while True:
            # 监听来自服务器的消息
            message = self.socket.recv(1024)
            if message:
                if message == b"Game Starting":
                    self.initialize_game()
                else:
                    # 其他消息处理
                    pass

    def initialize_game(self):
        # 初始化游戏状态
        serialized_state = self.shm.read()
        game_state = pickle.loads(serialized_state)

        self.hand = ["X"] * 5  # 玩家初始手牌
        self.other_hands = {i: [] for i in range(1, game_state['num_players'] + 1) if i != self.player_id}
        self.info_tokens = game_state['info_tokens']
        self.fuse_tokens = game_state['fuse_tokens']

        print(f"Game initialized for Player {self.player_id}.")
        print(f"Hand: {self.hand}")
        print(f"Info Tokens: {self.info_tokens}, Fuse Tokens: {self.fuse_tokens}")

    def send_action(self, action):
        # 序列化并发送动作到服务器
        message = pickle.dumps(action)
        self.socket.sendall(message)

    def run(self):
        # 启动监听服务器消息的线程
        threading.Thread(target=self.listen_for_server_messages).start()

        # 处理用户输入
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
