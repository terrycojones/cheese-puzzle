#!/usr/bin/env python

# Hole sizes.
TINY = 0
SMALL = 1
MEDIUM = 2
LARGE = 3

# Portion of hole.
MAJOR = 4
MINOR = 5

NAMES = ['tiny', 'small', 'medium', 'big', 'major', 'minor']


class Hole:
    def __init__(self, size, portion):
        self.size = size
        self.portion = portion

    def matches(self, other):
        return self.size == other.size and self.portion != other.portion

    def __str__(self):
        return '(%s, %s)' % (NAMES[self.size], NAMES[self.portion])


class Tile:
    def __init__(self, number, top, right, bottom, left, rotationCount=0, flipped=False):
        # top, right, bottom, left are all instances of Hole.
        self.number = number
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.rotationCount = rotationCount
        self.flipped = flipped

    def flip(self):
        return Tile(self.number, self.top, self.left, self.bottom, self.right, flipped=True)

    def rotations(self):
        return [
            # Starting from self, rotate clockwise.
            Tile(self.number, self.top,    self.right,  self.bottom, self.left,   rotationCount=0, flipped=self.flipped),
            Tile(self.number, self.left,   self.top,    self.right,  self.bottom, rotationCount=1, flipped=self.flipped),
            Tile(self.number, self.bottom, self.left,   self.top,    self.right,  rotationCount=2, flipped=self.flipped),
            Tile(self.number, self.right,  self.bottom, self.left,   self.top,    rotationCount=3, flipped=self.flipped)
        ]

    def arrangements(self):
        return self.rotations() + self.flip().rotations()

    def __str__(self):
        return 'Tile %d (rotated %d, flipped %s): top=%s right=%s bottom=%s left=%s' % (
            self.number, self.rotationCount, self.flipped, self.top, self.right, self.bottom, self.left)


class State:
    def __init__(self):
        self.tiles = []

    def compatible(self, tile):
        n = len(self.tiles)

        if n == 0:
            return True
        if n == 1:
            return self.tiles[0].right.matches(tile.left)
        if n == 2:
            return self.tiles[1].right.matches(tile.left)
        if n == 3:
            return self.tiles[0].bottom.matches(tile.top)
        if n == 4:
            return self.tiles[3].right.matches(tile.left) and self.tiles[1].bottom.matches(tile.top)
        if n == 5:
            return self.tiles[4].right.matches(tile.left) and self.tiles[2].bottom.matches(tile.top)
        if n == 6:
            return self.tiles[3].bottom.matches(tile.top)
        if n == 7:
            return self.tiles[6].right.matches(tile.left) and self.tiles[4].bottom.matches(tile.top)
        if n == 8:
            return self.tiles[7].right.matches(tile.left) and self.tiles[5].bottom.matches(tile.top)

    def add(self, tile):
        self.tiles.append(tile)

    def removeLast(self):
        self.tiles.pop()

    def __str__(self):
        result = []
        for index, tile in enumerate(self.tiles):
            result.append('%d: %s' % (index, tile))
        return '\n'.join(result)


def solve(state, unused):
    if len(unused) == 0:
        print 'SOLUTION:\n%s' % state
    else:
        for tile in list(unused):
            unused.remove(tile)
            for arrangement in tile.arrangements():
                if state.compatible(arrangement):
                    state.add(arrangement)
                    solve(state, unused)
                    state.removeLast()
            unused.add(tile)


if __name__ == '__main__':
    state = State()
    unused = set([
        Tile(1, Hole(TINY,  MAJOR), Hole(MEDIUM, MAJOR), Hole(SMALL,  MINOR), Hole(MEDIUM, MINOR)),
        Tile(2, Hole(SMALL, MINOR), Hole(MEDIUM, MINOR), Hole(TINY,   MAJOR), Hole(LARGE,  MAJOR)),
        Tile(3, Hole(TINY,  MINOR), Hole(SMALL,  MAJOR), Hole(MEDIUM, MAJOR), Hole(LARGE,  MINOR)),
        Tile(4, Hole(TINY,  MAJOR), Hole(LARGE,  MAJOR), Hole(SMALL,  MINOR), Hole(LARGE,  MINOR)),
        Tile(5, Hole(SMALL, MINOR), Hole(LARGE,  MAJOR), Hole(TINY,   MAJOR), Hole(MEDIUM, MINOR)),
        Tile(6, Hole(TINY,  MINOR), Hole(LARGE,  MINOR), Hole(MEDIUM, MAJOR), Hole(SMALL,  MAJOR)),
        Tile(7, Hole(SMALL, MINOR), Hole(MEDIUM, MAJOR), Hole(LARGE,  MAJOR), Hole(TINY,   MINOR)),
        Tile(8, Hole(TINY,  MAJOR), Hole(LARGE,  MAJOR), Hole(LARGE,  MINOR), Hole(SMALL,  MINOR)),
        Tile(9, Hole(TINY,  MINOR), Hole(TINY,   MAJOR), Hole(SMALL,  MAJOR), Hole(LARGE,  MINOR)),
    ])
    solve(state, unused)
