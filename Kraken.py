'''Kraken
Usage:
  Kraken.py (--md5 | --sha1) (--hash <hash> | --hashFile <hashFile>) (-b | --wordList <wordList> | --lookupTable <tableFile>) [-v -q -o] --greed --numProcesses <int> --generateLookupTable <tableFile> --hostFile file]
  Kraken.py (-h | --help)

Options:
  -h --help                   Show this message.
  -v                          Display extra output. *Slows down program significantly*
  -q                          Do not display output.
  -o FILE                     Write output to file.
  --greed                     Stop on first successfully cracked hash
  --md5                       Use md5 hashing algorithm.
  --sha1                      Use sha1 hashing algorithm.
  --hash HASH                 Specify a single hash.
  --hashFile PATH             Specify hash file with one hash per line.
  -b                          Attack by generating all possible combinations of a set. Set can be modified in Kraken.config. Defaults to all lowercase letters in the english alphabet.
  --wordList PATH             Attack using a wordlist
  --numProcesses <int>        Define the number of processes Kraken may use. Minimum is 2. Not using this option has Kraken only use 1 process.
  --generateLookupTable PATH  Uses all the text and their corresponding hashes involved in the attack to create a lookup table.
  --lookupTable FILE          Attack using a lookup table generated by Kraken.
  --hostFile PATH             perform the wordlist attack over a cluster of computers using openMPI. Each line of the hostfile can hold 1 ip address. 

Examples:
  # Launch a wordlist attack on a single md5 hash
  Kraken.py --md5 --hash 5f4dcc3b5aa765d61d8327deb882cf99 --wordList rockyou.txt

  # Silently launch a wordlist attack on multiple hashes, using more processors and writting all successful matches to a file.
  Kraken.py --md5 --hashFile someHashes.txt --wordList rockyou.txt -q -o data.txt --numProcesses 5

  # Launch a brute force attack by generating all possible combinations using information specified in Kraken.config
  Kraken.py --md5 --hash 5f4dcc3b5aa765d61d8327deb882cf99 -b
'''

import multiprocessing
from docopt import docopt
import configparser
import os.path
from multiprocessing import Process,Queue
import pickle
from mpi4py import MPI

# DEBUG ONLY
import time

from CombinationGenerator import CombinationGenerator
from attacksParallel import parallelWordListAttackMultipleHashes, parallelWordListAttackSingleHash, parallelBruteForceSingleHash, parallelBruteForceMultipleHash, writeOutput, wordlistAttackCluster
from attacks import *
from KrakenTools import fileLen, divideIntoChunks


if __name__ == '__main__':

    #DEBUG
    programTime = time.time()

    args = docopt(__doc__)
    if args['--numProcesses']:
      args['--numProcesses'] = int(args['--numProcesses'])
      
    rank = ''
    comm = MPI.COMM_WORLD
    if args['--hostFile']:
      rank = comm.Get_rank()
    
    # only exists for debugging...
    print('*'*20+'\n',args,'\n'+'*'*20)

    # Generate config file if needed
    config = configparser.ConfigParser()
    if os.path.exists('Kraken.config'):
      if not args['-q']:
        print('Using existing Kraken.config file.')
      config.read('Kraken.config')
    else:
      #TODO: do something about how string size can be set to 0 and causes infinite loops
      if not args['-q']:
        print('Kraken.config does not exist... creating default file now.')
      config['DEFAULT'] = {'characterList':'abcdefghijklmnopqrstuvwxyz', 'maxStringSize': 4, 'minStringSize': 1} 
      with open('Kraken.config','x') as f:
        config.write(f)

    wordListLength = 0
    chunkSize = 0
    chunkStartPoints = 0
    CGen = CombinationGenerator()
    stopQ = Queue()
    p = list()
    writeQueue = Queue()
    lookupTable = {}

    # Test to make sure that the file paths are all good.
    if args['--wordList']:
      try:
        with open(args['--wordList'],mode='r'):
          pass
      except:
        if not args['-q']:
          print(f'ERROR: {args["--wordList"]} does not exist!')
        quit()
    if args['--hashFile']:
      try:
        with open(args['--hashFile'],mode='r'):
          pass
      except:
        if not args['-q']:
          print(f'ERROR: {args["--hashFile"]} does not exist!')
        quit()

    if args['--generateLookupTable'] and args['--numProcesses']:
      lookupTable = multiprocessing.Manager().dict()

    # quit if trying to run parallel without minimum required processors.
    if args['--numProcesses'] and args['--numProcesses'] < 2:
      if not args['-q']:
        print("ERROR: Atleast 2 processes must be allocated.")
      quit()
    elif args['--numProcesses']:
      # reserve 1 process for the writter process.
      args['--numProcesses'] -= 1

    if args['--lookupTable']:
      with open(args['--lookupTable'],'rb') as f:
        try:
          if not args['-q']:
            print(f'loading lookup table {args["--lookupTable"]}...')
          lookupTable = pickle.load(f)
        except:
          print(f'ERROR: {args["--lookupTable"]} not found!')
          quit()

    # calculate variables only if needed.
    if args['--numProcesses']:
      if args['--wordList']:
        wordListLength = fileLen(args['--wordList'])
        if not args['-q']:
          print("Distributing wordlist among processes... this may take a moment.")
        if args['--hostFile'] and rank == 0:
          divideIntoChunks(wordListLength, args['--wordList'], args[comm.Get_size])
        elif not args['--hostFile']:
          divideIntoChunks(wordListLength, args['--wordList'], args[comm.Get_size])
      else:
        bruteForceChunks = CGen.divideIntoChunks(args['--numProcesses'])

    if not args['-q']:
      print("==== Begin cracking hashes ======")
    
    ###########################
    # Select attack to launch #
    ###########################

    # Cluster attacks
    if args['--hostFile']:
      chunk = f'chunk{rank}'
      comm.barrier()
      wordlistAttackCluster(args,chunk)

    # Single thread attacks
    elif not args['--numProcesses']:
      # single thread attacks
      if args['-b'] and not args['--hashFile']:
        bruteForceSingleHash(CGen, args, lookupTable)
      elif args['-b'] and args['--hashFile']:
        bruteForceMultipleHash(CGen, args, lookupTable)
      elif args['--wordList'] and not args['--hashFile']:
        wordListAttackSingleHash(args, lookupTable)
      elif args['--wordList'] and args['--hashFile']:
        wordListAttackMultipleHashes(args, lookupTable)
      elif args['--lookupTable'] and not args['--hashFile']:
        lookupTableSingleHash(args,lookupTable)
      elif args['--lookupTable'] and args['--hashFile']:
        lookupTableMultipleHash(args,lookupTable)
    else:
      # parallel attacks

      # writterProcess deals with the output that the other processes find.
      writterProcess = Process(target=writeOutput,args=(args,writeQueue,stopQ))
      writterProcess.start()

      # attack single hash by generating combinations
      if args['-b'] and not args['--hashFile']:
        for i in range(args['--numProcesses']):
          p.append(Process(target=parallelBruteForceSingleHash,args=(CGen,args,writeQueue,bruteForceChunks[i],stopQ,lookupTable)))
          p[i].start()
        for i in range(args['--numProcesses']):
          p[i].join()

      # attack single
      elif args['-b'] and args['--hashFile']:
        for i in range(args['--numProcesses']):
          p.append(Process(target=parallelBruteForceMultipleHash,args=(CGen,args,writeQueue,bruteForceChunks[i],stopQ,lookupTable)))
          p[i].start()
        for i in range(args['--numProcesses']):
          p[i].join()

      # Attack on a single hash using wordlist
      elif args['--wordList'] and not args['--hashFile']:
        for i in range(args['--numProcesses']):
          p.append(Process(target=parallelWordListAttackSingleHash, args=(args,f'chunk{i}.txt',writeQueue,stopQ,lookupTable)))
          p[i].start()
        for i in range(args['--numProcesses']):
          p[i].join()

      # attack on multiple hashes using a wordlist.
      elif args['--wordList'] and args['--hashFile']:
        for i in range(args['--numProcesses']):
          p.append(Process(target=parallelWordListAttackMultipleHashes, args=(args,f'chunk{i}.txt',writeQueue,stopQ,lookupTable)))
          p[i].start()
        for i in range(args['--numProcesses']):
          p[i].join()
        
      # tell writterProcess to stop monitoring for more items.

    if not args['-q']:
      print("==== End cracking hashes ========")
    # DEBUG
    print(f'time spent running: {(time.time()-programTime)/60} minutes')

    # delete created chunk files
    if args['--numProcesses'] and args['--wordList']:
      for i in range(args['--numProcesses']):
        os.remove(f'chunk{i}.txt')

    # Save lookup table if needed.
    if args['--generateLookupTable']:
      if not args['-q']:
        print(f'Writting lookup table to {args["--generateLookupTable"]}...')
      with open(args['--generateLookupTable'],'wb') as f:
        pickle.dump(dict(lookupTable), f)

    # DEBUG
    print(f'time spent running: {(time.time()-programTime)/60} minutes')
