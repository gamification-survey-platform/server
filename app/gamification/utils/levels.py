import math

BASE_POINTS = 50
GROWTH_FACTOR = 2

def level_func(level):
    return BASE_POINTS * (GROWTH_FACTOR ** (level - 1))

def inv_level_func(exp):
    if exp < BASE_POINTS / GROWTH_FACTOR:
        return 0
    return math.floor(math.log(exp / (BASE_POINTS / GROWTH_FACTOR))/math.log(2))
