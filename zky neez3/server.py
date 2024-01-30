import pickle
from sysv_ipc import SharedMemory, IPC_CREAT
import socket
import threading
import random

class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.players = []
        self.client_id = 0  # 初始化client_id
        self.game_can_start = False
        self.shm = SharedMemory(12345, IPC_CREAT, size=4096)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Game server listening on {host}:{port}")


    def init_game(self, num_players):
        # 创建牌堆
        colors = ['Red', 'Yellow', 'Blue', 'Green', 'Purple'][:num_players]
        deck = [f"{color}{number}" for color in colors for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]]
        random.shuffle(deck)
        
        # 初始化烟花堆
        fireworks = {color: [] for color in colors}
        
        # 初始化令牌
        info_tokens = num_players + 3
        fuse_tokens = 3
        
        # 初始化弃牌堆
        discard_pile = []

        # 游戏状态包括玩家数量
        game_state = {
            'num_players': num_players,
            'deck': deck,
            'fireworks': fireworks,
            'info_tokens': info_tokens,
            'fuse_tokens': fuse_tokens,
            'discard_pile': discard_pile
        }
        serialized_state = pickle.dumps(game_state)
        self.shm.write(serialized_state)

        # 打印验证数据
        print("Server initialization completed.")
        print("Number of Players:", num_players)
        print("Deck:", deck)
        print("Fireworks:", fireworks)
        print("Info Tokens:", info_tokens)
        print("Fuse Tokens:", fuse_tokens)
        print("Discard Pile:", discard_pile)
        print("Wait for the initialization of the clients.")

        # 完成初始化后通知所有客户端
        for player in self.players:
            player.send(b"Initialization completed")

    def deal_cards(self, client_socket):
        # 从共享内存中读取游戏状态
        serialized_state = self.shm.read()
        game_state = pickle.loads(serialized_state)

        # 发牌
        cards_to_deal = game_state['deck'][:5]
        game_state['deck'] = game_state['deck'][5:]  # 更新牌堆

        # 将更新后的游戏状态写回共享内存
        serialized_state = pickle.dumps(game_state)
        self.shm.write(serialized_state)

        # 发送牌给客户端
        client_socket.sendall(pickle.dumps(cards_to_deal))

    def handle_client(self, client_socket, client_id):
        print(f"Sending client ID to client: {client_id}")
        client_socket.sendall(str(client_id).encode())
        self.players.append(client_socket)  # 将连接的套接字添加到列表中

        while True:
            data = client_socket.recv(1024).decode()
            if data == "start_game":
                if not self.game_can_start:
                    self.game_can_start = True
                    print("Let's start!")
                    self.init_game(client_id)  # 在这里调用 init_game
            elif data == "deal_cards":
                self.deal_cards(client_socket)  # 处理发牌请求
            # 可以添加更多处理其他类型请求的代码...

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