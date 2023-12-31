from character import Character


class Hero(Character):
    def __init__(self, x, y, hp=20, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "H"

