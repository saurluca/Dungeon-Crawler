import arcade
from random import choice
from maze import Maze
from hero import Hero
from helper import get_line
import time

# Only odd numbers
TILE_NUM_X = 25
TILE_NUM_Y = 25

# TODO because of this character slightly smaller then tiles
CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
TILE_SIZE = 32

SCREEN_TITLE = "Dungeon Crawler"
SCREEN_WIDTH = 15 * TILE_SIZE
SCREEN_HEIGHT = 16 * TILE_SIZE

# cheat mode for full vision
I_SEE_EVERYTHING = False
DIAGONAL_MOVEMENT = True

# either move smooth, half tile or full tile, change update time as well
PLAYER_MOVEMENT_SPEED = TILE_SIZE
VIEW_RANGE = 3 if not I_SEE_EVERYTHING else 40

NUM_COINS = 20


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.maze = None
        self.hero = None

        # tiles already seen
        self.uncovered_tiles = None

        # tiles that where uncovered in the last step
        self.new_tiles = None

        # used to speed up field of view calculation
        self.view_range_mask = None

        self.scene = None
        self.player_sprite = None
        self.coin_sprites = None

        # player camera
        self.camera = None

        # camera used for gui elements
        self.ui_camera = None

        # keeps track of time spent in a level
        self.start_time = None
        self.time_text = None

        self.score = 0
        self.score_text = None

        self.hp_text = None

        # TODO rename file
        # TODO first time sound is player, game lagg
        self.collect_coin_sound = arcade.load_sound("Sounds/beltHandle2.ogg")
        self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
        self.win_sound = arcade.load_sound("Sounds/you_win.ogg")

        arcade.set_background_color(arcade.csscolor.BLACK)

        self.player_change_x = 0
        self.player_change_y = 0

    # TODO loading screen
    def setup(self):
        # sets up and generates the maze
        self.maze = Maze(TILE_NUM_X, TILE_NUM_Y, 4, 1)

        self.new_tiles = []
        self.uncovered_tiles = [[False for _ in range(TILE_NUM_Y)] for _ in range(TILE_NUM_X)]

        self.create_view_range_mask()

        # set up the game camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Stairs", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Player")

        self.coin_sprites = self.scene.get_sprite_list("Coins")

        cx, cy = self.maze.two_points[0]
        self.hero = Hero(cx, cy)
        self.maze.set_tile(cx, cy, self.hero)

        # sets up the player, rendering at specific location
        player_texture = "Tiles/tile_0098.png"
        self.player_sprite = arcade.Sprite(player_texture, TILE_SCALING)
        self.player_sprite.center_x = cx * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = cy * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

        # generates coins
        for i in range(NUM_COINS):
            x, y = self.maze.get_a_free_tile()
            self.maze.set_tile(x, y, "c")

        # checks initial field of view
        self.check_field_of_view()
        # renders these tiles
        self.add_new_tiles()

        # tracks the time, of when the level was started
        self.start_time = time.time()

        # set up ui/ camera, extra so it does not move around like the rest of the game
        self.ui_camera = arcade.Camera(self.width, self.height)

        self.score_text = arcade.Text(f"Score: {self.score} / {NUM_COINS}", 8, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)
        self.time_text = arcade.Text(f"Time: {self.start_time}", 8 + 5 * TILE_SIZE, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)
        self.hp_text = arcade.Text(f"HP: {self.hero.get_hp()} / {self.hero.get_max_hp()}", 8 + 10 * TILE_SIZE, SCREEN_HEIGHT - 24,
                                   arcade.csscolor.BLACK, 18)

        # TODO reduce big loading time
        # arcade.play_sound(self.start_sound, volume=0.5)

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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 1
            if not DIAGONAL_MOVEMENT:
                self.player_change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = -1
            if not DIAGONAL_MOVEMENT:
                self.player_change_y = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 1
            if not DIAGONAL_MOVEMENT:
                self.player_change_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = -1
            if not DIAGONAL_MOVEMENT:
                self.player_change_x = 0

    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = 0

    # TODO change where and how cx and cy is saved
    # TODO move collision check with coins etc. here?
    # TODO change position in grid?
    def move_player(self):
        cx, cy = self.hero.get_position()
        dx, dy = self.player_change_x, self.player_change_y

        if self.maze.check_obstacle(cx + dx, cy + dy):
            self.player_sprite.center_x += dx * TILE_SIZE
            self.player_sprite.center_y += dy * TILE_SIZE
            self.hero.set_position(cx + dx, cy + dy)
        elif self.maze.check_obstacle(cx + dx, cy):
            self.player_sprite.center_x += dx * TILE_SIZE
            self.hero.set_x(cx + dx)
        elif self.maze.check_obstacle(cx, cy + dy):
            self.player_sprite.center_y += dy * TILE_SIZE
            self.hero.set_y(cy + dy)

    # TODO possible to check via maze?
    
    def check_coin_collision(self):
        for coin in self.coin_sprites:
            if self.hero.get_x() == int(coin.center_x / TILE_SIZE) and self.hero.get_y() == int(coin.center_y / TILE_SIZE):
                # arcade.play_sound(self.collect_coin_sound)
                self.coin_sprites.remove(coin)
                # update score
                self.score += 1
                self.score_text.text = f"Score: {self.score} / {NUM_COINS}"

    def check_stair_collision(self):
        if self.maze(*self.hero.get_position()) == "S":
            # arcade.play_sound(self.win_sound)
            print(f"Total time: {round(time.time() - self.start_time, 1)}")
            print(f"Score: {self.score} / {NUM_COINS}")
            # time.sleep(1.5)
            self.setup()

 '''   def check_item_collision(self):
        for item in self.item_sprites:
            if self.hero.get
'''
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
            screen_center_y = TILE_NUM_Y * TILE_SIZE - SCREEN_HEIGHT + TILE_SIZE

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # TODO: make more efficient
    def check_field_of_view(self):
        # hero position in the relative grid
        rx = VIEW_RANGE
        ry = VIEW_RANGE

        new_tiles = []
        for y in range(VIEW_RANGE * 2 + 1):
            for x in range(VIEW_RANGE * 2 + 1):
                # center of hero x + (vector of center hero to view range grid)
                abs_x = self.hero.get_x() + (x - rx)
                abs_y = self.hero.get_y() + (y - ry)
                # checks if in circular view range, if in bound of grid, that the block is in line of sight, block not seen before
                if self.view_range_mask[y][x] and self.in_bound(abs_x, abs_y) and self.check_block_visible(rx, ry, x, y) and not \
                        self.uncovered_tiles[abs_x][abs_y]:
                    new_tiles.append((abs_x, abs_y))
                    self.uncovered_tiles[abs_x][abs_y] = True

        self.new_tiles = new_tiles

    # calculates line approximation and checks if sight is blocked along the line
    def check_block_visible(self, rx, ry, x, y):
        cx, cy = self.hero.get_position()
        s = get_line((rx, ry), (x, y))
        for point in s:
            if not self.maze.check_obstacle(cx + point[0] - rx, cy + point[1] - ry) and point != (x, y):
                return I_SEE_EVERYTHING
        return True

    def in_bound(self, x, y):
        return 0 <= x < TILE_NUM_X and 0 <= y < TILE_NUM_Y

    def add_new_tiles(self):
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
        # clears the screen
        self.clear()

        # camera for main game
        self.camera.use()

        self.scene.draw()

        # camera for ui
        self.ui_camera.use()

        # TODO better UI
        # used as a background to draw on
        arcade.draw_rectangle_filled(0, SCREEN_HEIGHT - TILE_SIZE / 2, SCREEN_WIDTH * 2, TILE_SIZE, arcade.csscolor.SADDLE_BROWN)

        self.score_text.draw()
        self.time_text.draw()
        self.hp_text.draw()

    def update_things(self, delta_time):
        # updates player position
        self.move_player()

        self.center_camera_to_player()

        self.check_field_of_view()

        # adds new tiles to scene
        self.add_new_tiles()

        # TODO general collision check method?
        # collision checks
        self.check_coin_collision()
        self.check_stair_collision()
        # self.check_item_collision()

        # update time text
        self.time_text.text = f"Time: {round(time.time() - self.start_time, 1)}"
        # TODO create hp view method


def main():
    window = Game()
    window.setup()
    # window.maze.print_out()

    arcade.schedule(window.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
