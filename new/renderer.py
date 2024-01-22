"""
Renderer Class deals with the actual images and appearance of the game, updating them when the matrix is updated
by other classes like maze or level.
"""
from algoviz.svg.shapes import Image, Rect
from random import choice


# scales all items according to the tile size
TILE_SIZE = 16

POINT_SCALING = TILE_SIZE * 0.7
POINT_POS = (TILE_SIZE - POINT_SCALING) // 2

FOOD_SCALING = TILE_SIZE * 0.7
FOOD_POS = (TILE_SIZE - FOOD_SCALING) // 2

ITEM_SCALING = TILE_SIZE * 0.8
ITEM_POS = (TILE_SIZE - ITEM_SCALING) // 2

ARMOR_SCALING = TILE_SIZE * 1
ARMOR_POS = (TILE_SIZE - ARMOR_SCALING) // 2

HERO_SPRITE_PATH = "../Tiles/hero.png"
HERO_DAMAGED_SPRITE_PATH = "../Tiles/hero_damaged.png"
YOU_DIED_SPRITE_PATH = "../Tiles/you_died.png"

# dictionaries for texture file paths
ENEMY_TEXTURES = {"R": "Tiles/rat.png", "G": "Tiles/ghost.png", "X": "Tiles/spider.png", "C": "Tiles/cyclope.png",
                  "Z": "Tiles/wizard.png"}
ENEMY_DAMAGED_TEXTURES = {"R": "Tiles/rat_damaged.png", "G": "Tiles/ghost_damaged.png", "X": "Tiles/spider_damaged.png",
                          "C": "Tiles/cyclope_damaged.png", "Z": "Tiles/wizard_damaged.png"}
COLLECTABLES_TEXTURES = {"c": "Tiles/point.png", "F": "Tiles/food.png", "A": "Tiles/armor_pickup.png", "P": "Tiles/health_potion.png",
                         "D": "Tiles/door.png"}
WEAPON_TEXTURES = ("Tiles/axe.png", "Tiles/small_axe.png", "Tiles/hammer.png", "Tiles/dagger.png")
WALL_TEXTURES = ("Tiles/wall_0.png", "Tiles/wall_1.png")
FLOOR_TEXTURES = ("Tiles/floor_0.png", "Tiles/floor_1.png", "Tiles/floor_2.png")


class Renderer:
    # The constructor sets up the necessary properties and prepares containers for the sprites.
    def __init__(self, view, tile_num_x, tile_num_y):
        self.view = view  # The view where the game is rendered.
        self.tile_num_x = tile_num_x  # The number of tiles in the x-axis.
        self.tile_num_y = tile_num_y  # The number of tiles in the y-axis.

        # Initialize containers for sprites that will not move and for collectable sprites.
        self.static_sprites = [[None for _ in range(self.tile_num_y)] for _ in range(self.tile_num_x)]
        self.collectable_sprites = [[None for _ in range(self.tile_num_y)] for _ in range(self.tile_num_x)]

        # Initialize properties to store the hero, enemies, and death screen sprites.
        self.hero_sprite = None
        self.enemy_sprites = []
        self.death_screen_image = None

        # Create a rectangle to serve as the game's background
        self.background = Rect(0, 0, tile_num_x * TILE_SIZE, tile_num_y * TILE_SIZE, view)

    # generates the hero sprite at the provided position of the hero
    def generate_hero_sprite(self, hero_x, hero_y):
        hero_texture = HERO_SPRITE_PATH
        self.hero_sprite = Image(hero_texture, hero_x * TILE_SIZE, hero_y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)

    # generates the enemy sprites at the provided position of the enemies
    def generate_enemy_sprites(self, enemy_lst):
        for enemy in enemy_lst:
            x, y = enemy.get_position()
            enemy_sprite = Image(ENEMY_TEXTURES[enemy.enemy_type], x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
            enemy_sprite.hide()
            self.enemy_sprites.append(enemy_sprite)

    # paints the hero red if he gets damaged
    def render_hero_damaged(self, hero):
        x, y = hero.pos
        # if hero took damage, render him red
        if hero.took_damage:
            damaged_hero_sprite = Image(HERO_DAMAGED_SPRITE_PATH, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
            self.hero_sprite = damaged_hero_sprite
            hero.took_damage = False
            hero.took_damage_last_tick = True
        # otherwise render him normally again
        elif hero.took_damage_last_tick:
            normal_hero_sprite = Image(HERO_SPRITE_PATH, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
            self.hero_sprite = normal_hero_sprite
            hero.took_damage_last_tick = False

    # The render_enemy_damaged method updates the visual display of enemies based on if damage was taken.
    def render_enemy_damaged(self, enemy_lst):
        i = 0  # Index to keep track of enemy sprites within the list.
        for enemy in enemy_lst:
            x, y = enemy.pos
            # Check if the current enemy has taken damage and is still alive.
            if enemy.took_damage and enemy.is_alive:
                # If the enemy is damaged, create a new sprite showing the damaged texture at their position.
                damaged_enemy_sprite = Image(ENEMY_DAMAGED_TEXTURES[enemy.enemy_type], x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
                self.enemy_sprites[i] = damaged_enemy_sprite
                enemy.took_damage = False
                enemy.took_damage_last_tick = True
            # If the enemy took damage in the last tick but is no longer taking damage in this tick.
            elif enemy.took_damage_last_tick and enemy.is_alive:
                # Revert to the original sprite showing the enemy undamaged.
                normal_enemy_sprite = Image(ENEMY_TEXTURES[enemy.enemy_type], x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
                self.enemy_sprites[i] = normal_enemy_sprite
                enemy.took_damage_last_tick = False
            i += 1

    # moves the hero sprite to hero_x and hero_y coordinates
    def move_hero_sprite(self, hero_x, hero_y):
        self.hero_sprite.move_to(hero_x * TILE_SIZE, hero_y * TILE_SIZE)
        self.hero_sprite.to_front()

    # cycles through every enemy and moves the sprite to its respective position
    def move_enemy_sprites(self, enemy_lst):
        i = 0
        for enemy in enemy_lst:
            x, y = enemy.get_position()
            self.enemy_sprites[i].move_to(x * TILE_SIZE, y * TILE_SIZE)
            i += 1

    # hides or shows the enemy sprite depending on their visibility attribute
    def update_enemy_visibility(self, enemy_lst):
        i = 0
        for enemy in enemy_lst:
            if enemy.is_visible:
                self.enemy_sprites[i].show()
                self.enemy_sprites[i].to_front()
            else:
                self.enemy_sprites[i].hide()
            i += 1

    # This method adds new tiles to the scene, updating the graphics based on tile type
    def add_new_tiles_to_scene(self, new_tiles):
        # Loop through each tile information in the new_tiles list.
        for tile in new_tiles:
            # Extract the position (x, y coordinates) and object type from the tile tuple.
            pos, object_type = tile[0], tile[1]
            x, y = pos

            # If the object_type is a wall ("#"), choose a random wall texture.
            if object_type == "#":
                wall_texture = choice(WALL_TEXTURES)
                # Create and set the wall tile image using the chosen texture at the specified position.
                tile_image = Image(wall_texture, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)

            # If the object type is not a wall, it is a floor tile.
            else:
                # choose a random floor texture.
                floor_texture = choice(FLOOR_TEXTURES)
                # Create and set the floor tile image using the chosen texture at the specified position.
                tile_image = Image(floor_texture, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
            # Assign the generated image to the respective position in the static_sprites grid.
            self.static_sprites[x][y] = tile_image

            # Instantiate a placeholder for a potential collectible item image.
            tile_image = None

            # Depending on the object type, create different collectible item images.
            if object_type == "c":
                # Create an image for the point collectible.
                tile_image = Image(COLLECTABLES_TEXTURES["c"], x * TILE_SIZE + POINT_POS, y * TILE_SIZE + POINT_POS, POINT_SCALING, POINT_SCALING,
                                   self.view)
            elif object_type == "F":
                # Create an image for the food collectible.
                tile_image = Image(COLLECTABLES_TEXTURES["F"], x * TILE_SIZE + FOOD_POS, y * TILE_SIZE + FOOD_POS, FOOD_SCALING, FOOD_SCALING,
                                   self.view)
            elif object_type == "W":
                # Create an image for the weapon collectible using a randomly chosen texture.
                weapon_texture = choice(WEAPON_TEXTURES)
                tile_image = Image(weapon_texture, x * TILE_SIZE + ITEM_POS, y * TILE_SIZE + ITEM_POS, ITEM_SCALING, ITEM_SCALING, self.view)
            elif object_type == "A":
                # Create an image for the armor collectible.
                tile_image = Image(COLLECTABLES_TEXTURES["A"], x * TILE_SIZE + ARMOR_POS, y * TILE_SIZE + ARMOR_POS, ARMOR_SCALING, ARMOR_SCALING,
                                   self.view)
            elif object_type == "P":
                # Create an image for the potion collectible.
                tile_image = Image(COLLECTABLES_TEXTURES["P"], x * TILE_SIZE + ITEM_POS, y * TILE_SIZE + ITEM_POS, ITEM_SCALING, ITEM_SCALING,
                                   self.view)
            elif object_type == "D":
                # Create an image for the stair tile (exit to the next level).
                tile_image = Image(COLLECTABLES_TEXTURES["D"], x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE, self.view)
            # Assign the collectible item image to the respective position in the collectable_sprites grid if an image was created.
            if tile_image:
                self.collectable_sprites[x][y] = tile_image

    # deletes a sprite from dynamic images, mostly just collectables
    def remove_collectable_sprite(self, pos):
        if pos:
            x, y = pos
            self.collectable_sprites[x][y] = None

    # render the death screen, one big "YOU DIED"
    def death_screen(self, screen_width, screen_height):
        stop_texture = YOU_DIED_SPRITE_PATH
        self.death_screen_image = Image(stop_texture, -10, -10, screen_width + 20, screen_height - 2 * TILE_SIZE + 20, self.view)
