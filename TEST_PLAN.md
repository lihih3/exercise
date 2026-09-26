# Test Plan – Device Posture & Auto-Remediation

**Module under test:** `device_posture.py`
**Source of truth:** the docstring of each function (the SPEC). Test cases are designed from the spec, not from the implementation.

## Approach

- **Techniques:** equivalence partitioning, boundary value analysis, "one rule missing" cases for AND-combined rules, and negative/type testing.
- **Priority:**
  - **P0:** Failure lets a non-compliant or insecure device be reported as compliant (false green), or breaks remediation. Direct security impact on the customer.
  - **P1:** Failure wrongly flags a healthy device (false red) or gives wrong input validation. Safe but costly: noise, support tickets, loss of trust.
  - **P2:** Cosmetic or unlikely inputs, or behavior the spec leaves open.
- **Open questions:** where the spec is silent, the expected result is marked ❓ and raised with the product owner instead of being guessed.

---

## 1. `is_password_valid(password)`

**Priority: P0**

**Risk:** This is a security gate. If it **accepts a weak password**, customer devices run with easy-to-crack passwords while Remedio reports them as compliant. The customer trusts a false green, so this is the worst outcome. If it **rejects a strong password**, users are blocked, which is annoying but safe (P1).

### 1.1 Happy path
| ID | Input | Expected | Why |
|----|-------|----------|-----|
| PW-01 | `"Passw0rd!"` | `True` | Typical password that meets all 4 rules |

### 1.2 Boundary: length is "at least 8"
| ID | Input | Expected | Why |
|----|-------|----------|-----|
| PW-02 | `"Abcde1!"` (7 chars) | `False` | One under the limit |
| PW-03 | `"Abcdef1!"` (8 chars) | `True` | Exactly on the limit; catches `<` vs `<=` mistakes |
| PW-04 | `"Abcdefg1!"` (9 chars) | `True` | One over the limit |

### 1.3 Each rule on its own: "almost valid" passwords
The rules are joined by AND. For each rule, take a valid password and remove only that one thing. If the result is still `True`, that rule isn't enforced.

| ID | Input | Expected | Missing |
|----|-------|----------|---------|
| PW-05 | `"passw0rd!"` | `False` | Uppercase |
| PW-06 | `"Password!"` | `False` | Digit |
| PW-07 | `"Passw0rd"` | `False` | Special character |
| PW-08 | `"password!"` | `False` | Uppercase and digit (only the special-character rule is met); one rule alone must never be enough |
| PW-25 | `"Password"` | `False` | Digit and special (upper only) |
| PW-26 | `"passw0rd"` | `False` | Upper and special (digit only) |
| PW-27 | `"password"` | `False` | All three |

Together, PW-01 and PW-05 to PW-08 plus PW-25 to PW-27 form a **decision table** covering all 2³ = 8 combinations of upper / digit / special.

### 1.3.1 Every allowed character, in any position
| ID | Input | Expected | Why |
|----|-------|----------|-----|
| PW-30 | `"Passw0rd" + c` for each `c` in `!@#$%^&*` | `True` | Each allowed special character is accepted (catches a typo in the allowed list) |
| PW-31 | `"!Passw0rd"` | `True` | Special character first |
| PW-32 | `"P@ssw0rd"` | `True` | Special character in the middle |
| PW-33 | `"1Password!"` | `True` | Digit first |
| PW-34 | `"PASSW0RD!"` | `True` | No lowercase: the spec does not require it, so the code must not add that rule |

### 1.4 Special characters not on the allowed list (`!@#$%^&*`)
| ID | Input | Expected | Why |
|----|-------|----------|-----|
| PW-09 | `"Passw0rd?"` | `False` | `?` is not an allowed special character |
| PW-10 | `"Passw0rd_"` | `False` | Same check with a different character |
| PW-11 | `"Passw0rd "` (trailing space) | `False` | A space doesn't count as a special character |
| PW-28 | `"Passw0rd\t"` (tab) | `False` | Other whitespace doesn't count either |
| PW-29 | `"Passw0rd\n"` (newline) | `False` | Same as PW-28 |

### 1.5 Negative: wrong type → `TypeError`
Wrong types fall into two equivalence classes:
- **Group A (no length):** `len()` fails on its own, so `TypeError` is raised "by accident".
- **Group B (has a length and yields string "characters"):** can get past the length and character checks and be **wrongly accepted**. This is the higher-risk group.

| ID | Input | Expected | Group |
|----|-------|----------|-------|
| PW-12 | `None` | `TypeError` | A |
| PW-13 | `12345678` (int) | `TypeError` | A |
| PW-14 | `object()` | `TypeError` | A |
| PW-15 | `b"Passw0rd!"` (bytes) | `TypeError` | B |
| PW-16 | `list("Passw0rd!")` | `TypeError` | B |
| PW-17 | `set("Passw0rd!")` | `TypeError` | B |
| PW-18 | `dict.fromkeys("Passw0rd!")` | `TypeError` | B (iterating a dict yields its keys) |

### 1.6 Edge cases
| ID | Input | Expected | Why |
|----|-------|----------|-----|
| PW-19 | `""` | `False` | Empty string |
| PW-20 | `"        "` (8 spaces) | `False` | Long enough, but meets no other rule |
| PW-21 | `"Pass w0rd!"` | `True` | Spaces are allowed inside a password (they just don't count as special; see PW-11) |
| PW-22 | `"A1!" + "a" * 1000` | `True` | Very long input |
| PW-23 | `"Äbcdefg1!"` | ❓ | Non-ASCII uppercase; spec doesn't say whether it counts. **Open question.** |
| PW-24 | `"Abcdefg٣!"` | ❓ | Non-ASCII digit (Arabic-Indic `٣`); Python's `isdigit()` counts it. **Open question.** |
| PW-35 | `"Pa$s1😀😀"` | ❓ | Emoji: Python counts code points, a user counts visible characters. How is "8 characters" measured? **Open question.** |

### 1.7 Out of scope
- Password strength beyond the policy, such as dictionary words (`"Password1!"` passes the policy).
- How the password is stored or transmitted.
- UI behavior such as trimming leading or trailing spaces (an integration risk, noted for E2E testing).
