from random import choice
class Item:
    
    def __init__(self, canvas):
        
        self._x_pos = None
        self._y_pos = None
        self.set_position()
    
    def set_position(self,maze):
        position = choice(maze.free_tiles)
        self._y_pos, self._x_pos = position
        
        

        
        
       