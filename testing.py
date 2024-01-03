class Level:
    def __init__(self, on_level_complete):
        self.on_level_complete = on_level_complete

    def update(self):
        # Level logic...
        a = 1
        print(1)
        if a == 0:
            self.on_level_complete()


# Usage from the Main function or class:
def handle_level_complete():
    print("Level complete! Load next level.")


current_level = Level(on_level_complete=handle_level_complete())
