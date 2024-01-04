from random import choice

import arcade

CHARACTER_SCALING = 1.8
TILE_SCALING = 2.0
COIN_SCALING = 1.4
ITEM_SCALING = 1.6
FOOD_SCALING = 1.5
TILE_SIZE = 32

# height should be width +1, to accommodate the ui
SCREEN_WIDTH = 19 * TILE_SIZE
SCREEN_HEIGHT = 20 * TILE_SIZE


class Renderer:
    def __init__(self, scene, camera, ui_camera, tile_num_x, tile_num_y):
        self.scene = scene

        self.camera = camera
        self.ui_camera = ui_camera

        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y

        # player and coin sprite seperated, so they can be changed dynamically
        self.player_sprite = None
        self.coin_sprites = None
        self.item_sprites = None
        self.food_sprites = None
        self.enemy_sprites = None

    def set_up(self, hero_x, hero_y):
        # sets up the scene, container for sprites
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Stairs", use_spatial_hash=True)
        self.scene.add_sprite_list("Coins")
        self.scene.add_sprite_list("Food")
        self.scene.add_sprite_list("Items")
        self.scene.add_sprite_list("Enemies")
        self.scene.add_sprite_list("Player")

        self.coin_sprites = self.scene.get_sprite_list("Coins")
        self.item_sprites = self.scene.get_sprite_list("Items")
        self.food_sprites = self.scene.get_sprite_list("Food")
        self.enemy_sprites = self.scene.get_sprite_list("Enemies")

        # sets up the player, rendering at specific location
        player_texture = "Tiles/tile_0098.png"
        self.player_sprite = arcade.Sprite(player_texture, TILE_SCALING)
        self.player_sprite.center_x = hero_x * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = hero_y * TILE_SIZE + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

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

    # repositions player sprite to new position
    def update_player_sprite(self, cx, cy):
        self.player_sprite.center_x = cx * TILE_SIZE + TILE_SIZE // 2
        self.player_sprite.center_y = cy * TILE_SIZE + TILE_SIZE // 2

    def update_enemy_sprites(self, enemies_lst):
        i = 0
        for enemy in self.enemy_sprites:
            enemy.center_x = enemies_lst[i].get_x() * TILE_SIZE + TILE_SIZE // 2
            enemy.center_y = enemies_lst[i].get_y() * TILE_SIZE + TILE_SIZE // 2
            i += 1

    def update_item_sprites(self, hero_pos):
        for item in self.item_sprites:
            if hero_pos == (int(item.center_x / TILE_SIZE), int(item.center_y / TILE_SIZE)):
                self.item_sprites.remove(item)

    # TODO sound should not be here
    def update_coin_sprites(self, hero_pos):
        for coin in self.coin_sprites:
            if hero_pos == (int(coin.center_x / TILE_SIZE), int(coin.center_y / TILE_SIZE)):
                self.coin_sprites.remove(coin)

    def update_food_sprites(self, hero_pos):
        for food in self.food_sprites:
            if hero_pos == (int(food.center_x / TILE_SIZE), int(food.center_y / TILE_SIZE)):
                self.food_sprites.remove(food)

    # moves main camera, so it is centered on player, checks that it does not go out of bounds
    def center_camera_to_player(self):
        if self.tile_num_x >= SCREEN_WIDTH // TILE_SIZE and self.tile_num_y >= (SCREEN_HEIGHT - 1) // TILE_SIZE:
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
