# RFID Door Access – implementation and automated tests

Scope: "design and implement this system (OOP)" and
"Which Automation tests we can add here?"

## How to run
```
cd rfid
python3 -m pip install pytest
python3 -m pytest -v                 # all 16 tests
python3 -m pytest -m smoke -v        # 9 P0 tests only
python3 -m pytest -v -k N2           # one test by its id
```

## Design
- `Door`: id, `previous` door (none for the main door), `next_doors` (empty for dead ends).
- `AccessSystem.swipe(tag_id, door_id)` returns True (opens) or False (denied).
- The clock is passed in, so tests use a fake clock: no `sleep`, no flaky timing.

Clarified requirements:
- A swipe **exactly 2.000s** after the last open is allowed.
- Only a **real open** starts the 2-second wait; a denied swipe does not.

Assumptions (open questions, spec is silent):
- "Previous door opened" means opened by the **same tag**.
- Unknown door id raises `ValueError`; an empty tag is denied.

## What was tested (full plan: `../RFID_TEST_PLAN.md`)
- **P0 / smoke (9):** main door opens, next door opens, 1.999s denied,
  skipping doors / wrong branch denied, another employee's history not used,
  empty tag denied.
- **P1-P2 / regression (7):** exactly 2.0s and 2.001s allowed, re-opening a
  door already opened, two employees at the same moment, a denied swipe
  does not start the 2-second wait (E4), unknown door raises a clear error (N6).

## Bugs found
None. The implementation was written against the spec in this task, and every
test passes. Each key test was checked by breaking the code on purpose and
confirming it fails.

## Not tested, and why
- Real RFID hardware and locks: needs a hardware environment; reader is simulated.
- Real-time waits: replaced by a fake clock (deterministic and fast).
- Load / many swipes at scale: out of scope for this task and time.
- Resetting "already opened" (e.g. daily): not in the spec; open question.
- Lower-priority plan cases not automated yet: B5 (door ids 0/101),
  E3 (same door twice within 2s).

## OS
Pure Python with no file, path or OS calls, so behavior is the same on
Windows, Linux and macOS. No platform-specific tests needed.

## CI
- Every PR: `pytest -m smoke --junitxml=report.xml` (fast P0 gate).
- Nightly: `pytest -m regression --junitxml=report.xml` (full suite).
- The JUnit XML report is read by most CI tools; Allure or Report Portal could
  be plugged in for richer reports and history.

## With more time
- Automate the remaining plan cases (B5, E3).
- Confirm the open questions with the product owner and update tests.
