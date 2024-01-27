import threading
import queue

class Player(threading.Thread):
    def __init__(self, name, game_queue):
        super().__init__()
        self.name = name
        self.game_queue = game_queue

    def run(self):
        while True:
            # 玩家的动作逻辑
            action = input(f"{self.name}, enter your action: ")
            self.game_queue.put((self.name, action))
            # 更多逻辑...

class Game:
    def __init__(self):
        self.game_queue = queue.Queue()
        self.players = [Player("Player A", self.game_queue), Player("Player B", self.game_queue)]

    def start_game(self):
        for player in self.players:
            player.start()

        while True:
            # 游戏的主逻辑
            player_name, action = self.game_queue.get()
            print(f"Action received from {player_name}: {action}")
            # 更多逻辑...

if __name__ == "__main__":
    game = Game()
    game.start_game()
