from character import Character


class Hero(Character):
    def __init__(self, x=1, y=1, hp=20, damage=4):
        super().__init__(x, y, hp, damage)

    def __str__(self):
        return "H"

    def is_dead(self):
        if self.hp <= 0:
            return True
        else:
            return False
