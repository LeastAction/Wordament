#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      MTJacobson
#
# Created:     06/04/2014
# Copyright:   (c) MTJacobson 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re
import trie
import time
import unittest

DICT_LOC = "D:\Coding\Python Codes\Wordament\dictionary.txt"

class Grid:
    SIZE = 4
    ADJACENT_POINTS = {(0,0):[(0,1),(1,0),(1,1)],
                       (0,1):[(0,0),(0,2),(1,0),(1,1),(1,2)],
                       (0,2):[(0,1),(0,3),(1,1),(1,2),(1,3)],
                       (0,3):[(0,2),(1,2),(1,3)],
                       (1,0):[(0,0),(0,1),(1,1),(2,0),(2,1)],
                       (1,1):[(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)],
                       (1,2):[(0,1),(0,2),(0,3),(1,1),(1,3),(2,1),(2,2),(2,3)],
                       (1,3):[(0,2),(0,3),(1,2),(2,2),(2,3)],
                       (2,0):[(1,0),(1,1),(2,1),(3,0),(3,1)],
                       (2,1):[(1,0),(1,1),(2,2),(2,0),(2,2),(3,0),(3,1),(3,2)],
                       (2,2):[(1,1),(1,2),(1,3),(2,1),(2,3),(3,1),(3,2),(3,3)],
                       (2,3):[(1,2),(1,3),(2,2),(3,2),(3,3)],
                       (3,0):[(2,0),(2,1),(3,1)],
                       (3,1):[(2,0),(2,1),(2,2),(3,0),(3,2)],
                       (3,2):[(2,1),(2,2),(2,3),(3,1),(3,3)],
                       (3,3):[(2,2),(2,3),(3,2)]}

    def __init__(self, tiles='abcdefghijklmnop'):
        self.tiles = []
        # regular expression to match letters or parenthesized groups
        r = re.compile(r'[a-z]|[(][a-z]+[)]', re.IGNORECASE)
        self.tiles = [x.strip('(').strip(')') for x in r.findall(tiles)]
        self.grid = [[self.tiles[r*Grid.SIZE+c] for c in range(Grid.SIZE)] for r in range(Grid.SIZE)]
        self.words = {}

    def recursiveSearchPoint(self, node, validPoints, curPoint, prefix, path, minLength=0):
        # base case
        if node.isWord and len(prefix) >= minLength: self.words[prefix] = path

        if prefix != '':
            # current nodes recreation path
            path.append(curPoint)

            # ensure we don't step in same square twice
            validPoints.remove(curPoint)

            # list possible steps to take
            validSteps = [point for point in Grid.ADJACENT_POINTS[curPoint] if point in validPoints]
        else: # if starting new recursion must check starting point first
            validSteps = [curPoint]


        # check if Trie path exists for each valid step
        for point in validSteps:
            x,y = point
            tile = self.grid[x][y]
            if tile in node.letters:
                stepNode = node.letters[tile]
                self.recursiveSearchPoint(stepNode,validPoints[:],point,prefix+tile,path[:],minLength)
            elif len(tile) > 1:
                # if case for tiles that include multiple letters
                stepNode = node
                for letter in tile: # branch off to check mutiple letters
                    if letter in stepNode.letters:
                        stepNode = stepNode.letters[letter]
                    else:
                        stepNode = trie.Node() # Empty node will make sure we go to the next valid step
                self.recursiveSearchPoint(stepNode,validPoints[:],point,prefix+tile,path[:],minLength)

    # find words in grid that exist in given trie
    def findDictionaryWords(self, loadedTrie, minLength=0):
        # path will contain the current searches path to recreate the word
        path = []

        # list valid points
        validPoints = [(x,y) for x in range(Grid.SIZE) for y in range(Grid.SIZE)]

        # iterate through starting points and find words
        for x in range(Grid.SIZE):
            for y in range(Grid.SIZE):
                self.recursiveSearchPoint(loadedTrie.root, validPoints[:], (x,y), '', path[:], minLength)

        self.sortedWords = sorted(self.words,key=len,reverse=True)

class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = Grid('abcd(br)gfhijklmnop')
        self.grid.findDictionaryWords(t,3)


    def test_findDictionaryWords(self):
        self.assertEqual(sorted(self.grid.words.keys()),['abri', 'agin', 'bag', 'bra', 'brag', 'brig', 'brim', 'brin', 'brink', 'flop', 'gab', 'gin', 'gink', 'ink', 'jig', 'jin', 'jink', 'knop', 'kop', 'lop', 'mig', 'mink', 'nim', 'plonk', 'pol'])

if __name__ == '__main__':
    print 'Loading dictionary into trie...'
    start = time.time()
    t = trie.Trie()
    t.loadFile(DICT_LOC)
    end = time.time()
    print "Loaded dictionary in %ss\n" % (end-start)
    unittest.main()
