from lint import Linter

class JavaScript(Linter):
    language = 'javascript'
    cmd = ('jsl', '-stdin')
    regex = r'^\((?P<line>\d+)\):\s+(?P<error>.+)'
