# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_main.py

"""
Unit tests for the main application module.

This test suite contains tests for the main entry point of the Hangman
application. It focuses on verifying the correct setup and wiring of the
game components, such as the game instance factory.

Author: @seanl
Version: 1.1.1
Creation Date: 11/20/2025
Last Updated: 12/25/2025
"""

import unittest
import runpy
import sys
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

    def testNameEqualsMainBlock(self) -> None:
        """
        Test that the if __name__ == "__main__": block calls main().
        We use runpy to execute the module as a script.
        """
        # We mock sys.argv to avoid side effects
        with patch.object(sys, 'argv', ["main.py"]):
            # We patch 'main.HangmanApp' to prevent the real UI from initializing
            # and causing issues with the mocked tkinter environment during runpy execution.
            # Since runpy re-imports the module, we need to patch it in a way that affects
            # the execution. The easiest way is to patch the class in the module *before*
            # runpy executes it, but runpy reloads.
            
            # Instead, we can patch 'uiTkinter.HangmanApp' because main.py imports it.
            with patch('uiTkinter.HangmanApp') as mock_app_class:
                try:
                    runpy.run_path("main.py", run_name="__main__")
                except SystemExit:
                    pass
                
                # Verify that HangmanApp was instantiated, implying main() ran
                mock_app_class.assert_called_once()


if __name__ == "__main__":
    unittest.main()
