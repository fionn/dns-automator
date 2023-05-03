#!/usr/bin/env python3

import unittest

from app import create_app

class BasicTest(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app()

def main() -> None:
    """Entry point"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main()
