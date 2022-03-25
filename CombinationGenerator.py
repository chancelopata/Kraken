''' Chance Lopata
    This file handles everything to do with generating the next combination
    to us for creating the next hash.
'''

import configparser

class CombinationGenerator():
    def __init__(self) -> None:

        config = configparser.ConfigParser()
        config.read('Kraken.config')

        self.characterList = config.get('DEFAULT','characterlist')
        self.maxStringSize = int(config.get('DEFAULT','maxstringsize'))
        self.minStringSize = int(config.get('DEFAULT','minstringsize'))

        self.firstCombination = self.minStringSize*self.characterList[0]
        self.lastCombination = self.maxStringSize*self.characterList[-1]
        
        counter = 0
        self.rotationDict = {}
        for char in self.characterList:
            self.rotationDict[char] = counter
            counter += 1
        
    def rotateCharacterN(self,c,n):
        carry = 0
        nextIndex = self.rotationDict[c] + n
        if len(self.characterList) <= nextIndex:
            nextIndex %= len(self.characterList)
            carry = 1
        elif nextIndex < 0:
            nextIndex = nextIndex+len(self.characterList)-1
            carry = -1
        return (self.characterList[nextIndex],carry)

    def nextCombination(self,combo):
        '''
        Generate the next combination of a given string. The string 'combo' here is treated much like number a base n number system. The 'next combination'
        is created by ticking a the number up one and returning that result. Unlike a base n number system, the ticking takes place on the left instead of the far right.
        This is simply because it is easier to implement and for the purpose of generating all possible combinations the result is the same.

        Given a combo, you can repeatedly call nextCombination on its own output to eventaully generate all combinations.

        combo: string with characters found in characterList.
        '''
        nextCombo = ''
        # Add an additional digit if at the max value for current digits
        if  combo != self.lastCombination and combo in self.lastCombination:
            nextCombo = self.characterList[0]*(len(combo)+1)
            return nextCombo

        # Tick the leftmost digit up one and carry over the '1' if needed.
        carry = 1
        for i, e in enumerate(combo):
            char, carry = self.rotateCharacterN(e,carry)
            nextCombo += char
            if not carry:
                nextCombo += combo[i+1:]
                break
        return nextCombo
    
    def add(self,n1,n2):
        '''
        Adds two numbers together of base 'n'. Bases must be equal and characterLists must be the same as well.
        n1 and n2 are both strings created by combinationGenerator. n1 is "added" to n2.

        Remember that the 'numbers' are still handled in reverse order for the sake of number generation.
        '''
        result = ''
        digits = zip(n1,n2)
        carry = 0
        for digit in digits:
            char, carry = self.rotateCharacterN(digit[0], self.rotationDict[digit[1]] + carry)
            result += char
        return result

    def subtract(self,n1,n2):
        '''
        Subtracts n2 from n1. Does not support negative numbers.
        '''
        result = ''
        digits = zip(n1,n2)
        carry = 0
        for digit in digits:
            char, carry = self.rotateCharacterN(digit[0], (-(self.rotationDict[digit[1]] - carry)))
            if carry < 0:
                char = (self.rotateCharacterN(char,1))[0] # this line fixes subtract not carrying correctly.
            result += char
        return result

    def greaterThan(self,n1,n2):
        '''
        Checks to see if n1 is greater than n2.
        if n1 > n2 then return 1
        if n1 <= n2 then return 0
        '''
        n1 = reversed(n1)
        n2 = reversed(n2)
        digits = zip(n1,n2)
        for pair in digits:
            n1Value = self.rotationDict[pair[0]]
            n2Value = self.rotationDict[pair[1]]
            if n1Value > n2Value:
                return 1
            elif n1Value < n2Value:
                return 0

    # untested
    def divide(self,n1,n2):
        '''
        divides n1 by n2
        '''
        result = 0

        while (self.greaterThan(n1,n2) or n1 == n2) and n2 != 'aaaa':
            n1 = self.subtract(n1,n2)
            result += 1
        return self.decimalToBaseN(result)
    
    # extremely cheesey way of doing this. If n > 10,000 need new algorithm
    def decimalToBaseN(self,n):
        result = self.characterList[0]*self.maxStringSize
        
        while n != 0:
            result = self.nextCombination(result)
            n -= 1
        return result

    def convertToDecimal(self,n):
        '''
        Converts a system of base n to a decimal integer.
        '''
        base = len(self.characterList)
        exponent = 0
        result = 0
        for char in n:
            result += (self.rotationDict[char]*base**exponent)
            exponent += 1
        return result
        
    def divideIntoChunks(self,n):
        nBaseN = self.decimalToBaseN(n)
        chunkSize =  self.divide(self.lastCombination,nBaseN)
        currentCombo = self.firstCombination
        chunks = [(currentCombo,chunkSize)]

        m = chunkSize
        for i in range(n-1):
            startPoint = m
            m = self.add(chunkSize,m)
            if i == (n-2):
                endPoint = self.lastCombination
            else:
                endPoint = m
            chunks.append((startPoint,endPoint))

        return chunks