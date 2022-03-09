'''Kraken
Usage:
  Kraken.py (--md5 | --sha1) (--hash <hash> | --hashFile <hashFile>) (-b | --wordList <wordList>) [-v -q -o] [--greed --numProcesses <int>]]
  Kraken.py (-h | --help)

Options:
  -h --help             Show this message.
  -v                    Display extra output. *Slows down program significantly*
  -q                    Do not display output.
  -o FILE               Write output to file.
  --greed               Stop on first successfully cracked hash
  --md5                 Use md5 hashing algorithm.
  --sha1                Use sha1 hashing algorithm.
  --hash HASH           Specify a single hash.
  --hashFile PATH       Specify hash file with one hash per line.
  -b                    Attack by generating all possible combinations of a set. Set can be modified in Kraken.config. Defaults to all lowercase letters in the english alphabet.
  --wordList PATH       Attack using a wordlist
  --numProcesses <int>  Define the number of processes Kraken may use.

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
from attacks import *
import configparser
import os.path
from CombinationGenerator import CombinationGenerator
from multiprocessing import Process,Queue
from attacksParallel import parallelWordListAttackMultipleHashes, parallelWordListAttackMultipleHashes, parallelWordListAttackSingleHash,writeOutput
from KrakenTools import fileLen, divideIntoChunks


if __name__ == '__main__':
    args = docopt(__doc__)

    # only exists for debugging...
    print('*'*20+'\n',args,'\n'+'*'*20)

    wordListLength = 0
    chunkSize = 0
    chunkStartPoints = 0

    # calculate variables only if needed.
    if args['--wordList'] and args['--numProcesses']:
      wordListLength = fileLen(args['--wordList'])
      divideIntoChunks(wordListLength, args['--wordList'], int(args['--numProcesses']))

    # Generate config file if needed
    config = configparser.ConfigParser()
    if os.path.exists('Kraken.config'):
      print('Using existing Kraken.config file.')
      config.read('Kraken.config')
    else:
      #TODO: do something about how string size can be set to 0 and causes infinite loops
      print('Kraken.config does not exist... creating default file now.')
      config['DEFAULT'] = {'characterList':'abcdefghijklmnopqrstuvwxyz', 'maxStringSize': 4, 'minStringSize': 1} 
      with open('Kraken.config','x') as f:
        config.write(f)
    
    CGen = CombinationGenerator()
    
    # Launch correct attack

    # Single thread attacks
    if not args['--numProcesses']:
      # single thread attacks
      if args['-b'] and not args['--hashFile']:
        bruteForceSingleHash(CGen, args)
      elif args['-b'] and args['--hashFile']:
        bruteForceMultipleHash(CGen,args)
      elif args['--wordList'] and not args['--hashFile']:
        wordListAttackSingleHash(args)
      elif args['--wordList'] and args['--hashFile']:
        wordListAttackMultipleHashes(args)
    else:
      # parallel attacks
      p = list()
      writeQueue = Queue()
      if args['-b'] and not args['--hashFile']:
        pass
      elif args['-b'] and args['--hashFile']:
        pass
      elif args['--wordList'] and not args['--hashFile']:

        # Attack on a single hash
        for i in range(int(args['--numProcesses'])):
          p.append(Process(target=parallelWordListAttackSingleHash, args=(args,f'chunk{i}.txt')))
          p[i].start()
        for i in range(int(args['--numProcesses'])):
          p[i].join()

      elif args['--wordList'] and args['--hashFile']:
        # attack on multiple hashes. writterProcess deals with the output
        # that the other processes find.
        writterProcess = Process(target=writeOutput,args=(args,writeQueue))
        writterProcess.start()
        for i in range(int(args['--numProcesses'])):
          p.append(Process(target=parallelWordListAttackMultipleHashes, args=(args,f'chunk{i}.txt',writeQueue)))
          p[i].start()
        for i in range(int(args['--numProcesses'])):
          p[i].join()
        
        # tell writterProcess to stop monitoring for more items.
        writeQueue.put('')
        writterProcess.join()