'''
    Hanabi\main.py
    @author: HenriBlacksmith
'''
# -- imports
from Game import Game
'''
Tasks :
- Mix the card pile
- Provide every player with five cards
- 
'''
game = Game()
# Initializes the game
game.generate_card_shoe()
game.generate_played_piles()
game.add_player('Henry')
game.add_player('Joe')
game.distribute_card_hands()

# Game Workflow
game.play_card('Joe', 2)
game.give_card('Joe')
game.recycle_card('Henry', 2)
game.give_card('Henry')