# -*- coding: utf-8 -*-
# hangman/gameLogic.py

"""
Contains the core Hangman game logic.

This module defines the HangmanGame class, which encapsulates the state and
rules of a single round of Hangman. It tracks the secret word, guessed letters,
and win/loss conditions.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

from typing import Set


DEFAULT_MAX_ATTEMPTS: int = 6


class HangmanGame:
    """
    Encapsulates the logic and state of a Hangman game round.
    """

    def __init__(self, secret_word: str, max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> None:
        self.secret_word: str = secret_word.lower()
        self.max_attempts: int = max_attempts
        self.used_letters: Set[str] = set()
        self.wrong_guesses: int = 0

    def resetGame(self, new_secret_word: str) -> None:
        """
        Reset the game state with a new secret word.
        """
        self.secret_word = new_secret_word.lower()
        self.used_letters.clear()
        self.wrong_guesses = 0

    def getMaskedWord(self) -> str:
        """
        Return a representation of the word with unguessed letters masked (e.g., '_ a _ g m a n').
        """
        masked_characters = [
            letter if letter in self.used_letters else "_"
            for letter in self.secret_word
        ]
        return " ".join(masked_characters)

    def processGuess(self, letter: str) -> bool:
        """
        Process a single letter guess.

        Returns:
            True if the guess is correct (letter in secret_word),
            False if the guess is incorrect.
        """
        letter = letter.lower()

        if not letter.isalpha() or len(letter) != 1:
            # Invalid guess; in UI, you might show a message instead.
            return False

        if letter in self.used_letters:
            # Letter already used; treat as no-op. UI can handle user feedback.
            return False

        self.used_letters.add(letter)

        if letter not in self.secret_word:
            self.wrong_guesses += 1
            return False

        return True

    def isWon(self) -> bool:
        """
        Check if the game is won (all letters guessed).
        """
        return all(letter in self.used_letters for letter in self.secret_word)

    def isLost(self) -> bool:
        """
        Check if the game is lost (too many wrong guesses).
        """
        return self.wrong_guesses >= self.max_attempts

    def isFinished(self) -> bool:
        """
        Check if the game is either won or lost.
        """
        return self.isWon() or self.isLost()