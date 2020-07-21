
from collections import namedtuple
import re

Entry = namedtuple('Entry', ('key', 'value'))

'''
To make sure that the DELETED sentinel does not match
anything we actually want to have in the table, make it
a unique (content-free!) object.
'''


class _delobj: pass


DELETED = Entry(_delobj(), None)

class Hashmap:
    __slots__ = 'table', 'numkeys', 'cap', 'maxload', 'hashtype', 'probe', 'collision'

    def __init__(self, inittype, initsz=100, maxload=0.7):
        '''
        Creates an open-addressed hash map of given size and maximum load factor
        :param initsz: Initial size (default 100)
        :param maxload: Max load factor (default 0.7)
        '''
        self.cap = initsz
        self.table = [None for _ in range(self.cap)]
        self.numkeys = 0
        self.maxload = maxload
        self.hashtype = inittype
        self.probe = 0
        self.collision = 0


    def put(self, key, value):
        '''
        Adds the given (key,value) to the map, replacing entry with same key if present.
        :param key: Key of new entry
        :param value: Value of new entry
        '''
        firstDeleted = None  # we have to search through the whole line to to make sure we aren't adding duplicates

        if self.hashtype == 1:
            index = self.hash_func1(key) % self.cap
        elif self.hashtype == 0:
            index = self.hash_func(key) %self.cap
        else:
            index = self.hash_func2(key) % self.cap

        if self.table[index] is not None:
            self.probe += 1
            if self.contains(key):
                value = self.get(key) + 1
                while index < self.cap:
                    if self.table[index].key == key:
                        self.table[index] = Entry(key, value)
                        return None
                    index += 1
            else:
                self.collision += 1


        while self.table[index] is not None and \
                self.table[index].key != key:
            if self.table[index] == DELETED and firstDeleted == None:
                firstDeleted = index
            index += 1
            if index == len(self.table):
                index = 0
            if self.table[index] is not None:
                index += 1
                self.probe += 1
        # if we encountered a deleted and we didn't find the key change the key index to the first deleted index
        if firstDeleted != None and (self.table[index] == None or self.table[index].key != key):
            index = firstDeleted
        # otherwise if we haven't found the index then increase the size of the occupied cells
        elif self.table[index] is None:
            self.numkeys += 1

        self.table[index] = Entry(key, value)
        if self.numkeys / self.cap > self.maxload:

            # rehashing
            oldtable = self.table
            # refresh the table
            self.cap *= 2
            self.table = [None for _ in range(self.cap)]
            self.numkeys = 0
            # put items in new table
            for entry in oldtable:
                if entry is not None:
                    self.put(entry[0], entry[1])

    def remove(self, key):
        '''
        Remove an item from the table
        :param key: Key of item to remove
        :return: Value of given key
        '''
        if self.hashtype == 1:
            index = self.hash_func1(key) % self.cap
        elif self.hashtype == 0:
            index = self.hash_func(key) %self.cap
        else:
            index = self.hash_func2(key) % self.cap
        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            if index == len(self.table):
                index = 0
        if self.table[index] is not None:
            self.table[index] = DELETED

    def get(self, key):
        '''
        Return the value associated with the given key
        :param key: Key to look up
        :return: Value (or KeyError if key not present)
        '''
        if self.hashtype == 1:
            index = self.hash_func1(key) % self.cap
        elif self.hashtype == 0:
            index = self.hash_func(key) %self.cap
        else:
            index = self.hash_func2(key) % self.cap
        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            if index == self.cap:
                index = 0
        if self.table[index] is not None:
            return self.table[index].value
        else:
            raise KeyError('Key ' + str(key) + ' not present')

    def contains(self, key):
        '''
        Returns True/False whether key is present in map
        :param key: Key to look up
        :return: Whether key is present (boolean)
        '''
        if self.hashtype == 1:
            index = self.hash_func1(key) % self.cap
        elif self.hashtype == 0:
            index = self.hash_func(key) %self.cap
        else:
            index = self.hash_func2(key) % self.cap
        while self.table[index] is not None and self.table[index].key != key:
            index += 1
            if index == self.cap:
                index = 0
        return self.table[index] is not None

    def hash_func(self, key):
        '''
        Not using Python's built in hash function here since we want to
        have repeatable testing...
        However it is terrible.
        Assumes keys have a len() though...
        :param key: Key to store
        :return: Hash value for that key
        '''
        # if we want to switch to Python's hash function, uncomment this:
        return hash(key)
        #return len(key)

    def hash_func1(self, hashKey):
        """
        This was implemented in class (Lab - 8; Q2).
        :param hashKey: input key from the key,value pair to be inserted into the hash map
        :return hashOutput: Hashed output from the key which will be used to determine where/how to insert the (key,val) pair
        """
        keyLen = len(hashKey)
        index = 0
        hashOutput = 0
        while index < keyLen:
            hashOutput += ord(hashKey[index]) * 31 ** index
            index += 1

        return hashOutput

    def hash_func2(self, hashKey):
        """
        This was implemented in class (Lab - 8; Q1, Part 'c').
        :param hashKey: input key from the key,value pair to be inserted into the hash map
        :param mapSize: this is the size or the total number of slots in the map
        :return hashOutput: Hashed output from the key which will be used to determine where/how to insert the (key,val) pair
        """
        keyLen = len(hashKey)
        index = 0
        hashOutput = 0
        while index < keyLen:
            hashOutput += ord(hashKey[index])
            index += 1

        return hashOutput

def printMap(map):
    for i in range(map.cap):
        print(str(i) + ": " + str(map.table[i]))

def findMax(map):
    """
    find the word which appears the most in a hashmap.
    :return: word which appears the most and number of times it appears
    """
    index = 0
    max = 1
    wordMax = map.table[index]

    while index != map.cap:
        if map.table[index] != None:
            if map.table[index].value > max:
                max = map.table[index].value
                wordMax = map.table[index].key
        index += 1
    return wordMax, max

def testMapFile(filename, map0, map1, map2):
    f = open(filename, 'r')

    for line in f:
        wordList = re.split('\W+', line)
        for word in wordList:
            if word != '':
                map0.put(word.lower(), 1)
                map1.put(word.lower(), 1)
                map2.put(word.lower(), 1)
    print("Number of collisions with python's builtin hash function:", map0.collision)
    print("Number of collisions with hash_function1:", map1.collision)
    print("Number of collisions with hash_function2:", map2.collision)
    print("Number of probes with python's builtin hash function: ", map0.probe)
    print("Number of probes with hash_function1: ", map1.probe)
    print("Number of probes with hash_function2: ", map2.probe)


def testMap():
    print("------------------------------------Novel 1 -----------------------------------------")
    map0 = Hashmap(0, initsz=70000)
    map1 = Hashmap(1, initsz=70000)
    map2 = Hashmap(2, initsz=70000)

    testMapFile('EnglishNovels.txt', map0, map1, map2)

    temp = findMax(map0)
    print("The word which appears the maximum number of times (", temp[1], ") with python's builtin hash function is \"" + temp[0] + "\"")

    temp = findMax(map1)
    print("The word which appears the maximum number of times (", temp[1], ") with hash_function1 is \"" + temp[0] + "\"")

    temp = findMax(map2)
    print("The word which appears the maximum number of times (", temp[1], ") with hash_function2 is \"" + temp[0] + "\"")

    print("------------------------------------Novel 2 -----------------------------------------")
    map0 = Hashmap(0, initsz=70000)
    map1 = Hashmap(1, initsz=70000)
    map2 = Hashmap(2, initsz=70000)

    testMapFile('novels2.txt', map0, map1, map2)

    temp = findMax(map0)
    print("The word which appears the maximum number of times (", temp[1],
          ") with python's builtin hash function is \"" + temp[0] + "\"")

    temp = findMax(map1)
    print("The word which appears the maximum number of times (", temp[1],
          ") with hash_function1 is \"" + temp[0] + "\"")

    temp = findMax(map2)
    print("The word which appears the maximum number of times (", temp[1],
          ") with hash_function2 is \"" + temp[0] + "\"")

    print("------------------------------------Linux dictionnary -----------------------------------------")
    map0 = Hashmap(0, initsz=70000)
    map1 = Hashmap(1, initsz=70000)
    map2 = Hashmap(2, initsz=70000)

    testMapFile('Linuxdict.txt', map0, map1, map2)

    temp = findMax(map0)
    print("The word which appears the maximum number of times (", temp[1],
          ") with python's builtin hash function is \"" + temp[0] + "\"")

    temp = findMax(map1)
    print("The word which appears the maximum number of times (", temp[1],
          ") with hash_function1 is \"" + temp[0] + "\"")

    temp = findMax(map2)
    print("The word which appears the maximum number of times (", temp[1],
          ") with hash_function2 is \"" + temp[0] + "\"")

if __name__ == '__main__':
    testMap()
