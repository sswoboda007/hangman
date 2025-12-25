# -*- coding: utf-8 -*-
# hangman/ioCli.py

"""
Optional: Command-line interface for the Hangman game.

This module provides a simple command-line interface (CLI) for playing Hangman.
It is not wired into the main application by default, which uses a graphical user
interface (GUI), but can be used for manual testing or as an alternative front-end.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

from typing import Callable
from gameLogic import HangmanGame
from wordBank import WordBank, DEFAULT_CATEGORY


class HangmanCli:
    """
    Simple text-based CLI for playing Hangman in a terminal.
    """

    def __init__(self, word_bank: WordBank, game_factory: Callable[[str], HangmanGame]) -> None:
        self.word_bank = word_bank
        self.game_factory = game_factory
        self.game: HangmanGame = self.game_factory(
            self.word_bank.getRandomWord(DEFAULT_CATEGORY)
        )

    def runGameLoop(self) -> None:
        """
        Run a basic input/print loop for Hangman.
        Intended for manual testing or alternate interface.
        """
        print("Welcome to Hangman (CLI)!")
        while not self.game.isFinished():
            print("\nWord:", self.game.getMaskedWord())
            print(f"Wrong guesses: {self.game.wrong_guesses}/{self.game.max_attempts}")
            guess = input("Guess a letter: ").strip()
            self.game.processGuess(guess)

        if self.game.isWon():
            print(f"You won! The word was: {self.game.secret_word}")
        else:
            print(f"You lost! The word was: {self.game.secret_word}")