# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_gameLogic.py

"""
Unit tests for the HangmanGame class.

This test suite covers the core game logic encapsulated in the HangmanGame
class. It tests game state, guess processing, and win/loss conditions.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/21/2025
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
        wrong_letters = "abcdfghijklmnopqrsuvwxyz"
        for i in range(self.game.max_attempts):
            self.game.processGuess(wrong_letters[i])
        self.assertTrue(self.game.isLost())

    def test_resetGame(self) -> None:
        """
        Verify that resetGame correctly re-initializes the game state.
        """
        self.game.processGuess("t")
        self.game.processGuess("x") # wrong guess
        self.game.resetGame("newword")
        self.assertEqual(self.game.secret_word, "newword")
        self.assertEqual(len(self.game.used_letters), 0)
        self.assertEqual(self.game.wrong_guesses, 0)

    def test_getMaskedWord(self) -> None:
        """
        Verify that getMaskedWord returns the correctly formatted masked word.
        """
        game = HangmanGame("hangman")
        self.assertEqual(game.getMaskedWord(), "_ _ _ _ _ _ _")
        game.processGuess("a")
        self.assertEqual(game.getMaskedWord(), "_ a _ _ _ a _")

    def test_processGuess_invalid_input(self) -> None:
        """
        Verify that processGuess handles invalid (non-alphabetic, multi-char) input.
        """
        result = self.game.processGuess("1")
        self.assertFalse(result)
        self.assertEqual(len(self.game.used_letters), 0)

    def test_processGuess_already_used_letter(self) -> None:
        """
        Verify that processGuess handles already used letters correctly.
        """
        self.game.processGuess("t")
        result = self.game.processGuess("t")
        self.assertFalse(result)
        self.assertEqual(self.game.wrong_guesses, 0)

    def test_isFinished(self) -> None:
        """
        Verify that isFinished correctly identifies the end of a game.
        """
        # Test win condition
        game_win = HangmanGame("hi", max_attempts=1)
        game_win.processGuess("h")
        game_win.processGuess("i")
        self.assertTrue(game_win.isFinished())

        # Test lose condition
        game_lose = HangmanGame("hi", max_attempts=1)
        game_lose.processGuess("x")
        self.assertTrue(game_lose.isFinished())


if __name__ == "__main__":
    unittest.main()
