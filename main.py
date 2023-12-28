import arcade
from random import choice
from maze import Maze
from hero import Hero
from helper import get_line
import time

TILE_NUM_X = 25
TILE_NUM_Y = 25

# TODO because of this character slightly smaller then tiles
CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
TILE_SIZE = 32

SCREEN_TITLE = "Dungeon Crawler"
SCREEN_WIDTH = 20 * TILE_SIZE
SCREEN_HEIGHT = 20 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = False

# either move smooth, half tile or full tile, change update time as well
PLAYER_MOVEMENT_SPEED = TILE_SIZE
VIEW_RANGE = 3 if not I_SEE_EVERYTHING else 40

NUM_COINS = 25


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

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
        self.maze = Maze(TILE_NUM_X, TILE_NUM_Y)

        self.new_tiles = []
        self.uncovered_tiles = [[False for _ in range(TILE_NUM_Y)] for _ in range(TILE_NUM_X)]
        self.create_view_range_mask()
        self.score = 0

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

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
        self.player_sprite = arcade.Sprite(player_texture, TILE_SCALING)
        self.player_sprite.center_x = x * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = y * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

        for i in range(NUM_COINS):
            x, y = self.maze.get_a_free_tile()
            self.maze.set_tile(x, y, "c")

        self.check_field_of_view()
        self.render_new_tiles()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.scene.get_sprite_list("Walls"))

        self.start_time = time.time()
        # for some reason big loading time
        arcade.play_sound(self.start_sound, volume=0.5)

    def create_view_range_mask(self):
        mask = []
        # center of field of view
        rx, ry = VIEW_RANGE, VIEW_RANGE
        for y in range(VIEW_RANGE * 2 + 1):
            row = []
            for x in range(VIEW_RANGE * 2 + 1):
                # if the relative x and y are not within the wanted field of view, set True
                row.append((abs(rx - x) + abs(ry - y) <= VIEW_RANGE))
            mask.append(row)
        self.view_range_mask = mask

    # TODO on short press loses input sometimes
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = - PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = - PLAYER_MOVEMENT_SPEED

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
        elif screen_center_x > TILE_NUM_X * TILE_SIZE - SCREEN_WIDTH:
            screen_center_x = TILE_NUM_X * TILE_SIZE - SCREEN_WIDTH
        if screen_center_y < 0:
            screen_center_y = 0
        elif screen_center_y > TILE_NUM_Y * TILE_SIZE - SCREEN_HEIGHT:
            screen_center_y = TILE_NUM_Y * TILE_SIZE - SCREEN_HEIGHT

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # TODO: make more efficient, also fucking diagonals
    def check_field_of_view(self):
        # hero position in the main grid
        cx = int(self.player_sprite.center_x / TILE_SIZE)
        cy = int(self.player_sprite.center_y / TILE_SIZE)

        # hero position in the relative grid
        rx = VIEW_RANGE
        ry = VIEW_RANGE
        new_tiles = []
        for y in range(VIEW_RANGE * 2 + 1):
            for x in range(VIEW_RANGE * 2 + 1):
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
                return I_SEE_EVERYTHING
        return True

    def in_bound(self, x, y):
        return 0 <= x < TILE_NUM_X and 0 <= y < TILE_NUM_Y

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
                self.set_texture(coin, "Coins", x, y, COIN_SCALING)
            # TODO better stair texture
            elif self.maze(x, y) == "S":
                stair_texture = "Tiles/tile_0039.png"
                self.set_texture(stair_texture, "Stairs", x, y)

    def set_texture(self, texture, scene_name, x, y, t_scaling=TILE_SCALING):
        sprite = arcade.Sprite(texture, t_scaling)
        sprite.center_x = x * TILE_SIZE + TILE_SIZE // 2
        sprite.center_y = y * TILE_SIZE + TILE_SIZE // 2
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

        cx = int(self.player_sprite.center_x / TILE_SIZE)
        cy = int(self.player_sprite.center_y / TILE_SIZE)

        # check for coin collision
        for coin in self.coin_sprites:
            if cx == int(coin.center_x / TILE_SIZE) and cy == int(coin.center_y / TILE_SIZE):
                arcade.play_sound(self.collect_coin_sound)
                self.coin_sprites.remove(coin)
                self.score += 1

        if self.maze(cx, cy) == "S":
            arcade.play_sound(self.win_sound)
            print(f"Time: {time.time() - self.start_time}")
            print(f"Score: {self.score} / {NUM_COINS}")
            time.sleep(1.5)
            self.setup()


def main():
    window = Game()
    window.setup()

    arcade.schedule(window.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
