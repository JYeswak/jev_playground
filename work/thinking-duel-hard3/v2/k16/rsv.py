import random


def sample(stream, k, seed):
    xs = list(stream)
    return random.Random(seed).sample(xs, k)
