import random


def order(n, seed):
    xs = list(range(n))
    random.Random(seed).shuffle(xs)
    return xs
