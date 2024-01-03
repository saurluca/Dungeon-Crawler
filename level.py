from maze import Maze
from field_of_view import FieldOfView


class Level:
    def __init__(self, hero, tile_num_x, tile_num_y, num_coins):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.num_coins = num_coins

        self.hero = hero
        self.maze = Maze(self.tile_num_x, self.tile_num_y, 3, 1)

        self.hero.set_position(*self.maze.get_start_hero_pos())
        self.maze.set_tile(*self.hero.get_position(), self.hero)

        self.fov = FieldOfView(self.maze)

        self.new_coin_collected = False
        self.generate_coins()

        self.generate_stair()

        self.completed = False

    # TODO keep it here or do item managing/generation class?
    def generate_coins(self):
        for i in range(self.num_coins):
            x, y = self.maze.get_free_tile()
            self.maze.set_tile(x, y, "c")

    def generate_stair(self):
        x, y = self.maze.generate_stair_pos2()
        self.maze.set_tile(x, y, "S")

    def move_player(self, dx, dy):
        cx, cy = self.hero.get_position()

        if self.maze.check_obstacle(cx + dx, cy + dy):
            self.check_special_collision(cx + dx, cy + dy)
            self.hero.set_position(cx + dx, cy + dy)
        elif self.maze.check_obstacle(cx + dx, cy):
            self.check_special_collision(cx + dx, cy)
            self.hero.set_x(cx + dx)
        elif self.maze.check_obstacle(cx, cy + dy):
            self.check_special_collision(cx, cy + dy)
            self.hero.set_y(cy + dy)

    # add item and other special thing collision here
    def check_special_collision(self, x, y):
        tile = self.maze(x, y)
        self.new_coin_collected = False
        if tile != ".":
            if tile == "c":
                self.new_coin_collected = True
                self.maze.set_tile(x, y, ".")
            elif tile == "S":
                print("Oh boy, here we go again")
                self.completed = True

    def check_completed(self):
        return self.completed

    def check_coin_collected(self):
        return self.new_coin_collected

    def get_newly_visible_tiles(self):
        return self.fov.calculate_fov(*self.hero.get_position())
