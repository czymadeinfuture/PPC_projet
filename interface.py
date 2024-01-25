from test_interface import *
import tkinter.simpledialog as simpledialog
import tkinter as tk


class HannabiGUI:
    def __init__(self, game):
        self.game = game
        self.window = tk.Tk()
        self.window.title("Hannabis Game")

        self.player_hand_labels = []
        self.played_cards_labels = {}
        
        self.create_player_areas()
        self.create_played_cards_area()
        self.create_control_area()
        self.create_game_info_area()

        self.update_display()

    def create_player_areas(self):
        self.player_frames = []  # 初始化 player_frames 属性
        for i in range(len(self.game.players)):
            frame = tk.Frame(self.window, borderwidth=2, relief="ridge")
            frame.pack(side="top", fill="x", padx=5, pady=5)

            label = tk.Label(frame, text=f"Player {i + 1}'s Hand:")
            label.pack(side="left")

            hand_label = tk.Label(frame, text="")
            hand_label.pack(side="left")
            self.player_frames.append(frame)  # 添加到 player_frames 列表
            self.player_hand_labels.append(hand_label)

    def create_played_cards_area(self):
        self.played_cards_frame = tk.Frame(self.window, borderwidth=2, relief="ridge")
        self.played_cards_frame.pack(side="top", fill="x", padx=5, pady=5)

        for color in self.game.played_cards.keys():
            label = tk.Label(self.played_cards_frame, text=f"{color} Pile: []")
            label.pack(side="left")
            self.played_cards_labels[color] = label  # 为每种颜色创建一个标签并存储在字典中


    def create_control_area(self):
        self.control_frame = tk.Frame(self.window, borderwidth=2, relief="ridge")
        self.control_frame.pack(side="top", fill="x", padx=5, pady=5)

        play_button = tk.Button(self.control_frame, text="Play Card", command=self.play_card)
        play_button.pack(side="left")

        info_button = tk.Button(self.control_frame, text="Give Information", command=self.give_information)
        info_button.pack(side="left")

        close_button = tk.Button(self.control_frame, text="Close Game", command=self.close_game)
        close_button.pack(side="right")

    def create_game_info_area(self):
        self.info_frame = tk.Frame(self.window, borderwidth=2, relief="ridge")
        self.info_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.info_tokens_label = tk.Label(self.info_frame, text="Info Tokens: " + str(self.game.info_tokens))
        self.info_tokens_label.pack(side="left")

        self.fuse_tokens_label = tk.Label(self.info_frame, text="Fuse Tokens: " + str(self.game.fuse_tokens))
        self.fuse_tokens_label.pack(side="left")

        self.current_player_label = tk.Label(self.info_frame, text="")
        self.current_player_label.pack(side="left")
        self.update_current_player_display()

    def update_current_player_display(self):
        current_player_text = f"Current Player: Player {self.game.current_player + 1}"
        self.current_player_label.configure(text=current_player_text)

    def update_display(self):
        # 更新手牌显示
        for i, frame in enumerate(self.player_frames):
            hand_label = frame.winfo_children()[1]
            hand_label.configure(text="Number of Cards: " + str(len(self.game.players[i].hand)))

        # 更新已出牌堆显示
        for color, pile in self.game.played_cards.items():
            cards_text = ", ".join(str(card) for card in pile)
            self.played_cards_labels[color].configure(text=f"{color} Pile: {cards_text}")

        # 更新信息代币和导火线代币显示
        self.info_tokens_label.configure(text="Info Tokens: " + str(self.game.info_tokens))
        self.fuse_tokens_label.configure(text="Fuse Tokens: " + str(self.game.fuse_tokens))

        for i, hand_label in enumerate(self.player_hand_labels):
            if i != self.game.current_player:
                hand_text = ", ".join(str(card) for card in self.game.players[i].hand)
            else:
                hand_text = "X " * len(self.game.players[i].hand)  # 隐藏当前玩家的手牌
            hand_label.configure(text=hand_text)

    def play_card(self):
        # 获取玩家选择要出的牌
        player_index = self.get_player_index()
        card_index = simpledialog.askinteger("Play Card", "Enter card index to play:", parent=self.window)

        if card_index is not None and 0 <= card_index < len(self.game.players[player_index].hand):
            self.game.play_card(player_index, card_index)
            self.game.next_turn() 
            self.update_current_player_display()
            self.update_display()

    def get_player_index(self):
        # 获取当前回合的玩家索引
        return (self.game.current_player -1 ) % len(self.game.players)
    
    def give_information(self):
        player_index = self.get_player_index()
        other_player_index = simpledialog.askinteger("Give Information", "Enter other player's index:", parent=self.window)
        info_type = simpledialog.askstring("Give Information", "Enter info type (color/number):", parent=self.window)
        info_value = simpledialog.askstring("Give Information", "Enter the color or number:", parent=self.window)

        if other_player_index is not None and info_type is not None and info_value is not None:
            self.game.give_information(player_index, other_player_index, info_type, info_value)
            self.update_display

        self.game.next_turn()
        self.update_current_player_display()
        self.update_display()

    def run(self):
        self.window.mainloop()
    
    def close_game(self):
        self.window.destroy()

if __name__ == "__main__":
    num_players = 3  # 可以根据需要修改
    game = Game(num_players)
    app = HannabiGUI(game)
    app.run()
