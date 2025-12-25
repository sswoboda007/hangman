# -*- coding: utf-8 -*-
# hangman/hangmanTests/conftest.py
"""
Pytest configuration and fixtures.

This module handles environment setup for tests, specifically mocking
tkinter for headless environments where system libraries might be missing.
This code runs before any tests are collected, preventing ImportError.

Author: @seanl
Version: 1.1.0
Creation Date: 12/24/2025
Last Updated: 12/25/2025
"""

import sys
from unittest.mock import MagicMock

# Create a mock module for tkinter
mock_tk = MagicMock()

# Ensure Tk and other widgets are classes that can be subclassed or instantiated
# We use a custom MagicMock subclass for Tk that ensures children are just MagicMocks,
# not instances of the subclass (like HangmanApp), to avoid recursion/init issues.
class SafeTkMock(MagicMock):
    def _get_child_mock(self, **kw):
        return MagicMock(**kw)

mock_tk.Tk = SafeTkMock
mock_tk.Frame = MagicMock
mock_tk.Label = MagicMock
mock_tk.Button = MagicMock
mock_tk.Entry = MagicMock
mock_tk.StringVar = MagicMock
mock_tk.OptionMenu = MagicMock
mock_tk.Canvas = MagicMock

# Mock messagebox specifically
mock_tk.messagebox = MagicMock()

# Define constants used in the app
mock_tk.NORMAL = 'normal'
mock_tk.DISABLED = 'disabled'
mock_tk.END = 'end'
mock_tk.BOTH = 'both'
mock_tk.X = 'x'
mock_tk.LEFT = 'left'

# Inject the mock into sys.modules to intercept imports
sys.modules['tkinter'] = mock_tk
sys.modules['_tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = mock_tk.messagebox
