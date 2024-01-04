from random import choice


class Item:

    def __init__(self, x, y):
        self.x_pos = x
        self.y_pos = y
    def __str__(self):
        return f"Item:({self.x_pos}, {self.y_pos})"


