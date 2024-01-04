from character import Character


class Enemy(Character):
    def __init__(self, x, y, hp=10, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "e"

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_position(self):
        return self.x, self.y

    def get_center(self):
        TILE_SIZE = 32
        ecx = self.x * TILE_SIZE + TILE_SIZE // 2
        ecy = self.y * TILE_SIZE + TILE_SIZE // 2
        return ecx, ecy