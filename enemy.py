from character import Character


class Enemy(Character):
    def __init__(self, pos, hp=10, damage=2):
        super().__init__(pos, hp, damage)
        self.standing_on = ""
        self.visible = False

    def __str__(self):
        if self.standing_on != ".":
            return "E"+self.standing_on
        else:
            return "E"
