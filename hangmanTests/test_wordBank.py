# -*- coding: utf-8 -*-
# hangman/hangmanTests/test_wordBank.py

"""
Unit tests for the WordBank class.

This test suite verifies the functionality of the WordBank class, ensuring that
it correctly manages word categories, retrieves words, and provides random words
for the game.

Author: @seanl
Version: 1.2.0
Creation Date: 11/20/2025
Last Updated: 12/25/2025
"""

import unittest

from wordBank import WordBank, DEFAULT_CATEGORY


class TestWordBank(unittest.TestCase):
    """
    Basic tests for WordBank behavior.
    """

    def setUp(self) -> None:
        self.word_bank = WordBank()

    def testDefaultCategoriesExist(self) -> None:
        """
        Ensure at least the default category exists.
        """
        categories = self.word_bank.getCategories()
        self.assertIn(DEFAULT_CATEGORY, categories)
        self.assertIn("movies", categories)
        self.assertIn("science", categories)

    def testGetWordsForValidCategory(self) -> None:
        """
        Ensure we can retrieve words for a known category.
        """
        words = self.word_bank.getWordsForCategory(DEFAULT_CATEGORY)
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 0)

    def testGetRandomWordReturnsString(self) -> None:
        """
        Ensure getRandomWord returns a non-empty string.
        """
        word = self.word_bank.getRandomWord(DEFAULT_CATEGORY)
        self.assertIsInstance(word, str)
        self.assertGreater(len(word), 0)

    def testGetRandomWordRaisesErrorForEmptyCategory(self) -> None:
        """
        Ensure getRandomWord raises ValueError for an empty category.
        """
        # Create a category with an empty list explicitly
        empty_category = "empty_test_category"
        self.word_bank.categories[empty_category] = []
        
        # Verify that accessing this category raises ValueError
        # This should hit line 55: raise ValueError(...)
        with self.assertRaises(ValueError) as cm:
            self.word_bank.getRandomWord(empty_category)
        
        self.assertIn(f"No words available for category '{empty_category}'", str(cm.exception))

    def testGetWordsForNonExistentCategoryReturnsDefault(self) -> None:
        """
        Ensure requesting a non-existent category falls back to default.
        """
        words = self.word_bank.getWordsForCategory("non_existent")
        default_words = self.word_bank.getWordsForCategory(DEFAULT_CATEGORY)
        self.assertEqual(words, default_words)


if __name__ == "__main__":
    unittest.main()
