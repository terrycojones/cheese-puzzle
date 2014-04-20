#!/usr/bin/env python

from PIL import Image

count = 0
solutions = 0

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

    def __eq__(self, other):
        return self.size == other.size and self.portion == other.portion

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

    def matches(self, other):
        return self.top == other.top and self.right == other.right and self.bottom == other.bottom and self.left == other.left

    # def __str__(self):
    #     return 'Tile %d (rotated %d, flipped %s): top=%s right=%s bottom=%s left=%s' % (
    #         self.number, self.rotationCount, self.flipped, self.top, self.right, self.bottom, self.left)

    def __str__(self):
        return 'Tile %d (rotated %d, flipped %s)' % (self.number, self.rotationCount, self.flipped)


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

    def __contains__(self, number):
        for tile in self.tiles:
            if tile.number == number:
                return True
        return False

    def add(self, tile):
        self.tiles.append(tile)

    def removeLast(self):
        self.tiles.pop()

    def __str__(self):
        result = []
        for index, tile in enumerate(self.tiles):
            result.append('%d: %s' % (index, tile))
        return '\n'.join(result)


def saveImage(state, number):
    # All tiles are 550x550 pixels
    image = Image.new('RGB', (1650, 1650))
    for index, tile in enumerate(state.tiles):
        row = index / 3
        col = index % 3
        tileImage = Image.open('tile-%s.jpg' % tile.number)
        if tile.flipped:
            tileImage = tileImage.transpose(Image.FLIP_LEFT_RIGHT)
        if tile.rotationCount:
            tileImage = tileImage.rotate(-90 * tile.rotationCount)
        image.paste(tileImage, (col * 550, row * 550))
    image.save('solution-%02d.jpg' % number)


def solve(state, unused):
    global solutions, count
    if len(unused) == 0:
        solutions += 1
        print 'SOLUTION %d\n%s\n' % (solutions, state)
        saveImage(state, solutions)
    else:
        for index, tile in enumerate(unused):
            # Insist that 2 is in the state before 5, and 3 is in the state before 6. These
            # are due to tile symmetries found by findIdenticals.
            if (tile.number == 5 and 2 not in state) or (tile.number == 6 and 3 not in state):
                continue
            for arrangement in tile.arrangements():
                count += 1
                # Insist that tile 1 is not rotated or flipped, to eliminate symetries.
                if tile.number == 1 and (arrangement.rotationCount != 0 or arrangement.flipped):
                    continue
                if state.compatible(arrangement):
                    state.add(arrangement)
                    solve(state, unused[0:index] + unused[index + 1:])
                    state.removeLast()


def findIdenticals(tiles):
    seen = set()
    for index, tile in enumerate(tiles):
        if not tile.number in seen:
            print 'Tile %d equivalent to:' % tile.number,
            seen.add(tile.number)
            for other in tiles[index + 1:]:
                if not other.number in seen:
                    for arrangement in other.arrangements():
                        if tile.matches(arrangement):
                            seen.add(other.number)
                            print arrangement,
                            break
            print
    print


if __name__ == '__main__':
    state = State()
    unused = [
        Tile(1, Hole(TINY,  MAJOR), Hole(MEDIUM, MAJOR), Hole(SMALL,  MINOR), Hole(MEDIUM, MINOR)),
        Tile(2, Hole(SMALL, MINOR), Hole(MEDIUM, MINOR), Hole(TINY,   MAJOR), Hole(LARGE,  MAJOR)),
        Tile(3, Hole(TINY,  MINOR), Hole(SMALL,  MAJOR), Hole(MEDIUM, MAJOR), Hole(LARGE,  MINOR)),
        Tile(4, Hole(TINY,  MAJOR), Hole(LARGE,  MAJOR), Hole(SMALL,  MINOR), Hole(LARGE,  MINOR)),
        Tile(5, Hole(SMALL, MINOR), Hole(LARGE,  MAJOR), Hole(TINY,   MAJOR), Hole(MEDIUM, MINOR)),
        Tile(6, Hole(TINY,  MINOR), Hole(LARGE,  MINOR), Hole(MEDIUM, MAJOR), Hole(SMALL,  MAJOR)),
        Tile(7, Hole(SMALL, MINOR), Hole(MEDIUM, MAJOR), Hole(LARGE,  MAJOR), Hole(TINY,   MINOR)),
        Tile(8, Hole(TINY,  MAJOR), Hole(LARGE,  MAJOR), Hole(LARGE,  MINOR), Hole(SMALL,  MINOR)),
        Tile(9, Hole(TINY,  MINOR), Hole(TINY,   MAJOR), Hole(SMALL,  MAJOR), Hole(LARGE,  MINOR)),
    ]
    findIdenticals(unused)
    solve(state, unused)
    print 'Found %d solutions after testing %d configurations' % (solutions, count)
