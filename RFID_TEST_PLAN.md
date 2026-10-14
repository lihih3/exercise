# Test Plan – RFID Door Access (interview practice)

Based only on the task text. Door layout from the task's diagram:
`1 -> 2 -> 3`, `1 -> 6 -> 10`, `1 -> 7 -> 11` (1 = main door).

**Assumptions to confirm with the interviewer** (marked "TBD" below):
- A1: "previous already opened" means opened by the **same tag**.
- A2: The diagram means door 1 has three next doors: 2, 6, 7.
- A3: Exactly 2.000s after the last open is allowed or not – TBD.
- A4: Whether a denied swipe also starts the 2-second wait – TBD.

## 1. What the feature does
An RFID reader on each of 100 doors lets a tag open a door only if that tag
already opened the previous door (or this door), and at most one door
every 2 seconds per employee.

## 2. Risks
| Angle | What can go wrong | Danger to user |
|---|---|---|
| It fails | A valid employee is refused (main door, next door, re-open) | Locked out, can't work |
| It reports wrong | Says "opened" but no open is recorded, or records an open that was denied | Later doors wrongly allowed or refused |
| It breaks something else | One employee's or branch's state leaks into another | Wrong people get in |
| Who is allowed | Skipping doors, unknown tag, beating the 2s limit | Security breach – worst case |

## 3–4. Test cases

### Happy
| ID | Case | Expected | Priority |
|---|---|---|---|
| H1 | New tag swipes main door 1 | Opens | P0 |
| H2 | Tag opened 1, waits >2s, swipes 2 | Opens | P0 |
| H3 | Full path 1 → 2 → 3, >2s between swipes | All open | P1 |
| H4 | Tag opened 2, waits >2s, swipes 2 again | Opens (current already opened) | P1 |
| H5 | Other branch: 1 → 6 → 10, >2s apart (A2) | All open | P1 |

### Boundary
| ID | Case | Expected | Priority |
|---|---|---|---|
| B1 | Opened 1, swipes 2 after 1.999s | Denied (too fast) | P0 |
| B2 | Opened 1, swipes 2 after exactly 2.000s | TBD (A3) | P1 |
| B3 | Opened 1, swipes 2 after 2.001s | Opens | P1 |
| B4 | Leaf door 3 (no next door), reached correctly | Opens | P1 |
| B5 | Door ID 100 (last) vs 101 and 0 (don't exist) | 100 valid; 0/101 rejected | P2 |

### Negative
| ID | Case | Expected | Priority |
|---|---|---|---|
| N1 | New tag swipes door 2 without door 1 | Denied | P0 |
| N2 | Opened 1, swipes 3 (skips 2) | Denied | P0 |
| N3 | Opened 1, 2; swipes 10 (its previous, 6, not opened) | Denied | P0 |
| N4 | A opened 1, 2. B opened only 1, swipes 3 (A1) | Denied for B | P0 |
| N5 | Unknown / empty tag swipes any door | Denied | P0 |
| N6 | Valid tag, unknown door ID | Clear rejection, no crash | P2 |

### Edge
| ID | Case | Expected | Priority |
|---|---|---|---|
| E1 | Two employees swipe the same door at the same moment | Each decided on their own (limit is per employee) | P1 |
| E2 | Opened 1, 2, 3, then goes back and swipes 2 | Opens (2 already opened) | P2 |
| E3 | Same door swiped twice within 2s | Second denied | P2 |
| E4 | Denied swipe, then valid swipe 1s later (A4) | TBD | P2 |

## 5. Not tested, and why
- **Real RFID hardware and physical locks** – needs a hardware environment; the reader is mocked.
- **Real clock waits** – slow and flaky; a fake clock is used instead.
- **Load / many swipes at once at scale** – out of scope for this task and time.
- **Resetting "already opened" (e.g. daily)** – not in the spec; asked as a question.
