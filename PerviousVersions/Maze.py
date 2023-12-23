from random import randint, choice
from algoviz.svg import SVGView, Rect, Circle
from time import time


class Maze:
    def __init__(self, tile_num_x=12, tile_num_y=12):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        self.grid = []
        self.generate_maze()

        self.free_tiles = []
        self.set_free_tiles()

        # drawing
        self.tile_size = 20
        self.static_board = [[0 for i in range(tile_num_x)] for _ in range(tile_num_y)]
        self.view = SVGView(tile_num_x * self.tile_size, tile_num_y * self.tile_size, "Maze in a haze")
        # background used as wall
        self.base = Rect(0, 0, tile_num_x * self.tile_size, tile_num_y * self.tile_size, self.view)

        print("start render")
        start_time = time()
        self.initial_render()
        print(time()-start_time)
        print("finish render")

    def __call__(self, x, y):
        return self.grid[y][x]

    # generates a grid using prims algorithm
    # "#" represents a wall, "." a free tile
    def generate_maze(self):
        # sets up a grid full of walls
        grid = [["#" for i in range(self.tile_num_x)] for _ in range(self.tile_num_y)]

        # sets one cell as open, that is not on the edge
        pos = [randint(1, self.tile_num_y - 2), randint(1, self.tile_num_x - 2)]
        grid[pos[0]][pos[1]] = "."

        # list of walls adjacent to an open cells, that need to be looked at
        frontier_lst = [[pos[0] + 1, pos[1]], [pos[0] - 1, pos[1]], [pos[0], pos[1] + 1], [pos[0], pos[1] - 1]]

        # checks a wall in frontier list
        while frontier_lst:
            # chooses a random cell/wall from the frontier list
            cell = choice(frontier_lst)
            y = cell[0]
            x = cell[1]
            lst = []
            neighbors = 0

            # checks for number of neighboring open cells
            if y < self.tile_num_y - 1:
                lst.append([y + 1, x])
                if grid[y + 1][x] == ".":
                    neighbors += 1

            if y > 0:
                lst.append([y - 1, x])
                if grid[y - 1][x] == ".":
                    neighbors += 1

            if x < self.tile_num_x - 1:
                lst.append([y, x + 1])
                if grid[y][x + 1] == ".":
                    neighbors += 1

            if x > 0:
                lst.append([y, x - 1])
                if grid[y][x - 1] == ".":
                    neighbors += 1

            # if that wall has exactly one neighbour, make it an open cell
            # and at it's neighboring walls to the frontier list
            if neighbors == 1:
                frontier_lst = frontier_lst + lst
                grid[y][x] = "."

            frontier_lst.remove(cell)

        self.grid = grid

    def set_free_tiles(self):
        for y in range(self.tile_num_y):
            for x in range(self.tile_num_x):
                if self.grid[y][x] == ".":
                    self.free_tiles.append((x, y))

    def get_free_tiles(self):
        self.set_free_tiles()
        return self.free_tiles

    def get_a_free_tile(self):
        return choice(self.get_free_tiles())

    def get_view(self):
        return self.view

    def set_tile(self, x, y, object):
        self.grid[y][x] = object

    def move_object_by(self, x, y, x_direction, y_direction):
        self.grid[y + y_direction][x + x_direction] = self.grid[y][x]
        self.grid[y][x] = "."

    # outputs the grid in the console as a string
    def print_out(self):
        for lines in self.grid:
            for tile in lines:
                print(tile, end="")
            print("")

    # very slow, why??
    def initial_render(self):
        gray = (143, 143, 143)

        # render tiles, walls are the background
        for y in range(self.tile_num_y):
            for x in range(self.tile_num_x):
                if self.grid[y][x] == ".":
                    self.static_board[y][x] = Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, self.view)
                    self.static_board[y][x].set_fill_rgb(*gray)