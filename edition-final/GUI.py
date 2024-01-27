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
        self.game = Game()  # 创建 Game 实例
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

        # 添加用于显示当前玩家的标签
        self.current_player_label_left = tk.Label(self.left_frame, text="Current Player: Player A")
        self.current_player_label_left.pack()

        self.current_player_label_right = tk.Label(self.right_frame, text="Current Player: Player A")
        self.current_player_label_right.pack()

    def init_player_view(self, frame, current_player, other_player):
        # 当前玩家的手牌（隐藏）
        self.hand_label = tk.Label(frame)
        self.hand_label.pack()

        # 对手玩家的手牌（显示）
        self.other_hand_label = tk.Label(frame)
        self.other_hand_label.pack()

        # 出牌堆标签
        self.pile_label = tk.Label(frame, text="Piles:")
        self.pile_label.pack()

        # 动作按钮
        play_button = tk.Button(frame, text="Play Card", command=self.play_card)
        play_button.pack()

        info_button = tk.Button(frame, text="Give Information", command=self.give_information)
        info_button.pack()

        # 游戏信息标签
        self.info_tokens_label = tk.Label(frame, text="Info Tokens: 5")
        self.info_tokens_label.pack()

        self.fuse_tokens_label = tk.Label(frame, text="Fuse Tokens: 3")
        self.fuse_tokens_label.pack()

    def start_game(self):
        self.game.setup_game()  # 设置游戏
        self.update_ui()  # 更新UI显示初始状态

    def update_ui(self):
        # 假设 'Player A' 和 'Player B' 是游戏中的玩家
        player_a_hand = ' '.join(['X' for _ in self.game.players['Player A'].card_hand])
        player_b_hand = ' '.join(['X' for _ in self.game.players['Player B'].card_hand])

        # 根据游戏状态更新手牌显示
        self.left_frame.hand_label.config(text=f"Player A's Hand: {player_a_hand}")
        self.right_frame.hand_label.config(text=f"Player B's Hand: {player_b_hand}")

        # ... 更新对方玩家手牌和其他游戏状态 ...

    def play_card(self):
        # 实现出牌逻辑
        # 例如: self.game.play_card("Player A", card_index)
        self.update_ui()

    def give_information(self):
        # 实现提供信息的逻辑
        # 例如: self.game.give_information("Player A", "Player B", info)
        self.update_ui()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    start_app = StartWindow()
    start_app.run()
