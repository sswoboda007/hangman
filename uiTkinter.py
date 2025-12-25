# -*- coding: utf-8 -*-
# hangman/uiTkinter.py

"""
Implements a futuristic Tkinter-based GUI for the Neo-Hangman game.

This module provides the HangmanApp class, a cyberpunk-themed graphical user
interface for the Hangman game. Neon glows, neural bonuses, score tracking.

Author: @seanl
Version: 1.6.0
Creation Date: 11/20/2025
Last Updated: 12/25/2025
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Any, Dict

from gameLogic import HangmanGame, HINT_COST, AUTO_REVEAL_LETTERS
from wordBank import WordBank, DEFAULT_CATEGORY


class HangmanApp(tk.Tk):
    """
    Main window for the Neo-Hangman game (Futuristic Tkinter GUI).
    """

    def __init__(
        self,
        word_bank: WordBank,
        game_factory: Callable[[str], HangmanGame],
        **kwargs: Any
    ) -> None:
        """
        Initialize the Neo-Hangman GUI.
        """
        super().__init__(**kwargs)
        self.title("Neo-Hangman: AI Edition 🚀")
        self.geometry("550x750")
        self.resizable(False, False)
        self.configure(bg="#000000")

        self.word_bank: WordBank = word_bank
        self.game_factory: Callable[[str], HangmanGame] = game_factory
        self.game: Optional[HangmanGame] = None
        self.current_category: str = DEFAULT_CATEGORY
        self.score: int = 0
        self.canvas_bg: str = "#000011"

        self.canvas: Optional[tk.Canvas] = None
        self.word_label: Optional[tk.Label] = None
        self.info_label: Optional[tk.Label] = None
        self.bonus_label: Optional[tk.Label] = None
        self.reset_button: Optional[tk.Button] = None
        self.hint_button: Optional[tk.Button] = None
        self.category_var: Optional[tk.StringVar] = None
        self.category_menu: Optional[tk.OptionMenu] = None
        
        # Virtual Keyboard
        self.letter_buttons: Dict[str, tk.Button] = {}

        self._setupUserInterface()
        self._startNewGame()

    def _setupUserInterface(self) -> None:
        """
        Builds cyberpunk GUI with neon styles.
        """
        main_frame = tk.Frame(self, bg="#0a0a0a", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Sector (Category) selection
        category_frame = tk.Frame(main_frame, bg="#0a0a0a")
        category_frame.pack(fill="x", pady=(0, 10))

        category_label = tk.Label(
            category_frame, 
            text="Sector:", 
            font=("Courier", 12, "bold"), 
            fg="#00bfff", 
            bg="#0a0a0a"
        )
        category_label.pack(side="left")

        self.category_var = tk.StringVar(value=self.current_category)
        categories = self.word_bank.getCategories()
        self.category_menu = tk.OptionMenu(
            category_frame,
            self.category_var,
            *categories,
            command=self._onCategoryChanged,
        )
        self.category_menu.configure(
            font=("Courier", 10, "bold"), 
            fg="#000", 
            bg="#00ffff", 
            activebackground="#0080ff", 
            activeforeground="#fff"
        )
        self.category_menu.pack(side="left", padx=(5, 0))

        # Neural Bonus Label
        self.bonus_label = tk.Label(
            main_frame,
            text="Initializing Neural Bonus...",
            font=("Courier", 11, "bold"),
            fg="#ffd700",
            bg="#0a0a0a",
            pady=5
        )
        self.bonus_label.pack(pady=(0, 10))

        # Cyber Canvas for Hangman (neon drawing)
        self.canvas = tk.Canvas(main_frame, width=220, height=280, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(pady=(0, 20))

        # Masked word label (neon green)
        self.word_label = tk.Label(
            main_frame,
            text="",
            font=("Courier", 32, "bold"),
            fg="#00ff41",
            bg="#0a0a0a",
            pady=10,
        )
        self.word_label.pack()

        # Info label (cyber stats)
        self.info_label = tk.Label(
            main_frame,
            text="",
            font=("Courier", 12, "bold"),
            fg="#00bfff",
            bg="#0a0a0a",
        )
        self.info_label.pack(pady=(0, 10))

        # Virtual Keyboard (3-row layout)
        keyboard_frame = tk.Frame(main_frame, bg="#0a0a0a")
        keyboard_frame.pack(pady=10)

        # Define keyboard rows
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        
        for i, row_letters in enumerate(rows):
            row_frame = tk.Frame(keyboard_frame, bg="#0a0a0a")
            row_frame.pack(pady=2)
            
            for char in row_letters:
                btn = tk.Button(
                    row_frame,
                    text=char,
                    width=4,
                    height=2,
                    font=("Courier", 10, "bold"),
                    fg="#00ffff",
                    bg="#16213e",
                    activeforeground="#fff",
                    activebackground="#533483",
                    relief="raised",
                    bd=2,
                    command=lambda c=char: self._onGuess(c)
                )
                btn.pack(side="left", padx=2)
                self.letter_buttons[char] = btn

        # Bind physical keyboard
        self.bind("<Key>", self._onPhysicalKey)

        # Control Buttons
        control_frame = tk.Frame(main_frame, bg="#0a0a0a")
        control_frame.pack(pady=(20, 0))

        # Neural Hint
        self.hint_button = tk.Button(
            control_frame,
            text=f"Neural Hint (-{HINT_COST} lives)",
            command=self._onHintButtonClicked,
            font=("Courier", 10, "bold"),
            fg="#fff",
            bg="#4169e1",
            activebackground="#1e3a8a",
            relief="raised",
            padx=10
        )
        self.hint_button.pack(side="left", padx=10)

        # Warp Restart
        self.reset_button = tk.Button(
            control_frame,
            text="Warp Restart",
            command=self._onResetButtonClicked,
            font=("Courier", 10, "bold"),
            fg="#fff",
            bg="#2f4f4f",
            activebackground="#1c2f36",
            relief="raised",
            padx=10
        )
        self.reset_button.pack(side="left", padx=10)

    def _onCategoryChanged(self, new_category: object) -> object | None:
        if self.category_var is not None:
            self.current_category = self.category_var.get()
        else:
            self.current_category = str(new_category)
        self._startNewGame()
        return None

    def _startNewGame(self) -> None:
        secret_word = self.word_bank.getRandomWord(self.current_category)
        self.game = self.game_factory(secret_word)
        
        # UI Reset
        if self.word_label:
            self.word_label.config(fg="#00ff41", text=self.game.getMaskedWord())
        
        self._updateWordLabel()
        self._updateInfoLabel()
        self._updateCanvas()
        self._enableInput()
        self._updateButtons()
        self._updateHintButton()
        self._updateBonusLabel()

    def _updateBonusLabel(self) -> None:
        if self.bonus_label:
            bonus_str = " ".join(sorted(AUTO_REVEAL_LETTERS)).upper()
            self.bonus_label.config(text=f"Neural Bonus: {bonus_str} ACTIVATED! 💫")

    def _updateWordLabel(self) -> None:
        if self.game is not None and self.word_label is not None:
            self.word_label.config(text=self.game.getMaskedWord())

    def _updateInfoLabel(self) -> None:
        if self.game is None or self.info_label is None:
            return

        remaining_attempts = self.game.max_attempts - self.game.wrong_guesses
        info_text = f"Lives: {remaining_attempts}/{self.game.max_attempts} | Sector: {self.current_category.upper()} | Score: {self.score}"
        self.info_label.config(text=info_text)

    def _updateCanvas(self) -> None:
        if self.game is None or self.canvas is None:
            return

        self.canvas.delete("all")
        self.canvas.configure(bg=self.canvas_bg)

        # Neon Gallows (cyan glow)
        self.canvas.create_line(60, 260, 160, 260, fill="#00ffff", width=5, capstyle=tk.ROUND)  # Base
        self.canvas.create_line(110, 260, 110, 60, fill="#00ffff", width=5, capstyle=tk.ROUND)  # Pole
        self.canvas.create_line(110, 60, 160, 60, fill="#00ffff", width=5, capstyle=tk.ROUND)  # Top
        self.canvas.create_line(160, 60, 160, 90, fill="#ff00ff", width=4, capstyle=tk.ROUND)  # Rope (magenta)

        wrong = self.game.wrong_guesses

        if wrong >= 1:  # Head (glow effect)
            self.canvas.create_oval(145, 85, 175, 115, outline="#00ffff", width=4)
            self.canvas.create_oval(150, 90, 170, 110, outline="#ffff00", width=2, fill="#ff00ff")
        if wrong >= 2:  # Body (magenta)
            self.canvas.create_line(160, 110, 160, 190, fill="#ff1493", width=4)
        if wrong >= 3:  # Left Arm
            self.canvas.create_line(160, 140, 140, 160, fill="#ff69b4", width=3)
        if wrong >= 4:  # Right Arm
            self.canvas.create_line(160, 140, 180, 160, fill="#ff69b4", width=3)
        if wrong >= 5:  # Left Leg
            self.canvas.create_line(160, 190, 140, 220, fill="#ff1493", width=3)
        if wrong >= 6:  # Right Leg
            self.canvas.create_line(160, 190, 180, 220, fill="#ff1493", width=3)

    def _onPhysicalKey(self, event: tk.Event) -> None:  # type: ignore[name-defined]
        if event.char and event.char.isalpha():
            self._onGuess(event.char.upper())

    def _onGuess(self, letter: str) -> None:
        if self.game is None or self.game.isFinished():
            return

        if letter.lower() in self.game.used_letters:
            return

        was_correct = self.game.processGuess(letter)
        if not was_correct:
            self.bell()  # System error beep
            # Quick red flash
            self.canvas.configure(bg="#220000")
            self.after(150, lambda: self.canvas.configure(bg=self.canvas_bg))

        self._refreshUiAfterAction()

    def _onHintButtonClicked(self) -> None:
        if self.game is None or self.game.isFinished():
            return

        revealed = self.game.useHint()
        if revealed:
            messagebox.showinfo(
                "🧠 Neural Hint", 
                f"AI Scan Complete!\nRevealed: **{revealed.upper()}**\nLives deducted: {HINT_COST}"
            )
            self._refreshUiAfterAction()
        else:
            messagebox.showwarning("Neural Hint Unavailable", "Insufficient energy! Need more lives or all letters scanned.")

    def _refreshUiAfterAction(self) -> None:
        if self.game is None:
            return

        self._updateWordLabel()
        self._updateInfoLabel()
        self._updateCanvas()
        self._updateButtons()
        self._updateHintButton()

        if self.game.isWon():
            self._handleWin()
        elif self.game.isLost():
            self._handleLoss()

    def _updateButtons(self) -> None:
        if self.game is None:
            return
            
        for char, btn in self.letter_buttons.items():
            if char.lower() in self.game.used_letters:
                btn.config(state=tk.DISABLED, bg="#333333", fg="#666")
            else:
                btn.config(state=tk.NORMAL, bg="#16213e", fg="#00ffff")

    def _updateHintButton(self) -> None:
        if self.game is None or self.hint_button is None:
            return
            
        remaining = self.game.max_attempts - self.game.wrong_guesses
        self.hint_button.config(state=tk.NORMAL if remaining >= HINT_COST else tk.DISABLED)

    def _handleWin(self) -> None:
        self._disableInput()
        if self.word_label:
            self.word_label.config(fg="#00ff41")
        points = (self.game.max_attempts - self.game.wrong_guesses) * len(self.game.secret_word)
        self.score += points
        self._updateInfoLabel()
        self.bell()
        self.after(200, self.bell)
        self.after(400, self.bell)
        messagebox.showinfo(
            "🎉 Neural Victory!", 
            f"Network Secured!\nWord: **{self.game.secret_word.upper()}**\nPoints Earned: +{points} | Total: {self.score}"
        )

    def _handleLoss(self) -> None:
        self._disableInput()
        if self.word_label and self.game:
            self.word_label.config(text=self.game.secret_word.upper(), fg="#ff0000")
        self._updateCanvas()
        messagebox.showinfo(
            "💀 System Breach!", 
            f"Decryption Failed!\nSecret: **{self.game.secret_word.upper()}**\nTotal Score: {self.score}"
        )

    def _disableInput(self) -> None:
        for btn in self.letter_buttons.values():
            btn.config(state=tk.DISABLED)
        if self.hint_button:
            self.hint_button.config(state=tk.DISABLED)

    def _enableInput(self) -> None:
        for btn in self.letter_buttons.values():
            btn.config(state=tk.NORMAL)
        if self.hint_button:
            self.hint_button.config(state=tk.NORMAL)

    def _onResetButtonClicked(self) -> None:
        self._startNewGame()
