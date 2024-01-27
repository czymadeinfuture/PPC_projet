'''
    @author: HenriBlacksmith
    @license: CC-BY-NC
'''
# -- imports
from Player import Player
from Card import Card
from numpy.random import randint

# -- class
class Game(object):
    # -- builder
    def __init__(self):
        self.n_tokens = 8
        self.n_red_tokens = 0
        self.active_tokens = self.n_tokens
        self.card_shoe = []
        self.players = {}
        self.recycled_cards = []
        self.played_cards = []
        self.played_card_piles = {}
        
        self.COLORS = ['Blue', 'Red', 'Green', 'Yellow', 'White']
        self.NUMBERS = ['1', '2', '3', '4', '5']
        self.AMOUNTS = [3, 2, 2, 2, 1]
        
    # -- getters
    
    # -- public methods
    def generate_played_piles(self):
        '''
            @summary: Generates a dictionary containing the number of the cards at the top of the pile for each color
        '''
        for color in self.COLORS :
            self.played_card_piles[color] = 0
            
    def burn_token(self):
        '''
            @summary: Burns one blue token when a player gives a hint to another player
            @warning: The Game Over implemented has to be improved
        '''
        self.active_tokens -= 1
        if self.active_tokens < 0:
            print('Game Over')
    
    def red_token(self):
        '''
            @summary: Adds a red token when a mistake is detected
        '''
        self.n_red_tokens += 1
        if self.n_red_tokens > 3:
            print('Game Over')
    
    def generate_card_shoe(self):
        '''
            @summary: Generates a random card shoe 
        '''
        ordered_card_shoe = self.__generate_ordered_shoe()
        card_shoe = []
        n_cards = len(ordered_card_shoe)
        for i in range(n_cards):
            n_cards_remaining = n_cards - i
            index_card_to_pile = randint(n_cards_remaining)
            card_shoe.append(ordered_card_shoe[index_card_to_pile])
            del ordered_card_shoe[index_card_to_pile]
        self.card_shoe = card_shoe
            
    
    def display_shoe(self):
        '''
            @summary: Displays all the cards remaining in the card shoe
        '''
        for card in self.card_shoe:
            card.display_card()
    
    def get_card(self):
        '''
            @summary: Extracts a card from the card shoe when it is possible
            @return: Returns a card or None
        '''
        if len(self.card_shoe) > 0:
            card = self.card_shoe[-1]
            del self.card_shoe[-1]
            return card
        else :
            print('The card shoe is empty')
            return None
        
    def distribute_card_hands(self):
        for i in range(5):
            for player_name in self.players.keys():
                self.players[player_name].take_card(self.get_card())
    
    def add_player(self, name): 
        self.players[name] = Player(name)
        
    def recycle_card(self, player_name, index):
        '''
            @param player_name: Name of the player who recycles a card 
            @param index: Position of the card in player's hand 
            @summary: Puts a card into the shoe of recycled cards an deletes the card from player's hand
        '''
        card = self.players[player_name].recycle_card(index)
        self.recycled_cards.append(card)
        
    def give_card(self, player_name):
        '''
            @param player_name : Name of the player who needs a card
            @summary: Gives a card to the player
        '''
        self.players[player_name].take_card(self.get_card())
    
    def play_card(self, player_name, index):
        '''
            @param player_name: Name of the player who plays a cards
            @param index : Position of the card in player's hand 
            @summary: Manages the different outcomes in the case where a player plays one of his cards
        '''
        card = self.players[player_name].play_card(index)
        card_color = card.get_color()
        card_number = card.get_number()
        print(player_name, 'plays the', card_number, card_color)
        for played_card in self.played_cards :
            if played_card == card :
                self.red_token()
                print('This card has already been played - you get one red token')
                self.recycle_card(player_name, index)
                return None
        if card_number == self.played_card_piles[card_color] + 1:
            self.played_card_piles[card_color] += 1
            self.played_cards.append(card)
            print('Well done')
            return None
        else :
            self.red_token()
            print('You can\'t play this card - you get one red token')
            self.recycled_cards.append(card)
            return None
        
    def show_hands(self):
        '''
            @summary: Shows the hand of every player
        '''
        for player_name in self.players.keys():
            self.players[player_name].display_hand()
    
    # -- private methods
    def __generate_ordered_shoe(self):
        '''
            @summary: Generates an ordered card shoe
        '''
        ordered_shoe = []
        for color in self.COLORS:
            for i,number in enumerate(self.NUMBERS):
                for k in range(self.AMOUNTS[i]):
                    current_card = Card(color, number, k)
                    ordered_shoe.append(current_card)
        return ordered_shoe
    