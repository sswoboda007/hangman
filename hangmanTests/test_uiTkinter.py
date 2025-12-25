# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_uiTkinter.py
"""
Unit tests for the Tkinter-based GUI (HangmanApp).

This test suite verifies the functionality of the HangmanApp, ensuring that
UI elements are created, updated, and respond correctly to user interactions.
It uses extensive mocking to isolate the GUI logic from the Tkinter framework,
allowing tests to run in a headless environment without a display.

Author: @seanl
Version: 2.0.3
Creation Date: 11/21/2025
Last Updated: 12/24/2025
"""

import tkinter as tk
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

import pytest

from gameLogic import HangmanGame
from uiTkinter import DEFAULT_CATEGORY, HangmanApp
from wordBank import WordBank


@pytest.fixture
def hangmanApp():
    with ExitStack() as stack:
        # Since tkinter is mocked in conftest.py, we don't need to patch Tk.__init__
        # to prevent the GUI from launching. The global mock handles it.
        
        # Remove autospec=True because these are now mocking Mocks (due to conftest.py)
        mock_messagebox = stack.enter_context(patch('uiTkinter.messagebox'))

        mock_option_menu = stack.enter_context(patch('tkinter.OptionMenu'))
        mock_option_menu.return_value = MagicMock(name="OptionMenu")

        mock_string_var = stack.enter_context(patch('tkinter.StringVar'))
        category_var = MagicMock(name="StringVar")
        mock_string_var.return_value = category_var

        mock_button = stack.enter_context(patch('tkinter.Button'))
        guess_button = MagicMock(name="GuessButton")
        guess_button.config = MagicMock(name="GuessButton.config")
        reset_button = MagicMock(name="ResetButton")
        reset_button.config = MagicMock(name="ResetButton.config")
        mock_button.side_effect = [guess_button, reset_button]

        mock_entry = stack.enter_context(patch('tkinter.Entry'))
        input_entry = MagicMock(name="Entry")
        input_entry.config = MagicMock(name="Entry.config")
        input_entry.get = MagicMock(name="Entry.get", return_value="")
        input_entry.delete = MagicMock(name="Entry.delete")
        mock_entry.return_value = input_entry

        mock_label = stack.enter_context(patch('tkinter.Label'))
        category_label = MagicMock(name="CategoryLabel")
        word_label = MagicMock(name="WordLabel")
        info_label = MagicMock(name="InfoLabel")
        input_label = MagicMock(name="InputLabel")
        mock_label.side_effect = [category_label, word_label, info_label, input_label]

        mock_frame = stack.enter_context(patch('tkinter.Frame'))
        mock_frame.side_effect = [
            MagicMock(name="MainFrame"),
            MagicMock(name="CategoryFrame"),
            MagicMock(name="InputFrame"),
        ]

        word_bank = MagicMock(spec=WordBank)
        word_bank.getRandomWord.return_value = "test"
        word_bank.getCategories.return_value = ["general", "animals"]

        game_instance = HangmanGame("test", max_attempts=6)
        game_instance.isWon = MagicMock(return_value=False)
        game_instance.isLost = MagicMock(return_value=False)
        game_instance.processGuess = MagicMock(name="processGuess")

        app = HangmanApp(word_bank=word_bank, game_factory=lambda word: game_instance)
        
        # Manually inject attributes that might be expected by Tkinter internals or app code
        # if they were previously set by the fakeTkInit
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
            inputEntry=input_entry,
            guessButton=guess_button,
            resetButton=reset_button,
        )


def testInitSetsUpGameAndWidgets(hangmanApp) -> None:
    ns = hangmanApp
    ns.wordBank.getRandomWord.assert_called_with(DEFAULT_CATEGORY)
    assert ns.app.game is ns.gameInstance
    ns.inputEntry.config.assert_called_with(state=tk.NORMAL)
    ns.guessButton.config.assert_called_with(state=tk.NORMAL)


def testStartNewGameRefreshesUiState(hangmanApp) -> None:
    ns = hangmanApp
    ns.wordBank.getRandomWord.reset_mock()
    ns.wordLabel.config.reset_mock()
    ns.infoLabel.config.reset_mock()
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.app.current_category = "animals"
    ns.wordBank.getRandomWord.return_value = "kangaroo"

    ns.app._startNewGame()

    ns.wordBank.getRandomWord.assert_called_once_with("animals")
    assert ns.wordLabel.config.call_count == 1
    assert ns.infoLabel.config.call_count == 1
    ns.inputEntry.config.assert_called_with(state=tk.NORMAL)
    ns.guessButton.config.assert_called_with(state=tk.NORMAL)


def testOnCategoryChangedUpdatesStateAndRestarts(hangmanApp) -> None:
    ns = hangmanApp
    # Configure the mock StringVar to return the expected category
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
    assert ns.infoLabel.config.call_args_list[-1] == call(
        text="Used letters: t | Remaining attempts: 6"
    )


def testProcessCurrentGuessHandlesInputAndUpdatesUi(hangmanApp) -> None:
    ns = hangmanApp
    ns.inputEntry.get.return_value = "E"
    ns.gameInstance.processGuess.reset_mock()

    with patch.object(ns.app, '_updateWordLabel') as mock_update_word, \
         patch.object(ns.app, '_updateInfoLabel') as mock_update_info:
        ns.app._processCurrentGuess()

    ns.gameInstance.processGuess.assert_called_once_with("E")
    ns.inputEntry.delete.assert_called_once_with(0, tk.END)
    mock_update_word.assert_called_once_with()
    mock_update_info.assert_called_once_with()


def testProcessCurrentGuessIgnoresEmptyInput(hangmanApp) -> None:
    ns = hangmanApp
    ns.inputEntry.get.return_value = "   "
    ns.gameInstance.processGuess.reset_mock()
    ns.inputEntry.delete.reset_mock()

    ns.app._processCurrentGuess()

    ns.inputEntry.delete.assert_called_once_with(0, tk.END)
    ns.gameInstance.processGuess.assert_not_called()


def testProcessCurrentGuessHandlesWinAndLoss(hangmanApp) -> None:
    ns = hangmanApp
    ns.inputEntry.get.return_value = "a"
    ns.messagebox.showinfo.reset_mock()
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.gameInstance.isWon.return_value = True
    ns.gameInstance.isLost.return_value = False
    ns.app._processCurrentGuess()

    ns.messagebox.showinfo.assert_called_with("Hangman", "You won! The word was: test")
    ns.inputEntry.config.assert_called_with(state=tk.DISABLED)
    ns.guessButton.config.assert_called_with(state=tk.DISABLED)

    ns.messagebox.showinfo.reset_mock()
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.gameInstance.isWon.return_value = False
    ns.gameInstance.isLost.return_value = True
    ns.app._processCurrentGuess()

    ns.messagebox.showinfo.assert_called_with("Hangman", "You lost! The word was: test")
    ns.inputEntry.config.assert_called_with(state=tk.DISABLED)
    ns.guessButton.config.assert_called_with(state=tk.DISABLED)


def testOnGuessSubmitDelegatesToProcess(hangmanApp) -> None:
    ns = hangmanApp
    with patch.object(ns.app, '_processCurrentGuess') as mock_process:
        ns.app._onGuessSubmit(event=None)
        mock_process.assert_called_once_with()


def testOnGuessButtonClickedDelegatesToProcess(hangmanApp) -> None:
    ns = hangmanApp
    with patch.object(ns.app, '_processCurrentGuess') as mock_process:
        ns.app._onGuessButtonClicked()
        mock_process.assert_called_once_with()


def testDisableAndEnableInputToggleWidgets(hangmanApp) -> None:
    ns = hangmanApp
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.app._disableInput()
    ns.inputEntry.config.assert_called_with(state=tk.DISABLED)
    ns.guessButton.config.assert_called_with(state=tk.DISABLED)

    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.app._enableInput()
    ns.inputEntry.config.assert_called_with(state=tk.NORMAL)
    ns.guessButton.config.assert_called_with(state=tk.NORMAL)


def testHandleWinShowsMessageAndDisablesInput(hangmanApp) -> None:
    ns = hangmanApp
    ns.messagebox.showinfo.reset_mock()
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.app._handleWin()

    ns.messagebox.showinfo.assert_called_with("Hangman", "You won! The word was: test")
    ns.inputEntry.config.assert_called_with(state=tk.DISABLED)
    ns.guessButton.config.assert_called_with(state=tk.DISABLED)


def testHandleLossShowsMessageAndDisablesInput(hangmanApp) -> None:
    ns = hangmanApp
    ns.messagebox.showinfo.reset_mock()
    ns.inputEntry.config.reset_mock()
    ns.guessButton.config.reset_mock()

    ns.app._handleLoss()

    ns.messagebox.showinfo.assert_called_with("Hangman", "You lost! The word was: test")
    ns.inputEntry.config.assert_called_with(state=tk.DISABLED)
    ns.guessButton.config.assert_called_with(state=tk.DISABLED)


def testOnResetButtonClickedStartsNewGame(hangmanApp) -> None:
    ns = hangmanApp
    with patch.object(ns.app, '_startNewGame') as mock_start:
        ns.app._onResetButtonClicked()
        mock_start.assert_called_once_with()
