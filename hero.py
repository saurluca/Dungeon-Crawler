
class Hero:
    def __init__(self, maze):
        self.maze = maze

        # spawn in random position
        self.x, self.y = self.maze.get_a_free_tile()
        self.maze.set_tile(self.x, self.y, self)

    def __call__(self):
        return "H"

    def get_position(self):
        return self.x, self.y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def check_wall_collision(self, x_direction, y_direction):
        if self.maze(self.x + x_direction, self.y + y_direction) == "#":
            return True
        else:
            return False

    # def get_next_key(self):
    #     while True:
    #         return self.view.last_key()

    # def move_by(self, x_direction, y_direction):
    #     self.maze.move_object_by(self.x, self.y, x_direction, y_direction)
    #     self.drawing.move_by(x_direction * self.tile_size, y_direction * self.tile_size)
    #     self.x += x_direction
    #     self.y += y_direction

    # def move(self):
    #     size_x = self.maze.tile_num_x
    #     size_y = self.maze.tile_num_y
    #
    #     while True:
    #         key = self.get_next_key()
    #
    #         if key == "ArrowRight" and self.x < size_x and not self.check_wall_collision(1, 0):
    #             self.move_by(1, 0)
    #
    #         elif key == "ArrowLeft" and self.x > 0 and not self.check_wall_collision(-1, 0):
    #             self.move_by(-1, 0)
    #
    #         elif key == "ArrowDown" and self.y < size_y and not self.check_wall_collision(0, 1):
    #             self.move_by(0, 1)
    #
    #         elif key == "ArrowUp" and self.y > 0 and not self.check_wall_collision(0, -1):
    #             self.move_by(0, -1)
