/* Chance Lopata
    This file handles everything to do with generating the next combination
    to us for creating the next hash.
*/

#include <string>
#include <iostream>
#include <map>
using namespace std;

// all possible unique characters that could be involved in creating the hash.
char characters[] = {'a','b','c','d'};

// Maps character in characters to its index.
map <char,int> characterMap = { {'a',0},
                                {'b',1},
                                {'c',2},
                                {'d',3}};

/***********************************************************
* Take a char from characters[] and return the character 
* in the next index. Wrap to begining if needed.
***********************************************************/
char rotateCharacter(char c)
{
    int nextCharIndex = characterMap[c] + 1;
    if (nextCharIndex > sizeof(characters)-1)
        nextCharIndex = 0;
    return characters[nextCharIndex];
}

/***********************************************************
* Start with the rightmost char and rotates it.
* repeate until the rotation does not wrap.
************************************************************/
string generateNextCombination(string combination)
{
    for (int i = sizeof(characters)-1; i >= 0; i--)
    {
        combination[i] = rotateCharacter(combination[i]);
        if (combination[i] != 'a')
            break;
    }
    return combination;
}