# -*- coding: utf-8 -*-
# hangman/uiTkinter.py

"""
Implements a simple Tkinter-based GUI for the Hangman game,

This module provides the HangmanApp class, a Tkinter-based graphical user
interface for the Hangman game. It handles user interactions, displays game
state, and communicates with the core game logic.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from gameLogic import HangmanGame
from wordBank import WordBank, DEFAULT_CATEGORY


class HangmanApp(tk.Tk):
    """
    Main window for the Hangman game (Tkinter GUI).
    """

    def __init__(
        self,
        word_bank: WordBank,
        game_factory: Callable[[str], HangmanGame],
    ) -> None:
        """
        Initialize the Hangman GUI.

        Args:
            word_bank: An instance of WordBank to supply words.
            game_factory: A callable that takes a secret word and returns a HangmanGame.
        """
        super().__init__()

        self.title("Hangman")
        self.resizable(False, False)

        self.word_bank: WordBank = word_bank
        self.game_factory: Callable[[str], HangmanGame] = game_factory
        self.game: Optional[HangmanGame] = None
        self.current_category: str = DEFAULT_CATEGORY

        self.word_label: Optional[tk.Label] = None
        self.info_label: Optional[tk.Label] = None
        self.input_entry: Optional[tk.Entry] = None
        self.guess_button: Optional[tk.Button] = None
        self.reset_button: Optional[tk.Button] = None
        self.category_var: Optional[tk.StringVar] = None
        self.category_menu: Optional[tk.OptionMenu] = None

        self._setupUserInterface()
        self._startNewGame()

    def _setupUserInterface(self) -> None:
        """
        Build and lay out all GUI widgets.
        """
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Category selection
        category_frame = tk.Frame(main_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))

        category_label = tk.Label(category_frame, text="Category:")
        category_label.pack(side=tk.LEFT)

        self.category_var = tk.StringVar(value=self.current_category)
        categories = self.word_bank.getCategories()
        self.category_menu = tk.OptionMenu(
            category_frame,
            self.category_var,
            *categories,
            command=self._onCategoryChanged,
        )
        self.category_menu.pack(side=tk.LEFT, padx=(5, 0))

        # Masked word label
        self.word_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 24),
            pady=10,
        )
        self.word_label.pack()

        # Info label (used letters, remaining attempts, etc.)
        self.info_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 10),
            fg="gray",
        )
        self.info_label.pack(pady=(0, 10))

        # Input + button
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        input_label = tk.Label(input_frame, text="Guess a letter:")
        input_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(input_frame, width=5)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.bind("<Return>", self._onGuessSubmit)

        self.guess_button = tk.Button(
            input_frame,
            text="Guess",
            command=self._onGuessButtonClicked,
        )
        self.guess_button.pack(side=tk.LEFT)

        # Reset button
        self.reset_button = tk.Button(
            main_frame,
            text="New Game",
            command=self._onResetButtonClicked,
        )
        self.reset_button.pack(pady=(10, 0))

    def _onCategoryChanged(self, new_category: str) -> None:
        """
        Handler called when the user selects a new category.
        """
        self.current_category = new_category
        self._startNewGame()

    def _startNewGame(self) -> None:
        """
        Create a new HangmanGame and refresh the UI state.
        """
        secret_word = self.word_bank.getRandomWord(self.current_category)
        self.game = self.game_factory(secret_word)
        self._updateWordLabel()
        self._updateInfoLabel()
        self._enableInput()

    def _updateWordLabel(self) -> None:
        """
        Update the label that shows the masked word.
        """
        if self.game is not None and self.word_label is not None:
            self.word_label.config(text=self.game.getMaskedWord())

    def _updateInfoLabel(self) -> None:
        """
        Update info label (used letters & remaining attempts).
        """
        if self.game is None or self.info_label is None:
            return

        used_letters = ", ".join(sorted(self.game.used_letters)) or "None"
        remaining_attempts = self.game.max_attempts - self.game.wrong_guesses

        info_text = (
            f"Used letters: {used_letters} | "
            f"Remaining attempts: {remaining_attempts}"
        )
        self.info_label.config(text=info_text)

    def _onGuessSubmit(self, event: tk.Event) -> None:  # type: ignore[name-defined]
        """
        Handle the Return/Enter key to submit a guess.
        """
        self._processCurrentGuess()

    def _onGuessButtonClicked(self) -> None:
        """
        Handle the Guess button click.
        """
        self._processCurrentGuess()

    def _processCurrentGuess(self) -> None:
        """
        Read the current entry, send it to game logic, and update the UI.
        """
        if self.game is None or self.input_entry is None:
            return

        letter = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)

        if not letter:
            return

        # Process guess and update UI
        self.game.processGuess(letter)
        self._updateWordLabel()
        self._updateInfoLabel()

        if self.game.isWon():
            self._handleWin()
        elif self.game.isLost():
            self._handleLoss()

    def _handleWin(self) -> None:
        """
        Show a win message and disable further input.
        """
        self._disableInput()
        if self.game is not None:
            messagebox.showinfo("Hangman", "You won! The word was: " + self.game.secret_word)

    def _handleLoss(self) -> None:
        """
        Show a loss message and disable further input.
        """
        self._disableInput()
        if self.game is not None:
            messagebox.showinfo("Hangman", "You lost! The word was: " + self.game.secret_word)

    def _disableInput(self) -> None:
        """
        Disable the guess input and button.
        """
        if self.input_entry is not None:
            self.input_entry.config(state=tk.DISABLED)
        if self.guess_button is not None:
            self.guess_button.config(state=tk.DISABLED)

    def _enableInput(self) -> None:
        """
        Enable the guess input and button.
        """
        if self.input_entry is not None:
            self.input_entry.config(state=tk.NORMAL)
        if self.guess_button is not None:
            self.guess_button.config(state=tk.NORMAL)

    def _onResetButtonClicked(self) -> None:
        """
        Handler for the 'New Game' button.
        """
        self._startNewGame()