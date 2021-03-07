NOT_FOUND = -1
ITEMS_HASH_SIZE = 8192
TABLES_HASH_SIZE = 128
NPC_HASH_SIZE = 1024

class hashTable:
    def __init__(self, tableSize, stringDictIndex):
        self.dictIndex = stringDictIndex
        self.size = tableSize
        self.data = [None] * self.size

    # Private functions to hash/rehash (if needed) each string
    def __hashFunction(self, stringData):
        hashValue = 0
        counter = 1
        for charInstance in stringData:
            hashValue += counter * ord(charInstance)
            counter += 1

        return hashValue % self.size

    def __rehashFunction(self, oldValue, rehashCounter):
        return (oldValue + rehashCounter ** 2) % self.size

    # Public function to add a dictionary in data list
    def add(self, stringData, stringDict):
        hashIndex = self.__hashFunction(stringData)

        if self.data[hashIndex] == None:
            self.data[hashIndex] = stringDict
            return
        else:
            rehashCounter = 1
            nextIndex = self.__rehashFunction(hashIndex, rehashCounter)
            while self.data[nextIndex] != None:
                rehashCounter += 1
                nextIndex = self.__rehashFunction(hashIndex, rehashCounter)
            if self.data[nextIndex] == None:
                self.data[nextIndex] = stringDict
                return


    # Public function to search a dictionary from a string
    def search(self, stringData, dictIndexToReturn):
        hashIndex = self.__hashFunction(stringData)

        if (self.data[hashIndex] != None):
            if self.data[hashIndex][self.dictIndex] == stringData:
                return self.data[hashIndex][dictIndexToReturn]
            else:
                rehashCounter = 1
                nextIndex = self.__rehashFunction(hashIndex, rehashCounter)
                while (self.data[nextIndex] != None) and (self.data[nextIndex][self.dictIndex] != stringData):
                    rehashCounter += 1
                    nextIndex = self.__rehashFunction(hashIndex, rehashCounter)
                if self.data[nextIndex] == None:
                    return NOT_FOUND
                elif self.data[nextIndex][self.dictIndex] == stringData:
                    return self.data[nextIndex][dictIndexToReturn]
        else:
            return NOT_FOUND
