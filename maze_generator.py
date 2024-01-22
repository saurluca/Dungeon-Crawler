"""
This file provides different functions to generate a maze. Now mainly used generate
growing tree maze. Which can, depends on the parameters, be a hybrid between a recursive
backtracking algorithm.
"""

from random import choice


# generates a 2D grid, alternating between walls "#" and open tiles ".", with a wall drawn around
# used as a base for further generation, this way does not produce diagonal pathways
def generate_alternating_grid(tile_num_x, tile_num_y):
    # Initialize the grid with a border row of walls
    grid = [["#" for _ in range(tile_num_y)]]

    # Generate rows with an alternating pattern of walls and spaces
    for x in range((tile_num_x - 2) // 2 + 1):
        flip = True
        row = []
        for y in range(tile_num_y):
            # Alternate between wall and space
            row.append("#") if flip else row.append(".")
            flip = not flip
        # Add the generated row and a full wall row to the grid
        grid.append(row)
        grid.append(["#" for _ in range(tile_num_y)])
    return grid


# produces a list of neighbors that have not been visited before
def check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y):
    # List to keep track of neighboring cells that have not been visited
    open_neighbors = []

    # Potential directions to find neighbors
    for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        neighbor_cell = (current_cell[0] + dx, current_cell[1] + dy)
        # Check if the potential neighbor is within bounds and has not been visited
        if 0 < neighbor_cell[0] < tile_num_x - 1 and 0 < neighbor_cell[1] < tile_num_y - 1 and neighbor_cell not in visited:
            open_neighbors.append(neighbor_cell)
    return open_neighbors


# Return the position of the wall cell between two adjacent open tiles
def in_between(x1, y1, x2, y2):
    if x1 < x2:
        return x2 - 1, y1
    elif x1 > x2:
        return x2 + 1, y1
    elif y1 < y2:
        return x2, y2 - 1
    elif y1 > y2:
        return x2, y2 + 1


# only uneven x and y num, otherwise ugly, because the alternating grid wouldn't really work
def generate_growing_tree_maze(tile_num_x, tile_num_y, recursive_weight=3, random_weight=1):
    # Generate a grid with an alternating pattern to start the maze
    grid = generate_alternating_grid(tile_num_x, tile_num_y)

    # Determine the method of maze expansion based on provided weights
    # determine the way the next cell to work on is chosen
    weights = [True for _ in range(recursive_weight)] + [False for _ in range(random_weight)]

    # starting cell
    visited = [(1, 1)]

    # -2 because of wall border, // 2 + 1 to half it and round up, of x and y tiles
    num_free_tiles = ((tile_num_x - 2) // 2 + 1) * ((tile_num_y - 2) // 2 + 1)
    i = 0
    not_found = 0
    while i < num_free_tiles - 1:
        # Choose whether to proceed recursively or randomly based on weights
        recursive = choice(weights)
        if recursive:
            # this is similar to a recursive backtracking algorithm
            current_cell = visited[-1 - not_found]
        else:
            # this is similar to Prim's algorithm for maze generation
            current_cell = choice(visited)

        # Determine unvisited neighbors of the current cell
        open_neighbors = check_unvisited_neighbors(current_cell, visited, tile_num_x, tile_num_y)

        # If there are unvisited neighbors, proceed to carve a path
        if open_neighbors:
            next_cell = choice(open_neighbors)
            x, y = in_between(*current_cell, *next_cell)
            grid[x][y] = "."  # Carve the wall to create a path
            visited.append(next_cell)  # Add the new cell to the visited list
            i += 1
            not_found = 0
        elif recursive:
            # Increment the counter to backtrack if necessary
            not_found += 1

    return grid


# generates a list of tiles that are empty (".") and not a dead end
def calculate_open_tiles(grid, dead_ends, tile_num_x, tile_num_y):
    open_tiles = []
    for x in range(tile_num_x):
        for y in range(tile_num_y):
            if grid[x][y] == "." and (x, y) not in dead_ends:
                open_tiles.append((x, y))
    return open_tiles


# checks if a tile is a dead end, i.e. there is only one adjacent open tile
def check_dead_end(x, y, grid):
    if grid[x][y] == ".":
        open_tiles = 0
        # checks in every direction
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if grid[x + dx][y + dy] == ".":
                open_tiles += 1
        return open_tiles == 1


# generates a list of all dead ends
def search_dead_ends(grid, tile_num_x, tile_num_y):
    dead_ends = []
    for x in range(tile_num_x):
        for y in range(tile_num_y):
            if check_dead_end(x, y, grid):
                dead_ends.append((x, y))
    return dead_ends
