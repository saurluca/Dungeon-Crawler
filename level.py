from random import choice
from maze import Maze
from field_of_view import FieldOfView
from item import Item
from weapon import Weapon
from enemy import Enemy
from food import Food

BASE_HP_LOSS = 0.01


class Level:
    def __init__(self, hero, tile_num_x, tile_num_y, num_coins, num_coins_collected, num_food, num_enemies, enemies_lst):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.num_coins = num_coins
        self.num_coins_collected = num_coins_collected
        self.num_enemies = num_enemies
        self.num_food = num_food
        self.item_list = []

        self.hero = hero
        self.maze = Maze(self.tile_num_x, self.tile_num_y, 3, 1)

        self.enemies_lst = enemies_lst

        self.hero.set_position(*self.maze.get_start_hero_pos())
        self.maze.set_tile(*self.hero.get_position(), self.hero)

        self.fov = FieldOfView(self.maze)

        # TODO possible to simplify further, play sound in level?
        self.generate_coins()
        self.new_coin_collected = False

        self.generate_food()
        self.new_food_collected = False

        self.generate_items()

        self.generate_stair()
        self.generate_enemies()

        self.completed = False

    # TODO keep it here or do item managing/generation class?
    def generate_coins(self):
        for i in range(self.num_coins):
            x, y = self.maze.get_free_tile()
            self.maze.set_tile(x, y, "c")

    def generate_stair(self):
        x, y = self.maze.generate_stair_pos2()
        self.maze.set_tile(x, y, "S")

    # TODO Item generation for different Items
    def generate_food(self):
        for i in range(self.num_food):
            x, y = self.maze.get_free_tile()
            self.maze.set_tile(x, y, "F")

    def generate_items(self):
        x, y = self.maze.get_free_tile()
        self.maze.set_tile(x, y, "I")
        self.item_list.append(Weapon(x, y, 10))

    # TODO should enemies be saved in maze?
    def generate_enemies(self):
        for i in range(self.num_enemies):
            pos = self.maze.get_free_tile()
            enemy = Enemy(*pos)
            self.maze.set_tile(*pos, enemy)
            self.enemies_lst.append(enemy)

    def move_hero(self, dx, dy):
        cx, cy = self.hero.get_position()
        # first checks for both vertical and horizontal input
        if self.maze.check_obstacle(cx + dx, cy + dy):
            self.check_special_collision(cx + dx, cy + dy)
            self.maze.move_tile(cx, cy, cx + dx, cy + dy)
            self.hero.set_position(cx + dx, cy + dy)

        # if not possible, check horizontal, then vertical
        elif self.maze.check_obstacle(cx + dx, cy):
            self.check_special_collision(cx + dx, cy)
            self.maze.move_tile(cx, cy, cx + dx, cy)
            self.hero.set_x(cx + dx)
        elif self.maze.check_obstacle(cx, cy + dy):
            self.check_special_collision(cx, cy + dy)
            self.maze.move_tile(cx, cy, cx, cy + dy)
            self.hero.set_y(cy + dy)

    def move_enemies(self):
        for enemy in self.enemies_lst:
            pos = enemy.get_position()
            next_pos = choice(self.maze.get_viable_tiles(*pos))
            enemy.set_position(*next_pos)
            self.maze.move_tile(*pos, *next_pos)

    # add item and other special thing collision here
    def check_special_collision(self, x, y):
        # if collided, do action
        tile = self.maze(x, y)
        # does not check walls and empty tiles
        if tile != "." and tile != "#":
            if tile == "c":
                self.num_coins_collected[0] += 1
                self.new_coin_collected = True
            elif tile == "F":
                self.update_food()
                self.new_food_collected = True
            elif tile == "I":
                self.update_items(self.hero.x, self.hero.y)
            elif tile == "S":
                self.completed = True
            # remove thing, set maze to empty tile
            self.maze.set_tile(x, y, ".")

    def update_items(self, x, y):
        for item in self.item_list:
            if item.x_pos == x and item.y_pos == y:
                item.collected(self.hero)

    def update_food(self):
        food = Food(1)
        food.collected(self.hero)

    def reset_collected_status(self):
        self.new_coin_collected = False

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

    # TODO, two liner, with in "string"
    # adds to the list of new tiles, the type, so the checking and access to maze is handled in level
    def add_tile_type(self, new_tiles):
        for i in range(len(new_tiles)):
            new_tiles[i] = (new_tiles[i], self.maze(*new_tiles[i]))
        return new_tiles
