import hashlib

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