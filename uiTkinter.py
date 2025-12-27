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
        self.title("⚡ QUANTUM HANGMAN - NEURAL INTERFACE ⚡")
        self.geometry("800x800")
        self.resizable(True, True)
        self.minsize(650, 750)
        self.configure(bg="#000000")

        self.word_bank: WordBank = word_bank
        self.game_factory: Callable[[str], HangmanGame] = game_factory
        self.game: Optional[HangmanGame] = None
        self.current_category: str = DEFAULT_CATEGORY
        self.score: int = 0
        self.canvas_bg: str = "#000511"

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
        self.after_idle(self._autosizeWindowToContent)

    def _setupUserInterface(self) -> None:
        """
        Builds cyberpunk GUI with neon styles.
        """
        self.scroll_canvas = tk.Canvas(self, bg="#000000", highlightthickness=0)
        scroll_bar = tk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        scroll_root = tk.Frame(self.scroll_canvas, bg="#000000")
        scroll_window = self.scroll_canvas.create_window((0, 0), window=scroll_root, anchor="nw")

        def _on_scroll_root_configure(event: tk.Event) -> None:  # type: ignore[name-defined]
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

        def _on_canvas_configure(event: tk.Event) -> None:  # type: ignore[name-defined]
            self.scroll_canvas.itemconfigure(scroll_window, width=event.width)

        scroll_root.bind("<Configure>", _on_scroll_root_configure)
        self.scroll_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event: tk.Event) -> None:  # type: ignore[name-defined]
            if not hasattr(event, "delta"):
                return
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main_frame = tk.Frame(scroll_root, bg="#000000", padx=40, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Header Frame with Gradient Effect
        header_frame = tk.Frame(main_frame, bg="#000000", height=40)
        header_frame.pack(fill="x", pady=(0, 5))
        
        title_label = tk.Label(
            header_frame,
            text="⚡ QUANTUM HANGMAN ⚡",
            font=("Consolas", 20, "bold"),
            fg="#00ffff",
            bg="#000000"
        )
        title_label.pack(pady=2)
        
        subtitle_label = tk.Label(
            header_frame,
            text="◈ NEURAL DECRYPTION PROTOCOL v3.0 ◈",
            font=("Consolas", 9),
            fg="#6666ff",
            bg="#000000"
        )
        subtitle_label.pack(pady=1)

        # Sector (Category) selection
        category_frame = tk.Frame(main_frame, bg="#0a0a1f", relief="solid", bd=1)
        category_frame.pack(fill="x", pady=(0, 15))
        
        category_inner = tk.Frame(category_frame, bg="#0a0a1f")
        category_inner.pack(pady=10, padx=15, fill="x")

        category_label = tk.Label(
            category_inner, 
            text="◈ SECTOR SELECT:",
            font=("Consolas", 10, "bold"), 
            fg="#00ffff", 
            bg="#0a0a1f"
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
            font=("Consolas", 10, "bold"), 
            fg="#000000", 
            bg="#00ffff", 
            activebackground="#66ffff", 
            activeforeground="#000000",
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        self.category_menu.pack(side="right", padx=(5, 0))

        # Holographic Display Canvas
        canvas_frame = tk.Frame(main_frame, bg="#000511", relief="solid", bd=2)
        canvas_frame.pack(pady=(0, 20))
        
        self.canvas = tk.Canvas(canvas_frame, width=240, height=300, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        # Decryption Display
        self.word_label = tk.Label(
            main_frame,
            text="",
            font=("Consolas", 36, "bold"),
            fg="#00ffff",
            bg="#000000",
            pady=10,
        )
        self.word_label.pack()

        # Mission Status
        self.info_label = tk.Label(
            main_frame,
            text="",
            font=("Consolas", 11, "bold"),
            fg="#6666ff",
            bg="#000000",
        )
        self.info_label.pack(pady=(0, 15))

        # Quantum Keyboard Interface
        keyboard_frame = tk.Frame(main_frame, bg="#0a0a1f", relief="solid", bd=2)
        keyboard_frame.pack(pady=20, fill="both", expand=True)
        
        keyboard_title = tk.Label(
            keyboard_frame,
            text="◈ NEURAL KEYBOARD INTERFACE ◈",
            font=("Consolas", 10, "bold"),
            fg="#6666ff",
            bg="#0a0a1f"
        )
        keyboard_title.pack(pady=(20, 15))

        key_container = tk.Frame(keyboard_frame, bg="#0a0a1f")
        key_container.pack(pady=15, padx=40)

        # Define keyboard rows
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        
        for i, row_letters in enumerate(rows):
            row_frame = tk.Frame(key_container, bg="#0a0a1f")
            row_frame.pack(pady=10)
            
            # Center the middle row (ASDFGHJKL)
            if i == 1:  # Middle row
                # Add left padding to center
                left_spacer = tk.Frame(row_frame, bg="#0a0a1f", width=25)
                left_spacer.pack(side="left")
            
            for char in row_letters:
                btn = tk.Button(
                    row_frame,
                    text=char,
                    width=6,
                    height=2,
                    font=("Consolas", 11, "bold"),
                    fg="#000000",
                    bg="#00ffff",
                    activeforeground="#000511",
                    activebackground="#66ffff",
                    relief="solid",
                    bd=1,
                    highlightthickness=2,
                    highlightbackground="#00ffff",
                    command=lambda c=char: self._onGuess(c)
                )
                btn.pack(side="left", padx=3)
                self.letter_buttons[char] = btn

        # Bind physical keyboard
        self.bind("<Key>", self._onPhysicalKey)

        # Command Center
        control_frame = tk.Frame(main_frame, bg="#0a0a1f", relief="solid", bd=1)
        control_frame.pack(pady=(20, 10), fill="x")
        
        control_inner = tk.Frame(control_frame, bg="#0a0a1f")
        control_inner.pack(pady=15)

        # Quantum Hint Button
        self.hint_button = tk.Button(
            control_inner,
            text=f"◉ NEURAL SCAN [-{HINT_COST} ENERGY]",
            command=self._onHintButtonClicked,
            font=("Consolas", 10, "bold"),
            fg="#000511",
            bg="#6666ff",
            activeforeground="#000000",
            activebackground="#8888ff",
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground="#6666ff",
            padx=20,
            pady=8
        )
        self.hint_button.pack(side="left", padx=10)

        # System Reset Button
        self.reset_button = tk.Button(
            control_inner,
            text="◈ SYSTEM RESET",
            command=self._onResetButtonClicked,
            font=("Consolas", 10, "bold"),
            fg="#000000",
            bg="#ff3366",
            activeforeground="#000000",
            activebackground="#ff6699",
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground="#ff3366",
            padx=20,
            pady=8
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
            self.bonus_label.config(text=f"◉ NEURAL BONUS MATRIX: {bonus_str} ACTIVATED")

    def _updateWordLabel(self) -> None:
        if self.game is not None and self.word_label is not None:
            self.word_label.config(text=self.game.getMaskedWord())

    def _updateInfoLabel(self) -> None:
        if self.game is None or self.info_label is None:
            return

        remaining_attempts = self.game.max_attempts - self.game.wrong_guesses
        info_text = f"◉ ENERGY: {remaining_attempts}/{self.game.max_attempts} | SECTOR: {self.current_category.upper()} | SCORE: {self.score}"
        self.info_label.config(text=info_text)

    def _updateCanvas(self) -> None:
        if self.game is None or self.canvas is None:
            return

        self.canvas.delete("all")
        self.canvas.configure(bg=self.canvas_bg)

        # Quantum Gallows Structure
        # Base platform
        self.canvas.create_rectangle(50, 255, 170, 265, fill="#0a0a1f", outline="#00ffff", width=2)
        # Main pillar
        self.canvas.create_line(110, 255, 110, 50, fill="#00ffff", width=6, capstyle=tk.ROUND)
        # Support beam
        self.canvas.create_line(110, 50, 170, 50, fill="#00ffff", width=5, capstyle=tk.ROUND)
        # Energy node
        self.canvas.create_oval(165, 45, 175, 55, fill="#6666ff", outline="#3333ff", width=2)
        # Plasma rope
        self.canvas.create_line(170, 55, 170, 85, fill="#ff3366", width=4, capstyle=tk.ROUND, dash=(5, 2))

        wrong = self.game.wrong_guesses

        if wrong >= 1:  # Head - Neural interface
            self.canvas.create_oval(155, 85, 185, 115, outline="#00ffff", width=4)
            self.canvas.create_oval(160, 90, 180, 110, outline="#6666ff", width=2, fill="#000511")
            # Neural nodes
            self.canvas.create_oval(165, 95, 170, 100, fill="#00ffff", outline="#00ffff")
            self.canvas.create_oval(170, 95, 175, 100, fill="#00ffff", outline="#00ffff")
        if wrong >= 2:  # Body - Energy core
            self.canvas.create_line(170, 110, 170, 190, fill="#00ffff", width=5)
            # Core reactor
            self.canvas.create_rectangle(165, 145, 175, 155, fill="#6666ff", outline="#9999ff", width=2)
        if wrong >= 3:  # Left Arm - Plasma conduit
            self.canvas.create_line(170, 130, 150, 160, fill="#ff3366", width=4)
            self.canvas.create_oval(148, 158, 152, 162, fill="#ff3366", outline="#ff3366")
        if wrong >= 4:  # Right Arm - Plasma conduit
            self.canvas.create_line(170, 130, 190, 160, fill="#ff3366", width=4)
            self.canvas.create_oval(188, 158, 192, 162, fill="#ff3366", outline="#ff3366")
        if wrong >= 5:  # Left Leg - Quantum stabilizer
            self.canvas.create_line(170, 190, 150, 220, fill="#6666ff", width=4)
            self.canvas.create_oval(148, 218, 152, 222, fill="#00ffff", outline="#00ffff")
        if wrong >= 6:  # Right Leg - Quantum stabilizer
            self.canvas.create_line(170, 190, 190, 220, fill="#6666ff", width=4)
            self.canvas.create_oval(188, 218, 192, 222, fill="#00ffff", outline="#00ffff")
            # System overload effect
            self.canvas.create_text(110, 280, text="⚠ SYSTEM OVERLOAD ⚠", fill="#ff3366", font=("Consolas", 10, "bold"))

    def _autosizeWindowToContent(self) -> None:
        if not self.winfo_exists():
            return

        self.update_idletasks()

        req_w = self.winfo_reqwidth()
        req_h = self.winfo_reqheight()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        target_w = min(req_w + 40, screen_w - 80)
        target_h = min(req_h + 40, screen_h - 80)

        self.geometry(f"{target_w}x{target_h}")
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

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
            # Critical error flash
            self.canvas.configure(bg="#2a0000")
            self.after(150, lambda: self.canvas.configure(bg=self.canvas_bg))

        self._refreshUiAfterAction()

    def _onHintButtonClicked(self) -> None:
        if self.game is None or self.game.isFinished():
            return

        revealed = self.game.useHint()
        if revealed:
            messagebox.showinfo(
                "◉ QUANTUM SCAN COMPLETE", 
                f"Neural Network Analysis:\nRevealed: **{revealed.upper()}**\nEnergy Cost: {HINT_COST} units"
            )
            self._refreshUiAfterAction()
        else:
            messagebox.showwarning("Quantum Hint Unavailable", "⚠ Insufficient energy reserves!\nRequire more life units or all sectors scanned.")

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
                btn.config(state=tk.DISABLED, bg="#333366", fg="#6666ff")
            else:
                btn.config(state=tk.NORMAL, bg="#00ffff", fg="#000000")

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
        # Ensure messagebox appears on top
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        
        messagebox.showinfo(
            "◉ DECRYPTION SUCCESS!", 
            f"Network Access Granted!\nTarget: **{self.game.secret_word.upper()}**\nPoints Awarded: +{points} | Total Score: {self.score}"
        )

    def _handleLoss(self) -> None:
        self._disableInput()
        if self.word_label and self.game:
            self.word_label.config(text=self.game.secret_word.upper(), fg="#ff0000")
        self._updateCanvas()
        # Ensure messagebox appears on top
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        
        messagebox.showinfo(
            "◉ SYSTEM BREACH DETECTED", 
            f"Decryption Protocol Failed!\nTarget: **{self.game.secret_word.upper()}**\nFinal Score: {self.score}"
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
