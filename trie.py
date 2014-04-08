# naive trie implementation using python dictionary lookups

class Node(object):
    def __init__(self):
        self.letters = {}
        self.isWord = False

    # adds letter
    # returns Node (create if doesn't already exist)
    def addLetter(self, letter):
        if letter in self.letters:
            return self.letters[letter]
        self.letters[letter] = Node()
        return self.letters[letter]

class Trie(object):
    def __init__(self):
        self.root = Node()

    def loadWord(self, word):
        curRef = self.root

        # traverse through links
        for letter in word:
            curRef = curRef.addLetter(letter)

        # mark end Node as a word
        curRef.isWord = True

    # load file of words, each on new line
    def loadFile(self, fileName):
        f = open(fileName)
        for line in f.readlines():
            word = line.strip()
            self.loadWord(word)
        f.close()

    def __printRecursive(self, node, prefix):
        # base case: empty dict
        if node.letters == {}:
            print prefix
            return

        if node.isWord:
            print prefix

        # traverse nodes of sorted keys
        sortedKeys = sorted(node.letters.keys())
        for letter in sortedKeys:
            self.printRecursive(node.letters[letter], prefix+letter)

    # wrapper around printRecursive
    def printWords(self):
        self.__printRecursive(self.root, '')

    # checks for word existence in trie
    def hasWord(self, word):
        curRef = self.root
        for letter in word:
            if letter in curRef.letters:
                curRef = curRef.letters[letter]
            else:
                return False
        if curRef.isWord:
            return True
        return False

def main():
    print "Loading dictionary file..."
    t = Trie()
    t.loadFile('dictionary.txt')
    print "Dictionary loaded.\n"

if __name__ == '__main__':
    main()
