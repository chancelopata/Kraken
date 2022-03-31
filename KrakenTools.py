'''
This file is for all Functions that Kraken will use that are not attacks or part of combinationGenerator.py
'''
import hashlib

def fileLen(path):
    '''
    Calculates the number of lines in a file.
    path: path to the file.
    '''
    i = 0
    with open(path,mode='r',encoding='latin-1') as f:
        for _ in f:
            i += 1
    return i

def divideIntoChunks (linesInFile,filePath,numProcesses):
    '''
    Takes a file and divides it into smaller files. Does not edit or remove the initial file.
    Assumes latin-1 encoding.
    *** FIXME: all but last chunk have a \n character at the end of the file.
    '''
    chunkSize = -(linesInFile // -numProcesses)
    chunkEndPoints = [chunkSize]

    # get a list of all the line numbers where a chunk should stop writing and a new one should be made.
    for i in range(numProcesses-1):
        chunkEndPoints.append(chunkEndPoints[i] + chunkSize)

    currentLine = 0
    with open(filePath,mode='r',encoding='latin-1') as file:
        listOfChunks = []
        for i in range(numProcesses):
            listOfChunks.append(f'chunk{i}.txt')
            with open(f'chunk{i}.txt',mode='w+',encoding='latin-1') as chunk:
                for line in file:
                    chunk.write(line)
                    currentLine += 1
                    if not (currentLine % chunkSize):
                        break
        return listOfChunks

def generateHash(text,args):
  '''
  Accepts a string and returns its hash.
  The type of hash algorithm used is determined by docopt args
  text: string to hash
  args: docopt arguments
  '''
  hash = ''
  text = text.encode('UTF-8')

  if args['--md5']:
    hash = hashlib.md5(text).hexdigest()
  elif args['--sha1']:
    hash = hashlib.sha1(text).hexdigest()
  else:
    print("ERROR: somehow the hash algorithm is not specified!")
  return hash