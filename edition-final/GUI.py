import tkinter as tk
from Game import Game  # 假设 Game 类已经包含了必要的逻辑

class StartWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hannabi Game - Start")

        start_button = tk.Button(self.root, text="Start", command=self.start_game)
        start_button.pack(pady=10)

        exit_button = tk.Button(self.root, text="Exit", command=self.root.destroy)
        exit_button.pack(pady=10)

    def start_game(self):
        self.root.destroy()  # 关闭启动窗口
        game_app = HannabiGUI()  # 打开主游戏窗口
        game_app.run()

    def run(self):
        self.root.mainloop()

class HannabiGUI:
    def __init__(self):
        self.game = Game()
        self.window = tk.Tk()
        self.window.title("Hannabis Game for 2 Players")

        # 创建两个玩家的视角
        self.left_frame = tk.Frame(self.window)
        self.right_frame = tk.Frame(self.window)

        self.left_frame.pack(side="left", fill="both", expand=True)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # 初始化玩家视角
        self.init_player_view(self.left_frame, "Player A", "Player B")
        self.init_player_view(self.right_frame, "Player B", "Player A")

        self.start_game()

    def init_player_view(self, frame, player_name, other_player):
        # 当前玩家的手牌（隐藏）
        hand_label = tk.Label(frame, text=f"{player_name}'s Hand: XXXXX")
        hand_label.pack()

        # 对手玩家的手牌（显示）
        other_hand_label = tk.Label(frame, text=f"{other_player}'s Hand:")
        other_hand_label.pack()

        # 动作按钮
        play_button = tk.Button(frame, text="Play Card", command=self.play_card)
        play_button.pack()

        info_button = tk.Button(frame, text="Give Information", command=self.give_information)
        info_button.pack()

        # 游戏信息
        info_tokens_label = tk.Label(frame, text="Remaining Info Tokens: 5")
        info_tokens_label.pack()

        fuse_tokens_label = tk.Label(frame, text="Remaining Fuse Tokens: 3")
        fuse_tokens_label.pack()

        current_player_label = tk.Label(frame, text=f"Current Player: {player_name}")
        current_player_label.pack()

    def play_card(self):
        # 实现出牌逻辑
        pass

    def give_information(self):
        # 实现给信息的逻辑
        pass

    def start_game(self):
        # 初始化游戏逻辑
        pass

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    start_app = StartWindow()
    start_app.run()
