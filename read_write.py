# TODO full screen
# TODO why the hell getter and setter functions again?

# TODO idea: write maze solving algorithm, to get good spots for spawning shit
# TODO idea: read out stats
# TODO idea: sort for high num_coins_collected, make list
# TODO Idea, write a) programm that plays the game or b) write a reinforcement learning programm that place the game
# TODO Idea: write a custom level builder
# TODO idea: different type of maze, with connecting passages?

def write_down_stats(level, time, score, total_score):
    name = input("What's your name?\n")
    with open("score.txt", "a") as file:
        file.write(f"{name}\nreached level: {level}\nin: {time}s\nnum_coins_collected of: {score}/{total_score}\n---\n")


if __name__ == '__main__':
    write_down_stats(2, 2, 2, 2)

# remove coins all together and put items into dead ends?
# easy to implement

# make possible to have to things on one tile in maze. coins not object, so maybe easily possible?
# advantage: can keep the coins

# put items into the dead ends, coins not objects, tf can save enemy easily with coin


