# AGENTS.md — Master Operational Guide for the Hangman Project Agent
Version: 1.1
Last Updated: 11/19/2025

## 1) Purpose and Scope
This document defines how the development agent works: its mission, process, boundaries, and coordination with other project files. It does not duplicate product requirements; instead, it tells the agent how to work to implement those requirements safely and incrementally.

- Audience: contributors and automation agents working on the hangman project.
- Goal: ensure safety, traceability, and test-driven, incremental delivery.

## 2) Relationship to Other Project Docs
- Rules (authoritative constraints): Separate file named Rules. Those rules are mandatory and take precedence.
- guidelines (requirements): Single source of truth for user-facing requirements/specifications for the hangman game.
- LOG.md (verified history): Chronological record of verified outcomes only (PASS/FAIL), with commands and salient outputs.

How to use these together:
1. Read guidelines to understand what to build.
2. Follow Rules to determine how to build it (incrementally, test-first, one logical operation at a time).
3. Record verified outcomes in LOG.md after each cycle.

## 3) Agent Mission
Deliver a fully functional Hangman game that:
- Selects a word from a predefined bank.
- Displays the word to the user as a series of blanks.
- Accepts user guesses (single letters).
- Reveals letters in the word if the guess is correct.
- Tracks incorrect guesses and draws parts of the hangman figure.
- Ends the game with a win or loss message.

Reference: See guidelines for detailed requirements.

## 4) Operating Cycle (Stop-and-Wait)
The agent follows an incremental, test-driven loop:
1. Propose exactly one logical operation.
   - For simple, single-file changes, provide a minimal diff directly.
   - For complex changes requiring multiple edits, propose an Atomic Change Set (ACS) plan by outlining the goal and files to be modified. Await user approval before providing the batched diffs.
2. Stop and wait for the user to run commands and return full outputs.
3. Analyze outputs:
   - On failure: propose (a) LOG.md entry diff with verified facts, and (b) a focused fix diff.
   - On success: propose (a) LOG.md entry diff documenting success, and (b) the next incremental diff.
4. Repeat. Never bundle unrelated operations.

Commands must be explicit (e.g., `python main.py`), and outcomes must be interpreted strictly from actual outputs/exit codes.

A key part of this cycle is the **Iterative Synthesis** approach to code generation. When the user provides multiple code examples or suggestions from different sources, the agent's role is not to simply pick the best one. Instead, it performs a synthesis: it analyzes all inputs, identifies the unique strengths of each (e.g., superior test coverage, clearer documentation, better edge-case handling), and integrates these strengths into a single, cohesive proposal. This ensemble-based method ensures the final code is more robust, maintainable, and well-documented than any individual suggestion, while still adhering to all project standards.

## 5) Change Management
- One logical operation per proposal cycle. This may be a single diff or a pre-approved, multi-diff Atomic Change Set.
- Incremental modifications only; avoid sweeping refactors.
- Do not move/rename/delete files or restructure without explicit approval. Propose first with rationale.
- Automatic updates allowed without special approval: formatting, non-critical comments/docs, and standard bug fixes.
- Controlled files (require explicit approval before modifying): AGENTS.md and guidelines.

## 6) Coding & Documentation Standards (Summary)
Follow these technical standards when editing or adding Python modules:
- Required file header (see Example Header below).
- Imports grouped/alphabetized: standard library, third-party, then application-specific.
- Public modules/classes/functions require docstrings with purpose, Args, Returns.
- Naming:
  - Classes: PascalCase
  - Functions & Methods (Internal): camelCase
  - Variables, Instances, Parameters: snake_case
  - Constants (Module-level): UPPER_SNAKE_CASE
  - Overridden Methods (e.g., PyQt, Python): snake_case
  - File names: camelCase for source files; tests use test_sourceFileName.py
  - Test function names: camelCase
- Formatting: lines under ~100 chars where feasible; clarity over novelty.

## 7) Current Focus & Milestones
- Immediate priority: Implement the core game logic for Hangman.
- Next priorities:
  - Word selection from `wordBank.py`.
  - User input handling for letter guesses.
  - Game state management (correct/incorrect guesses, remaining lives).
  - UI implementation using Tkinter.
  - Win/loss condition checking and display.
- Final integration: Ensure all modules (`main.py`, `gameLogic.py`, `uiTkinter.py`, `wordBank.py`) work together seamlessly.

## 8) Commands & Validation (Typical)
- Local CLI:
    `python main.py`

Always request that users paste full command outputs for verification.

## 9) Example Header (for Python Files)
Use this exact structure for all new or modified Python files. The "Last Updated" date must always be the current date of the modification (e.g., today's date).
# -*- coding: utf-8 -*-
# hangman/path/to/your/file.py
"""
One-sentence module purpose.

Detailed explanation of the module’s role within the hangman project and key
dependencies/interactions.

Author: @seanl
Version: 0001 # R-21
Creation Date: 08/27/2025
Last Updated: 11/19/2025
"""

from __future__ import annotations
# 1) Standard library imports (alphabetized)

# 2) Third-party imports (alphabetized)

# 3) Application-specific imports (alphabetized)
# from hangman.moduleX import Y

def exampleInternalFunction(arg1: int) -> int:
    """
    Demonstrates the required docstring and naming format.

    Args:
        arg1: Example integer argument.

    Returns:
        The incremented integer value.
    """
    return arg1 + 1

## 10) Allocation of Content Across Files
- AGENTS.md (this file): How we work. Mission, rules interface, cycle, standards, focus, commands, examples.
- Rules (separate file): Binding constraints and procedures. Agent must comply fully.
- guidelines: Product requirements, implementation strategy, output formats, milestones, acceptance criteria.
- LOG.md: Only verified outcomes from executed commands (no speculation), with timestamps and next steps.

## 11) Maintenance Checklist
- Before proposing a change: Re-read guidelines and Rules.
- During proposal: Ensure the scope is one logical operation (either a single diff or an ACS); include exact commands for validation.
- After validation: Update LOG.md with verified facts only (PASS/FAIL, command, salient output, interpretation).
- When editing code: Ensure headers, imports ordering, docstrings, naming, and line length compliance.
- When modifying controlled files (AGENTS.md, guidelines): Seek explicit approval first.

## 12) Compliance Reminder
- This guide is enforceable. If a violation occurs (e.g., bundling changes, missing tests), the next cycle must include an explicit correction plan and a LOG.md entry documenting the verified issue and the fix.
