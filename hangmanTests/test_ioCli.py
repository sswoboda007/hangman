# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_ioCli.py
#
"""
Unit tests for the command-line interface.
 
This test suite verifies the functionality of the HangmanCli class, which
provides an optional command-line interface for the game. These tests ensure
the game loop handles both win and loss conditions correctly.

Author: @seanl
Version: 2.1.0
Creation Date: 11/20/2025
Last Updated: 12/25/2025
"""

from unittest.mock import patch, call

import pytest

from ioCli import HangmanCli
from wordBank import WordBank
from gameLogic import HangmanGame


@pytest.fixture
def cli_dependencies():
    """
    Provides the necessary dependencies for instantiating HangmanCli.
    """
    word_bank = WordBank()
    def game_factory(word: str) -> HangmanGame:
        return HangmanGame(word)
    return word_bank, game_factory


def testCliInitialization(cli_dependencies) -> None:
    """
    Ensure HangmanCli can be instantiated without errors.
    """
    word_bank, game_factory = cli_dependencies
    cli = HangmanCli(word_bank=word_bank, game_factory=game_factory)
    assert cli.game is not None


def testRunGameLoopWinCondition(cli_dependencies) -> None:
    """
    Test the game loop for a win condition, covering the win message.
    """
    word_bank, game_factory = cli_dependencies
    secret_word = "hi"

    cli = HangmanCli(word_bank=word_bank, game_factory=game_factory)
    # Directly set the game with a predictable word to control the test
    cli.game = game_factory(secret_word)

    # Simulate user inputs 'h', then 'i' to win the game
    user_inputs = ["h", "i"]

    with patch('builtins.input', side_effect=user_inputs), \
         patch('builtins.print') as mock_print:
        cli.runGameLoop()

        # Verify intermediate game state prints
        # We expect calls like: print("\nWord:", "_ _"), print("Wrong guesses: 0/6")
        # Then after 'h': print("\nWord:", "h _"), print("Wrong guesses: 0/6")
        
        # Check for the final win message
        final_message = mock_print.call_args_list[-1][0][0]
        assert "You won!" in final_message
        assert secret_word in final_message


def testRunGameLoopLossCondition(cli_dependencies) -> None:
    """
    Test the game loop for a loss condition, covering the loss message.
    """
    word_bank, game_factory = cli_dependencies
    secret_word = "hi"
    max_attempts = 1

    cli = HangmanCli(word_bank=word_bank, game_factory=game_factory)
    # Directly set the game with a predictable word and limited attempts
    cli.game = HangmanGame(secret_word, max_attempts=max_attempts)

    # Simulate a single wrong guess to lose the game
    user_inputs = ["z"]

    with patch('builtins.input', side_effect=user_inputs), \
         patch('builtins.print') as mock_print:
        cli.runGameLoop()

        # Check for the final loss message
        final_message = mock_print.call_args_list[-1][0][0]
        assert "You lost!" in final_message
        assert secret_word in final_message


def testRunGameLoopPrintsState(cli_dependencies) -> None:
    """
    Verify that the CLI prints the masked word and wrong guess count during the loop.
    """
    word_bank, game_factory = cli_dependencies
    secret_word = "a"
    
    cli = HangmanCli(word_bank=word_bank, game_factory=game_factory)
    cli.game = game_factory(secret_word)
    
    # Input 'z' (wrong), then 'a' (correct/win)
    user_inputs = ["z", "a"]
    
    with patch('builtins.input', side_effect=user_inputs), \
         patch('builtins.print') as mock_print:
        cli.runGameLoop()
        
        # Verify specific print calls occurred
        # Initial state
        assert call("\nWord:", "_") in mock_print.call_args_list
        assert call("Wrong guesses: 0/6") in mock_print.call_args_list
        
        # After wrong guess 'z'
        assert call("Wrong guesses: 1/6") in mock_print.call_args_list
        
        # Win message
        assert call(f"You won! The word was: {secret_word}") in mock_print.call_args_list
