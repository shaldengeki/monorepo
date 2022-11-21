from unittest import TestCase
from src.main import main

class MainTest(TestCase):
    def test_main(self):
        self.assertEqual(main(), 0)
