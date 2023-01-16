import itertools


def lmap(f, items):
    return list(map(f, items))


def flatmap(f, items):
    return list(itertools.chain.from_iterable(lmap(f, items)))
