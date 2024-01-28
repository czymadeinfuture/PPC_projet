import random

# 定义卡牌类
class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __repr__(self):
        return f"{self.color}{self.number}"

# 定义卡牌堆类
class Deck:
    def __init__(self, num_players):
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'White'][:num_players]
        self.cards = [Card(color, number) for color in colors for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None

# 定义玩家类
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

    def receive_information(self, info_type, info_value):
        for card_info, card in zip(self.hand_info, self.hand):
            if getattr(card, info_type) == info_value:
                card_info[info_type] = info_value

# 定义游戏类
class Game:
    def __init__(self, num_players):
        self.deck = Deck(num_players)
        self.players = [Player([self.deck.deal_card() for _ in range(5)]) for _ in range(num_players)]
        self.info_tokens = num_players + 3
        self.fuse_tokens = 3
        self.played_cards = {color: [] for color in ['Red', 'Blue', 'Green', 'Yellow', 'White'][:num_players]}
        self.discard_pile = []
        self.max_info_tokens = num_players + 3

    def play_card(self, player_index, card_index):
        player = self.players[player_index]
        card = player.play_card(card_index)
        if card and self.is_playable(card):
            self.played_cards[card.color].append(card)
            if card.number == 5:
                self.info_tokens = min(self.info_tokens + 1, self.max_info_tokens)
        else:
            self.fuse_tokens -= 1
            self.discard_pile.append(card)
        player.draw_card(self.deck.deal_card())

    def give_information(self, player_index, other_player_index, info_type, info_value):
        if self.info_tokens > 0 and player_index != other_player_index:
            self.players[other_player_index].receive_information(info_type, info_value)
            self.info_tokens -= 1

    def is_playable(self, card):
        return (not self.played_cards[card.color] and card.number == 1) or \
               (self.played_cards[card.color] and card.number == self.played_cards[card.color][-1].number + 1)

    def get_game_state(self):
        return {
            'played_cards': self.played_cards,
            'info_tokens': self.info_tokens,
            'fuse_tokens': self.fuse_tokens,
            'discard_pile': self.discard_pile
        }

    def is_game_over(self):
        return self.fuse_tokens <= 0 or all(len(pile) == 5 for pile in self.played_cards.values())

    def check_win_condition(self):
        return all(len(pile) == 5 for pile in self.played_cards.values())


