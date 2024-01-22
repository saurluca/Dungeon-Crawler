"""
This file includes the UI class, which provides a graphical user interface for the game, displaying and updating player
statistics like health, food, and experience through dynamic bars and icons.
"""

import time
from algoviz.svg.shapes import Image, Text, Rect
import math

# Define dictionary with paths to textures for different states of the food bar.
FOOD_BAR_TEXTURES = {
    'full': "Tiles/food_bar_full.png",
    'half': "Tiles/food_bar_half.png",
    'empty': "Tiles/food_bar_empty.png"
}
FOOD_BAR_LENGTH = 5  # Set the length of the food bar (number of icons).

# Define dictionary with paths to textures for different states of the HP bar.
HP_BAR_TEXTURES = {
    'full': "Tiles/hp_full.png",
    'half': "Tiles/hp_half.png",
    'empty': "Tiles/hp_empty.png"
}
HP_PER_HEART = 20  # Set the HP per heart icon.

# Define a dictionary with paths to textures for the XP bar.
XP_BAR_TEXTURES = {
    'full': "Tiles/xp_full.png",
    'empty': "Tiles/xp_empty.png"
}

ICON_SCALING = 1.1  # Define a size scaling factor for the icons.
ICON_TEXT_RGB = (0, 0, 0)  # Define the RGB color value for the icon texts.


# Define a User Interface (UI) class to handle the display of different UI elements.
class UI:
    def __init__(self, view, tile_size, tile_num_x, tile_num_y, start_time, hero):
        # Store various properties for use in drawing the UI.
        self.tile_size = tile_size
        self.tile_num_x = tile_num_x
        self.tile_num_y = tile_num_y
        self.start_time = start_time
        self.view = view

        # Create a background rectangle for the UI at the bottom of the view.
        self.background = Rect(0, tile_num_y * tile_size, tile_num_y * tile_size, 3 * tile_size, view)
        self.background.set_fill_rgb(200, 200, 150, 1)

        # Calculate and store Y coordinates for the experience bar, icons, and bars for consistency.
        self.xp_y = tile_num_y * tile_size
        self.icon_y = (tile_num_y + 1.75) * tile_size
        self.bar_y = (tile_num_y + 0.6) * tile_size

        # Calculate and store X coordinates for various UI elements based on the tile size and number.
        self.armor_x = (tile_num_x - 2) * tile_size - 5
        self.floor_x = (tile_num_x - 4.75) * tile_size
        self.score_x = (tile_num_x - 10) * tile_size
        self.damage_x = (tile_num_x - 12.5) * tile_size
        self.hp_x = self.damage_x
        self.food_x = 5

        self.text_offset = 13  # Define a constant offset for text position adjustments.

        # Create and position text objects for time and level, then set their color.
        self.time_text = Text(5, self.icon_y + self.text_offset, "", view)
        self.time_text.set_color_rgb(*ICON_TEXT_RGB)
        self.level_text = Text(tile_size * 5, self.icon_y + self.text_offset, "", view)
        self.level_text.set_color_rgb(*ICON_TEXT_RGB)

        # Create and position images for armor, current_score, floor, and damage icons, then place associated text.
        self.armor_image = Image("Tiles/armor.png", self.armor_x, self.icon_y, tile_size * ICON_SCALING,
                                 tile_size * ICON_SCALING, view)
        self.armor_text = Text(self.armor_x + tile_size * 1.1, self.icon_y + self.text_offset, "", view)
        self.armor_text.set_color_rgb(*ICON_TEXT_RGB)

        self.score_image = Image("Tiles/point.png", self.score_x, self.icon_y, tile_size * ICON_SCALING + 2,
                                 tile_size * ICON_SCALING + 2, view)
        self.score_text = Text(self.score_x + tile_size * 1.3, self.icon_y + self.text_offset, "", view)
        self.score_text.set_color_rgb(*ICON_TEXT_RGB)

        self.floor_image = Image("Tiles/door.png", self.floor_x, self.icon_y, tile_size, tile_size, view)
        self.floor_text = Text(self.floor_x + tile_size * 1.25, self.icon_y + self.text_offset, "", view)
        self.floor_text.set_color_rgb(*ICON_TEXT_RGB)

        self.damage_image = Image("Tiles/axe.png", self.damage_x, self.icon_y, tile_size * ICON_SCALING,
                                  tile_size * ICON_SCALING, view)
        self.damage_text = Text(self.damage_x + tile_size * 1.2, self.icon_y + self.text_offset, "", view)
        self.damage_text.set_color_rgb(*ICON_TEXT_RGB)

        # Calculate the number of slots in the health bar based on the hero's maximum health and initial HP per heart icon.
        self.hp_bar_length = int(hero.max_hp / HP_PER_HEART)
        self.hp_bar = ["full"] * int(self.hp_bar_length)
        self.hp_bar_images = None
        self.draw_hp_bar()  # Call method to draw the health bar.

        # Initialize the food bar with the maximum number of "full" icons and call method to draw it.
        self.food_bar = ["full"] * FOOD_BAR_LENGTH
        self.food_bar_images = None
        self.draw_food_bar()

        # Initialize the XP bar with "empty" slots based on the horizontal tile count and call method to draw it.
        self.xp_bar_length = tile_num_x
        self.xp_bar = ["empty"] * self.xp_bar_length
        self.xp_bar_images = None
        self.draw_xp_bar()

    # draws the food bar with images representing the current state of food points.
    def draw_food_bar(self):
        food_bar = []
        # Iterate over the defined number of elements in the food bar.
        for i in range(FOOD_BAR_LENGTH):
            # Create an image representing the current state (full, half, or empty) at the correct position.
            food_bar.append(
                Image(FOOD_BAR_TEXTURES[self.food_bar[i]], self.food_x + 15 * i, self.bar_y, self.tile_size,
                      self.tile_size,
                      self.view))
        # Save the list of images that comprise the food bar.
        self.food_bar_images = food_bar

    # sets the state of the food bar based on the provided food points.
    def set_food_bar(self, food_points):
        food_points = math.ceil(food_points)  # Round up the number of food points.
        for i in range(FOOD_BAR_LENGTH):
            # Determine whether the food slot should be full, half, or empty based on remaining food points.
            if food_points >= 2:
                self.food_bar[i] = "full"
                food_points -= 2
            elif food_points == 1:
                self.food_bar[i] = "half"
                food_points -= 1
            else:
                self.food_bar[i] = "empty"

    # This method draws the HP bar with images representing the current HP.
    def draw_hp_bar(self):
        hp_bar = []
        # Iterate over the defined number of hearts in the HP bar.
        for i in range(self.hp_bar_length):
            hp_bar_x = self.hp_x + (self.tile_size - 3) * i
            # Create an image for each heart icon at the correct position.
            hp_bar.append(Image(HP_BAR_TEXTURES[self.hp_bar[i]], hp_bar_x, self.bar_y, self.tile_size, self.tile_size,
                                self.view))
        # Save the list of images that make up the HP bar.
        self.hp_bar_images = hp_bar

    # This method sets the state of the HP bar based on current HP and maximum HP.
    def set_hp_bar(self, hp_points, max_hp):
        # Calculate the HP to display, rounding up to the nearest half-heart increment.
        hp_display = math.ceil(hp_points / (HP_PER_HEART // 2)) * (HP_PER_HEART // 2)
        # Recalculate the HP bar length based on the new maximum HP.
        self.hp_bar_length = int(math.ceil(max_hp / HP_PER_HEART))
        self.hp_bar = ["empty"] * self.hp_bar_length
        # Set the state of each heart icon in the HP bar.
        for i in range(self.hp_bar_length):
            if hp_display >= HP_PER_HEART:
                self.hp_bar[i] = "full"
                hp_display -= HP_PER_HEART
            elif hp_display >= HP_PER_HEART // 2:
                self.hp_bar[i] = "half"
                hp_display -= HP_PER_HEART // 2

    # This method initiates the drawing of the XP bar.
    def draw_xp_bar(self):
        xp_bar = []
        # Iterate over the XP bar length.
        for i in range(self.xp_bar_length):
            xp_bar_x = self.tile_size * i
            # Create an image for each XP slot at the correct position.
            xp_bar.append(
                Image(XP_BAR_TEXTURES[self.xp_bar[i]], xp_bar_x, self.xp_y, self.tile_size, self.tile_size / 2 - +1,
                      self.view))
        # Save the list of images that make up the XP bar.
        self.xp_bar_images = xp_bar

    # This method sets the state of the XP bar based on current XP points.
    def set_xp_bar(self, xp_points, xp_to_next_level, xp_past_level):
        # Calculate the XP points represented by each icon in the bar.
        xp_per_icon = self.calculate_xp_per_icon(xp_to_next_level, xp_past_level)
        # Subtract the XP earned in previous levels to start fresh for the current level.
        xp_points -= xp_past_level
        # Set the state of each icon in the XP bar.
        for i in range(self.xp_bar_length):
            if xp_points >= xp_per_icon:
                self.xp_bar[i] = "full"
                xp_points -= xp_per_icon
            else:
                self.xp_bar[i] = "empty"

    # Calculate the amount of XP represented by each icon in the XP bar.
    def calculate_xp_per_icon(self, xp_to_next_level, xp_past_level):
        return (xp_to_next_level - xp_past_level) / self.xp_bar_length

    # This method updates UI elements like level, damage, armor, etc. based on the current game status.
    def update(self, hero, current_score, possible_score, on_floor):
        self.update_level(hero.level)
        self.update_damage(hero.damage)
        self.update_armor(hero.armor)
        self.update_food_bar(hero.food_points)
        self.update_hp_bar(hero.hp, hero.max_hp)
        self.update_xp_bar(hero.current_xp, hero.xp_to_next_level[hero.level], hero.xp_to_next_level[hero.level - 1])
        self.update_score(current_score, possible_score)
        self.update_floor_text(on_floor)
        self.update_display_time()

    # This method updates the level text with the hero's current level.
    def update_level(self, hero_level):
        self.level_text.set_text(f"Lvl: {hero_level}")

    # This method updates the damage text with the hero's current damage.
    def update_damage(self, damage):
        self.damage_text.set_text(f": {damage}")

    # This method updates the armor text with the hero's current armor value.
    def update_armor(self, armor):
        self.armor_text.set_text(f": {armor}")

    # This method updates the food bar based on the current food points.
    def update_food_bar(self, food_points):
        self.set_food_bar(food_points)
        self.draw_food_bar()

    # This method updates the HP bar based on the hero's current HP and max HP.
    def update_hp_bar(self, hp_points, max_hp_points):
        self.set_hp_bar(hp_points, max_hp_points)
        self.draw_hp_bar()

    # This method updates the XP bar based on the hero's current XP and the thresholds for the next and previous levels.
    def update_xp_bar(self, xp_points, xp_to_next_level, xp_past_level):
        self.set_xp_bar(xp_points, xp_to_next_level, xp_past_level)
        self.draw_xp_bar()

    # This method updates the current_score display with the current and possible current_score.
    def update_score(self, current_score, possible_score):
        self.score_text.set_text(f": {current_score[0]} / {possible_score}")

    # This method updates the floor text to display the current floor.
    def update_floor_text(self, on_floor):
        self.floor_text.set_text(f": {on_floor}")

    # This method updates the display with the time elapsed since the start of the game.
    def update_display_time(self):
        # Note: The 'time' module is required to use 'time.time()'.
        self.time_text.set_text(f"Time: {int(time.time() - self.start_time)}")
