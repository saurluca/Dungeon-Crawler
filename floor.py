"""
Floor handles the main game logic, positions, collision checks, combat, item collection
"""

from random import choice, randint
from maze import Maze
from field_of_view import FieldOfView
from enemy import Enemy

import arcade

POINT_RATIO_TO_OPEN_TILES = 3
FOOD_RATIO_TO_OPEN_TILES = 40
ENEMY_RATIO_TO_OPEN_TILES = 13
ENEMY_GROWTH = 1.05

XP_PER_COIN = 3

FOOD_VALUE = 6.5
POTION_MIN_HEAL = 30
POTION_MAX_HEAL = 60
WEAPON_MIN_DAMAGE = 1
WEAPON_MAX_DAMAGE = 1
ARMOR_MIN_VALUE = 1
ARMOR_MAX_VALUE = 1

ENEMY_TYPES = set("RGXCZ")  # creates a set of possible enemy types
COLLECTABLE_TYPES = "cFAWPD"  # sets collectable types


class Floor:
    def __init__(self, hero, on_floor, difficulty, tile_num_x, tile_num_y, current_score, invincibility_cheat_mode, GENERATE_ENEMIES):
        self.hero = hero
        self.on_floor = on_floor
        self.difficulty = difficulty
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.current_score = current_score
        self.invincibility_on = invincibility_cheat_mode

        # generates the maze
        self.maze = Maze(self.tile_num_x, self.tile_num_y, 3, 1)

        # list of tiles, False if the hero has not uncovered them yet, True otherwise
        self.uncovered_tiles = [[False for _ in range(self.tile_num_y)] for _ in range(self.tile_num_x)]
        self.fov = FieldOfView(self.maze, self.uncovered_tiles)

        # places the hero into the maze
        self.hero.set_position(self.maze.start_hero_pos)
        self.maze.set_tile(*self.hero.get_position(), self.hero)

        # will contain all the enemies
        self.enemy_lst = []
        # list of possible enemies, used to choose which enemy is generated, repetitions used to increase change
        self.possible_enemies = ["R", "R", "R", "R", "G", "G", "G", "X"]

        # does not include dead_ends
        self.num_open_tiles = len(self.maze.free_tiles)

        # calculates num enemies, food, and possible points according to the floor and ratios set, increases enemy ratio per floor by 15% (1,15)
        if GENERATE_ENEMIES:
            self.num_enemies = int((self.num_open_tiles / ENEMY_RATIO_TO_OPEN_TILES) * pow(ENEMY_GROWTH, on_floor) * difficulty)
        else:
            self.num_enemies = 0
        self.points_on_floor = int((self.num_open_tiles // POINT_RATIO_TO_OPEN_TILES) * (self.difficulty / 2))
        self.num_food = self.num_open_tiles // FOOD_RATIO_TO_OPEN_TILES

        # generates all new sprites and possible points for the new level
        self.generate_enemies()
        self.generate_points()
        self.generate_food()
        self.generate_stair()
        self.generate_weapons()
        self.generate_armor()
        self.generate_potions()

        self.completed = False
        self.sprite_to_delete = None

        # sets up the dictionary for the individual collectables, and refers to a specific method
        self.ON_COLLISION_DO = {
            "c": lambda: self.point_collected(),
            "F": lambda: self.food_collected(),
            "A": lambda: self.armor_collected(),
            "W": lambda: self.weapon_collected(),
            "P": lambda: self.potion_collected(),
            "D": lambda: self.stair_found()
        }

        self.pick_up_sound = arcade.load_sound("Sounds/pick_me_up.mp3")
        self.eating_sound = arcade.load_sound("Sounds/eating.mp3")
        self.point_collected_sound = arcade.load_sound("Sounds/point.mp3")
        self.hit_sound = arcade.load_sound("Sounds/hit.mp3")
        self.potion_sound = arcade.load_sound("Sounds/potion.mp3")
        self.level_up_sound = arcade.load_sound("Sounds/level_up.mp3")

    """
    following are methods used to generate enemies and collectables on the floor
    """

    def generate_enemies(self):
        if self.on_floor >= 3:
            self.possible_enemies = self.possible_enemies + ["C", "X"]

        for i in range(self.num_enemies):
            pos = self.maze.get_free_tile()
            while self.check_position_adjacent(*pos, self.hero.pos):  # ensures enemies don't spawn directly next to hero
                pos = self.maze.get_free_tile()
            enemy_level = choice((0, 0, 0, 1, 1, 2)) + self.on_floor + self.difficulty - 1

            enemy_type = choice(self.possible_enemies)

            # on floor 3 and 5 spawn boss, the wizard
            if (self.on_floor == 3 or self.on_floor == 5) and i == self.num_enemies - 1:
                enemy_type = "Z"
                enemy_level = self.difficulty + self.on_floor

            enemy = Enemy(pos, enemy_level, enemy_type)  # sets up new enemy
            self.maze.set_tile(*pos, enemy)
            self.enemy_lst.append(enemy)

    def generate_stair(self):
        pos = self.maze.stair_pos
        self.maze.set_tile(*pos, "D")

    def generate_points(self):
        for i in range(self.points_on_floor):
            pos = self.maze.get_free_tile()
            self.maze.set_tile(*pos, "c")

    def generate_food(self):
        for i in range(self.num_food):
            pos = self.maze.get_free_tile()
            self.maze.set_tile(*pos, "F")

    def generate_items(self, item, count):
        for i in range(count):
            if self.maze.check_dead_end_available():
                pos = self.maze.get_dead_end()
                self.maze.set_tile(*pos, item)

    def generate_weapons(self):
        num_weapons = self.on_floor//3 + 1
        self.generate_items("W", num_weapons)

    def generate_armor(self):
        num_armor = self.on_floor//3 + 1
        self.generate_items("A", num_armor)

    def generate_potions(self):
        num_potions = self.on_floor//2 + randint(1, 3)
        self.generate_items("P", num_potions)

    """
    next come methods to interact with collectables
    """

    def check_for_collectables(self, pos):
        tile = self.maze(*pos)
        return tile in COLLECTABLE_TYPES  # if the tile at that position is in collectable types, will return true

    def execute_item_function(self, pos):
        tile = self.maze(*pos)
        # on_collision executes the corresponding method saved in a dictionary
        self.ON_COLLISION_DO[tile]()
        # removes the special item (collectable?) from the maze and the renderer
        self.maze.set_tile(*pos, ".")
        self.sprite_to_delete = pos

    def point_collected(self):
        # stepping on a point, increases possible_score
        self.current_score[0] += 1
        self.hero.increase_xp(XP_PER_COIN)
        arcade.play_sound(self.point_collected_sound, volume=0.5)

    def food_collected(self):
        # stepping on food increases hero's food bar
        self.hero.eat(FOOD_VALUE)
        arcade.play_sound(self.eating_sound, volume=0.5)

    def weapon_collected(self):
        # stepping on a weapon increases the damage of the hero
        weapon_damage = randint(WEAPON_MIN_DAMAGE, WEAPON_MAX_DAMAGE)
        self.hero.increase_damage(weapon_damage)
        arcade.play_sound(self.pick_up_sound, volume=0.5)

    def armor_collected(self):
        # stepping on armor increases the armor of the hero
        armor_value = randint(ARMOR_MIN_VALUE, ARMOR_MAX_VALUE)
        self.hero.increase_armor(armor_value)
        arcade.play_sound(self.pick_up_sound, volume=0.5)

    def potion_collected(self):
        # stepping on a potion heals the hero
        heal_value = randint(POTION_MIN_HEAL, POTION_MAX_HEAL) + self.on_floor*5
        self.hero.heal(heal_value)
        arcade.play_sound(self.potion_sound, volume=0.5)

    def stair_found(self):
        # stepping on the stair finishes the floor and transport the hero to the next
        self.completed = True

    """
    next come methods to move the hero and enemies and implement combat
    """

    # checks if the hero would collide with an enemy
    def check_collision_with_enemy(self, pos):
        """
        enemy types is a set, meaning it has only unique characters
        the content of the maze at pos is also converted to a set
        the & operation creates a new set of characters that both
        sets contain. bool return False if that set is empty and
        True if it contains any character
        """
        return bool(ENEMY_TYPES & set(self.maze(*pos)))

    # finds a specific enemy for the list of enemies, that corresponds with a certain position
    def get_enemy_from_list(self, pos):
        for enemy in self.enemy_lst:
            if enemy.get_position() == pos:
                return enemy

    # commences the fight, hero and enemy take damage and at the end the hero might get xp
    def hero_attack(self, pos):
        enemy = self.get_enemy_from_list(pos)
        self.hero.attack(enemy)
        arcade.play_sound(self.hit_sound, volume=0.5)

        # if the hero killed the enemy
        if not enemy.is_alive:
            self.hero.increase_xp(enemy.xp_on_kill)

            # if hero has enough xp for level up, level up
            if self.hero.current_xp >= self.hero.xp_to_next_level[self.hero.level]:
                self.hero.level_up()
                arcade.play_sound(self.level_up_sound, volume=0.5)

            # removes the enemy from the maze
            self.maze.set_tile(*pos, enemy.standing_on)

    # can be used to check for items in the immediate vicinity of sprites
    @staticmethod
    def check_position_adjacent(x, y, pos):
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            if (x + dx, y + dy) == pos:
                return x + dx, y + dy

    def move_hero(self, dx, dy):
        # Get the current position of the hero.
        current_x, current_y = self.hero.get_position()

        # Define the order of movement check: diagonal, horizontal, then vertical.
        move_checks = [(dx, dy), (dx, 0), (0, dy)]

        for delta_x, delta_y in move_checks:
            new_pos = (current_x + delta_x, current_y + delta_y)

            # checks if there is an enemy to attack first, second part is that he can not attack on diagonals
            if self.check_collision_with_enemy(new_pos) and (delta_x == 0 or delta_y == 0):
                self.hero_attack(new_pos)
                break

            # otherwise checks for a possible move
            elif self.maze.check_obstacle(*new_pos):
                # checks if for a collectable and then executes the effect
                if self.check_for_collectables(new_pos):
                    self.execute_item_function(new_pos)
                self.hero.set_position(new_pos)
                self.maze.move_entity(current_x, current_y, *new_pos)
                break

    # moves enemies and lets them attack
    def move_enemies(self):
        for enemy in self.enemy_lst:
            if enemy.is_visible:
                pos = enemy.get_position()
                viable_tiles = self.maze.get_viable_tiles(*pos)

                # if the hero was directly adjacent, chase
                if self.check_position_adjacent(*pos, self.hero.last_pos):
                    new_pos = self.hero.last_pos
                    # check if not another monster is already at this position, else waits a turn
                    if self.maze.check_obstacle(*new_pos):
                        enemy.set_position(new_pos)
                        enemy.standing_on = self.maze(*new_pos)
                        self.maze.move_entity(*pos, *new_pos)
                    enemy.attacked = False

                # random movement not enemy.attacked and
                # checks if the list of possible tiles is not empty, meaning no possible place to go to, else does not move
                elif not enemy.attacked and viable_tiles:
                    new_pos = choice(viable_tiles)
                    tmp = self.maze(*new_pos)
                    self.maze.move_entity(*pos, *new_pos)
                    enemy.standing_on = tmp
                    enemy.set_position(new_pos)

                    enemy.attacked = False

    def enemies_attack(self):
        for enemy in self.enemy_lst:
            # if enemy is visible (includes alive), near the hero and invincibility not on, attack
            if enemy.is_visible and self.check_position_adjacent(*enemy.pos, self.hero.pos):
                if not self.invincibility_on:
                    enemy.attack(self.hero)
                enemy.attacked = True

    # sets enemy.is_visible if standing on an uncovered tiles and being alive
    def update_enemy_visibility(self):
        # if enemy on an uncovered tile, set visibility to False, else True
        for enemy in self.enemy_lst:
            x, y = enemy.get_position()
            # if the enemy can not be seen or is dead, set invisible
            enemy.is_visible = self.uncovered_tiles[x][y] and enemy.is_alive

    # calculates the fov and then returns a list of tiles that have not been seen before
    def get_newly_visible_tiles(self):
        return self.fov.calculate_fov(*self.hero.get_position())

    # adds to the list of new tiles, the type in the form of a string, for the render, so the checking and access to maze is handled in floor
    def add_tile_type(self, new_tiles):
        for i in range(len(new_tiles)):
            new_tiles[i] = (new_tiles[i], self.maze(*new_tiles[i]))
        return new_tiles
