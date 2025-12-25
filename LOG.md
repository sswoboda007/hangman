# Project Log: Hangman

# Arrangement is: oldest log on top; newest log, on the bottom.

---
## 2025-11-22-001: Fix Failing UI Test for Win/Loss Handling

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
## 2025-11-22-002: Headless Tk Initialization Regression

- **Action:** Ran `pytest hangmanTests/test_uiTkinter.py` after refactoring the headless test setup.
- **Result:** `FAIL`. All 8 tests errored.
- **Salient Output:**
  ```
  RecursionError: maximum recursion depth exceeded
  ```
- **Analysis:** Patching `tkinter.Tk.__init__` to return `None` left `self.tk` unset, so subsequent widget configuration recursed when the app attempted to set the window title. Need to provide a fake initializer that seeds the expected Tk attributes.
- **Next Step:** Mock `Tk.__init__` with a helper that seeds `self.tk`, `self._w`, and related attributes before instantiating `HangmanApp` in tests, then rerun the suite.

---
## 2025-11-22-003: Tk Fake Init Signature Error

- **Action:** Re-ran `pytest hangmanTests/test_uiTkinter.py` after stubbing Tk attributes in tests.
- **Result:** `FAIL`. All 8 tests errored.
- **Salient Output:**
  ```
  TypeError: TestHangmanAppHeadless.setUp.<locals>._fake_tk_init() missing 1 required positional argument: 'instance'
  ```
- **Analysis:** Using `patch(..., side_effect=_fake_tk_init)` meant the fake initializer was invoked without the bound instance, causing the TypeError. Must replace the method with `new=_fake_tk_init` (signature `self, *args, **kwargs`) so the instance is passed correctly.
- **Next Step:** Swap the patch to use `new=_fake_tk_init`, rerun the tests.

---
## 2025-11-22-004: Headless GUI Tests Passing

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
## 2025-11-22-006: CLI Win/Loss Message Test Passing

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
## 2025-11-22-005: Pytest HangmanApp GUI Coverage Expansion

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
## 2025-12-24-001: Fix Headless Tkinter Tests

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
## 2025-12-24-002: Resolve Mocking Issues in Headless Tests

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
## 2025-12-24-003: Create pyproject.toml

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
