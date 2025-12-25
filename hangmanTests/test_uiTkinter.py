# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_uiTkinter.py
"""
Unit tests for the Tkinter-based GUI (HangmanApp).

This test suite verifies the functionality of the HangmanApp, ensuring that
UI elements are created, updated, and respond correctly to user interactions.
It uses extensive mocking to isolate the GUI logic from the Tkinter framework,
allowing tests to run in a headless environment without a display.

Author: @seanl
Version: 2.9.0
Creation Date: 11/21/2025
Last Updated: 12/25/2025
"""

import tkinter as tk
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

import pytest

from gameLogic import HangmanGame, HINT_COST
from uiTkinter import DEFAULT_CATEGORY, HangmanApp
from wordBank import WordBank


@pytest.fixture
def hangmanApp():
    with ExitStack() as stack:
        # Since tkinter is mocked in conftest.py, we don't need to patch Tk.__init__
        # to prevent the GUI from launching. The global mock handles it.
        
        mock_messagebox = stack.enter_context(patch('uiTkinter.messagebox'))

        mock_option_menu = stack.enter_context(patch('tkinter.OptionMenu'))
        mock_option_menu.return_value = MagicMock(name="OptionMenu")

        mock_string_var = stack.enter_context(patch('tkinter.StringVar'))
        category_var = MagicMock(name="StringVar")
        mock_string_var.return_value = category_var

        # Mock Button creation. We need to capture the buttons created for the keyboard.
        mock_button = stack.enter_context(patch('tkinter.Button'))
        
        # We'll use a side_effect to return distinct mocks for each button creation
        def button_side_effect(*args, **kwargs):
            btn = MagicMock(name="Button")
            btn.config = MagicMock(name="Button.config")
            return btn
        
        mock_button.side_effect = button_side_effect

        mock_label = stack.enter_context(patch('tkinter.Label'))
        category_label = MagicMock(name="CategoryLabel")
        bonus_label = MagicMock(name="BonusLabel") # Added for futuristic UI
        word_label = MagicMock(name="WordLabel")
        info_label = MagicMock(name="InfoLabel")
        # Updated side_effect to include bonus_label
        mock_label.side_effect = [category_label, bonus_label, word_label, info_label]

        mock_frame = stack.enter_context(patch('tkinter.Frame'))
        # Use a side_effect function for robust frame mocking
        def frame_side_effect(*args, **kwargs):
            return MagicMock(name="Frame")
        mock_frame.side_effect = frame_side_effect

        mock_canvas = stack.enter_context(patch('tkinter.Canvas'))
        canvas = MagicMock(name="Canvas")
        mock_canvas.return_value = canvas

        word_bank = MagicMock(spec=WordBank)
        word_bank.getRandomWord.return_value = "test"
        word_bank.getCategories.return_value = ["general", "animals"]

        # Note: "test" contains 't', 'e', 's' which are all in RSTLNE.
        # So used_letters will be populated on init.
        game_instance = HangmanGame("test", max_attempts=6)
        game_instance.isWon = MagicMock(return_value=False)
        game_instance.isLost = MagicMock(return_value=False)
        game_instance.processGuess = MagicMock(name="processGuess")
        game_instance.useHint = MagicMock(name="useHint")
        game_instance.isFinished = MagicMock(return_value=False)

        app = HangmanApp(word_bank=word_bank, game_factory=lambda word: game_instance)
        
        # Manually inject attributes that might be expected by Tkinter internals or app code
        app.tk = MagicMock(name="tk")
        app.tk.call = MagicMock(name="tk.call")
        app._w = "mocked_tk"
        app.children = {}

        yield SimpleNamespace(
            app=app,
            wordBank=word_bank,
            gameInstance=game_instance,
            messagebox=mock_messagebox,
            categoryVar=category_var,
            wordLabel=word_label,
            infoLabel=info_label,
            resetButton=app.reset_button,
            hintButton=app.hint_button,
            canvas=canvas,
            mockButton=mock_button
        )


def testInitSetsUpGameAndWidgets(hangmanApp) -> None:
    ns = hangmanApp
    ns.wordBank.getRandomWord.assert_called_with(DEFAULT_CATEGORY)
    assert ns.app.game is ns.gameInstance
    
    # Verify 26 letter buttons + hint + reset
    assert len(ns.app.letter_buttons) == 26
    assert ns.app.hint_button is not None
    assert ns.app.reset_button is not None
    
    # Verify canvas creation
    assert ns.app.canvas is ns.canvas


def testStartNewGameRefreshesUiState(hangmanApp) -> None:
    ns = hangmanApp
    ns.wordBank.getRandomWord.reset_mock()
    ns.wordLabel.config.reset_mock()
    ns.infoLabel.config.reset_mock()
    ns.canvas.delete.reset_mock()
    ns.hintButton.config.reset_mock()

    ns.app.current_category = "animals"
    ns.wordBank.getRandomWord.return_value = "kangaroo"

    ns.app._startNewGame()

    ns.wordBank.getRandomWord.assert_called_once_with("animals")
    assert ns.wordLabel.config.call_count >= 1
    assert ns.infoLabel.config.call_count == 1
    ns.canvas.delete.assert_called_with("all")
    ns.hintButton.config.assert_called_with(state=tk.NORMAL)


def testOnCategoryChangedUpdatesStateAndRestarts(hangmanApp) -> None:
    ns = hangmanApp
    ns.categoryVar.get.return_value = "animals"

    with patch.object(ns.app, '_startNewGame') as mock_start:
        ns.app._onCategoryChanged("animals")
        assert ns.app.current_category == "animals"
        mock_start.assert_called_once_with()


def testUpdateLabelsRefreshesWordAndInfo(hangmanApp) -> None:
    ns = hangmanApp
    with patch.object(ns.app.game, 'getMaskedWord', return_value="t _ _ t"):
        ns.app.game.used_letters = {"t"}
        ns.app.game.wrong_guesses = 0
        ns.app._updateWordLabel()
        ns.app._updateInfoLabel()

    assert ns.wordLabel.config.call_args_list[-1] == call(text="t _ _ t")
    # Updated for futuristic UI text
    assert "Lives: 6/6" in ns.infoLabel.config.call_args_list[-1][1]['text']


def testOnGuessHandlesInputAndUpdatesUi(hangmanApp) -> None:
    ns = hangmanApp
    ns.gameInstance.processGuess.reset_mock()

    with patch.object(ns.app, '_updateWordLabel') as mock_update_word, \
         patch.object(ns.app, '_updateInfoLabel') as mock_update_info, \
         patch.object(ns.app, '_updateCanvas') as mock_update_canvas, \
         patch.object(ns.app, '_updateButtons') as mock_update_buttons, \
         patch.object(ns.app, '_updateHintButton') as mock_update_hint:
        
        # Use 'Z' because 'E' is in RSTLNE and is auto-revealed in "test"
        ns.app._onGuess("Z")

    ns.gameInstance.processGuess.assert_called_once_with("Z")
    mock_update_word.assert_called_once_with()
    mock_update_info.assert_called_once_with()
    mock_update_canvas.assert_called_once_with()
    mock_update_buttons.assert_called_once_with()
    mock_update_hint.assert_called_once_with()


def testOnGuessIgnoresUsedLetters(hangmanApp) -> None:
    ns = hangmanApp
    ns.gameInstance.used_letters = {"z"}
    ns.gameInstance.processGuess.reset_mock()

    ns.app._onGuess("Z")

    ns.gameInstance.processGuess.assert_not_called()


def testOnGuessIgnoresFinishedGame(hangmanApp) -> None:
    ns = hangmanApp
    ns.gameInstance.isFinished.return_value = True
    ns.gameInstance.processGuess.reset_mock()

    ns.app._onGuess("A")

    ns.gameInstance.processGuess.assert_not_called()


def testOnGuessHandlesWinAndLoss(hangmanApp) -> None:
    ns = hangmanApp
    ns.messagebox.showinfo.reset_mock()
    
    # Test Win
    ns.gameInstance.isWon.return_value = True
    ns.gameInstance.isLost.return_value = False
    # Use 'A' (not in RSTLNE)
    ns.app._onGuess("A")

    # Updated for futuristic UI text
    args, _ = ns.messagebox.showinfo.call_args
    assert "Neural Victory!" in args[0]
    ns.app.letter_buttons['A'].config.assert_called_with(state=tk.DISABLED)
    ns.wordLabel.config.assert_called_with(fg="#00ff41")

    # Reset for Loss test
    ns.messagebox.showinfo.reset_mock()
    ns.gameInstance.isWon.return_value = False
    ns.gameInstance.isLost.return_value = True
    
    # Use 'B' (not in RSTLNE)
    ns.app._onGuess("B")

    # Updated for futuristic UI text
    args, _ = ns.messagebox.showinfo.call_args
    assert "System Breach!" in args[0]
    ns.app.letter_buttons['B'].config.assert_called_with(state=tk.DISABLED)


def testUpdateButtonsDisablesUsedLetters(hangmanApp) -> None:
    ns = hangmanApp
    ns.gameInstance.used_letters = {"a", "z"}
    
    ns.app._updateButtons()
    
    ns.app.letter_buttons['A'].config.assert_called_with(state=tk.DISABLED, bg="#333333", fg="#666")
    ns.app.letter_buttons['Z'].config.assert_called_with(state=tk.DISABLED, bg="#333333", fg="#666")
    ns.app.letter_buttons['B'].config.assert_called_with(state=tk.NORMAL, bg="#16213e", fg="#00ffff")


def testPhysicalKeyBinding(hangmanApp) -> None:
    ns = hangmanApp
    event = MagicMock()
    event.char = "k"
    
    with patch.object(ns.app, '_onGuess') as mock_guess:
        ns.app._onPhysicalKey(event)
        mock_guess.assert_called_once_with("K")


def testUpdateCanvasDrawsAllBodyParts(hangmanApp) -> None:
    """
    Test that _updateCanvas draws all body parts for 6 wrong guesses.
    """
    ns = hangmanApp
    ns.canvas.delete.reset_mock()
    ns.canvas.create_line.reset_mock()
    ns.canvas.create_oval.reset_mock()

    # Simulate 6 wrong guesses
    ns.app.game.wrong_guesses = 6
    ns.app._updateCanvas()

    # Should clear canvas
    ns.canvas.delete.assert_called_with("all")

    # Gallows (4 lines) + Head (2 ovals) + Body (1 line) + 4 Limbs (4 lines) = 9 lines
    assert ns.canvas.create_line.call_count == 9
    assert ns.canvas.create_oval.call_count == 2
    assert ns.canvas.create_oval.called


def testUpdateCanvasHandlesNone(hangmanApp) -> None:
    """
    Test defensive check: _updateCanvas should not crash if game or canvas is None.
    """
    ns = hangmanApp
    
    # Case 1: game is None
    ns.app.game = None
    ns.canvas.delete.reset_mock()
    ns.app._updateCanvas()
    ns.canvas.delete.assert_not_called()
    
    # Case 2: canvas is None
    ns.app.game = ns.gameInstance
    ns.app.canvas = None
    ns.app._updateCanvas()
    # No crash expected
    
    # Restore canvas
    ns.app.canvas = ns.canvas

def testHintButtonCallsUseHint(hangmanApp) -> None:
    """
    Test that clicking the hint button calls game.useHint().
    """
    ns = hangmanApp
    ns.gameInstance.useHint.return_value = "e"
    
    with patch.object(ns.app, '_refreshUiAfterAction') as mock_refresh:
        ns.app._onHintButtonClicked()
        
        ns.gameInstance.useHint.assert_called_once()
        # Updated for futuristic UI text
        args, _ = ns.messagebox.showinfo.call_args
        assert "Neural Hint" in args[0]
        mock_refresh.assert_called_once()

def testHintButtonShowsWarningIfFailed(hangmanApp) -> None:
    """
    Test that hint button shows warning if useHint returns None.
    """
    ns = hangmanApp
    ns.gameInstance.useHint.return_value = None
    
    ns.app._onHintButtonClicked()
    
    # Updated for futuristic UI text
    args, _ = ns.messagebox.showwarning.call_args
    assert "Neural Hint Unavailable" in args[0]

def testUpdateHintButtonDisablesIfLowLives(hangmanApp) -> None:
    """
    Test that hint button is disabled if remaining attempts < HINT_COST.
    """
    ns = hangmanApp
    # Max 6, wrong 5 -> 1 remaining. Cost is 2. Should disable.
    ns.gameInstance.max_attempts = 6
    ns.gameInstance.wrong_guesses = 5
    
    ns.app._updateHintButton()
    
    ns.hintButton.config.assert_called_with(state=tk.DISABLED)

def testUpdateHintButtonEnablesIfEnoughLives(hangmanApp) -> None:
    """
    Test that hint button is enabled if remaining attempts >= HINT_COST.
    """
    ns = hangmanApp
    # Max 6, wrong 0 -> 6 remaining. Cost is 2. Should enable.
    ns.gameInstance.max_attempts = 6
    ns.gameInstance.wrong_guesses = 0
    
    ns.app._updateHintButton()
    
    ns.hintButton.config.assert_called_with(state=tk.NORMAL)

def testOnResetButtonClicked(hangmanApp) -> None:
    """
    Test that clicking the reset button calls _startNewGame.
    """
    ns = hangmanApp
    with patch.object(ns.app, '_startNewGame') as mock_start:
        ns.app._onResetButtonClicked()
        mock_start.assert_called_once()

def testDefensiveChecksForNoneGame(hangmanApp) -> None:
    """
    Test that methods with `if self.game is None: return` are covered.
    """
    ns = hangmanApp
    
    # Reset mocks to clear any calls from fixture setup
    ns.infoLabel.config.reset_mock()
    ns.gameInstance.processGuess.reset_mock()
    ns.gameInstance.useHint.reset_mock()

    ns.app.game = None
    
    # These methods should not raise an error
    ns.app._updateInfoLabel()
    ns.app._onGuess("A")
    ns.app._onHintButtonClicked()
    ns.app._refreshUiAfterAction()
    ns.app._updateButtons()
    ns.app._updateHintButton()
    
    # Verify no downstream calls were made
    ns.infoLabel.config.assert_not_called()
    ns.gameInstance.processGuess.assert_not_called()
    ns.gameInstance.useHint.assert_not_called()
    
def testOnCategoryChangedWithStrArgument(hangmanApp) -> None:
    """
    Test _onCategoryChanged when the argument is a plain string.
    """
    ns = hangmanApp
    ns.app.category_var = None # Simulate case where it's not set
    with patch.object(ns.app, '_startNewGame') as mock_start:
        ns.app._onCategoryChanged("new_category")
        assert ns.app.current_category == "new_category"
        mock_start.assert_called_once()
