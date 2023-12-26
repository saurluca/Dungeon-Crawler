import arcade
from random import choice
from maze import Maze
from helper import get_line

tile_num_x = 20
tile_num_y = 20

character_scaling = 1.8
tile_scaling = 2
tile_size = 32

screen_title = "Dungeon Crawler"
screen_width = tile_num_x * tile_size
screen_height = tile_num_y * tile_size

# either move smooth, half tile or full tile, change update time as well
player_movement_speed = tile_size
view_range = 2


class Game(arcade.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height, screen_title)

        self.maze = None
        self.uncovered_tiles = None
        self.new_tiles = None
        self.view_range_mask = None

        self.scene = None
        self.player_sprite = None

        self.physics_engine = None

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.maze = Maze(tile_num_x, tile_num_y)

        self.new_tiles = []
        self.uncovered_tiles = [[False for _ in range(tile_num_x)] for _ in range(tile_num_y)]

        self.create_view_range_mask()

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")

        # renders the hero
        x, y = self.maze.get_a_free_tile()
        self.player_sprite = arcade.Sprite("Tiles/tile_0098.png", character_scaling)
        self.player_sprite.center_x = x * tile_size + tile_size / 2
        self.player_sprite.center_y = y * tile_size + tile_size / 2
        self.scene.add_sprite("Player", self.player_sprite)

        self.check_field_of_view()
        self.render_new_tiles()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.scene.get_sprite_list("Walls"))

    def create_view_range_mask(self):
        mask = []
        # center of field of view
        rx, ry = view_range, view_range
        for y in range(view_range * 2 + 1):
            row = []
            for x in range(view_range * 2 + 1):
                # if the relative x and y are not within the wanted field of view, set True
                row.append((abs(rx - x) + abs(ry - y) <= view_range))
            mask.append(row)
        self.view_range_mask = mask

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = player_movement_speed
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = - player_movement_speed
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = player_movement_speed
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = - player_movement_speed

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0

    # somewhere index out of range, also make more efficient, also fucking diagonals
    def check_field_of_view(self):
        # hero position in the main grid
        cx = int(self.player_sprite.center_x / tile_size)
        cy = int(self.player_sprite.center_y / tile_size)

        # hero position in the relative grid
        rx = view_range
        ry = view_range
        new_tiles = []
        for y in range(view_range * 2 + 1):
            for x in range(view_range * 2 + 1):
                # center of hero x + (vector of center hero to view range grid)
                abs_x = cx + (x - rx)
                abs_y = cy + (y - ry)
                # checks if in circular view range and if in bound of grid and that the block is in line of sight
                if self.view_range_mask[y][x] and self.in_bound(abs_x, abs_y) and self.check_block_visible(cx, cy, rx, ry, x, y):
                    # checks block not seen before
                    if not self.uncovered_tiles[abs_x][abs_y]:
                        new_tiles.append((abs_x, abs_y))
                        self.uncovered_tiles[abs_x][abs_y] = True

        self.new_tiles = new_tiles

    # calculates line approximation and checks if sight is blocked along the line
    def check_block_visible(self, cx, cy, rx, ry, x, y):
        s = get_line((rx, ry), (x, y))
        for point in s:
            if not self.maze.check_obstacle(cx + point[0] - rx, cy + point[1] - ry) and point != (x, y):
                return False
        return True
        #   and point != (rx, ry):
    def in_bound(self, x, y):
        return 0 <= x < tile_num_x and 0 <= y < tile_num_y

    def render_new_tiles(self):
        for tile in self.new_tiles:
            x, y = tile
            if self.maze(x, y) == "#":
                # random walls and floor tiles to make it look nicer
                wall_textures = ["Tiles/tile_0014.png", "Tiles/tile_0040.png"]
                wall = arcade.Sprite(choice(wall_textures), tile_scaling)
                wall.center_x = x * tile_size + tile_size / 2
                wall.center_y = y * tile_size + tile_size / 2
                self.scene.add_sprite("Walls", wall)
            elif self.maze(x, y) == ".":
                floor_textures = ["Tiles/tile_0042.png", "Tiles/tile_0048.png", "Tiles/tile_0049.png"]
                floor = arcade.Sprite(choice(floor_textures), tile_scaling)
                floor.center_x = x * tile_size + tile_size / 2
                floor.center_y = y * tile_size + tile_size / 2
                self.scene.add_sprite("Floor", floor)

    def on_draw(self):
        arcade.start_render()

        self.scene.draw()

    def update_things(self, delta_time):
        self.physics_engine.update()

        self.check_field_of_view()
        self.render_new_tiles()


def main():
    window = Game()
    window.setup()

    arcade.schedule(window.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
