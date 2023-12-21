from random import randint, choice
from algoviz.svg import SVGView
from Hero import Hero


class Maze:
    def __init__(self, tile_num_x=12, tile_num_y=12):
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.tile_size = 20

        self.maze = []
        self.view = SVGView(size_x * self.tile_size + self.border * 2, size_y * self.tile_size + self.border * 2, "Maze in a haze")
        generate_maze()

        self.static_board = [[0 for i in range(size_x)] for _ in range(size_y)]
        self.base = Rect(0, 0, size_x * self.tile_size + self.border * 2, size_y * self.tile_size + self.border * 2, self.view)
        initial_render()


    # generates a maze using prims algorithm
    # "#" represents a wall, "." a free tile
    def generate_maze(self):
        # sets up a maze full of walls
        maze = [["#" for i in range(self.tile_num_x)] for _ in range(self.tile_num_y)]

        # sets one cell as open, that is not on the edge
        pos = [randint(1, self.tile_num_y - 2), randint(1, self.tile_num_x - 2)]
        maze[pos[0]][pos[1]] = "."

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
                if maze[y + 1][x] == ".":
                    neighbors += 1

            if y > 0:
                lst.append([y - 1, x])
                if maze[y - 1][x] == ".":
                    neighbors += 1

            if x < self.tile_num_x - 1:
                lst.append([y, x + 1])
                if maze[y][x + 1] == ".":
                    neighbors += 1

            if x > 0:
                lst.append([y, x - 1])
                if maze[y][x - 1] == ".":
                    neighbors += 1

            # if that wall has exactly one neighbour, make it an open cell
            # and at it's neighboring walls to the frontier list
            if neighbors == 1:
                frontier_lst = frontier_lst + lst
                maze[y][x] = "."

            frontier_lst.remove(cell)

        self.maze = maze

    # outputs the maze in the console as a string
    def print_out(self):
        for lines in self.maze:
            for tile in lines:
                print(tile, end="")
            print("")

    def get_view(self):
        return self.view

    def set_tile(self, x, y, object):
        self.maze[y][x] = object

    def get_maze(self):
        return self.maze

    def move_object_by(self, x, y, x_direction, y_direction):
        self.maze[y+y_direction][x+x_direction] = self.maze[y][x]
        self.maze[y][x] = "."

    def initial_render(self):
        gray = (143, 143, 143)

        # render tiles, walls are the background
        for y in range(self.tile_num_y):
            for x in range(self.tile_num_x):
                if self.maze[y][x] == ".":
                    print("hello")
                    self.static_board[y][x] = Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, self.view)
                    self.static_board[y][x].set_fill_rgb(*gray)
