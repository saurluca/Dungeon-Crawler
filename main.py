import arcade
import time
from random import choice
from hero import Hero
from level import Level
from read_write import write_down_stats

CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
ITEM_SCALING = 1.6
FOOD_SCALING = 1.5
TILE_SIZE = 32

# height should be width +1, to accommodate the ui
SCREEN_WIDTH = 19 * TILE_SIZE
SCREEN_HEIGHT = 20 * TILE_SIZE


# cheat mode for full vision
I_SEE_EVERYTHING = True
# no damage
I_AM_INVINCIBLE = False
# enables or disables diagonal movement
DIAGONAL_MOVEMENT = True


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Dungeon Crawler")
        self.hero = Hero()
        self.level = None

        self.tick = 0
        self.player_is_dead = False

        # only odd numbers
        self.tile_num_x = 19
        self.tile_num_y = 19

        self.num_enemies = 5
        self.enemies_lst = []

        self.num_coins = 12
        self.total_num_coins = self.num_coins
        self.num_food = 10

        # used for interaction between level and main class
        self.player_change_x = 0
        self.player_change_y = 0

        # scene is an object containing all sprites that are currently rendered
        self.scene = None

        # player and coin sprite seperated, so they can be changed dynamically
        self.player_sprite = None
        self.coin_sprites = None
        self.item_sprites = None
        self.food_sprites = None
        self.enemy_sprites = None

        # player camera
        self.camera = None
        # camera used for gui elements
        self.ui_camera = arcade.Camera()

        # text display object
        self.hp_text = None

        # keeps track of and displays the score, currently coins collected
        self.score = 0
        self.score_text = None

        # keeps track of number of levels played
        self.levels_played = 1
        self.level_played_text = None

        # keeps track of time spent in a level
        self.start_time = time.time()
        self.time_text = None

        # TODO first time sound is played, the game lags
        self.collect_coin_sound = arcade.load_sound("Sounds/coin_sound.ogg")
        self.start_sound = arcade.load_sound("Sounds/prepare_yourself.ogg")
        self.win_sound = arcade.load_sound("Sounds/you_win.ogg")
        self.game_over_sound = arcade.load_sound("Sounds/dark-souls-you-died.wav")
        #self.food_sound = arcade.load_sound("")

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.level = Level(self.hero, self.tile_num_x, self.tile_num_y, self.num_coins, self.num_food, self.num_enemies, self.enemies_lst)
        print("jooo")
        # set up the game camera
        self.camera = arcade.Camera()

        # set up ui/ camera, extra so it does not move around like the rest of the game
        # self.ui_camera = arcade.Camera(self.width, self.height)

        # sets up the scene, container for sprites
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Stairs", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Food")
        self.scene.add_sprite_list("Enemies")
        self.scene.add_sprite_list("Items")
        self.scene.add_sprite_list("Player")

        self.coin_sprites = self.scene.get_sprite_list("Coins")
        self.item_sprites = self.scene.get_sprite_list("Items")
        self.food_sprites = self.scene.get_sprite_list("Food")
        self.enemy_sprites = self.scene.get_sprite_list("Enemies")

        # sets up the player, rendering at specific location
        player_texture = "Tiles/tile_0098.png"
        self.player_sprite = arcade.Sprite(player_texture, TILE_SCALING)
        self.player_sprite.center_x = self.hero.get_x() * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = self.hero.get_y() * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

        # display ui texts
        self.hp_text = arcade.Text(f"HP: {self.hero.get_hp():.1f} / {self.hero.get_max_hp()}", 8, SCREEN_HEIGHT - 24,
                                   arcade.csscolor.GREEN, 18, bold=True)
        self.score_text = arcade.Text(f"Score: {self.score} / {self.total_num_coins}", 8 + 5 * TILE_SIZE + 16, SCREEN_HEIGHT - 24,
                                      arcade.csscolor.BLACK, 18)
        self.level_played_text = arcade.Text(f"Level: {self.levels_played}", 8 + 10 * TILE_SIZE + 16, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)
        self.time_text = arcade.Text(f"Time: {self.start_time}", 8 + 14 * TILE_SIZE, SCREEN_HEIGHT - 24, arcade.csscolor.BLACK, 18)

        # Cheat mode to see everything
        if I_SEE_EVERYTHING:
            every_tile = []
            for x in range(self.tile_num_x):
                for y in range(self.tile_num_y):
                    every_tile.append((x, y))
            self.add_new_tiles_to_scene(self.level.add_tile_type(every_tile))

        # TODO reduce big loading time
        arcade.play_sound(self.start_sound, volume=0.5)

    # colour [00, 00, 00, 0.7])
    def stop_game(self):
        # write_down_stats(self.levels_played, round(time.time() - self.start_time, 1), self.score, self.total_num_coins)
        arcade.play_sound(self.game_over_sound, volume=0.5)

        self.clear()
        arcade.draw_xywh_rectangle_filled(0, 0, SCREEN_HEIGHT, SCREEN_WIDTH, [00, 00, 00, 0.7])

        arcade.Text("YOU DIED", SCREEN_HEIGHT//4, SCREEN_WIDTH//2, arcade.csscolor.RED, 50).draw()

        # problem was, that the screen never got updated, because never went into on_draw() again
        arcade.finish_render()

        time.sleep(3)
        self.close()

    # if a key is pressed, changes movement speed in the pressed direction
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
        # finish game when pressing escape, save current stats
        elif key == arcade.key.ESCAPE:
            self.stop_game()

    # if key is released, resets movement speed in that direction
    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_change_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_change_y = 0

    # TODO, if maze smaller then window, ugly
    # moves main camera, so it is centered on player, checks that it does not go out of bounds
    def center_camera_to_player(self):
        if self.tile_num_x >= SCREEN_WIDTH//TILE_SIZE and self.tile_num_y >= (SCREEN_HEIGHT - 1)//TILE_SIZE:
            screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
            screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

            # Don't let camera travel past 0 or past border
            if screen_center_x < 0:
                screen_center_x = 0
            elif screen_center_x > self.tile_num_x * TILE_SIZE - SCREEN_WIDTH:
                screen_center_x = self.tile_num_x * TILE_SIZE - SCREEN_WIDTH
            if screen_center_y < 0:
                screen_center_y = 0
            elif screen_center_y > self.tile_num_y * TILE_SIZE - SCREEN_HEIGHT:
                screen_center_y = self.tile_num_y * TILE_SIZE - SCREEN_HEIGHT + TILE_SIZE

            player_centered = screen_center_x, screen_center_y

            self.camera.move_to(player_centered)

    # creates a new sprite
    def create_sprite(self, texture, scene_name, x, y, t_scaling=TILE_SCALING):
        sprite = arcade.Sprite(texture, t_scaling)
        sprite.center_x = x * TILE_SIZE + TILE_SIZE // 2
        sprite.center_y = y * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite(scene_name, sprite)

    # adds the tiles not seen before to the scene
    def add_new_tiles_to_scene(self, new_tiles):
        for tile in new_tiles:
            pos, object_type = tile[0], tile[1]
            # random walls and floor tiles to make it look nicer
            if object_type == "#":
                wall_texture = choice(("Tiles/tile_0014.png", "Tiles/tile_0040.png"))
                self.create_sprite(wall_texture, "Walls", *pos)
            else:
                floor_texture = choice(("Tiles/tile_0042.png", "Tiles/tile_0048.png", "Tiles/tile_0049.png"))
                self.create_sprite(floor_texture, "Floor", *pos)
            if object_type == "c":
                coin_texture = "Tiles/tile_0003.png"
                self.create_sprite(coin_texture, "Coins", *pos, COIN_SCALING)
            if object_type == "F":
                food_texture = "Tiles/tile_0066.png"
                self.create_sprite(food_texture, "Food", *pos, FOOD_SCALING)
            elif object_type == "E":
                enemy_texture = "Tiles/tile_0124.png"
                self.create_sprite(enemy_texture, "Enemies", *pos, CHARACTER_SCALING)
            elif object_type == "I":
                item_texture = "Tiles/tile_0118.png"
                self.create_sprite(item_texture, "Items", *pos, ITEM_SCALING)
            # TODO better stair texture, make more obvious
            elif object_type == "S":
                stair_texture = "Tiles/tile_0039.png"
                self.create_sprite(stair_texture, "Stairs", *pos)

    def update_hp_display(self):
        if self.hero.hp > 0:
            self.hp_text.text = f"HP: {self.hero.get_hp():.1f} / {self.hero.get_max_hp()}"

    def update_score(self):
        if self.level.check_coin_collected():
            self.score += 1
        self.score_text.text = f"Score: {self.score} / {self.total_num_coins}"

    def update_levels_played(self):
        self.levels_played += 1
        self.level_played_text.text = f"Level: {self.levels_played}"

    def update_display_time(self):
        self.time_text.text = f"Time: {round(time.time() - self.start_time, 1)}"

    # repositions player sprite to new position
    def update_player_sprite(self):
        self.player_sprite.center_x = self.hero.get_x() * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = self.hero.get_y() * TILE_SIZE + TILE_SIZE // 2

    def update_enemy_sprites(self):
        i = 0
        for enemy in self.enemy_sprites:
            enemy.center_x = self.enemies_lst[i].get_x() * TILE_SIZE + TILE_SIZE // 2
            enemy.center_y = self.enemies_lst[i].get_y() * TILE_SIZE + TILE_SIZE // 2
            i += 1

    # score allowed to be here?
    def update_coin_sprites(self):
        if self.level.check_coin_collected():
            for coin in self.coin_sprites:
                if self.hero.get_position() == (int(coin.center_x / TILE_SIZE), int(coin.center_y / TILE_SIZE)):
                    self.coin_sprites.remove(coin)

    def update_food_sprites(self):
        if self.level.check_food_collected():
            for food in self.food_sprites:
                if self.hero.get_position() == (int(food.center_x / TILE_SIZE), int(food.center_y / TILE_SIZE)):
                    self.food_sprites.remove(food)

    def update_item_sprites(self):
        if self.level.check_item_collected():
            for item in self.item_sprites:
                if self.hero.get_position() == (int(item.center_x / TILE_SIZE), int(item.center_y / TILE_SIZE)):
                    self.item_sprites.remove(item)

    # background square and text for score, time and hp displayed on the top
    def draw_ui(self):
        # used as a background to draw on
        arcade.draw_rectangle_filled(0, SCREEN_HEIGHT - TILE_SIZE / 2, SCREEN_WIDTH * 2, TILE_SIZE, arcade.csscolor.SADDLE_BROWN)
        self.hp_text.draw()
        self.score_text.draw()
        self.level_played_text.draw()
        self.time_text.draw()

    # if player walks on stair, generates new level
    # with more coins, and bigger maze
    # TODO this function checks and changes something, 2 purpose
    def advance_to_next_level(self):
        self.update_levels_played()
        self.num_coins += self.levels_played * 2 + 3
        self.num_food += self.levels_played * 2
        self.total_num_coins += self.num_coins
        # only even numbers, so the end result will be odd
        self.tile_num_x += 2
        self.tile_num_y += 2
        self.setup()

    def on_draw(self):
        # clears the screen
        self.clear()

        # camera for main game
        self.camera.use()

        self.scene.draw()

        # camera for ui
        self.ui_camera.use()

        self.draw_ui()

    # noinspection PyUnusedLocal

    def update_things(self, delta_time):
        if self.level.check_completed():
            self.advance_to_next_level()

        if self.tick % 2 == 0:
            # self.level.move_enemies()
            self.update_enemy_sprites()

        # updates player position
        self.level.move_player(self.player_change_x, self.player_change_y)

        # adds new tiles to scene
        if not I_SEE_EVERYTHING:
            new_tiles = self.level.add_tile_type(self.level.get_newly_visible_tiles())
            self.add_new_tiles_to_scene(new_tiles)

        self.center_camera_to_player()

        # update dynamic sprites
        self.update_player_sprite()
        self.update_coin_sprites()
        self.update_food_sprites()
        self.update_item_sprites()

        if not I_AM_INVINCIBLE:
            self.level.base_hp_loss(self.levels_played)
            self.player_is_dead = self.hero.is_dead()

        # update ui, later, if more stuff, put in extra method
        self.update_hp_display()
        self.update_score()
        self.update_display_time()

        self.tick += 1

        if self.player_is_dead:
            self.stop_game()


def main():
    game = Game()
    game.setup()
    # game.level.maze.print_out()

    arcade.schedule(game.update_things, 1 / 8)

    arcade.run()


if __name__ == "__main__":
    main()
