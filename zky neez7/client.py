import socket
import pickle
from sysv_ipc import SharedMemory, MessageQueue, IPC_CREAT


class PlayerClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))
        self.mq = MessageQueue(12345, IPC_CREAT)  # 创建消息队列

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

        # 创建所有玩家的手牌状态列表（用于显示）
        hands = [["X"] * 5 for _ in range(num_players)]  # 每位玩家5张牌，初始为未知
        # 创建并初始化当前玩家的实际手牌列表
        self.my_hand = []  # 把 my_hand 初始化为实例属性
        # 打印游戏状态信息
        print("Number of Players:", num_players)
        print("Deck:", deck)
        print("Fireworks:", fireworks)
        print("Info Tokens:", info_tokens)
        print("Fuse Tokens:", fuse_tokens)
        print("Discard Pile:", discard_pile)

        # 打印所有玩家的手牌状态
        for i, hand in enumerate(hands):
            print(f"Player {i+1}'s hand:", hand)

        print("My actual hand:", self.my_hand)  # 打印当前玩家的实际手牌

        # 将初始化的数据保存到客户端对象中
        self.num_players = num_players
        self.hands = hands
        self.game_state = game_state

        # 在这里可以进行其他初始化工作，例如创建玩家之间的通信队列等

    def request_and_receive_cards(self):
        # 请求发牌
        print("Requesting cards from server...")
        self.socket.sendall(b"deal_cards")

        # 接收牌
        cards_received = pickle.loads(self.socket.recv(1024))
        self.my_hand = cards_received
        print("Received cards:", self.my_hand)

        # 重新从共享内存读取游戏状态来查看 deck
        serialized_state = SharedMemory(12345).read()
        game_state = pickle.loads(serialized_state)
        print("Updated deck:", game_state['deck'])

    def update_hand_to_others(self):
        # 向其他玩家发送自己的手牌信息
        for i in range(1, self.num_players + 1):
            if i != self.client_id:  # 不向自己发送
                self.mq.send(pickle.dumps((self.client_id, self.my_hand)), type=i)

        # 接收其他玩家的手牌信息
        for _ in range(self.num_players - 1):
            msg, t = self.mq.receive(type=self.client_id)
            sender_id, hand = pickle.loads(msg)
            self.hands[sender_id - 1] = hand

        # 打印所有玩家的手牌状态
        for i, hand in enumerate(self.hands):
            print(f"Player {i+1}'s hand:", hand)
        print("My actual hand:", self.my_hand)  # 打印当前玩家的实际手牌

    def handle_play_card(self):
        # 玩家选择要打出的牌
        card_index = int(input("Which card would you like to play? (1-5): ")) - 1
        if 0 <= card_index < len(self.my_hand):
            # 发送打出的牌的信息给服务器
            card_to_play = self.my_hand[card_index]
            self.socket.sendall(f"play_card {card_index}".encode())
            print(f"You played: {card_to_play}")

            # 接收服务器响应和新牌
            response = self.socket.recv(1024).decode()
            print(response)  # 打印服务器发来的响应

            new_card_info = self.socket.recv(1024).decode()
            if new_card_info.startswith("new_card"):
                new_card = new_card_info.split()[1]
                if new_card != "None":
                    self.my_hand[card_index] = new_card  # 更新手牌
                    print(f"New card received: {new_card}")
                    self.update_hand_to_others()  # 更新手牌信息给其他玩家
                    self.socket.sendall("hand_updated".encode())
                else:
                    print("No more cards in the deck")
        else:
            print("Invalid card selection.")
            self.handle_play_card()  # 重新选择牌

        # 发送确认消息
        self.socket.sendall("action_complete".encode())


    def handle_give_information(self):
        # 获取可用的信息令牌数量
        game_state = self.get_game_state()
        if game_state['info_tokens'] <= 0:
            print("You cannot give information! No info tokens left.")
            return

        print("You can give information.")
        target_player_id = int(input("Which player would you like to inform? (Enter player ID): "))
        info_type = input("What information would you like to give? (A: Color, B: Number): ").upper()
        
        if info_type == "A":
            info = input("Enter the color to inform: ").capitalize()
        elif info_type == "B":
            info = input("Enter the number to inform: ")
        else:
            print("Invalid input. Please try again.")
            self.handle_give_information()
            return

        # 发送信息给目标玩家
        self.mq.send(pickle.dumps(("info", self.client_id, info)), type=target_player_id)
        
        # 等待目标玩家确认接收
        _, _ = self.mq.receive(type=self.client_id)
        print("The player has acknowledged the information.")

        # 通知服务器完成了信息令牌操作
        self.socket.sendall(b"info_token_used")

        # 操作完成后通知服务器
        self.socket.sendall("action_complete".encode())
    
    def get_game_state(self):
        """从共享内存中读取游戏状态。"""
        serialized_state = SharedMemory(12345).read()
        return pickle.loads(serialized_state)

    def run(self):
        # 接收从服务器发送的客户端ID，并保存
        self.client_id = int(self.socket.recv(1024).decode())
        print(f"Connected to server at {self.server_host}:{self.server_port} as Player {self.client_id}")

        if self.client_id > 1:
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

        # 请求并接收手牌，并打印更新后的 deck
        self.request_and_receive_cards()

        # 更新自己的手牌信息给其他玩家，并接收他们的手牌信息
        self.update_hand_to_others()

        # 通知服务器玩家准备好了
        print("Notifying server that player is ready...")
        self.socket.sendall(b"player_ready")
        
        while True:
            # 接收来自服务器的消息
            message = self.socket.recv(1024).decode()
            if message.startswith("Game over"):
                # 游戏结束消息
                print(message)  # 在客户端打印游戏结束信息
                break  # 跳出循环，结束客户端程序

            elif message == "Your turn to act":
                # 玩家行动选择
                action = input("How would you like to act? (A: Play a card, B: Give information): ")
                if action.upper() == "A":
                    # 处理打出牌的逻辑
                    self.handle_play_card()
                elif action.upper() == "B":
                    # 处理信息令牌的逻辑
                    self.handle_give_information()
                # 可以在这里添加其他必要的逻辑

if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345
    client = PlayerClient(SERVER_HOST, SERVER_PORT)
    client.run()
