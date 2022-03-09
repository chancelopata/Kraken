'''
Attacks Parallel:
This file is to hold all of the functions that perform attacks against a set of given hashesh using more than one process.
'''

from generateHash import generateHash
import itertools
# TODO: I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.
# I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.

def compareHashesThreadSafe(text,hash, args, q) -> int:
  '''
  takes text and hashes it then compares it to the other hash. returns 1 if they are equal and 0 if they are not.
  Generates a message and stacks it on a queue.
  text: unhashed string
  hash: a hash
  args: args from docopt
  q: mp.queue
  '''
  text = text.rstrip('\n')
  hash = hash.rstrip('\n')
  if generateHash(text,args) == hash:
    q.put(f'Success: {text} : {hash}')
    return 1
  else:
    if args['-v']:
      q.put(f'Fail: {text} : {hash}')
    return 0

def writeOutput(args, q):
  '''
  Takes an item from a queue and prints it out / writes it to a file based on whats in args. Designed
  for multithreading. Will terminate once a blank string is pulled from q.
  args: args from docopt
  q: mp.queue
  '''
  # FIXME: should probably figure out which encoding this needs to be

  # run this if it needs to write to a file
  if args['-o']:
    with open(args['-o'],mode='w+') as f:
      while True:
        msg = q.get()
        if msg != '':
          if not args['-q']:
            print(msg)
          f.write(msg +'\n')
        else:
          return
  # run this if it does not need to write to a file.
  elif not args['-q']:
    while True:
        msg = q.get()
        if msg != '':
          print(msg)
        else:
          return

#################
# NEEDS TO WORK #
#################
def bruteForceSingleHash(CGen, args, q):
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
      if compareHashesThreadSafe(combo,args['--hash'],args,q):
          return
      combo = CGen.nextCombination(combo)
  compareHashesThreadSafe(combo,args['--hash'],args,q)

def parallelWordListAttackSingleHash(args, chunk):
  '''
  Launch a wordlist attack on a single hash.
  '''
  with open(chunk,mode='r',encoding='latin-1') as wordList:
    for word in wordList:
      if compareHashesThreadSafe(word,args['--hash'],args):
        break

def parallelWordListAttackMultipleHashes(args,chunk,q):
  '''
  Launch a wordlist attack on a set of hashes.
  '''
  with open(chunk,mode='r',encoding='latin-1') as wordList, open(args['--hashFile'],'r') as hashFile:
    for word in wordList:      
      #??? is it faster to do this for loop or to create a list from the hashlist and loop through that?
      hashFile.seek(0)
      for hash in hashFile:
        compareHashesThreadSafe(word,hash,args,q)