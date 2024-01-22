"""
   A Hero class in a game, derived from the Character base class. This class adds specific attributes
   for max food points, an XP system for leveling up, and methods to handle damage, healing,
   eating. Leveling increases stats. It also includes methods for reducing HP and food points
   over time.
"""

from character import Character

BASE_HP_LOSS = 0.05
FOOD_POINT_LOSS = 0.03
# Percentage of food_points necessary to still regenerate hp
FOOD_HEAL_THRESHOLD = 0.6
FOOD_REGEN_COST = 0.1
BASE_XP_NEEDED = 100
XP_GROWTH_RATE = 1.4

DAMAGE_INCREASE = 1
HP_INCREASE = 10
MAX_POSSIBLE_HP = 300

# for Jeelka
ONE_PIECE = 1


class Hero(Character):
    def __init__(self, hp, damage, armor, level):
        super().__init__((1, 1), hp, damage, armor, level)
        self.max_food_points = 10
        self.food_points = self.max_food_points

        # default assignment
        self.last_pos = (0, 0)
        self.current_xp = 0

        # list at index tracks xp need for level up
        self.xp_to_next_level = [0, BASE_XP_NEEDED]

    # represents the Hero as a String as "H
    def __str__(self):
        return "H"

    # sets the position
    def set_position(self, pos):
        self.last_pos = self.pos
        self.pos = pos

    # increases damage
    def increase_damage(self, value):
        self.damage += value

    # increases armor
    def increase_armor(self, value):
        self.armor += value

    # increases xp
    def increase_xp(self, value):
        self.current_xp += value

    # exponential growth function of xp need for next level
    def calculate_xp_for_next_level(self):
        return int(BASE_XP_NEEDED * (XP_GROWTH_RATE ** self.level))

    def level_up(self):
        # levels the hero up, increasing his damage, level, max_hp and heals him
        self.level += ONE_PIECE
        self.damage += DAMAGE_INCREASE
        # ensures the hero does not have more hp than is displayable
        self.max_hp = min(self.max_hp + HP_INCREASE, MAX_POSSIBLE_HP)
        # heals the hero
        self.hp = self.max_hp

        # calculates the xp to next level
        self.xp_to_next_level.append(self.xp_to_next_level[-1] + self.calculate_xp_for_next_level())

    # heals hp, if more than max hp, sets hp to max hp
    def heal(self, value):
        self.hp = min(self.hp + value, self.max_hp)

    # restores food points, if more than max food points, sets food points to max food points
    def eat(self, value):
        self.food_points = min(self.food_points + value, self.max_food_points)

    # makes the hero constantly take small amounts of damage as time goes by unless he keeps his food bar up
    def hp_decay(self, levels_played):
        # Base + scaling
        hp_loss = BASE_HP_LOSS * (1 + levels_played * 0.5)
        self.take_damage(hp_loss, with_armor=False)
        self.took_damage = not self.took_damage_last_tick

    # reduces current food points
    def food_point_loss(self):
        self.food_points = self.food_points - FOOD_POINT_LOSS
        # Use max to prevent food points from going below zero
        if self.food_points < 0:
            self.food_points = 0

    def food_decay(self, on_floor, invincibility):
        # if no more food, hero loses hp
        if self.food_points > 0 and not invincibility:
            self.food_point_loss()
        elif not invincibility:
            self.hp_decay(on_floor)

    # food helps hero heal, regenerates food bar and prevents hp decay
    def food_heal(self):
        if self.max_food_points * FOOD_HEAL_THRESHOLD <= self.food_points and self.hp != self.max_hp:
            self.food_points -= FOOD_REGEN_COST
            self.hp = min(self.max_hp, self.hp + ONE_PIECE)
