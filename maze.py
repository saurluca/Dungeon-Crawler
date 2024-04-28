

"""
    Maze generation and manipulation class. Objects in the maze are represented as strings
    This class includes methods for dynamically generating a maze layout,
    managing special tile positions such as hero start and stairs, and
    interacting with tiles (e.g., checking for obstacles, moving entities).
"""

from random import choice
from maze_generator import generate_growing_tree_maze, search_dead_ends, calculate_open_tiles


class Maze:
    def __init__(self, tile_num_x=15, tile_num_y=15, recursive_weight=4, random_weight=1):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight, random_weight)

        self.unused_dead_ends = search_dead_ends(self.grid, tile_num_x, tile_num_y)
        self.free_tiles = calculate_open_tiles(self.grid, self.unused_dead_ends, tile_num_x, tile_num_y)

        self.start_hero_pos = self.get_dead_end()
        self.stair_pos = self.generate_stair_pos()

    def __call__(self, x, y):
        return str(self.grid[x][y])

    def get_tile_num_x(self):
        return self.tile_num_x

    def get_tile_num_y(self):
        return self.tile_num_y

    # approximates a distant position for the stair
    def generate_stair_pos(self):
        # A constant representing how many distant points to consider.
        NUM_DISTANT_POINTS = 3
        hero_x, hero_y = self.start_hero_pos
        distant_points = []

        # Evaluate all unused dead ends for their distance.
        for dead_end_x, dead_end_y in self.unused_dead_ends:
            # calculates the displacement between two points
            distance = abs(dead_end_x - hero_x) + abs(dead_end_y - hero_y)
            distant_points.append((distance, (dead_end_x, dead_end_y)))

        # Sort the distant points by their distance, descending, and take the top points.
        distant_points = sorted(distant_points, reverse=True)[:NUM_DISTANT_POINTS]

        final_point = choice(distant_points)[1]
        self.unused_dead_ends.remove(final_point)
        return final_point

    # open tiles an enemy could walk to
    def get_viable_tiles(self, x, y):
        viable_tiles = []
        # checks in every direction
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            if self.check_obstacle(x + dx, y + dy):
                viable_tiles.append((x + dx, y + dy))
        return viable_tiles

    # returns a tile that nothing is place on yet
    def get_free_tile(self):
        free_tile = choice(self.free_tiles)
        self.free_tiles.remove(free_tile)
        return free_tile

    # returns a dead end in the maze, if there is at least one left
    def get_dead_end(self):
        if len(self.unused_dead_ends) >= 1:
            dead_end = choice(self.unused_dead_ends)
            self.unused_dead_ends.remove(dead_end)
            return dead_end

    def check_dead_end_available(self):
        return len(self.unused_dead_ends) >= 1

    # used to calculate fov, checks if line of sight can go through a tile, i.e. is a wall
    def check_see_through(self, x, y):
        return not self.grid[x][y] == "#"

    def is_wall(self, x, y):
        return self.grid[x][y] == "#"

    # things that are not walk through
    blockers = set("#RGXCZH")

    # check for collision, if either a wall, an enemy, or the hero. Returns True if there is an obstacle
    def check_obstacle(self, x, y):
        return not bool(self.blockers & set(str(self.grid[x][y])))

    def set_tile(self, x, y, thing):
        self.grid[x][y] = thing

    # checks which enemy is fought, used for hero attack
    def check_which_enemy(self, x, y):
        return set(str(self.grid[x][y]))

    # moves an entity from one position in the maze to another
    def move_entity(self, x, y, new_x, new_y):
        self.grid[new_x][new_y] = self.grid[x][y]
        # checks if the entity is standing on something
        if len(str(self.grid[x][y])) > 1:
            self.grid[x][y] = str(self.grid[x][y])[1]
        else:
            self.grid[x][y] = "."

    # prints out the maze and its content as a string, used when fixing bugs theoretical could play this way as well
    def print_out(self):
        for y in range(self.tile_num_y):
            for x in range(self.tile_num_x):
                print(self.grid[x][y], end="")
            print("")
        print("")
