# -*- coding: utf-8 -*-
# hangman/main.py

"""
Entry point for the Hangman application.

This module serves as the main entry point for the Hangman game. It is responsible
for initializing the core components of the application, including the word bank,
the game logic, and the user interface. It wires these components together to
create a fully functional game instance.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

from typing import Callable

from wordBank import WordBank
from gameLogic import HangmanGame, DEFAULT_MAX_ATTEMPTS
from uiTkinter import HangmanApp


def createGameInstance(secret_word: str) -> HangmanGame:
    """
    Factory function to create a HangmanGame instance.
    This keeps construction logic centralized, in case you
    want to vary max_attempts or add additional parameters later.
    """
    return HangmanGame(secret_word, max_attempts=DEFAULT_MAX_ATTEMPTS)


def main() -> None:
    """
    Main entry point for running the Hangman GUI.
    """
    word_bank = WordBank()
    game_factory: Callable[[str], HangmanGame] = createGameInstance

    app = HangmanApp(word_bank=word_bank, game_factory=game_factory)
    app.mainloop()


if __name__ == "__main__":
    main()