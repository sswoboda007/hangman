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
Last Updated: 11/21/2025
"""

import unittest
from unittest.mock import patch, MagicMock

from main import createGameInstance, main
from gameLogic import HangmanGame
from wordBank import WordBank


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

    @patch('main.HangmanApp')
    def testMainFunctionWiring(self, mock_hangman_app: MagicMock) -> None:
        """
        Test the main function to ensure it wires components correctly.
        This covers the main() function logic by mocking the UI.
        """
        # Call the main function, which should trigger the UI setup
        main()

        # Verify that HangmanApp was instantiated
        mock_hangman_app.assert_called_once()

        # Get the arguments it was called with for verification
        args, kwargs = mock_hangman_app.call_args

        # Check the keyword arguments passed to HangmanApp
        self.assertIn('word_bank', kwargs)
        self.assertIsInstance(kwargs['word_bank'], WordBank)
        self.assertIn('game_factory', kwargs)
        self.assertEqual(kwargs['game_factory'], createGameInstance)

        # Verify that the mainloop method was called on the HangmanApp instance
        mock_instance = mock_hangman_app.return_value
        mock_instance.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
