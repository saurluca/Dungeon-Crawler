class Character:

    def __init__(self, pos, hp, damage):
        self.pos = pos
        self.hp = hp
        self.max_hp = hp
        self.damage = damage

    def get_hp(self):
        return self.hp

    def get_max_hp(self):
        return self.max_hp

    def get_damage(self):
        return self.damage

    def get_position(self):
        return self.pos

    def set_position(self, pos):
        self.pos = pos
