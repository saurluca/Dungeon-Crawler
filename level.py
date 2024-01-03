from maze import Maze
from field_of_view import FieldOfView

NUM_COINS = 20
VIEW_RANGE = 3


# TODO put generation into level class
class Level:
    def __init__(self, hero, tile_num_x, tile_num_y):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.hero = hero

        self.maze = None

        self.fov = None

        self.coins_collected = 0

        self.set_up()

    # TODO either use set_up function, then no new level object, or put in init
    def set_up(self):
        self.maze = Maze(self.tile_num_x, self.tile_num_y, 3, 1)

        self.fov = FieldOfView(self.maze, VIEW_RANGE)

        # puts the hero on his starting tile in the new maze
        self.hero.set_position(*self.maze.get_start_hero_pos())
        self.maze.set_tile(*self.hero.get_position(), self.hero)

        self.generate_coins()

    # TODO keep it here or do item managing class?
    def generate_coins(self):
        for i in range(NUM_COINS):
            x, y = self.maze.get_free_tile()
            self.maze.set_tile(x, y, "c")

    def move_player(self, dx, dy):
        cx, cy = self.hero.get_position()

        if self.maze.check_obstacle(cx + dx, cy + dy):
            self.hero.set_position(cx + dx, cy + dy)
        elif self.maze.check_obstacle(cx + dx, cy):
            self.hero.set_x(cx + dx)
        elif self.maze.check_obstacle(cx, cy + dy):
            self.hero.set_y(cy + dy)

    # TODO temporally moved to main
    # add item and other special thing collision here
    # def check_special_collision(self):
    #     cx, cy = self.hero.get_position()
    #     tile = self.maze(cx, cy)
    #     if tile != ".":
    #         if tile == "c":
    #             self.coins_collected += 1
    #             return "c"
    #         elif tile == "S":
    #             print("Oh boy, here we go again")
    #             # self.set_up()

    def get_coins_collected(self):
        return self.coins_collected

    def get_newly_visible_tiles(self):
        return self.fov.calculate_fov(*self.hero.get_position())
