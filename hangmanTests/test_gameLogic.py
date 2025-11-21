# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_gameLogic.py

"""
Unit tests for the HangmanGame class.

This test suite covers the core game logic encapsulated in the HangmanGame
class. It tests game state, guess processing, and win/loss conditions.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

import unittest

from gameLogic import HangmanGame, DEFAULT_MAX_ATTEMPTS


class TestHangmanGame(unittest.TestCase):
    """
    Basic tests for HangmanGame behavior.
    """

    def setUp(self) -> None:
        self.secret_word = "test"
        self.game = HangmanGame(secret_word=self.secret_word, max_attempts=DEFAULT_MAX_ATTEMPTS)

    def testInitialState(self) -> None:
        """
        Game starts with zero wrong guesses and no used letters.
        """
        self.assertEqual(self.game.wrong_guesses, 0)
        self.assertEqual(len(self.game.used_letters), 0)
        self.assertFalse(self.game.isWon())
        self.assertFalse(self.game.isLost())

    def testCorrectGuessUpdatesState(self) -> None:
        """
        Correct guesses should not increase wrong_guesses.
        """
        result = self.game.processGuess("t")
        self.assertTrue(result)
        self.assertIn("t", self.game.used_letters)
        self.assertEqual(self.game.wrong_guesses, 0)

    def testIncorrectGuessIncrementsWrongGuesses(self) -> None:
        """
        Incorrect guesses should increase wrong_guesses.
        """
        result = self.game.processGuess("z")
        self.assertFalse(result)
        self.assertIn("z", self.game.used_letters)
        self.assertEqual(self.game.wrong_guesses, 1)

    def testWinCondition(self) -> None:
        """
        Guessing all letters should result in a win.
        """
        for letter in set(self.secret_word):
            self.game.processGuess(letter)
        self.assertTrue(self.game.isWon())
        self.assertFalse(self.game.isLost())

    def testLossCondition(self) -> None:
        """
        Too many wrong guesses should result in a loss.
        """
        # Guess unique incorrect letters up to the max_attempts limit.
        # The previous implementation repeatedly guessed 'z', but the game
        # logic correctly ignores duplicate guesses after the first one.
        wrong_letters = "abcdfghijklmnopqrsuvwxyz"
        for i in range(self.game.max_attempts):
            self.game.processGuess(wrong_letters[i])
        self.assertTrue(self.game.isLost())


if __name__ == "__main__":
    unittest.main()
