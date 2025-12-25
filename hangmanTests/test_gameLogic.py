# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_gameLogic.py

"""
Unit tests for the HangmanGame class.

This test suite covers the core game logic encapsulated in the HangmanGame
class. It tests game state, guess processing, and win/loss conditions.

Author: @seanl
Version: 1.4.0
Creation Date: 11/20/2025
Last Updated: 12/25/2025
"""

import unittest
from unittest.mock import patch

from gameLogic import HangmanGame, DEFAULT_MAX_ATTEMPTS, HINT_COST, AUTO_REVEAL_LETTERS


class TestHangmanGame(unittest.TestCase):
    """
    Basic tests for HangmanGame behavior.
    """

    def setUp(self) -> None:
        self.secret_word = "test" # contains 'e', 's', 't' -> all in RSTLNE
        self.game = HangmanGame(secret_word=self.secret_word, max_attempts=DEFAULT_MAX_ATTEMPTS)

    def testInitialStateWithAutoReveal(self) -> None:
        """
        Game starts with zero wrong guesses, but RSTLNE letters should be revealed if present.
        'test' contains 't', 'e', 's' which are all in RSTLNE.
        """
        self.assertEqual(self.game.wrong_guesses, 0)
        # 't', 'e', 's' should be in used_letters
        self.assertIn('t', self.game.used_letters)
        self.assertIn('e', self.game.used_letters)
        self.assertIn('s', self.game.used_letters)
        # Since 'test' is fully composed of RSTLNE, it should be won immediately!
        self.assertTrue(self.game.isWon())

    def testAutoRevealPartial(self) -> None:
        """
        Test a word that has some RSTLNE and some other letters.
        'python' -> 'n', 't' (from RSTLNE) should be revealed.
        """
        game = HangmanGame("python")
        self.assertEqual(game.wrong_guesses, 0)
        self.assertIn('n', game.used_letters)
        self.assertIn('t', game.used_letters)
        # 'p', 'y', 'h', 'o' should NOT be revealed
        self.assertNotIn('p', game.used_letters)
        self.assertNotIn('y', game.used_letters)
        self.assertNotIn('h', game.used_letters)
        self.assertNotIn('o', game.used_letters)

    def testAutoRevealNone(self) -> None:
        """
        Test a word with NO RSTLNE letters.
        'jazz' -> no RSTLNE.
        """
        game = HangmanGame("jazz")
        self.assertEqual(game.wrong_guesses, 0)
        # UPDATED: RSTLNE are always added now, so len should be 6
        self.assertEqual(len(game.used_letters), 6)
        for char in AUTO_REVEAL_LETTERS:
            self.assertIn(char, game.used_letters)

    def testCorrectGuessUpdatesState(self) -> None:
        """
        Correct guesses should not increase wrong_guesses.
        """
        # Use a word without RSTLNE to test basic guessing cleanly
        game = HangmanGame("jazz")
        result = game.processGuess("j")
        self.assertTrue(result)
        self.assertIn("j", game.used_letters)
        self.assertEqual(game.wrong_guesses, 0)

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
        # 'test' is already won due to auto-reveal in setUp
        self.assertTrue(self.game.isWon())
        
        # Try another word
        game = HangmanGame("ab") # 'a', 'b' not in RSTLNE
        game.processGuess("a")
        game.processGuess("b")
        self.assertTrue(game.isWon())

    def testLossCondition(self) -> None:
        """
        Too many wrong guesses should result in a loss.
        """
        wrong_letters = "abcdfghijklmnopqrsuvwxyz"
        # Filter out letters that might be in the secret word "test" or in RSTLNE to ensure they are "wrong"
        # "test" has t, e, s. RSTLNE has r, s, t, l, n, e.
        # We need purely wrong guesses.
        # "test" -> t, e, s.
        # Wrong: a, b, c, d, f, g, h, i, j, k, m, o, p, q, u, v, w, x, y, z
        purely_wrong = "abcdfghijk"
        
        for i in range(self.game.max_attempts):
            self.game.processGuess(purely_wrong[i])
        self.assertTrue(self.game.isLost())

    def test_resetGame(self) -> None:
        """
        Verify that resetGame correctly re-initializes the game state and applies auto-reveal.
        """
        self.game.resetGame("jazz") # No RSTLNE
        self.assertEqual(self.game.secret_word, "jazz")
        # UPDATED: RSTLNE are always added now
        self.assertEqual(len(self.game.used_letters), 6)
        self.assertEqual(self.game.wrong_guesses, 0)
        
        self.game.resetGame("line") # l, i, n, e -> l, n, e are RSTLNE
        self.assertIn('l', self.game.used_letters)
        self.assertIn('n', self.game.used_letters)
        self.assertIn('e', self.game.used_letters)
        self.assertNotIn('i', self.game.used_letters)

    def test_getMaskedWord(self) -> None:
        """
        Verify that getMaskedWord returns the correctly formatted masked word.
        """
        game = HangmanGame("hangman") # h, a, n, g, m, a, n. n is in RSTLNE.
        # 'n' should be revealed.
        # _ a _ _ m a n -> _ _ n _ m _ n ? No.
        # h (no), a (no), n (yes), g (no), m (no), a (no), n (yes)
        # _ _ n _ _ _ n
        self.assertEqual(game.getMaskedWord(), "_ _ n _ _ _ n")
        
        game.processGuess("a")
        self.assertEqual(game.getMaskedWord(), "_ a n _ _ a n")

    def test_processGuess_invalid_input(self) -> None:
        """
        Verify that processGuess handles invalid (non-alphabetic, multi-char) input.
        """
        result = self.game.processGuess("1")
        self.assertFalse(result)
        # used_letters might contain auto-revealed ones, so check count relative to start
        initial_count = len(self.game.used_letters)
        self.assertEqual(len(self.game.used_letters), initial_count)

    def test_processGuess_already_used_letter(self) -> None:
        """
        Verify that processGuess handles already used letters correctly.
        """
        # 't' is auto-revealed in "test"
        result = self.game.processGuess("t")
        self.assertFalse(result) # Already used
        self.assertEqual(self.game.wrong_guesses, 0)

    def test_isFinished(self) -> None:
        """
        Verify that isFinished correctly identifies the end of a game.
        """
        # Test win condition
        game_win = HangmanGame("hi", max_attempts=1) # 'i' not in RSTLNE, 'h' not.
        game_win.processGuess("h")
        game_win.processGuess("i")
        self.assertTrue(game_win.isFinished())

        # Test lose condition
        game_lose = HangmanGame("hi", max_attempts=1)
        game_lose.processGuess("x")
        self.assertTrue(game_lose.isFinished())

    def testSecretWordCaseInsensitivity(self) -> None:
        """
        Verify that the game handles mixed-case secret words by normalizing them.
        """
        game = HangmanGame("TeSt")
        self.assertEqual(game.secret_word, "test")
        
        # 't', 'e', 's' auto revealed.
        self.assertTrue(game.isWon())

    def testRepeatedCorrectGuessDoesNotPenalize(self) -> None:
        """
        Verify that guessing a correct letter again returns False (no-op) 
        but does NOT increment wrong_guesses.
        """
        # 't' is auto-revealed
        initial_wrong = self.game.wrong_guesses
        
        # Guess 't' again
        result = self.game.processGuess("t")
        
        self.assertFalse(result) # Should return False as it's already used
        self.assertEqual(self.game.wrong_guesses, initial_wrong) # No penalty

    def testZeroMaxAttempts(self) -> None:
        """
        Edge case: Game initialized with 0 max attempts.
        Should be lost immediately if not won immediately.
        """
        game = HangmanGame("test", max_attempts=0)
        # 'test' is auto-won because of RSTLNE
        self.assertTrue(game.isWon())
        
        game2 = HangmanGame("jazz", max_attempts=0)
        self.assertTrue(game2.isLost())

    def testUseHintRevealsLetterAndCostsLives(self) -> None:
        """
        Verify useHint reveals a letter and increments wrong_guesses.
        """
        game = HangmanGame("jazz") # No RSTLNE
        # Mock random.choice to return 'j'
        with patch('random.choice', return_value='j'):
            revealed = game.useHint()
            
        self.assertEqual(revealed, 'j')
        self.assertIn('j', game.used_letters)
        self.assertEqual(game.wrong_guesses, HINT_COST)

    def testUseHintFailsIfNotEnoughLives(self) -> None:
        """
        Verify useHint returns None if remaining attempts < HINT_COST.
        """
        # Set wrong guesses so only 1 life remains (assuming max=6, cost=2)
        self.game.wrong_guesses = self.game.max_attempts - 1
        
        revealed = self.game.useHint()
        
        self.assertIsNone(revealed)
        # Verify state didn't change
        self.assertEqual(self.game.wrong_guesses, self.game.max_attempts - 1)

    def testUseHintFailsIfNoLettersLeft(self) -> None:
        """
        Verify useHint returns None if all letters are already guessed.
        """
        # 'test' is already won (all letters guessed via auto-reveal)
        revealed = self.game.useHint()
        self.assertIsNone(revealed)


if __name__ == "__main__":
    unittest.main()
