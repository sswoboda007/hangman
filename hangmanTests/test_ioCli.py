# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_ioCli.py

"""
Unit tests for the command-line interface.

This test suite contains basic structural tests for the HangmanCli class,
which provides an optional command-line interface for the game. These tests
focus on ensuring that the CLI can be instantiated correctly.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

import unittest

from ioCli import HangmanCli
from wordBank import WordBank
from gameLogic import HangmanGame


class TestHangmanCli(unittest.TestCase):
    """
    Minimal tests for HangmanCli initialization.
    """

    def testCliInitialization(self) -> None:
        """
        Ensure HangmanCli can be instantiated without errors.
        """
        word_bank = WordBank()

        def gameFactory(secret_word: str) -> HangmanGame:
            return HangmanGame(secret_word)

        cli = HangmanCli(word_bank=word_bank, game_factory=gameFactory)
        self.assertIsNotNone(cli.game)


if __name__ == "__main__":
    unittest.main()