from character import Character


class Hero(Character):
    def __init__(self, x, y, hp=20, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "H"

    def get_x(self):
        return self.x

    def set_x(self, new_x):
        self.x = new_x

    def get_y(self):
        return self.y

    def set_y(self, new_y):
        self.y = new_y

    def get_position(self):
        return self.x, self.y

    def set_position(self, new_x, new_y):
        self.x, self.y = new_x, new_y
