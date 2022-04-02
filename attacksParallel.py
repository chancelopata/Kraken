'''
Attacks Parallel:
This file is to hold all of the functions that perform attacks against a set of given hashesh using more than one process.
'''

from KrakenTools import generateHash
# TODO: I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.
# I think if i perfect this code then i can reduce singlehash / multiple hash attacks into once function and make them easier to read.
STOP = 0
def compareHashesThreadSafe(text,hash, args, q, lookupTable) -> int:
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
  generatedHash = generateHash(text,args)

  if args['--generateLookupTable']:
    lookupTable[generatedHash] = text

  if generatedHash == hash:
    q.put(f'Success: {text} : {hash}')
    #if not args['--greed']:
    return 1
  else:
    if args['-v']:
      q.put(f'Fail: {text} : {hash}')
    return 0

def writeOutput(args, q, stopQueue):
  '''
  Takes an item from a queue and prints it out / writes it to a file based on whats in args. Designed
  for multithreading. Will terminate once a blank string is pulled from q.
  args: args from docopt
  q: mp.queue
  '''
  # run this if it needs to write to a file
  if args['-o']:
    with open(args['-o'],mode='w+') as f:
      while True:
        msg = q.get()
        if msg != '':
          if not args['-q']:
            print(msg)
          f.write(msg +'\n')
          if msg[0] == "S" and args['--greed']:
              stopQueue.put("stop")
              return
        else:
          stopQueue.put("stop")
          return
  # run this if it does not need to write to a file.
  elif not args['-q']:
    while True:
        msg = q.get()
        if msg != '':
          print(msg)
          if msg[0] == 'S' and args['--greed']:
              stopQueue.put("stop")
              return
        else:
          stopQueue.put("stop")
          return

def parallelBruteForceSingleHash(CGen, args, q, chunk, stopQueue, lookupTable):
  '''
  Launch a brute force attack against a single hash by generating our own text. Generation is specified in Kraken.config.
  combo: starting point for the text to be generated
  args: arguments from docopt.
  CGen: CombinationGenerator object.
  q: mp.Queue for processing output.
  chunk: a tuple of a starting combination and the ending combination.
  *** printing out significantly slows down the process.
  '''
  combo = chunk[0]
  while(combo != chunk[1]):
    if not stopQueue.empty():
      return
    compareHashesThreadSafe(combo,args['--hash'],args,q,lookupTable)
    combo = CGen.nextCombination(combo)
  compareHashesThreadSafe(combo,args['--hash'],args,q,lookupTable)

def parallelBruteForceMultipleHash(CGen, args, q, chunk, stopQueue, lookupTable):
  '''
  Launch a brute force attack against a list of hashes by generating our own text. Generation is specified in Kraken.config.
  combo: starting point for the text to be generated.
  args: arguments from docopt.
  q: mp.Queue for processing output.
  chunk: a tuple of a starting combination and the ending combination.

  '''
  stopPoint = chunk[1]
  combo = chunk[0]
  with open(args['--hashFile']) as hashFile:
    while True:
      #compare to every hash in the file
      hashFile.seek(0)
      for hash in hashFile:
        if not stopQueue.empty():
          return
        compareHashesThreadSafe(combo, hash, args, q, lookupTable)
      # stop after the final combination has been generated
      combo = CGen.nextCombination(combo)
      if combo == stopPoint:
        break
    # Catch the last combo.
    hashFile.seek(0)
    for hash in hashFile:
      if not stopQueue.empty():
        return
      compareHashesThreadSafe(combo, hash, args, q, lookupTable)

def parallelWordListAttackSingleHash(args, chunk, q, stopQueue, lookupTable):
  '''
  Launch a wordlist attack on a single hash.
  '''
  with open(chunk,mode='r',encoding='latin-1') as wordList:
    for word in wordList:
      compareHashesThreadSafe(word, args['--hash'], args, q, lookupTable)
      if not stopQueue.empty():
        return

def parallelWordListAttackMultipleHashes(args, chunk, q, stopQueue, lookupTable):
  '''
  Launch a wordlist attack on a set of hashes.
  '''
  with open(chunk,mode='r',encoding='latin-1') as wordList, open(args['--hashFile'],'r') as hashFile:
    for word in wordList:
      #??? is it faster to do this for loop or to create a list from the hashlist and loop through that?
      hashFile.seek(0)
      for hash in hashFile:
        compareHashesThreadSafe(word, hash, args, q, lookupTable)
        if not stopQueue.empty():
          return

# Attacks for cluster computing

def compareHashesCluster(text, hash, args):
  text = text.rstrip('\n')
  hash = hash.rstrip('\n')
  generatedHash = generateHash(text,args)

  if generatedHash == hash:
    from mpi4py import MPI
    c = MPI.COMM_WORLD
    r = c.Get_rank()
    print(f'Success: {text} : {hash} : found by rank {r}')

def wordlistAttackClusterSingleHash(args,chunk):
    hash = args['--hash']
    with open(chunk,encoding='latin-1', mode='r') as wordList:
      for word in wordList:
        compareHashesCluster(word, hash, args)

def wordlistAttackClusterMultipleHash(args,chunk):
  with open(chunk,mode='r',encoding='latin-1') as wordList, open(args['--hashFile'],'r') as hashFile:
    for word in wordList:
      hashFile.seek(0)
      for hash in hashFile:
        compareHashesCluster(word, hash, args)