import socket
import threading
import random
import time
from sysv_ipc import MessageQueue, IPC_CREAT

max_wait = 30  # 最大等待时间

class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __repr__(self):
        return f"{self.color}{self.number}"

class Deck:
    def __init__(self, num_players):
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'White'][:num_players]
        self.cards = [Card(color, number) for color in colors for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None

class Game:
    def __init__(self):
        self.players = {}  # 玩家ID到套接字的映射
        self.deck = None # 初始时没有玩家，牌堆为空
        self.suits = {color: 0 for color in ['Red', 'Blue', 'Green', 'Yellow', 'White']}  # 正在构建的花色牌堆
        self.info_tokens = 8  # 信息令牌的初始数量
        self.fuse_tokens = 3  # 导火线令牌的初始数量
        self.current_player_index = 0

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        broadcast_message(f"It's now Player {list(self.players.keys())[self.current_player_index]}'s turn.", self)

    def add_player(self, player_id, socket):
        self.players[player_id] = socket
        if len(self.players) == 1:  # 第一个玩家加入时初始化牌堆
            self.deck = Deck(len(self.players))

        # 为每个玩家创建消息队列
        mq_key = 1000 + player_id
        MessageQueue(mq_key, IPC_CREAT)  # 创建消息队列
        socket.sendall(f"mq_key:{mq_key}".encode())  # 发送消息队列键值给客户端


    def play_card(self, player_id, card_index):
        player_socket = self.players[player_id]
        card = self.player_hands[player_id].pop(card_index)  # 从玩家手牌中移除这张牌

        # 检查这张牌是否能够被成功打出
        if card.number == self.suits[card.color] + 1:
            self.suits[card.color] = card.number  # 更新对应花色卡堆的状态
            broadcast_message(f"Player {player_id} successfully played {card}.", self)
            # 检查是否是5号牌，恢复一个信息令牌
            if card.number == 5 and self.info_tokens < 8:
                self.info_tokens += 1
        else:
            # 出牌失败，消耗一个导火线令牌
            self.fuse_tokens -= 1
            broadcast_message(f"Player {player_id} played {card} incorrectly. Fuse token lost.", self)
            if self.fuse_tokens <= 0:
                self.end_game(False)  # 如果导火线令牌用尽，游戏结束

        # 给玩家抽一张新牌
        new_card = self.deck.deal_card()
        if new_card:
            self.player_hands[player_id].append(new_card)

    def discard_card(self, player_id, card_index):
        player_socket = self.players[player_id]
        discarded_card = self.player_hands[player_id].pop(card_index)  # 从玩家手牌中移除这张牌

        # 如果信息令牌不是最大值，则恢复一个信息令牌
        if self.info_tokens < 8:
            self.info_tokens += 1

        broadcast_message(f"Player {player_id} discarded {discarded_card}. Info token restored.", self)

        # 给玩家抽一张新牌
        new_card = self.deck.deal_card()
        if new_card:
            self.player_hands[player_id].append(new_card)

    '''def give_hint(self, target_player_id, hint_info):
    # 假设 hint_info 是一个包含提示类型和提示内容的元组，例如 ('color', 'Red')
        hint_type, hint_value = hint_info

        # 消耗一个信息令牌
        if self.info_tokens > 0:
            self.info_tokens -= 1
            # 向目标玩家发送提示信息
            target_socket = self.players[target_player_id]
            target_socket.sendall(f"Hint: Your {hint_type} is {hint_value}.\n".encode())
            broadcast_message(f"Player {target_player_id} received a hint about their {hint_type}.", self)
        else:
            broadcast_message("No info tokens left. Cannot give hint.", self)'''

    def check_end_conditions(self):
        if self.fuse_tokens <= 0:
            self.end_game(False, "All fuse tokens have been used. Game over.")
        elif all(card.number == 5 for piles in self.played_cards.values() for card in piles):
            self.end_game(True, "Congratulations! All 5s have been successfully played.")
        elif not self.deck.cards:
            self.end_game(False, "The deck is empty. Game over.")

    def end_game(self, win, message):
        broadcast_message(message, self)
        shutdown_server()

def handle_client_connection(client_socket, player_id, game):
    global game_started, server_running
    try:
        client_socket.sendall(f"Your Player ID is {player_id}, all players joined? (yes/no): ".encode())
        
        # 等待玩家回应是否所有玩家都已加入
        while not game_started.is_set():
            response = client_socket.recv(1024).decode().strip().lower()
            if response == "yes":
                game_started.set()
                broadcast_message(f"All players are ready. Game starting. {len(game.players)} players in the game.", game)
                deal_cards_to_players(game)
                break
            elif response == "no":
                client_socket.sendall("Waiting for all players to join.\n".encode())
            else:
                client_socket.sendall("Invalid response. Please answer 'yes' or 'no'.\n".encode())

        # 游戏开始后，持续接收和处理玩家的动作
        while game_started.is_set() and server_running:
            while player_id != list(game.players.keys())[game.current_player_index]:
                if not server_running:
                    return  # 如果服务器不再运行，退出循环
                time.sleep(0.1) 

            action = client_socket.recv(1024).decode().strip()
            if action.startswith("play"):
                _, card_index = action.split()
                game.play_card(player_id, int(card_index))
                game.next_player() 
            elif action.startswith("discard"):
                _, card_index = action.split()
                game.discard_card(player_id, int(card_index))
                game.next_player() 
            #elif action.startswith("hint"):
             #   _, target_player_id, hint_type, hint_value = action.split()
              #  game.give_hint(int(target_player_id), hint_type, hint_value)
            else:
                client_socket.sendall("Invalid action. Please use 'play', 'discard', or 'hint'.\n".encode())


            # 检查游戏结束条件
            game.check_end_conditions()

    except Exception as e:
        print(f"Error processing action from player {player_id}: {e}")
    finally:
        client_socket.close()


def broadcast_message(message, game):
    for player_socket in game.players.values():
        player_socket.sendall(message.encode())

def deal_cards_to_players(game):
    if game.deck is None:
        game.deck = Deck(len(game.players))  # 根据玩家数量初始化牌堆
    for player_id, player_socket in game.players.items():
        hand = [game.deck.deal_card() for _ in range(5)]  # 发牌
        hand_str = ', '.join([str(card) for card in hand])
        player_socket.sendall(f"Your hand: {hand_str}\n".encode())

def start_game_timer(server_socket):
    global game_started
    time.sleep(max_wait)
    if not game_started.is_set():
        print("No 'yes' response within 30 seconds. Shutting down the server...")
        shutdown_server(server_socket)

def shutdown_server(server_socket):
    global server_running
    server_running = False
    broadcast_message("We don't make a game", game)
    server_socket.close()
    print("Server and all clients have been shut down.")

def game_server():
    global server_running, game_started, game
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 65432))
    server_socket.listen()
    print("Server listening on localhost:65432. Waiting for players to connect...")

    game_started = threading.Event()
    server_running = True
    game = Game()
    player_id = 1

    timer_thread = threading.Thread(target=start_game_timer, args=(server_socket,))
    timer_thread.start()

    try:
        while True:
            if not server_running:
                break

            client_socket, _ = server_socket.accept()
            game.add_player(player_id, client_socket)
            threading.Thread(target=handle_client_connection, args=(client_socket, player_id, game)).start()
            player_id += 1
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    game_server()

