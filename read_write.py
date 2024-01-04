# TODO read out stats
# TODO ask if player wants to safe score
# TODO sort for high score, make list
# TODO Idea, write a) programm that plays the game or b) write a reinforcement learning programm that place the game
# TODO Idea: write a custom level builder
# TODO full screen
def write_down_stats(level, time, score, total_score):
    name = input("What's your name?\n")
    with open("score.txt", "a") as file:
        file.write(f"{name}\nreached level: {level}\nin: {time}s\nscore of: {score}/{total_score}\n---\n")


if __name__ == '__main__':
    write_down_stats(2, 2, 2, 2)
