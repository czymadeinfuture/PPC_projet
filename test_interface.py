import random


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

    def draw_card(self):
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, hand):
        self.hand = hand
        self.hand_info = [{'color': None, 'number': None} for _ in hand]

    def play_card(self, index):
        return self.hand.pop(index) if index < len(self.hand) else None

    def draw_card(self, card):
        if card:
            self.hand.append(card)
            self.hand_info.append({'color': None, 'number': None})

    def receive_information(self, card_index, info_type, info_value):
        self.hand_info[card_index][info_type] = info_value

    def give_information(self, other_player, info_type, info_value):
        # info_type can be 'color' or 'number'
        for i, card in enumerate(other_player.hand):
            if getattr(card, info_type) == info_value:
                other_player.receive_information(i, info_type, info_value)


class Game:
    def __init__(self, num_players):
        self.deck = Deck(num_players)
        self.players = [Player([self.deck.draw_card() for _ in range(5)]) for _ in range(num_players)]
        self.info_tokens = num_players + 3
        self.fuse_tokens = 3
        self.played_cards = {color: [] for color in ['Red', 'Blue', 'Green', 'Yellow', 'White'][:num_players]}
        self.discard_pile = []
        self.max_info_tokens = num_players + 3
        self.current_player = 0

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        
    def give_information(self, player_index, other_player_index, info_type, info_value):
        if self.info_tokens > 0 and player_index != other_player_index:
            self.players[player_index].give_information(self.players[other_player_index], info_type, info_value)
            self.info_tokens -= 1
        else:
            print("No info tokens left or invalid player index!")

    def play_card(self, player_index, card_index):
        player = self.players[player_index]
        card = player.play_card(card_index)
        if card:
            if self.is_playable(card):
                self.played_cards[card.color].append(card)
                print(f"Card {card} successfully played on the {card.color} pile.")
                if card.number == 5:
                    self.info_tokens = min(self.info_tokens + 1, self.max_info_tokens)
            else:
                self.fuse_tokens -= 1
                self.discard_pile.append(card)
                print(f"Invalid play. Card {card} discarded. Fuse token lost.")
                if self.fuse_tokens == 0:
                    self.end_game(False)
            player.draw_card(self.deck.draw_card())
            self.next_turn()

    def is_playable(self, card):
        return not self.played_cards[card.color] or self.played_cards[card.color][-1].number == card.number - 1

    def add_to_played_cards(self, card):
        self.played_cards[card.color] = card.number

    def run_game(self):
        current_player = 0
        while not self.is_game_over():
            self.display_game_state()
            self.display_other_players_hands(current_player)
            self.handle_player_turn(current_player)
            current_player = (current_player + 1) % len(self.players)

    def display_other_players_hands(self, current_player_index):
        print("\nOther Players' Hands:")
        for i, player in enumerate(self.players):
            if i != current_player_index:
                print(f"Player {i + 1}: {player.hand}")

    def is_game_over(self):
        return self.fuse_tokens <= 0 or self.check_win_condition()

    def display_game_state(self):
        print("\nPlayed Cards:")
        for color, pile in self.played_cards.items():
            print(f"{color} Pile: {pile}")
        print(f"Info Tokens: {self.info_tokens}, Fuse Tokens: {self.fuse_tokens}")


    def handle_player_turn(self, player_index):
        player = self.players[player_index]
        print(f"Player {player_index + 1}'s turn.")
        print(f"Your hand: {player.hand_info}")
        action = input("Choose action: (1) Give information (2) Play card: ")
        if action == '1':
            self.handle_information_action(player_index)
        elif action == '2':
            self.handle_play_card_action(player_index)

    def handle_information_action(self, player_index):
        valid_input = False
        while not valid_input:
            other_player_index = int(input("Choose another player: ")) - 1
            if other_player_index < 0 or other_player_index >= len(self.players) or other_player_index == player_index:
                print("Invalid player index. Please choose again.")
                continue

            info_type = input("Give information on (color/number): ").lower()
            if info_type not in ['color', 'number']:
                print("Invalid information type. Please choose 'color' or 'number'.")
                continue

            info_value = input("Enter the color or number: ")
            if info_type == 'color' and info_value not in ['Red', 'Blue', 'Green', 'Yellow', 'White']:
                print("Invalid color. Please enter a valid color.")
                continue
            elif info_type == 'number' and info_value not in ['1', '2', '3', '4', '5']:
                print("Invalid number. Please enter a valid number.")
                continue

            valid_input = True
            self.give_information(player_index, other_player_index, info_type, info_value)


    def handle_play_card_action(self, player_index):
        card_index = int(input("Choose a card index to play: ")) - 1
        self.play_card(player_index, card_index)


    def check_win_condition(self):
        return all(value == 5 for value in self.played_cards.values())
    

    def calculate_score(self):
        score = 0
        for pile in self.played_cards.values():
            score += sum(card.number for card in pile)
        return score

    def end_game(self, win):
        if win:
            print("Congratulations, you have won the game!")
        else:
            print("Game over. Better luck next time!")
        print(f"Your score: {self.calculate_score()}")
    

if __name__ == "__main__":
    num_players = 3  # 或者从用户输入中获取
    game = Game(num_players)
    game.run_game()
