import socket
import pickle
from sysv_ipc import SharedMemory


class PlayerClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))

    def handle_initialization(self):
        data = self.socket.recv(1024).decode()
        if data == "Initialization completed":
            print("Server initialization completed. Initializing client...")
            self.initialize_client()  # 调用初始化客户端的函数

    def initialize_client(self):
        # 从共享内存读取游戏状态数据
        shm = SharedMemory(12345)
        serialized_state = shm.read()
        game_state = pickle.loads(serialized_state)

        num_players = game_state['num_players']
        deck = game_state['deck']
        fireworks = game_state['fireworks']
        info_tokens = game_state['info_tokens']
        fuse_tokens = game_state['fuse_tokens']
        discard_pile = game_state['discard_pile']

        # 创建自己的手牌列表，初始时全是"X"
        my_hand = ["X"] * 5  # 假设每个玩家的手牌有5张

        # 打印游戏状态信息
        print("Number of Players:", num_players)
        print("Deck:", deck)
        print("Fireworks:", fireworks)
        print("Info Tokens:", info_tokens)
        print("Fuse Tokens:", fuse_tokens)
        print("Discard Pile:", discard_pile)
        print("My_hand:", my_hand)

        # 将初始化的数据保存到客户端对象中
        self.num_players = num_players
        self.my_hand = my_hand
        self.game_state = game_state

        # 在这里可以进行其他初始化工作，例如创建玩家之间的通信队列等


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

        # 等待服务器发送初始化完成消息
        self.handle_initialization()

        while True:
            pass


if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345
    client = PlayerClient(SERVER_HOST, SERVER_PORT)
    client.run()
