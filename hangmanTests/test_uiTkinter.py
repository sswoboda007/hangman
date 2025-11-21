# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_uiTkinter.py

"""
Unit tests for the HangmanApp Tkinter GUI.

This test suite contains tests for the Tkinter-based GUI of the Hangman game.
It uses mocks to isolate the GUI components and verify their behavior in
response to user actions and game state changes.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

import unittest
from unittest.mock import MagicMock, patch

import tkinter as tk

from uiTkinter import HangmanApp
from wordBank import WordBank
from gameLogic import HangmanGame


# --- Conditional Skip for Headless Environments ---
# Attempt to create a root window to check for a valid display environment.
# If it fails with a TclError, set a flag to skip all tests in this module.
try:
    tk.Tk().destroy()
    _is_headless = False
except tk.TclError:
    _is_headless = True


@unittest.skipIf(_is_headless, "Skipping UI tests in a headless environment (no display).")
class TestHangmanApp(unittest.TestCase):
    """
    Basic tests for the HangmanApp GUI behavior.
    """

    def setUp(self) -> None:
        """
        Create a Tk root and a HangmanApp instance in a headless-friendly way.
        """
        # The module-level skip should prevent this from running in a truly
        # headless environment. If it still fails here, it's an intermittent
        # or environment-specific issue.
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the dummy window.
        except tk.TclError:
            self.skipTest("Tkinter initialization failed in setUp.")

        self.word_bank = MagicMock(spec=WordBank)
        self.word_bank.getCategories.return_value = ["general"]
        self.word_bank.getRandomWord.return_value = "test"

        def gameFactory(secret_word: str) -> HangmanGame:
            # Create a real game or a mock; here we use a MagicMock with required interface
            game = MagicMock(spec=HangmanGame)
            game.secret_word = secret_word
            game.max_attempts = 6
            game.wrong_guesses = 0
            game.used_letters = set()
            game.getMaskedWord.return_value = "_ _ _ _"
            game.isWon.return_value = False
            game.isLost.return_value = False
            return game

        self.game_factory = gameFactory

        # Instantiate the app, passing the hidden root as the master.
        self.app = HangmanApp(word_bank=self.word_bank, game_factory=self.game_factory)
        # Hide the GUI window so tests do not pop a window
        self.app.withdraw()

    def tearDown(self) -> None:
        """
        Destroy the app after each test to clean up Tk resources.
        """
        self.app.destroy()
        self.root.destroy()  # Destroy the dummy root as well

    def testWidgetsAreInitialized(self) -> None:
        """
        Ensure core widgets are created after initialization.
        """
        self.assertIsNotNone(self.app.word_label)
        self.assertIsNotNone(self.app.info_label)
        self.assertIsNotNone(self.app.input_entry)
        self.assertIsNotNone(self.app.guess_button)
        self.assertIsNotNone(self.app.reset_button)
        self.assertIsNotNone(self.app.category_var)
        self.assertIsNotNone(self.app.category_menu)

    def testNewGameIsStartedOnInit(self) -> None:
        """
        A new game should be created at initialization using WordBank and game_factory.
        """
        # WordBank.getRandomWord should be called with the default category
        self.word_bank.getRandomWord.assert_called_once()
        self.assertIsNotNone(self.app.game)
        # Masked word label should be updated
        self.assertEqual(self.app.word_label.cget("text"), "_ _ _ _")  # type: ignore[union-attr]

    def testProcessCurrentGuessCallsGameLogic(self) -> None:
        """
        When a guess is made, the game logic's processGuess should be invoked.
        """
        # Replace existing game with a controllable mock
        mock_game = MagicMock(spec=HangmanGame)
        mock_game.getMaskedWord.return_value = "_ e _ t"
        mock_game.isWon.return_value = False
        mock_game.isLost.return_value = False
        mock_game.used_letters = {"e"}
        mock_game.max_attempts = 6
        mock_game.wrong_guesses = 0

        self.app.game = mock_game

        # Simulate user entering a letter and pressing Guess
        assert self.app.input_entry is not None
        self.app.input_entry.insert(0, "e")
        self.app._processCurrentGuess()

        mock_game.processGuess.assert_called_once_with("e")
        # Label update should reflect mock's masked word
        self.assertEqual(self.app.word_label.cget("text"), "_ e _ t")  # type: ignore[union-attr]

    @patch("uiTkinter.messagebox.showinfo")
    def testHandleWinShowsMessageAndDisablesInput(self, mock_showinfo: MagicMock) -> None:
        """
        When the game is won, a message box should be shown and input disabled.
        """
        mock_game = MagicMock(spec=HangmanGame)
        mock_game.secret_word = "test"
        mock_game.getMaskedWord.return_value = "t e s t"
        mock_game.isWon.return_value = True
        mock_game.isLost.return_value = False
        mock_game.max_attempts = 6
        mock_game.wrong_guesses = 0
        mock_game.used_letters = set("test")
        self.app.game = mock_game

        # Ensure input is enabled first
        self.app._enableInput()

        assert self.app.input_entry is not None
        self.app.input_entry.insert(0, "t")
        self.app._processCurrentGuess()

        mock_showinfo.assert_called_once()
        # Input should now be disabled
        self.assertEqual(self.app.input_entry.cget("state"), tk.DISABLED)  # type: ignore[union-attr]
        self.assertEqual(self.app.guess_button.cget("state"), tk.DISABLED)  # type: ignore[union-attr]

    @patch("uiTkinter.messagebox.showinfo")
    def testHandleLossShowsMessageAndDisablesInput(self, mock_showinfo: MagicMock) -> None:
        """
        When the game is lost, a message box should be shown and input disabled.
        """
        mock_game = MagicMock(spec=HangmanGame)
        mock_game.secret_word = "test"
        mock_game.getMaskedWord.return_value = "_ _ _ _"
        mock_game.isWon.return_value = False
        mock_game.isLost.return_value = True
        mock_game.max_attempts = 6
        mock_game.wrong_guesses = 6
        mock_game.used_letters = set("xyz")
        self.app.game = mock_game

        self.app._enableInput()

        assert self.app.input_entry is not None
        self.app.input_entry.insert(0, "z")
        self.app._processCurrentGuess()

        mock_showinfo.assert_called_once()
        self.assertEqual(self.app.input_entry.cget("state"), tk.DISABLED)  # type: ignore[union-attr]
        self.assertEqual(self.app.guess_button.cget("state"), tk.DISABLED)  # type: ignore[union-attr]

    def testCategoryChangeStartsNewGame(self) -> None:
        """
        Changing the category should trigger a new game creation.
        """
        # Reset call count and simulate a category change
        self.word_bank.getRandomWord.reset_mock()
        self.app._onCategoryChanged("general")
        self.word_bank.getRandomWord.assert_called_once_with("general")
        self.assertIsNotNone(self.app.game)


if __name__ == "__main__":
    unittest.main()