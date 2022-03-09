'''
Attacks:
This file is to hold all of the functions that perform attacks against a set of given hashesh.
'''

from KrakenTools import generateHash

# TODO: I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.
# I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.
# FIXME: strip screws up passwords with whitespace!
def compareHashes(text,hash, args) -> int:
  '''
  takes text and hashes it then compares it to the other hash. returns 1 if they are equal and 0 if they are not.
  This function also handles writting output to a file or displaying any of the information that is needed depending on
  args.
  text: string
  hash: a hash
  args: args from docopt
  '''
  text = text.rstrip('\n')
  hash = hash.rstrip('\n')

  # write to file
  if args['-o']:
    with open(args['-o'],mode='a+') as f:
      if generateHash(text,args) == hash:
        if not args['-q']:
          print(f'Success: {text} : {hash}')
        f.write(f'Success: {text} : {hash}\n')
        return 1
      else:
        if args['-v']:
          if not args['-q']:
            print(f'Fail: {text} : {hash}')
          f.write(f'Fail: {text} : {hash}\n')
        return 0

  # Only print result to terminal
  elif not args['-q']:
    if generateHash(text,args) == hash:
      print(f'Success: {text} : {hash}')
      return 1
    else:
      if args['-v']:
        print(f'Fail: {text} : {hash}')
      return 0

  # do not display results or write to file
  else:
    return generateHash(text,args) == hash


def wordListAttackSingleHash(args):
  '''
  Launch a wordlist attack on a single hash.
  '''
  with open(args['--wordList'],'r') as wordList:
    for word in wordList:
      if compareHashes(word,args['--hash'],args):
        break

def wordListAttackMultipleHashes(args):
  '''
  Launch a wordlist attack on a set of hashes.
  '''
  with open(args['--wordList'],'r') as wordList, open(args['--hashFile'],'r') as hashFile:
    for word in wordList:
      #??? is it faster to do this for loop or to create a list from the hashlist and loop through that?
      hashFile.seek(0)
      for hash in hashFile:
        hash = hash.strip()
        if compareHashes(word,hash,args) and args['--greed']:
          return

def bruteForceSingleHash(CGen, args):
  '''
  Launch a brute force attack against a single hash by generating our own text. Generation is specified in Kraken.config.
  combo: starting point for the text to be generated
  args: arguments from docopt
  CGen: CombinationGenerator object.
  *** printing out significantly slows down the process.
  '''
  counter = 0
  combo = CGen.firstCombination
  while(combo != CGen.lastCombination):
      if compareHashes(combo,args['--hash'],args):
          return
      combo = CGen.nextCombination(combo)
  compareHashes(combo,args['--hash'],args)

def bruteForceMultipleHash(CGen, args):
  '''
  Launch a brute force attack against a list of hashes by generating our own text. Generation is specified in Kraken.config.
  combo: starting point for the text to be generated
  args: arguments from docopt
  '''
  stopPoint = CGen.firstCombination
  with open(args['--hashFile']) as hashFile:
    combo = CGen.firstCombination
    while True:

      #compare to every hash in the file
      hashFile.seek(0)
      for hash in hashFile:
        if compareHashes(combo,hash,args) and args['--greed']:
          return

      # stop once the final combination has been generated
      combo = CGen.nextCombination(combo)
      if combo == stopPoint:
        break
