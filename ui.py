import arcade
import time


class UI:
    def __init__(self, screen_height, screen_width, tile_size, start_time):
        self.ui_camera = arcade.Camera()

        self.tile_size = tile_size
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time

        self.hp_text = arcade.Text("", 8, screen_height - 24, arcade.csscolor.GREEN, 18, bold=True)
        self.score_text = arcade.Text("", 8 + 5 * tile_size + 16, screen_height - 24, arcade.csscolor.BLACK, 18)
        self.level_played_text = arcade.Text("", 8 + 10 * tile_size + 16, screen_height - 24, arcade.csscolor.BLACK, 18)
        self.time_text = arcade.Text("", 8 + 14 * tile_size, screen_height - 24, arcade.csscolor.BLACK, 18)

    def set_up(self, hero_hp, hero_max_hp, coins_collected, total_num_coins, levels_played):
        self.update_hp_display(hero_hp, hero_max_hp)
        self.update_score(coins_collected, total_num_coins)
        self.update_levels_played(levels_played)
        self.update_display_time()

    def update_hp_display(self, hero_hp, hero_max_hp):
        # TODO else what?
        if hero_hp > 0:
            self.hp_text.text = f"HP: {hero_hp:.1f} / {hero_max_hp}"

    def update_score(self, coins_collected, total_num_coins):
        self.score_text.text = f"Score: {coins_collected} / {total_num_coins}"

    def update_levels_played(self, levels_played):
        self.level_played_text.text = f"Level: {levels_played}"

    def update_display_time(self):
        self.time_text.text = f"Time: {round(time.time() - self.start_time, 1)}"

    # background square and text for num_coins_collected, time and hp displayed on the top
    def draw_ui(self):
        self.ui_camera.use()

        # used as a background to draw on
        arcade.draw_rectangle_filled(0, self.screen_height - self.tile_size / 2, self.screen_width * 2, self.tile_size, arcade.csscolor.SADDLE_BROWN)

        self.hp_text.draw()
        self.score_text.draw()
        self.level_played_text.draw()
        self.time_text.draw()
