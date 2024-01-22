"""
Character class is the parent class of Hero and Enemy class and handles position, hp, damage, armor and level
"""


class Character:
    def __init__(self, pos, hp, damage, armor, level):
        self.pos = pos
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.armor = armor
        self.level = level

        self.is_alive = True
        self.is_visible = False

        # Flags for damage tracking (used in rendering)
        self.took_damage = False
        self.took_damage_last_tick = False

    def get_position(self):
        return self.pos

    def set_position(self, pos):
        self.pos = pos

    # calculates damage reduced by armor
    def take_damage(self, damage, with_armor=True):
        if with_armor:
            actual_damage = max(damage - self.armor, 1)
            self.hp -= max(actual_damage, 0)
        else:
            self.hp -= max(damage, 0)

        # this is necessary for the renderer class in order to determine when the character is painted red or not
        if self.took_damage:
            self.took_damage_last_tick = True
        self.took_damage = True

        # if hp drops below zero, removes the character from the game
        if self.hp <= 0:
            self.is_alive = False  # prevents character from taking actions, for example in move functions
            self.is_visible = False  # makes the sprite invisible
            self.pos = (0, 0)  # moves the character out of the accessible matrix

    # allows character to attack another character
    def attack(self, target):
        target.take_damage(self.damage)
