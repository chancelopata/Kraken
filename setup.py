import pip

try:
    __import__('docopt')
except ImportError:
    pip.main(['install', 'docopt'])