# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_main.py

"""
Unit tests for the main application module.

This test suite contains tests for the main entry point of the Hangman
application. It focuses on verifying the correct setup and wiring of the
game components, such as the game instance factory.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

import unittest
from typing import Callable

from main import createGameInstance
from gameLogic import HangmanGame


class TestMainModule(unittest.TestCase):
    """
    Simple tests around game factory and wiring assumptions.
    """

    def testCreateGameInstanceReturnsHangmanGame(self) -> None:
        """
        Ensure createGameInstance returns a HangmanGame.
        """
        instance = createGameInstance("example")
        self.assertIsInstance(instance, HangmanGame)


if __name__ == "__main__":
    unittest.main()