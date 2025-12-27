# Project Log: Hangman

# Arrangement is: oldest log on top; newest log, on the bottom.
Example 
## [LOG - xxx] yyyy-mm-dd: title

---
## [LOG - 000] 2025-11-22: Fix Failing UI Test for Win/Loss Handling

- **Action:** Ran the `hangmanTests/test_uiTkinter.py` test suite.
- **Result:** `FAIL`. 7 of 8 tests passed.
- **Salient Output:**
  ```
  FAILED hangmanTests/test_uiTkinter.py::TestHangmanAppHeadless::test_win_and_loss_handling
  AssertionError: expected call not found.
  Expected: showinfo('Hangman', 'You won! The word was: test')
  Actual: not called.
  ```
- **Analysis:** The `test_win_and_loss_handling` test failed because it was calling the real `game.processGuess()` method. This method has internal logic that likely prevented the mocked `isWon()` from being evaluated as expected, because the game state wasn't actually a "win". The test was not properly isolated.
- **Fix (ACS):**
  - In `hangmanTests/test_uiTkinter.py`, the `test_win_and_loss_handling` method was modified to also mock `game.processGuess()`. This prevents the real game logic from running and allows the test to focus solely on verifying that the UI's win/loss handling logic is triggered correctly based on the mocked return values of `isWon()` and `isLost()`.
- **Next Step:** Apply the patch and re-run the test suite to confirm the fix.

---
## [LOG - 001] 2025-11-22: Headless Tk Initialization Regression

- **Action:** Ran `pytest hangmanTests/test_uiTkinter.py` after refactoring the headless test setup.
- **Result:** `FAIL`. All 8 tests errored.
- **Salient Output:**
  ```
  RecursionError: maximum recursion depth exceeded
  ```
- **Analysis:** Patching `tkinter.Tk.__init__` to return `None` left `self.tk` unset, so subsequent widget configuration recursed when the app attempted to set the window title. Need to provide a fake initializer that seeds the expected Tk attributes.
- **Next Step:** Mock `Tk.__init__` with a helper that seeds `self.tk`, `self._w`, and related attributes before instantiating `HangmanApp` in tests, then rerun the suite.

---
## [LOG - 002] 2025-11-22: Tk Fake Init Signature Error

- **Action:** Re-ran `pytest hangmanTests/test_uiTkinter.py` after stubbing Tk attributes in tests.
- **Result:** `FAIL`. All 8 tests errored.
- **Salient Output:**
  ```
  TypeError: TestHangmanAppHeadless.setUp.<locals>._fake_tk_init() missing 1 required positional argument: 'instance'
  ```
- **Analysis:** Using `patch(..., side_effect=_fake_tk_init)` meant the fake initializer was invoked without the bound instance, causing the TypeError. Must replace the method with `new=_fake_tk_init` (signature `self, *args, **kwargs`) so the instance is passed correctly.
- **Next Step:** Swap the patch to use `new=_fake_tk_init`, rerun the tests.

---
## [LOG - 003] 2025-11-22: Headless GUI Tests Passing

- **Action:** Ran `pytest hangmanTests/test_uiTkinter.py` after updating the Tk initializer patching strategy.
- **Result:** `PASS`. All 8 tests succeeded.
- **Salient Output:**
  ```
  hangmanTests/test_uiTkinter.py ........  [100%]
  8 passed in 0.14s
  ```
- **Analysis:** Replacing the Tk `__init__` patch with a helper that seeds the required attributes resolved the recursion and signature errors. Headless GUI tests now instantiate `HangmanApp` safely.
- **Next Step:** Clean up outdated comments in the test module to reflect the new setup approach.

--- 
## [LOG - 004] 2025-11-22: CLI Win/Loss Message Test Passing

- **Action:** Ran `pytest hangmanTests\test_ioCli.py` after fixing the print statement formatting.
- **Result:** `PASS`. All 2 tests succeeded.
- **Salient Output:**
  ```
  hangmanTests\test_ioCli.py ..                                                                                    [100%]
  ================================================== 2 passed in 0.03s ==================================================
  ```
- **Analysis:** Using an f-string to format the win/loss messages into a single string argument for `print()` resolved the `AssertionError`. The test mock now correctly captures the full message, including the secret word, allowing the assertion to pass.
- **Next Step:** Standardize test suites by migrating `test_ioCli.py` from `unittest` to `pytest`.

---
## [LOG - 005] 2025-11-22: Pytest HangmanApp GUI Coverage Expansion

- **Action:** Replaced unittest-based suite with pytest fixtures using headless Tk mocks and reran `pytest hangmanTests/test_uiTkinter.py`.
- **Result:** `PASS`. 13 tests succeeded.
- **Salient Output:**
  ```
  hangmanTests/test_uiTkinter.py ...F.........
  AssertionError: Expected 'config' to be called once. Called 2 times.
  ```
- **Analysis:** Initial run failed because `_updateWordLabel` gets invoked during `__init__`, leaving an earlier `config` call. Adjusted assertions to check the latest call only.
- **Fix:** Updated `testUpdateLabelsRefreshesWordAndInfo` to inspect `call_args_list` tail entries and import `call` helper.
- **Next Step:** Monitor coverage to ensure all HangmanApp branches remain exercised.

---
## [LOG - 006] 2025-12-24: Fix Headless Tkinter Tests

- **Action:** Created `hangmanTests/conftest.py` to mock `tkinter` in `sys.modules` and updated `uiTkinter.py` to accept `**kwargs`.
- **Result:** `FAIL`. 31 passed, 1 failed.
- **Salient Output:**
  ```
  FAILED hangmanTests/test_uiTkinter.py::testOnCategoryChangedUpdatesStateAndRestarts
  AssertionError: assert <MagicMock name='StringVar.get()' id='...'> == 'animals'
  ```
- **Analysis:** The test `testOnCategoryChangedUpdatesStateAndRestarts` fails because `ns.app.current_category` is now a `MagicMock` (specifically `StringVar.get()`) instead of the string "animals". This is likely because `HangmanApp` inherits from `MagicMock` (via `SafeTkMock`), and attribute access on `MagicMock` returns another `MagicMock` unless explicitly set. The `current_category` attribute was probably not set to a concrete string value in the test setup or during the method call, so it defaulted to a mock.
- **Fix:** Investigate why `current_category` is becoming a mock. It seems `HangmanApp` attributes are being intercepted by `MagicMock` behavior. We need to ensure `current_category` is treated as a real attribute or explicitly set it in the test.
- **Next Step:** Fix the failing test in `test_uiTkinter.py`.

---
## [LOG - 007] 2025-12-24: Resolve Mocking Issues in Headless Tests

- **Action:** Updated `hangmanTests/test_uiTkinter.py` to set `ns.categoryVar.get.return_value = "animals"`.
- **Result:** `PASS`. All 32 tests passed.
- **Salient Output:**
  ```
  hangmanTests\test_uiTkinter.py .............                                          [ 87%]
  hangmanTests\test_wordBank.py ....                                                    [100%]
  ==================================== 32 passed in 0.20s ====================================
  ```
- **Analysis:** The `AssertionError` was resolved by explicitly configuring the mock `StringVar.get()` to return the expected string "animals". This confirms that the application logic relies on `category_var.get()` and that the test environment now correctly simulates this behavior. The `TypeError` and `RecursionError` encountered earlier were also resolved by using `SafeTkMock` in `conftest.py` and updating `HangmanApp` to accept `**kwargs`.
- **Next Step:** Proceed with any further migration or feature tasks, now that the test suite is stable and passing in the headless environment.

---
## [LOG - 008] 2025-12-24: Create pyproject.toml

- **Action:** Created `pyproject.toml` based on `requirements.txt` and existing `pytest.ini` settings.
- **Result:** `PASS`. All 32 tests passed.
- **Salient Output:**
  ```
  configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
  ...
  ==================================== 32 passed in 0.20s ====================================
  ```
- **Analysis:** `pyproject.toml` was successfully created with build system requirements, project metadata, and test dependencies. The test run confirmed that the new file does not interfere with the existing test setup (though `pytest.ini` currently takes precedence for configuration).
- **Next Step:** Consider removing `pytest.ini` in a future step to consolidate configuration into `pyproject.toml`.

---
## [LOG - 009] 2025-12-25: Implement Visual Hangman and Virtual Keyboard

- **Action:** Updated `uiTkinter.py` to include a `tk.Canvas` for drawing the hangman and a virtual keyboard for input. Updated `hangmanTests/test_uiTkinter.py` and `hangmanTests/conftest.py` to support these changes.
- **Result:** `PASS`. All 37 tests passed.
- **Salient Output:**
  ```
  hangmanTests\test_uiTkinter.py ............                                           [ 86%]
  ==================================== 37 passed in 0.37s ====================================
  ```
- **Analysis:** The new UI features (Canvas and Virtual Keyboard) were successfully implemented and tested. The tests verify that the canvas is updated with the correct body parts and that the virtual keyboard buttons are disabled after use. The physical keyboard binding also works as expected.
- **Next Step:** Remove `pytest.ini` as it is now redundant with `pyproject.toml`.

---
## [LOG - 010] 2025-12-25: Implement Hint System and Expand Word Bank

- **Action:** Updated `gameLogic.py` to add `useHint()` method. Updated `wordBank.py` with new categories and words. Updated `uiTkinter.py` to add a Hint button. Updated tests to cover new features.
- **Result:** `PASS`. All 44 tests passed.
- **Salient Output:**
  ```
  hangmanTests\test_gameLogic.py ................                                       [ 36%]
  hangmanTests\test_ioCli.py ....                                                       [ 45%]
  hangmanTests\test_main.py ...                                                         [ 52%]
  hangmanTests\test_uiTkinter.py ................                                       [ 88%]
  hangmanTests\test_wordBank.py .....                                                   [100%]
  ==================================== 44 passed in 0.61s ====================================
  ```
- **Analysis:** The Hint System and Expanded Word Bank were successfully implemented and verified. The tests confirm that hints cost lives, reveal letters correctly, and are disabled when appropriate. The new categories are also available and functional.
- **Next Step:** Project is feature complete for this milestone.

---
## [LOG - 011] 2025-12-25: Futuristic Hangman Upgrade (Neo-Hangman)

- **Action:** Applied a major "Futuristic" overhaul to `uiTkinter.py` (neon colors, cyberpunk theme, new labels) and updated `gameLogic.py` to always auto-reveal RSTLNE letters. Updated tests to match the new logic and UI structure.
- **Result:** `PASS`. All 46 tests passed.
- **Salient Output:**
  ```
  hangmanTests\test_gameLogic.py ..................                                     [ 39%]
  hangmanTests\test_uiTkinter.py ................                                       [ 89%]
  ==================================== 46 passed in 0.58s ====================================
  ```
- **Analysis:** The "Neo-Hangman" upgrade was successfully integrated.
  - **Logic:** `HangmanGame` now correctly initializes with all RSTLNE letters in `used_letters`, preventing accidental guesses and penalties. Tests confirm this behavior (`testAutoRevealNone` now expects 6 used letters).
  - **UI:** The Tkinter interface now features a dark theme, neon accents, and a "Neural Bonus" label. The test fixture `hangmanApp` was updated to mock the new `bonus_label`, resolving `StopIteration` errors.
  - **Tests:** All tests, including those for the new UI elements and logic changes, are passing.
- **Next Step:** Launch the game via `python main.py` to enjoy the future!

---
## [LOG - 012] 2025-12-25: Improve Test Coverage for uiTkinter

- **Action:** Added new tests to `hangmanTests/test_uiTkinter.py` to cover previously untested code paths identified by a coverage report.
- **Result:** `PASS`. All 49 tests passed.
- **Salient Output:**
  ```
  ==================================== 49 passed in 0.65s ====================================
  ```
- **Analysis:** The new tests successfully cover the `_onResetButtonClicked` function and various defensive `if self.game is None:` checks, increasing the overall test coverage and robustness of the `uiTkinter` module. A failure in `testDefensiveChecksForNoneGame` was fixed by resetting mock call counts to ignore setup-phase calls.
- **Next Step:** The project is now more thoroughly tested. Ready for the next task.

---
## [LOG - 013] 2025-12-25: Fix Keyboard Layout and Test Suite

- **Action:** Modified the keyboard layout in `uiTkinter.py` from a 2x13 grid to a 3-row QWERTY layout to fix a visual overflow issue. Updated the `hangmanApp` test fixture in `test_uiTkinter.py` to accommodate the new layout.
- **Result:** `PASS`. All 49 tests passed.
- **Salient Output:**
  ```
  ==================================== 49 passed in 0.76s ====================================
  ```
- **Analysis:** The UI overflow was resolved by changing the keyboard to a 3-row layout. This change broke the test suite because the `hangmanApp` fixture's mock for `tk.Frame` had a hardcoded number of side effects. The fixture was updated to use a `side_effect` function, making it robust to changes in the number of frames. All tests now pass.
- **Next Step:** The keyboard is now fully visible and the test suite is stable. Ready for the next task.

---
## [LOG - 014] 2025-12-25: Update UI Test Expected Button Colors for 2026 Theme

- **Action:** Ran `pytest hangmanTests`.
- **Result:** `FAIL`. 48 passed, 1 failed.
- **Salient Output:**
  ```
  FAILED hangmanTests/test_uiTkinter.py::testUpdateButtonsDisablesUsedLetters
  Expected: Button.config(state='disabled', bg='#2a2a3e', fg='#555555')
    Actual: Button.config(state='disabled', bg='#333366', fg='#6666ff')
  ```

---
## [LOG - 015] 2025-12-25: Restore Reliable Main-Window Scrolling for Small Window Sizes

- **Action:** Updated `uiTkinter.py` to restore reliable vertical scrolling when the app window is made smaller.
- **Result:** **User-reported** `PASS` (scrolling works when the window is small).
- **Salient Implementation Details:**
  - Replaced the prior non-scrolling layout with a standard Tk pattern:
    - One main `tk.Canvas` + vertical `tk.Scrollbar`
    - A `scroll_root` frame embedded via `Canvas.create_window(...)`
  - Added `<Configure>` handlers:
    - Update `scrollregion` from `canvas.bbox("all")` when content size changes.
    - Keep embedded window width synced to the canvas width so content wraps/resizes correctly.
  - Bound mousewheel scrolling to the canvas.
- **Analysis:** The previous “auto-size only” approach prevented access to lower UI controls when the window was reduced in height. Using a single scroll container for the whole UI makes the layout robust at any window size.