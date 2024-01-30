import pickle
from sysv_ipc import SharedMemory, IPC_CREAT
import socket
import threading
import random
import os
import signal

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
        signal.signal(signal.SIGUSR1, self.handle_game_over_signal)
        self.lock = threading.Lock()  # 初始化一个锁
        self.shm = SharedMemory(12345, IPC_CREAT, size=4096)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Game server listening on {host}:{port}")

    def handle_game_over_signal(self, signum, frame):
        """处理游戏结束信号 Handling game over signals"""
        print("Game over signal received.")
        # 通知所有客户端游戏结束 Notify all clients of the end of the game
        for player_socket in self.players:
            player_socket.sendall("Game over".encode())
        # 可以在这里添加其它清理资源和准备下一轮游戏的代码 Additional code to clean up resources and prepare for the next round of the game can be added here

    def accept_connections(self):
        """在单独的线程中接受玩家连接"""
        while True:
            client_socket, addr = self.server_socket.accept()
            self.client_id += 1
            print(f"Client {self.client_id} connected from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, self.client_id)).start()

    def init_game(self, num_players):
        with self.lock:  # 使用锁
            # 创建牌堆 Create piles of cards
            colors = ['Red', 'Yellow', 'Blue', 'Green', 'Purple'][:num_players]
            deck = [f"{color}{number}" for color in colors for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]]
            random.shuffle(deck)
            
            # 初始化烟花堆 Initialize the fireworks pile
            fireworks = {color: [] for color in colors}
            
            # 初始化令牌 Initialization Token
            info_tokens = num_players + 3
            fuse_tokens = 3
            
            # 初始化弃牌堆 Initialize the discard pile
            discard_pile = []

            # 游戏状态包括玩家数量 Game status including number of players
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

            # 打印验证数据 Printing validation data
            print("Server initialization completed.")
            print("Number of Players:", num_players)
            print("Deck:", deck)
            print("Fireworks:", fireworks)
            print("Info Tokens:", info_tokens)
            print("Fuse Tokens:", fuse_tokens)
            print("Discard Pile:", discard_pile)
            print("Wait for the initialization of the clients.")

            # 完成初始化后通知所有客户端 Notify all clients when initialization is complete
            for player in self.players:
                player.send(b"Initialization completed")

    def deal_cards(self, client_socket):
        with self.lock:  # 使用锁
            # 从共享内存中读取游戏状态 Read game state from shared memory
            serialized_state = self.shm.read()
            game_state = pickle.loads(serialized_state)

            # 发牌 licensing
            cards_to_deal = game_state['deck'][:5]
            game_state['deck'] = game_state['deck'][5:]  # 更新牌堆 Update Pile

            # 将更新后的游戏状态写回共享内存 Write updated game state back to shared memory
            serialized_state = pickle.dumps(game_state)
            self.shm.write(serialized_state)

            # 发送牌给客户端 Sending cards to the client
            client_socket.sendall(pickle.dumps(cards_to_deal))

    def handle_ready(self, client_socket):
        self.ready_players += 1
        print(f"Player ready: {self.ready_players}/{self.client_id}")
        if self.ready_players == self.client_id:
            print("All players are ready. Game starting...")
            self.game_start_event.set()  # 设置事件，表示游戏可以开始 Setting an event to indicate that the game is ready to start
            # 可以在这里发送游戏开始的消息给所有客户端 A game start message can be sent to all clients here
            for player in self.players:
                player.send(b"Game starting")

    def handle_client(self, client_socket, client_id):
        print(f"Sending client ID to client: {client_id}")
        client_socket.sendall(str(client_id).encode())
        self.players.append(client_socket)  # 将连接的套接字添加到列表中 Adding connected sockets to the list

        while not self.game_started:
            data = client_socket.recv(1024).decode()
            if data.startswith("play_card"):
                # 提取牌信息并处理 Extract card information and process
                card = data.split()[1]
                self.handle_play_card(client_socket, client_id, card)
            elif data == "info_token_used":
                # 处理信息令牌的使用 Handling the use of information tokens
                self.handle_info_token_use(client_socket, client_id)
            elif data == "start_game":
                # 启动游戏 Launching the game
                if not self.game_can_start:
                    self.game_can_start = True
                    print("Let's start!")
                    self.init_game(client_id)
            elif data == "deal_cards":
                # 发牌请求 Licensing requests
                self.deal_cards(client_socket)
            elif data == "player_ready":
                # 玩家准备就绪 Players ready to go.
                self.handle_ready(client_socket)
            elif data == "info_token_used":
                self.handle_info_token_use(client_socket, client_id)

            # ... 其他类型请求的处理 ...
                
    def handle_play_card(self, client_socket, client_id, card_index):
        with self.lock:  # 使用锁来确保线程安全 Using Locks to Ensure Thread Safety
            game_state = self.get_game_state()  # 获取当前游戏状态 Get current game status

            # 检查玩家选择的牌是否有效 Checking the validity of a player's chosen card
            if card_index >= len(game_state['players_hands'][client_id - 1]) or card_index < 0:
                print(f"Invalid card index from Player {client_id}")
                client_socket.sendall("Invalid card selection.".encode())
                return

            card = game_state['players_hands'][client_id - 1][card_index]  # 获取玩家选择的牌 Get the player's choice of cards
            color, number = card[:-1], int(card[-1])  # 分解牌的颜色和数字 Breaking down the colors and numbers of the cards

            # 判断牌是否可以被成功打出 Determine if a card can be successfully played
            if self.can_play_card(game_state, color, number):
                # 如果可以打出，更新烟花堆 Update the fireworks pile if you can hit it
                game_state['fireworks'][color].append(card)
                response = "Card played successfully"
                print(f"Player {client_id} played {card} successfully.")
            else:
                # 如果不可以打出，牌放入弃牌堆，炸弹令牌减1 If it cannot be played, the card is put into the discard pile and the bomb token is reduced by 1
                game_state['discard_pile'].append(card)
                game_state['fuse_tokens'] -= 1
                response = "Card played unsuccessfully"
                print(f"Player {client_id} played {card} unsuccessfully.")

            # 从牌堆中抽取一张新牌替换打出的牌 Take a new card from the pile to replace the one played.
            new_card = game_state['deck'].pop(0) if game_state['deck'] else None
            game_state['players_hands'][client_id - 1][card_index] = new_card if new_card else "No more cards"
            client_socket.sendall(f"new_card {new_card}".encode() if new_card else "new_card None".encode())

            # 更新共享内存中的游戏状态 Update game status in shared memory
            serialized_state = pickle.dumps(game_state)
            self.shm.write(serialized_state)

            # 检查游戏是否结束 Check if the game is over
            game_status, reason = self.check_game_over()
            if game_status != "continue":
                self.end_game(reason)  # 调用结束游戏的函数 Call the function that ends the game

            # 发送打出牌的结果给客户端 Sends the result of playing a card to the client
            client_socket.sendall(response.encode())

            # 发送行动完成的确认，准备接收下一次行动 Send confirmation of action completion and prepare to receive the next action
            client_socket.sendall("action_complete".encode())

    def end_game(self, reason):
        """结束游戏并向所有进程发送游戏结束信号"""
        print("Game over:", reason)
        os.kill(os.getpid(), signal.SIGUSR1)  # 向当前进程发送SIGUSR1信号 Send SIGUSR1 signal to the current process


    def can_play_card(self, game_state, color, number):
        # 检查牌是否可以被成功打出 Check if the card can be played successfully
        if number == 1 and len(game_state['fireworks'][color]) == 0:
            return True
        if number > 1 and f"{color}{number-1}" in game_state['fireworks'][color]:
            return True
        return False
    
    def handle_info_token_use(self, client_socket, client_id):
        with self.lock:
            game_state = self.get_game_state()
            if game_state['info_tokens'] > 0:
                game_state['info_tokens'] -= 1
                # 更新游戏状态 Update game status
                serialized_state = pickle.dumps(game_state)
                self.shm.write(serialized_state)
                # 响应客户端 Responding to the client
                client_socket.sendall("info_token_used successfully".encode())
                print(f"Player {client_id} used an info token.")
            else:
                client_socket.sendall("No info tokens left".encode())


    def start_game_loop(self):
        """开始游戏循环，轮询玩家让他们依次行动。"""
        self.game_started = True  # 游戏开始 Game Start
        self.current_player_index = 0  # 当前玩家索引 Current Player Index
        while True:
            # 获取当前玩家的套接字 Get the current player's socket
            current_player_socket = self.players[self.current_player_index]

            # 通知当前玩家轮到他们行动 Notify the current player that it is their turn to act
            current_player_socket.sendall(b"Your turn to act")
            print(f"Now it's Player {self.current_player_index + 1}'s turn!")

            # 等待当前玩家完成行动 Wait for the current player to complete the action
            while True:
                response = current_player_socket.recv(1024).decode()
                if response == "action_complete":
                    break  # 玩家已完成行动，退出等待循环 The player has completed the action and exits the wait cycle

            # 更新当前玩家索引以移至下一位玩家 Update current player index to move to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            # 检查游戏是否结束 Check if the game is over
            game_status, reason = self.check_game_over()
            if game_status != "continue":
                # 如果游戏结束，通知所有玩家并退出循环 If the game ends, notify all players and exit the loop
                for player_socket in self.players:
                    player_socket.sendall(f"Game over: {reason}".encode())
                break

    def check_game_over(self):
        with self.lock:  # 使用锁
            """检查游戏是否结束，返回游戏状态和结束原因（如果游戏未结束，则为 None）。"""
            game_state = self.get_game_state()

            # 检查炸弹令牌是否用完 Checking to see if the bomb tokens have run out
            if game_state['fuse_tokens'] <= 0:
                return "lose", "All fuse tokens are used up!"

            # 检查是否所有烟花堆都达到了5 Check to make sure all fireworks piles are at 5
            if all(len(game_state['fireworks'][color]) == 5 for color in game_state['fireworks']):
                return "win", "All fireworks reached 5!"

            # 检查牌堆是否为空 Check if the pile is empty
            if not game_state['deck']:
                return "end", "No more cards in the deck!"

            # 检查弃牌堆中是否有无法放入烟花堆的牌 Check the discard pile for cards that can't fit into the fireworks pile
            for card in game_state['discard_pile']:
                color, number = card[:-1], int(card[-1])
                if number == 5 or game_state['fireworks'][color].count(f"{color}{number}") > 1:
                    return "lose", "Invalid cards found in the discard pile!"

            # 如果以上条件都不满足，游戏继续 If none of the above conditions are met, the game continues
            return "continue", None

    def get_game_state(self):
        """从共享内存中读取游戏状态。"""
        serialized_state = self.shm.read()
        return pickle.loads(serialized_state)



    def run(self):
        print(f"Server listening on {self.host}:{self.port}")

        # 启动一个新线程来接受玩家连接 Start a new thread to accept player connections
        threading.Thread(target=self.accept_connections).start()

        # 等待开始游戏的确认 Waiting for confirmation to start the game
        self.game_start_event.wait()

        print("Game starting...")
        self.start_game_loop()  # 开始游戏循环 Start game loop



if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12345

    server = GameServer(HOST, PORT)
    server.run()