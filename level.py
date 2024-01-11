from random import choice
from maze import Maze
from field_of_view import FieldOfView
from weapon import Weapon
from enemy import Enemy

BASE_HP_LOSS = 0.01


# TODO rework pos and x and y


class Level:
    def __init__(self, hero, tile_num_x, tile_num_y, num_coins, num_coins_collected, num_food, num_enemies):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.num_coins = num_coins
        self.num_coins_collected = num_coins_collected
        self.num_enemies = num_enemies
        self.num_food = num_food
        self.item_list = []

        self.num_items = 0

        self.hero = hero
        self.maze = Maze(self.tile_num_x, self.tile_num_y, 3, 1)

        self.enemy_lst = []

        self.hero.set_position(self.maze.start_hero_pos)
        self.maze.set_tile(*self.hero.get_position(), self.hero)

        self.uncovered_tiles = [[False for _ in range(self.tile_num_y)] for _ in range(self.tile_num_x)]
        self.fov = FieldOfView(self.maze, self.uncovered_tiles)

        # has to be generated first
        self.generate_enemies()

        self.generate_coins()
        self.new_coin_collected = False

        self.generate_food()
        self.new_food_collected = False

        self.generate_items()
        self.generate_stair()

        self.completed = False

    def generate_enemies(self):
        for i in range(self.num_enemies):
            pos = self.maze.get_free_tile()
            enemy = Enemy(pos)
            self.maze.set_tile(*pos, enemy)
            self.enemy_lst.append(enemy)

    def generate_coins(self):
        for i in range(self.num_coins):
            pos = self.maze.get_free_tile()
            self.maze.set_tile(*pos, "c")

    def generate_stair(self):
        pos = self.maze.generate_stair_pos2()
        self.maze.set_tile(*pos, "S")

    def generate_food(self):
        for i in range(self.num_food):
            pos = self.maze.get_free_tile()
            self.maze.set_tile(*pos, "F")

    def generate_items(self):
        for i in range(self.num_items):
            pos = self.maze.get_dead_end()
            item = Weapon(pos, 10)
            self.maze.set_tile(*pos, item)
            self.item_list.append(item)

    def move_hero(self, dx, dy):
        cx, cy = self.hero.get_position()
        # first checks for both vertical and horizontal input
        if self.maze.check_obstacle(cx + dx, cy + dy):
            self.check_collision_for_hero((cx + dx, cy + dy))
            self.maze.move_entity(cx, cy, cx + dx, cy + dy)
            self.hero.set_position((cx + dx, cy + dy))

        # if not possible, check horizontal, then vertical
        elif self.maze.check_obstacle(cx + dx, cy):
            self.check_collision_for_hero((cx + dx, cy))
            self.maze.move_entity(cx, cy, cx + dx, cy)
            self.hero.set_position((cx + dx, cy))
        elif self.maze.check_obstacle(cx, cy + dy):
            self.check_collision_for_hero((cx, cy + dy))
            self.maze.move_entity(cx, cy, cx, cy + dy)
            self.hero.set_position((cx, cy + dy))

    def move_enemies(self):
        for enemy in self.enemy_lst:
            pos = enemy.get_position()
            viable_tiles = self.maze.get_viable_tiles(*pos)
            # checks if the list of possible tiles is not empty, else does not move
            if viable_tiles:
                new_pos = choice(viable_tiles)
                enemy.set_position(new_pos)
                enemy.standing_on = self.maze(*new_pos)
                self.maze.move_entity(*pos, *new_pos)

    def update_enemy_visibility(self):
        # if enemy on an uncovered tile, set visibility to False, else True
        for enemy in self.enemy_lst:
            x, y = enemy.get_position()
            enemy.visible = self.uncovered_tiles[x][y]

    # add item and other special thing collision here
    def check_collision_for_hero(self, pos):
        # if collided, do action
        tile = self.maze(*pos)
        # does not check walls and empty tiles
        if tile != "." and tile != "#":
            if tile == "c":
                self.num_coins_collected[0] += 1
                self.new_coin_collected = True
            elif tile == "F":
                self.hero.heal(5)
                self.new_food_collected = True
            elif tile == "I":
                self.update_items(self.hero.get_position())
            elif tile == "S":
                self.completed = True
            # remove thing, set maze to empty tile
            self.maze.set_tile(*pos, ".")

    def update_items(self, pos):
        for item in self.item_list:
            if item.pos == pos:
                item.collected(self.hero)

    def check_completed(self):
        return self.completed

    def check_coin_collected(self):
        collected = self.new_coin_collected
        self.new_coin_collected = False
        return collected

    def check_food_collected(self):
        collected = self.new_food_collected
        self.new_food_collected = False
        return collected

    # calculates the fov and then returns a list of tiles that have not been seen before
    def get_newly_visible_tiles(self):
        return self.fov.calculate_fov(*self.hero.get_position())

    # adds to the list of new tiles, the type, so the checking and access to maze is handled in level
    def add_tile_type(self, new_tiles):
        for i in range(len(new_tiles)):
            new_tiles[i] = (new_tiles[i], self.maze(*new_tiles[i]))
        return new_tiles
