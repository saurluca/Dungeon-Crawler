import arcade
from random import choice
from maze import Maze
from hero import Hero
from helper import get_line
import time

tile_num_x = 25
tile_num_y = 25

character_scaling = 1.8
tile_scaling = 2.0
coin_scaling = 1.4
tile_size = 32

screen_title = "Dungeon Crawler"
screen_width = 20 * tile_size
screen_height = 20 * tile_size

# cheat mode for full vision
I_SEE = False

# either move smooth, half tile or full tile, change update time as well
player_movement_speed = tile_size
view_range = 3 if not I_SEE else 40

num_coins = 25


class Game(arcade.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height, screen_title)

        self.maze = None

        self.uncovered_tiles = None
        self.new_tiles = None
        self.view_range_mask = None

        self.scene = None
        self.player_sprite = None
        self.coin_sprites = None

        self.physics_engine = None

        self.camera = None

        self.start_time = None
        self.score = None

        # TODO rename file
        # TODO first time sound is player, game lagg
        self.collect_coin_sound = arcade.load_sound("Sounds/beltHandle2.ogg")
        self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
        self.win_sound = arcade.load_sound("Sounds/you_win.ogg")

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.maze = Maze(tile_num_x, tile_num_y)

        self.new_tiles = []
        self.uncovered_tiles = [[False for _ in range(tile_num_y)] for _ in range(tile_num_x)]
        self.create_view_range_mask()
        self.score = 0

        self.camera = arcade.Camera(screen_width, screen_height)

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Stairs", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Player")

        self.coin_sprites = self.scene.get_sprite_list("Coins")

        # renders the hero
        x, y = self.maze.get_a_free_tile()
        self.maze.set_tile(x, y, Hero(x, y))

        player_texture = "Tiles/tile_0098.png"
        self.player_sprite = arcade.Sprite(player_texture, tile_scaling)
        self.player_sprite.center_x = x * tile_size + tile_size // 2
        self.player_sprite.center_y = y * tile_size + tile_size // 2
        self.scene.add_sprite("Player", self.player_sprite)

        for i in range(num_coins):
            x, y = self.maze.get_a_free_tile()
            self.maze.set_tile(x, y, "c")

        self.check_field_of_view()
        self.render_new_tiles()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.scene.get_sprite_list("Walls"))

        self.start_time = time.time()
        # for some reason big loading time
        # arcade.play_sound(self.start_sound)

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

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0 or past border
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_x > tile_num_x * tile_size - screen_width:
            screen_center_x = tile_num_x * tile_size - screen_width
        if screen_center_y > tile_num_y * tile_size - screen_height:
            screen_center_y = tile_num_y * tile_size - screen_height

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # TODO: make more efficient, also fucking diagonals
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
                # checks if in circular view range, if in bound of grid, that the block is in line of sight, block not seen before
                if self.view_range_mask[y][x] and self.in_bound(abs_x, abs_y) and self.check_block_visible(cx, cy, rx, ry, x, y) and not \
                        self.uncovered_tiles[abs_x][abs_y]:
                    new_tiles.append((abs_x, abs_y))
                    self.uncovered_tiles[abs_x][abs_y] = True

        self.new_tiles = new_tiles

    # calculates line approximation and checks if sight is blocked along the line
    def check_block_visible(self, cx, cy, rx, ry, x, y):
        s = get_line((rx, ry), (x, y))
        for point in s:
            if not self.maze.check_obstacle(cx + point[0] - rx, cy + point[1] - ry) and point != (x, y):
                return I_SEE
        return True

    def in_bound(self, x, y):
        return 0 <= x < tile_num_x and 0 <= y < tile_num_y

    def render_new_tiles(self):
        for tile in self.new_tiles:
            x, y = tile
            # random walls and floor tiles to make it look nicer
            if self.maze(x, y) == "#":
                wall_texture = choice(("Tiles/tile_0014.png", "Tiles/tile_0040.png"))
                self.set_texture(wall_texture, "Walls", x, y)
            else:
                floor_texture = choice(("Tiles/tile_0042.png", "Tiles/tile_0048.png", "Tiles/tile_0049.png"))
                self.set_texture(floor_texture, "Floor", x, y)
            if self.maze(x, y) == "c":
                coin = "Tiles/tile_0003.png"
                self.set_texture(coin, "Coins", x, y, coin_scaling)
            elif self.maze(x, y) == "S":
                stair_texture = "Tiles/tile_0039.png"
                self.set_texture(stair_texture, "Stairs", x, y)

    def set_texture(self, texture, scene_name, x, y, t_scaling=tile_scaling):
        sprite = arcade.Sprite(texture, t_scaling)
        sprite.center_x = x * tile_size + tile_size // 2
        sprite.center_y = y * tile_size + tile_size // 2
        self.scene.add_sprite(scene_name, sprite)

    def on_draw(self):
        arcade.start_render()

        self.camera.use()

        self.scene.draw()

    def update_things(self, delta_time):
        self.physics_engine.update()

        self.render_new_tiles()
        self.check_field_of_view()

        self.center_camera_to_player()

        cx = int(self.player_sprite.center_x / tile_size)
        cy = int(self.player_sprite.center_y / tile_size)

        # check for coin collision
        for coin in self.coin_sprites:
            if cx == int(coin.center_x / tile_size) and cy == int(coin.center_y / tile_size):
                arcade.play_sound(self.collect_coin_sound)
                self.coin_sprites.remove(coin)
                self.score += 1

        if self.maze(cx, cy) == "S":
            arcade.play_sound(self.win_sound)
            print(f"Time: {time.time() - self.start_time}")
            print(f"Score: {self.score} / {num_coins}")
            time.sleep(1.5)
            self.setup()


def main():
    window = Game()
    window.setup()

    arcade.schedule(window.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
