from random import choice, randint
from maze_generator import MazeGenerator


class Maze(MazeGenerator):
    def __init__(self, tile_num_x=9, tile_num_y=9, recursive_weight=4, random_weight=1):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = super().generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight, random_weight)

        self.dead_ends = super().search_dead_ends(tile_num_x, tile_num_y, self.grid)
        self.unused_dead_ends = self.dead_ends

        self.free_tiles = []
        self.set_free_tiles()

        self.start_hero_pos = self.get_dead_end()
        # self.stair_pos = self.generate_stair_pos()
        # self.generate_stair()

    def __call__(self, x, y):
        return str(self.grid[x][y])

    def set_free_tiles(self):
        for x in range(self.tile_num_y):
            for y in range(self.tile_num_x):
                if self.grid[x][y] == "." and (x, y) not in self.dead_ends:
                    self.free_tiles.append((x, y))

    # TODO for generation of things, not complete random, eg not in hero view range
    # TODO refactor to get_free_tile
    def get_a_free_tile(self):
        free_tile = choice(self.free_tiles)
        self.free_tiles.remove(free_tile)
        return free_tile

    def get_dead_end(self):
        dead_end = choice(self.unused_dead_ends)
        self.unused_dead_ends.remove(dead_end)
        return dead_end

    def set_tile(self, x, y, thing):
        self.grid[x][y] = thing

    # currently only checking for walls
    def check_obstacle(self, x, y):
        return not self.grid[x][y] == "#"

    def get_start_hero_pos(self):
        return self.start_hero_pos

    # TODO should not be in maze
    def generate_stair(self):
        # x, y = self.get_dead_end()
        # print(x, y)
        x, y = self.stair_pos
        self.grid[x][y] = "S"

    def print_out(self):
        super().print_out(self.grid)

    # approximation
    def generate_stair_pos(self):
        longest = [(0, (0, 0)) for _ in range(6)]
        i = 0
        x1, y1 = self.start_hero_pos
        for x2, y2 in self.unused_dead_ends:
            distance = abs(x2 - x1) + abs(y2 - y1)
            minimum = (min(self.tile_num_x, self.tile_num_y) - 3) // 2
            if distance > minimum and distance > longest[i][0]:
                longest[i] = (distance, (x2, y2))
                i = (i + 1) % 6

        return choice(longest)[1]

    # TODO fuck you break
    def generate_stair_pos2(self):
        long_len = 4
        distant_points = [(0, (0, 0)) for _ in range(long_len)]
        x1, y1 = self.start_hero_pos

        for x2, y2 in self.unused_dead_ends:
            distance = abs(x2 - x1) + abs(y2 - y1)
            minimum = (min(self.tile_num_x, self.tile_num_y)) // 2
            if distance > minimum and distance > distant_points[-1][0]:
                for i in range(long_len):
                    if distance > distant_points[i][0]:
                        distant_points[i] = (distance, (x2, y2))
                        break

        while True:
            a = choice(distant_points)
            if a[0] != 0:
                return distant_points

    def generate_stair_pos3(self):
        """using the unused_dead_ends list this method returns an object of that list calculating the distances between the
        dead_end and the Hero position increasing the chance of more distant dead_ends being chosen
        """
        dead_ends = self.unused_dead_ends
        # print(dead_ends)
        list_distance = []
        distances = []
        x1, y1 = self.start_hero_pos
        for i in range(0, len(dead_ends)):
            x2, y2 = dead_ends[i]
            distances.append(abs(x2 - x1) + abs(y2))
            list_distance.append(100 * (abs(x2 - x1) + abs(y2 - y1)))
            # print(list_distance)
            if i > 0:
                list_distance[i] += list_distance[i - 1]

        a = randint(0, list_distance[-1])
        # print(list_distance)
        # print(distances)
        # print(f"a: {a} list_distance: {list_distance[-1]}")
        # print(x1, y1)
        for i in range(len(list_distance)):
            if a <= list_distance[i]:
                # return dead_ends[i]
                return distances[i]

    def move_object_by(self, x, y, x_direction, y_direction):
        self.grid[x + x_direction][y + y_direction] = self.grid[x][y]
        self.grid[x][y] = "."


def test1():
    average = 0
    n_times = 1000
    for i in range(n_times):
        maze = Maze(15, 15)
        average += maze.generate_stair_pos3()
    print(average / n_times)


def test2():
    for i in range(100):
        maze = Maze(15, 15)
        # maze.print_out()
        # print("-----")
        possible_pos = maze.generate_stair_pos2()
        for pos in possible_pos:
            if pos[0] > 0:
                print(f"{pos[0]}, ", end="")
        print("")


def test3():
    average = 0
    looser = 0
    n_times = 1000
    for i in range(n_times):
        maze = Maze(15, 15)
        c = choice(maze.generate_stair_pos2())[0]
        if c == 0:
            looser += 1
        average += c
    print(average / n_times)
    print(looser)


if __name__ == '__main__':
    test3()
