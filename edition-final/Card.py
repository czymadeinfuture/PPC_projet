'''
    @author: HenriBlacksmith
    @copyright: CC-BY-NC
'''
# -- class
class Card(object):
    # -- builder
    def __init__(self, color, number, id):
        self.__color = color # Card color
        self.__number = number # Card number
        self.__id = id
    
    # -- getters
    def get_color(self):
        return self.__color
    
    def get_number(self):
        return self.__number
    
    def get_id(self):
        return self.__id
    
    # -- public methods
    def display_card(self):
        '''
            @return: Returns a string describing the card attributes
        '''
        return 'Color = ' + self.get_color() + ' Number = ' + self.get_number()