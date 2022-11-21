import unittest
from src.main import main

class MainTest(unittest.TestCase):
    def test_main(self):
        self.assertEqual(main(), 0)

if __name__ == '__main__':
    unittest.main()