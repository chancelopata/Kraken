''' Chance Lopata
    This file handles everything to do with generating the next combination
    to us for creating the next hash.
'''

from lib2to3.pgen2.token import EQUAL
from pydoc import doc
import configparser
from typing import Counter

from numpy import partition

# TODO: Create a generator object that holds the characterList, max and min string sizes and can come up with the first and last combinations.
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
        
    def rotateCharacter(self,c):
        nextIndex = self.rotationDict[c] + 1
        if len(self.characterList) <= nextIndex:
            nextIndex = 0
        return self.characterList[nextIndex]

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
        for i, e in enumerate(combo):
            nextCombo += self.rotateCharacter(e)
            if nextCombo[i] != self.characterList[0]:
                nextCombo += combo[i+1:]
                break
        return nextCombo
    
    def divideRoughly(self,n):
        partitionSize =  len(self.characterList)/n

        partition = list()
        partition.append(self.firstCombination())
        

        #partition[0] = self.characterList[0]*