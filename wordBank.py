# -*- coding: utf-8 -*-
# hangman/wordBank.py

"""
Provides word lists and categories for the Hangman game.

This module defines the WordBank class, which is responsible for managing the
word lists used in the Hangman game. It allows for words to be organized into
categories, and provides methods to retrieve categories and select random words.

Author: @seanl
Version: 1.0.0
Creation Date: 11/20/2025
Last Updated: 11/20/2025
"""

from typing import Dict, List
import random

DEFAULT_CATEGORY: str = "general"


class WordBank:
    """
    Manages categories of words for the Hangman game.
    """

    def __init__(self) -> None:
        self.categories: Dict[str, List[str]] = {}
        self._initializeDefaultCategories()

    def _initializeDefaultCategories(self) -> None:
        """
        Initialize some default word categories.
        Extend this with more categories and words as needed.
        """
        self.categories = {
            "general": ["python", "hangman", "developer", "keyboard"],
            "animals": ["elephant", "giraffe", "kangaroo", "alligator"],
            "fruits": ["banana", "strawberry", "pineapple", "watermelon"],
        }

    def getCategories(self) -> List[str]:
        """
        Return a list of available category names.
        """
        return list(self.categories.keys())

    def getWordsForCategory(self, category_name: str) -> List[str]:
        """
        Return a list of words for the given category.
        If the category does not exist, falls back to DEFAULT_CATEGORY.
        """
        if category_name not in self.categories:
            category_name = DEFAULT_CATEGORY
        return self.categories.get(category_name, [])

    def getRandomWord(self, category_name: str = DEFAULT_CATEGORY) -> str:
        """
        Return a random word from the given category.
        """
        words = self.getWordsForCategory(category_name)
        if not words:
            # Fallback: in case the category is empty/misconfigured.
            raise ValueError(f"No words available for category '{category_name}'")
        return random.choice(words)