"""
Enemy is a subclass of Character that represents different enemy types in the game, each with unique properties and scaling stats by level.

"""

from character import Character

BASE_HP = 14  # Base hp of all enemy types
BASE_DAMAGE = 3  # base damage of all enemy types
BASE_ARMOR = 1  # Base armor of all enemy types
BASE_XP = 13    # Base xp on kill of all enemy types

# additional hp per level
HP_SCALING = 2
# additional damage per level
DAMAGE_SCALING = 1
# additional armor per level
ARMOR_SCALING = 1.25
# additional xp per level
XP_SCALING = 3


class Enemy(Character):
    def __init__(self, pos, level=1, enemy_type="R"):
        super().__init__(pos, 1, 1, 1, level)
        self.enemy_type = enemy_type

        # all of this is scaling hp, damage, armor and the amount of xp the enemy grants when killed
        # rat, basic bitch
        if enemy_type == "R":
            self.hp = int(BASE_HP + HP_SCALING * level)
            self.damage = int(BASE_DAMAGE + DAMAGE_SCALING * level)
            self.armor = 0
            self.xp_on_kill = int(BASE_XP + XP_SCALING * level)

        # ghost, high damage, little better than rat
        elif enemy_type == "G":
            self.hp = int(1.2 * (BASE_HP + HP_SCALING * level))
            self.damage = int(1.5 * (BASE_DAMAGE + DAMAGE_SCALING * level))
            self.armor = 0
            self.xp_on_kill = int(1.5 * (BASE_XP + XP_SCALING * level))

        # spider, higher damage, little armor, less HP
        elif enemy_type == "X":
            self.hp = int(0.5 * (BASE_HP + HP_SCALING * level))
            self.damage = int(2 * (BASE_DAMAGE + DAMAGE_SCALING * level))
            self.armor = int(1 * (BASE_ARMOR + ARMOR_SCALING * level))
            self.xp_on_kill = int(2.5 * (BASE_XP + XP_SCALING * level))

        # Cyclops, high damage, lots of armor, lots of HP
        elif enemy_type == "C":
            self.hp = int(0.8 * (BASE_HP + HP_SCALING * level))
            self.damage = int(1.4 * (BASE_DAMAGE + DAMAGE_SCALING * level))
            self.armor = int(1.5 * (BASE_ARMOR + ARMOR_SCALING * level))
            self.xp_on_kill = int(3 * (BASE_XP + XP_SCALING * level))

        # wiZard, the BOSS
        elif enemy_type == "Z":
            self.hp = int(2.5 * (BASE_HP + HP_SCALING * level))
            self.damage = int(1.5 * (BASE_DAMAGE + DAMAGE_SCALING * level))
            self.armor = int(1 * (BASE_ARMOR + ARMOR_SCALING * level))
            self.xp_on_kill = int(7 * (BASE_XP + XP_SCALING * level))

        self.standing_on = "."

    # this function defines how the enemy is represented as a string
    def __str__(self):
        # if standing on something enemy is represented as it's type and the symbol of the thing he is standing on
        if self.standing_on != ".":
            return self.enemy_type + self.standing_on
        # if he is not standing on something, i.e. "." an empty tile, does not show
        else:
            return self.enemy_type
