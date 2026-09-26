# תרגיל הכנה – Remedio QA Automation (Pytest)

**הקובץ הנבדק:** `device_posture.py`. ה-docstring של כל פונקציה הוא ה-SPEC. יש בקוד כמה באגים מוסתרים.
**זמן מומלץ:** כ-3 שעות, כמו במבחן. מותר להיעזר ב-Claude, אבל כל החלטה צריכה להיות מוסברת: מה ולמה.

---

## סעיף 1 – קריאת דרישות ו-Test Plan (בלי קוד!) · 30 דק'
צרי את `TEST_PLAN.md`. לכל פונקציה:
- Happy path
- Boundary values (גבולות: 8 תווים, ציון 39/40/69/70/100, בדיוק 24 שעות)
- Negative (קלט לא חוקי, טיפוס שגוי)
- Edge cases (רשימה ריקה, None, אותיות גדולות/קטנות)
- **עדיפות (P0/P1/P2) וסיכון:** מה הכי מסוכן ללקוח של Remedio אם זה נשבר?

## סעיף 2 – Exploratory Testing ודו"חות באגים · 25 דק'
הריצי את הפונקציות ב-Python console או בסקריפט. על כל פער בין הקוד ל-SPEC כתבי ב-`BUGS.md`:
כותרת · צעדים לשחזור · Expected · Actual · Severity · השפעה על הלקוח.

## סעיף 3 – Pytest בסיסי · 40 דק'
`tests/test_password.py`, `tests/test_ports.py`, `tests/test_os_version.py`, `tests/test_risk.py`
- להשתמש ב-`@pytest.mark.parametrize` עם `ids=` קריאים
- להשתמש ב-`pytest.raises` במקרים שה-SPEC דורש exception
- טסט שחושף באג צריך **להיכשל**. לא "מתקנים" אותו כדי שיעבור.

## סעיף 4 – Fixtures ו-conftest · 20 דק'
- `conftest.py` עם fixture של findings לדוגמה (ריק, low בלבד, מעל 100)
- markers: `smoke` / `regression`, רשומים ב-`pytest.ini`
- להריץ: `pytest -m smoke`, `pytest -k risk -v`

## סעיף 5 – Mocking ובידוד: RemediationEngine · 30 דק'
בלי להריץ תיקון אמיתי על מכשיר. משתמשים ב-`unittest.mock.Mock` בתור executor.
- הצלחה בניסיון הראשון / השני / השלישי: כמה ניסיונות הוחזרו?
- כל הניסיונות נכשלים: האם `rollback` נקרא **בדיוק פעם אחת**? נזרק `RemediationFailed`?
- `max_attempts=0` → ValueError?
- לבדוק גם את `apply.call_count`

## סעיף 6 – זמן ו-Flaky tests: is_scan_stale · 20 דק'
- למה טסט שמשתמש ב-`datetime.now()` עלול להיות flaky?
- איך הופכים אותו לדטרמיניסטי? (רמז: הפרמטר `now`)
- גבולות: 23:59:59, בדיוק 24h, 24h+1s, **יותר מיום שלם (למשל 49 שעות)**

## סעיף 7 – CI ודיווח · 10 דק'
- `pytest --junitxml=report.xml` ו-`pytest-html`
- מה רץ על כל PR ומה רץ ב-nightly? (smoke מול regression)
- טסט נכשל ב-CI ועובר אצלך מקומית: מה הצעדים שלך?

## סעיף 8 – הגנה בעל-פה · 15 דק'
תתאמני להסביר בקול:
1. איך בנית את ה-Test Plan, ולמה בסדר העדיפויות הזה?
2. איזה באג הכי חמור, ולמה? (לחשוב מנקודת המבט של הלקוח ושל האבטחה)
3. מה **לא** בדקת, ולמה?
4. מה ההבדל בין unit, integration ו-E2E בפיצ'ר הזה?
5. איך היית מוסיף/ה את זה ל-regression suite קיים?

---
**הרצה:** `python3 -m pip install pytest` ← `python3 -m pytest -v`
