import unittest, sys, os
sys.path.insert(0, '..')
from parser import BotParser 


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = BotParser()

    def test_create_ping_stmt(self):
        self.assertEqual("ping", self.parser.create_ping_stmt())

    def test_create_put_stmt(self):
        handle = open('test.file', 'w')
        handle.write('A line of text\n')
        handle.close()
        stmt = self.parser.create_put_stmt('test.file')
        self.assertEqual('put "test.file" A line of text\n', stmt)
        os.remove('test.file')

    def test_create_exec_stmt(self):
        self.assertEqual('exec "test.file"', self.parser.create_exec_stmt('test.file'))

if __name__ == '__main__':
    unittest.main()