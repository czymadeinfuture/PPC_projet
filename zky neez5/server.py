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
        self.ready_players = 0
        self.client_id = 0  # 初始化client_id
        self.game_start_event = threading.Event()  # 新增
        self.game_can_start = False
        self.game_started = False  # 新增
        self.shm = SharedMemory(12345, IPC_CREAT, size=4096)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Game server listening on {host}:{port}")

    def accept_connections(self):
        """在单独的线程中接受玩家连接"""
        while True:
            client_socket, addr = self.server_socket.accept()
            self.client_id += 1
            print(f"Client {self.client_id} connected from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, self.client_id)).start()

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

    def handle_ready(self, client_socket):
        self.ready_players += 1
        print(f"Player ready: {self.ready_players}/{self.client_id}")
        if self.ready_players == self.client_id:
            print("All players are ready. Game starting...")
            self.game_start_event.set()  # 设置事件，表示游戏可以开始
            # 可以在这里发送游戏开始的消息给所有客户端
            for player in self.players:
                player.send(b"Game starting")

    def handle_client(self, client_socket, client_id):
        print(f"Sending client ID to client: {client_id}")
        client_socket.sendall(str(client_id).encode())
        self.players.append(client_socket)  # 将连接的套接字添加到列表中

        while not self.game_started:  # 修改条件
            data = client_socket.recv(1024).decode()
            if data.startswith("play_card"):
                card = data.split()[1]
                self.handle_play_card(client_socket, client_id, card)
            if data == "start_game":
                if not self.game_can_start:
                    self.game_can_start = True
                    print("Let's start!")
                    self.init_game(client_id)  # 在这里调用 init_game
            elif data == "deal_cards":
                self.deal_cards(client_socket)  # 处理发牌请求
            elif data == "player_ready":
                self.handle_ready(client_socket)

            # 可以添加更多处理其他类型请求的代码...
                
    def handle_play_card(self, client_socket, client_id, card):
        # 提取牌的颜色和数字
        color, number = card[:-1], int(card[-1])

        # 从共享内存中读取游戏状态
        game_state = self.get_game_state()

        # 判断牌是否可以被成功打出
        if self.can_play_card(game_state, color, number):
            # 如果可以打出，更新游戏状态
            game_state['fireworks'][color].append(card)
            response = "Card played successfully"
            print(f"Player {client_id} played {card} successfully.")
        else:
            # 如果不可以打出，更新游戏状态
            game_state['discard_pile'].append(card)
            game_state['fuse_tokens'] -= 1
            response = "Card played unsuccessfully"
            print(f"Player {client_id} played {card} unsuccessfully.")

        # 更新共享内存中的游戏状态
        serialized_state = pickle.dumps(game_state)
        self.shm.write(serialized_state)

        # 发送结果给客户端
        client_socket.sendall(response.encode())

    def can_play_card(self, game_state, color, number):
        # 检查牌是否可以被成功打出
        if number == 1 and len(game_state['fireworks'][color]) == 0:
            return True
        if number > 1 and f"{color}{number-1}" in game_state['fireworks'][color]:
            return True
        return False


    def start_game_loop(self):
        """开始游戏循环，轮询玩家让他们依次行动。"""
        self.game_started = True  # 游戏开始
        self.current_player_index = 0  # 当前玩家索引
        while True:
            # 获取当前玩家的套接字
            current_player_socket = self.players[self.current_player_index]

            # 通知当前玩家轮到他们行动
            current_player_socket.sendall(b"Your turn to act")
            print(f"Now it's Player {self.current_player_index + 1}'s turn!")

            # 等待当前玩家完成行动
            while True:
                response = current_player_socket.recv(1024).decode()
                if response == "action_complete":
                    break  # 玩家已完成行动，退出等待循环

            # 更新当前玩家索引以移至下一位玩家
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            # 检查游戏是否结束
            game_status, reason = self.check_game_over()
            if game_status != "continue":
                # 如果游戏结束，通知所有玩家并退出循环
                for player_socket in self.players:
                    player_socket.sendall(f"Game over: {reason}".encode())
                break

    def check_game_over(self):
        """检查游戏是否结束，返回游戏状态和结束原因（如果游戏未结束，则为 None）。"""
        game_state = self.get_game_state()

        # 检查炸弹令牌是否用完
        if game_state['fuse_tokens'] <= 0:
            return "lose", "All fuse tokens are used up!"

        # 检查是否所有烟花堆都达到了5
        if all(len(game_state['fireworks'][color]) == 5 for color in game_state['fireworks']):
            return "win", "All fireworks reached 5!"

        # 检查牌堆是否为空
        if not game_state['deck']:
            return "end", "No more cards in the deck!"

        # 检查弃牌堆中是否有无法放入烟花堆的牌
        for card in game_state['discard_pile']:
            color, number = card[:-1], int(card[-1])
            if number == 5 or game_state['fireworks'][color].count(f"{color}{number}") > 1:
                return "lose", "Invalid cards found in the discard pile!"

        # 如果以上条件都不满足，游戏继续
        return "continue", None

    def get_game_state(self):
        """从共享内存中读取游戏状态。"""
        serialized_state = self.shm.read()
        return pickle.loads(serialized_state)



    def run(self):
        print(f"Server listening on {self.host}:{self.port}")

        # 启动一个新线程来接受玩家连接
        threading.Thread(target=self.accept_connections).start()

        # 等待开始游戏的确认
        self.game_start_event.wait()

        print("Game starting...")
        self.start_game_loop()  # 开始游戏循环



if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345

    server = GameServer(HOST, PORT)
    server.run()