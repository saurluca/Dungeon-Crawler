"""
This file provides different functions to generate a maze. Now mainly used generate
growing tree maze. Which can, depends on the parameters, be a hybrid between a recursive
backtracking algorithm and the prim's algorithm.
"""

import time
from random import choice, randint


# generates a grid using prims algorithm
# "#" represents a wall, "." a free tile
def generate_prim_maze(tile_num_x, tile_num_y):
    # sets up a grid full of walls
    grid = [["#" for _ in range(tile_num_y - 2)] for _ in range(tile_num_x - 2)]

    def check(x, y, value):
        if 0 <= x < tile_num_x - 3 and 0 <= y < tile_num_y - 3:
            if grid[x][y] == value:
                return True
        return False

    # sets one cell as open, that is not on the edge
    (start_x, start_y) = (randint(1, tile_num_x - 4), randint(1, tile_num_y - 4))
    grid[start_x][start_y] = "."

    # list of walls adjacent to an open cells, that need to be looked at
    frontier_lst = [(start_x + 1, start_y), (start_x - 1, start_y), (start_x, start_y + 1), (start_x, start_y - 1)]

    # checks a wall in frontier list
    while frontier_lst:
        # chooses a random cell/wall from the frontier list
        x, y = choice(frontier_lst)
        neighbors = 0
        diagonals = 0

        # checks for number of neighboring open cells
        for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if check(new_x, new_y, "."):
                neighbors += 1

        # check diagonals
        for (dx, dy) in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_x, new_y = x + dx, y + dy
            if check(new_x, new_y, "."):
                connected = False
                for (cx, cy) in [(new_x, y), (x, new_y)]:
                    if check(cx, cy, "."):
                        connected = True
                if not connected:
                    diagonals += 1

        # if that wall has exactly one neighbour, make it an open cell
        # and at it's neighboring walls to the frontier list
        if neighbors == 1 and diagonals == 0:
            grid[x][y] = "."
            for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = x + dx, y + dy
                if check(new_x, new_y, "#"):
                    frontier_lst.append((new_x, new_y))

        frontier_lst.remove((x, y))

    # Create the new grid with borders
    border_grid = ['#' * tile_num_y]  # Adds the top border

    # Add left and right borders to the original grid rows
    for row in grid:
        border_grid.append('#' + ''.join(row) + '#')

    border_grid += ['#' * tile_num_y]  # Adds the bottom border

    # converts it back to a list of separate strings
    return [list(row) for row in border_grid]


def generate_alternating_grid(tile_num_x, tile_num_y):
    grid = [["#" for _ in range(tile_num_y)]]
    for x in range((tile_num_x - 2) // 2 + 1):
        flip = True
        row = []
        for y in range(tile_num_y):
            row.append("#") if flip else row.append(".")
            flip = not flip
        grid.append(row)
        grid.append(["#" for _ in range(tile_num_y)])
    return grid


def check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y):
    open_neighbors = []
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        neighbor_cell = (current_cell[0] + dx, current_cell[1] + dy)
        if 0 < neighbor_cell[0] < tile_num_x - 1 and 0 < neighbor_cell[1] < tile_num_y - 1 and neighbor_cell not in visited:
            open_neighbors.append(neighbor_cell)
    return open_neighbors


def in_between(x1, y1, x2, y2):
    if x1 < x2:
        return x2 - 1, y1
    elif x1 > x2:
        return x2 + 1, y1
    elif y1 < y2:
        return x2, y2 - 1
    elif y1 > y2:
        return x2, y2 + 1


# only uneven x and y num, otherwise ugly
def generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight=3, random_weight=1):
    grid = generate_alternating_grid(tile_num_x, tile_num_y)
    weights = [True for _ in range(recursive_weight)] + [False for _ in range(random_weight)]

    visited = [(1, 1)]

    # -2 because of wall border, // 2 + 1 to half it and round up, of x and y tiles
    num_free_tiles = ((tile_num_x - 2) // 2 + 1) * ((tile_num_y - 2) // 2 + 1)
    i = 0
    not_found = 0
    while i < num_free_tiles - 1:
        # adjust weight of random vs backtracking
        recursive = choice(weights)
        if recursive:
            # this is similar to a recursive backtracking algorithm
            current_cell = visited[-1 - not_found]
        else:
            # this is similar to Prim's algorithm
            current_cell = choice(visited)

        open_neighbors = check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y)

        if open_neighbors:
            next_cell = choice(open_neighbors)
            x, y = in_between(*current_cell, *next_cell)
            grid[x][y] = "."
            visited.append(next_cell)
            i += 1
            not_found = 0
        elif recursive:
            not_found += 1

    return grid


def check_dead_end(x, y, grid):
    if grid[x][y] == ".":
        open_tiles = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if grid[x + dx][y + dy] == ".":
                open_tiles += 1
        return open_tiles == 1


def search_dead_ends(tile_num_x, tile_num_y, grid):
    dead_ends = []
    for x in range(tile_num_x):
        for y in range(tile_num_y):
            if check_dead_end(x, y, grid):
                dead_ends.append((x, y))
    return dead_ends


def print_out(grid):
    for row in grid:
        for tile in row:
            print(tile, end="")
        print("")


"""
following are just a few test functions, to experiment with different parameters ofr generating a maze
"""


def test_maze_gen_time_ratio():
    time_lst = []
    testing_num = 50
    sample_values = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (3, 1), (1, 3), (3, 2), (2, 3))
    for rr in sample_values:
        start_time = time.time()
        for i in range(testing_num):
            generate_growing_tree_maze(35, 35, *rr)
        time_lst.append(time.time() - start_time)

    print(sample_values)
    print(time_lst)


def test_maze_gen_time_size():
    time_lst = []
    testing_num = 50
    for x in range(5, 55, 2):
        start_time = time.time()
        for i in range(testing_num):
            generate_growing_tree_maze(x, x, 1, 1, )
        time_lst.append(time.time() - start_time)

    print(time_lst)


def test_maze_gen_time_one_size():
    total_time = 0
    testing_num = 50
    for i in range(testing_num):
        start_time = time.time()
        generate_growing_tree_maze(35, 35, 1, 1, )
        total_time += time.time() - start_time

    print(total_time / testing_num)


if __name__ == '__main__':
    tile_num_x = 9
    tile_num_y = 9
    grid = generate_growing_tree_maze(tile_num_x, tile_num_y)
    print_out(grid)
    a = search_dead_ends(tile_num_x, tile_num_y, grid)
    print(a)
