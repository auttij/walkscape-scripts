from math import floor
import csv

def xp_equate(level):
    return floor(level + 300 * 2**(level/7))

def xp_to_level_character(level):
    xp = 0
    for i in range(1, level):
        xp += xp_equate(i)
    return floor(xp / 4) * 4.6

def main():
    for lvl in range(1, 100):
        xp = xp_to_level_character(lvl)
        xp_formatted = "{:,.0f}".format(xp)
        print(f"{xp_formatted}")

if __name__ == "__main__":
    main()