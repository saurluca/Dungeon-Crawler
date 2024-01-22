"""
unused class. possible implementation: write down game stats in the end of a game in current_score.txt
"""


def write_down_stats(level, time, score, total_score):
    name = input("What's your name?\n")
    with open("score.txt", "a") as file:
        file.write(f"{name}\nreached level: {level}\nin: {time}s\nnum_coins_collected of: {score}/{total_score}\n---\n")


if __name__ == '__main__':
    write_down_stats(2, 2, 2, 2)
