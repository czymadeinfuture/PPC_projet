'''
    @author: HenriBlacksmith
    @license: CC-BY-NC
'''
# -- imports
from Card import Card

# -- class
class Player(object):
    # -- builder
    def __init__(self, name):
        '''
            @param name: Name of the player to build 
        '''
        self.player_name = name
        self.card_hand = []
    
    # -- getters
    def get_name(self):
        return self.player_name
        
    # -- public methods
    def take_card(self, card):
        '''
            @summary: Adds a card in player's hand
        '''
        self.card_hand.append(card)
    
    def display_hand(self):
        '''
            @summary: Prints the name of the player and the list of all his cards
        '''
        print self.get_name()
        for card in self.card_hand:
            print card.display_card()     
            
    def recycle_card(self, index):
        '''
            @summary: Deletes a card from player's hand
            @return: Returns the deleted card
        '''
        card = self.card_hand[index]
        del self.card_hand[index]
        return card
    
    def play_card(self, index):
        '''
            @summary: Same content as recycle_card method
            @return: Returns the played card
        '''
        card = self.card_hand[index]
        del self.card_hand[index]
        return card