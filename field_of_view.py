"""
the purpose of this class it to check the field of view of the hero
then returns the tiles that are uncovered for the first time
"""

VIEW_RANGE = 3  # view range if fog of war is activated


# The FieldOfView class calculates which tiles in a maze are visible to the player based on their position and view range.
class FieldOfView:
    # Initialize the FieldOfView class with a reference to the maze and a list of already uncovered tiles.
    def __init__(self, maze, uncovered_tiles):
        self.maze = maze  # The maze object, which contains the map and structure.
        self.view_range = VIEW_RANGE  # The range of view or visibility radius.
        # The dimensions of the maze (in tiles).
        self.tile_num_x, self.tile_num_y = maze.tile_num_x, maze.tile_num_y

        self.view_range_mask = self.create_view_range_mask()  # Create a mask for the view range.
        self.uncovered_tiles = uncovered_tiles  # Tiles that have already been uncovered.
        self.new_tiles = None  # To be set with newly discovered tiles each time the FOV is calculated.

    def create_view_range_mask(self):
        """
        A mask that defines a circular area representing the FOV based on the view range.Generates a 2D list containing
        True or False depending on whether the element is in a position inside the circular
        approximation around the center point
        returns: 2D list
        """
        mask = []  # Initialize the mask as an empty list.
        # Calculate the central point of the FOV based on the view range.
        rx, ry = self.view_range, self.view_range
        for x in range(self.view_range * 2 + 1):
            # Start a new row for each 'x' coordinate around the range.
            row = []
            for y in range(self.view_range * 2 + 1):
                # If the tile is within the view range, set the value to True.
                row.append((abs(rx - x) + abs(ry - y) <= self.view_range))
            # Append the row to the mask.
            mask.append(row)
        return mask  # Return the completed circular view range mask.

    # Calculates which new tiles have come into the player's FOV based on their current position.
    def calculate_fov(self, cx, cy):
        # The central point of FOV in relative terms to the player's position (cx, cy).
        rx, ry = self.view_range, self.view_range

        new_tiles = []  # Initialize a list to store new tiles that the player can now see.
        # Loop over the coordinates in the view range mask.
        for x in range(self.view_range * 2 + 1):
            for y in range(self.view_range * 2 + 1):
                # Translate coordinates from player's relative view range to absolute maze coordinates.
                abs_x = cx + (x - rx)
                abs_y = cy + (y - ry)
                # Check if the tile is within the circular FOV mask, if it's in bounds, unobstructed, and not seen before.
                if (self.view_range_mask[x][y] and self.in_bound(abs_x, abs_y)
                        and self.check_block_visible(cx, cy, rx, ry, x, y)
                        and not self.uncovered_tiles[abs_x][abs_y]):
                    # Add the tile to the list of new tiles and mark it as uncovered.
                    new_tiles.append((abs_x, abs_y))
                    self.uncovered_tiles[abs_x][abs_y] = True

        return new_tiles  # Return the list of newly visible tiles.

    # Checks for block visibility along a line between two points (hero and tile in FOV).
    def check_block_visible(self, cx, cy, rx, ry, x, y):
        # Get the line of tiles between the hero's position and the distant tile.
        s = get_line((rx, ry), (x, y))
        # Iterate through all the points (tiles) in the line.
        for point in s:
            # If a point along the line, except for the target tile, blocks sight, return False.
            if not self.maze.check_see_through(cx + point[0] - rx, cy + point[1] - ry) and point != (x, y):
                return False
        # If none of the points block sight, visibility is clear; return True.
        return True

    # Checks if a given coordinate (x, y) is within the bounds of the maze grid.
    def in_bound(self, x, y):
        return 0 <= x < self.tile_num_x and 0 <= y < self.tile_num_y


def get_line(start, end):
    """
    Bresenham's Line Algorithm: Returns a list of points that approximate a line between a start and end point
    """
    # Extract the start coordinates (x1, y1) and end coordinates (x2, y2)
    x1, y1 = start
    x2, y2 = end

    # Calculate the differences in the x and y directions
    dx = x2 - x1
    dy = y2 - y1

    # Determine whether the line is steep (greater change in y than in x)
    is_steep = abs(dy) > abs(dx)

    # If the line is steep, transpose it (swap x and y coordinates)
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap the start and end points if the line is drawn from right to left, to simplify the algorithm which assumes left-to-right drawing
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate the differences after any potential transposing or swapping
    dx = x2 - x1
    dy = y2 - y1

    # Initialize the error term used for incremental calculation
    error = int(dx / 2.0)
    # Determine the direction that y will step (up if end y > start y; down if end y < start y)
    ystep = 1 if y1 < y2 else -1

    # Start the y coordinate at the first y position.
    y = y1
    points = []  # Create an empty list to store the points of the line

    # Loop over the x coordinates from start to end
    for x in range(x1, x2 + 1):
        # If the line is steep, transpose the point back to the original orientation.
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)

        # Adjust the error term and the y coordinate as necessary
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # If the start and end points were swapped initially, reverse the list to get proper order
    if swapped:
        points.reverse()
    return points  # Return the list of points that approximates the line
