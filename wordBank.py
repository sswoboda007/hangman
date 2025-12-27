# -*- coding: utf-8 -*-
# hangman/wordBank.py

"""
Provides word lists and categories for the Hangman game.

This module defines the WordBank class, which is responsible for managing the
word lists used in the Hangman game. It allows for words to be organized into
categories, and provides methods to retrieve categories and select random words.

Author: @seanl
Version: 1.1.0
Creation Date: 11/20/2025
Last Updated: 12/25/2025
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
            "general": ["python", "hangman", "developer", "keyboard", "algorithm", "variable", "database", "interface", "framework", "encryption"],
            "animals": ["elephant", "giraffe", "kangaroo", "alligator", "platypus", "rhinoceros", "penguin", "cheetah", "dolphin", "octopus"],
            "fruits": ["banana", "strawberry", "pineapple", "watermelon", "blueberry", "pomegranate", "mango", "kiwi", "coconut", "papaya"],
            "movies": ["inception", "gladiator", "titanic", "avatar", "matrix", "godfather", "interstellar", "joker", "parasite", "dune"],
            "countries": ["australia", "brazil", "canada", "denmark", "egypt", "france", "japan", "mexico", "norway", "portugal"],
            "science": ["physics", "chemistry", "biology", "astronomy", "quantum", "gravity", "evolution", "molecule", "ecosystem", "hypothesis"],
            "winter 2025": ["blizzard", "snowflake", "hibernate", "avalanche", "frostbite", "snowstorm", "icicle", "reindeer", "polar", "solstice"],
            "minecraft": ["creeper", "diamond", "crafting", "redstone", "zombie", "steve", "enderman", "nether", "obsidian", "enchantment"],
            "among us": ["impostor", "suspect", "vent", "emergency", "crewmate", "sabotage", "medbay", "reactor", "oxygen", "electrical"],
            "fortnite": ["battle", "victory", "chug", "storm", "island", "building", "zero", "marvel", "legendary", "supply"],
            "coding": ["boolean", "function", "variable", "debug", "syntax", "compile", "recursion", "iteration", "polymorphism", "abstraction"],
            "space": ["galaxy", "nebula", "astronaut", "telescope", "planet", "asteroid", "cosmos", "satellite", "meteor", "universe"],
            "superheroes": ["thor", "wonder", "batman", "superman", "hulk", "widow", "panther", "vision", "quicksilver", "antman"],
            "fantasy": ["dragon", "wizard", "kingdom", "sorcery", "potion", "unicorn", "dungeon", "phoenix", "troll", "enchanted"],
            "ocean": ["submarine", "coral", "shipwreck", "treasure", "hurricane", "lighthouse", "buoy", "tsunami", "whale", "dolphin"],
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
