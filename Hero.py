from algoviz.svg import SVGView, Circle
from random import choice


class Hero:
    def __init__(self, maze):
        self.maze = maze
        self.view = maze.view
        self.tile_size = maze.tile_size

        self.y = 0
        # self.x = choice([i for i in range(maze.tile_num_x) if self.maze.get_grid()[0][i] == "."])
        self.x = 0
        self.maze.set_tile(self.x, self.y, self)

        # drawing
        self.radius = 6
        self.offset = self.tile_size / 2
        self.drawing = Circle(self.x * self.tile_size + self.offset, self.y * self.tile_size + self.offset, self.radius, self.view)
        self.drawing.set_fill_rgb(20, 150, 20)

    def move_by(self, x_direction, y_direction):
        self.maze.move_object_by(self.x, self.y, x_direction, y_direction)
        self.drawing.move_by(x_direction * self.tile_size, y_direction * self.tile_size)
        self.x += x_direction
        self.y += y_direction

    # very basic collision, improve
    def check_wall_collision(self, symbol):
        if symbol == "#":
            return True
        else:
            return False

    def get_next_key(self):
        while True:
            return self.view.last_key()

    def move(self):
        size_x = self.maze.tile_num_x
        size_y = self.maze.tile_num_y

        while True:
            key = self.get_next_key()

            if key == "ArrowRight" and self.x < size_x and not self.check_wall_collision():
                self.move_by(1, 0)

            elif key == "ArrowLeft" and self.x > 0:
                self.move_by(-1, 0)

            elif key == "ArrowDown" and self.y < size_y:
                self.move_by(0, 1)

            elif key == "ArrowUp" and self.y > 0:
                self.move_by(0, -1)
