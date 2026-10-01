import random


def sample_k(n, k, seed):
    return random.Random(seed).sample(range(n), k)
