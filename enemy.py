from character import Character


class Enemy(Character):
    def __init__(self, x, y, hp, damage):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "E"
