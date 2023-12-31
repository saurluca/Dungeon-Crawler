class Character:

    def __init__(self, x, y, hp, damage, ):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.damage = damage

    def get_hp(self):
        return self.hp
    def get_max_hp(self):
        return self.max_hp

    def get_damage(self):
        return self.damage

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

