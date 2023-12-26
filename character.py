class Character:

    def __init__(self, canvas):
        self.canvas = canvas
        self._hp = None
        self._x_pos = None
        self._y_pos = None
        self._damage = None

    def set_hp(self):
        pass

    def set_x_pos(self):
        pass

    def set_y_pos(self):
        pass

    def set_damage(self):
        pass

    def drop_item(self):
        """
        executes the dropped() method of Item
        """
