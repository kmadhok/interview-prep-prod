# Coding Cheat Sheet — Walmart Principal Data Analyst (5/29)

**30 min, SQL + Python, live screen-share, bare editor.** Glance, don't read.

---

## STRATEGY (read first, breathe)

- **Read all problems first** (1 min). Order by speed-of-points, not by listed order.
- **Bank easy points fast** — SQL/pandas you know cold, lock the score in before the hard problem.
- **Stuck rule:** 8–10 min with no traction → move on, come back. Never die on one problem.
- **Talk out loud.** State approach in one sentence before coding. Earns partial credit + invites hints.
- **For SQL:** write expected output columns/grain on paper first, then the query.
- **For Python:** write the signature + 1-line plan as a comment, then code.
- **Edge cases to mention out loud:** empty input, ties, NULLs, duplicates, single row, off-by-one.
- **If a test fails:** read the *exact* failing input, don't re-read your code first.

---

## SQL — WINDOW FUNCTIONS (most likely)

```sql
-- Rank within group
SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
FROM emp;
-- ROW_NUMBER: 1,2,3,4   RANK: 1,2,2,4   DENSE_RANK: 1,2,2,3

-- Top-N per group (Top-3 salary per dept)
WITH r AS (
  SELECT *, DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rk
  FROM emp
)
SELECT * FROM r WHERE rk <= 3;

-- Running total
SUM(amount) OVER (PARTITION BY user_id ORDER BY dt
                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

-- Prev / next row
LAG(amt, 1) OVER (PARTITION BY user_id ORDER BY dt) AS prev_amt
LEAD(amt, 1) OVER (PARTITION BY user_id ORDER BY dt) AS next_amt

-- Day-over-day delta
amt - LAG(amt) OVER (PARTITION BY user_id ORDER BY dt) AS delta

-- N-tile / percentile bucket
NTILE(4) OVER (ORDER BY revenue DESC) AS quartile

-- Moving avg (7-day)
AVG(x) OVER (ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

## SQL — JOINS

```sql
-- Anti-join (rows in A with no match in B)
SELECT a.* FROM a LEFT JOIN b ON a.id=b.a_id WHERE b.a_id IS NULL;

-- Self-join (manager → employee)
SELECT e.name, m.name AS mgr
FROM emp e LEFT JOIN emp m ON e.mgr_id = m.id;

-- Multi-key join
ON a.user_id = b.user_id AND a.dt = b.dt
```

**Join cardinality gotcha:** if right side has duplicates, left rows *multiply*. Check with `COUNT(*)` before/after.

## SQL — AGGREGATION PATTERNS

```sql
-- Conditional aggregation (pivot via CASE)
SELECT user_id,
  SUM(CASE WHEN status='paid'    THEN amt ELSE 0 END) AS paid,
  SUM(CASE WHEN status='refund'  THEN amt ELSE 0 END) AS refunded,
  COUNT(CASE WHEN status='paid'  THEN 1 END)          AS paid_count
FROM txn GROUP BY user_id;

-- Distinct count
COUNT(DISTINCT user_id)

-- HAVING vs WHERE: WHERE filters rows, HAVING filters groups
SELECT dept, AVG(sal) FROM emp
WHERE active = 1
GROUP BY dept
HAVING AVG(sal) > 100000;

-- First/last value per group
SELECT user_id, MIN(dt) AS first_seen, MAX(dt) AS last_seen
FROM events GROUP BY user_id;
```

## SQL — NULL & MISC

```sql
COALESCE(col, 0)          -- replace NULL
NULLIF(a, b)              -- NULL when a=b (safe divide: a / NULLIF(b,0))
col IS NULL / IS NOT NULL -- never col = NULL

-- COUNT(*) counts rows; COUNT(col) skips NULLs
-- ORDER BY col NULLS LAST   (Postgres)
-- String concat: a || b (ANSI) or CONCAT(a,b) (MySQL)
```

## SQL — DATES

```sql
-- MySQL
DATEDIFF(d2, d1)                     -- days between
DATE_ADD(d, INTERVAL 7 DAY)
DATE_FORMAT(dt, '%Y-%m')             -- year-month
YEAR(dt), MONTH(dt), DAYOFWEEK(dt)

-- Postgres
d2 - d1                              -- days (integer)
DATE_TRUNC('month', dt)
EXTRACT(YEAR FROM dt)
dt + INTERVAL '7 days'
```

## SQL — TEMPLATES YOU CAN PASTE

```sql
-- "Nth highest salary"
SELECT DISTINCT salary FROM emp
ORDER BY salary DESC LIMIT 1 OFFSET 1;   -- 2nd highest

-- "Customers who bought X but not Y"
SELECT user_id FROM orders WHERE product='X'
EXCEPT
SELECT user_id FROM orders WHERE product='Y';

-- "Consecutive duplicates" (find rows where same value repeats)
SELECT id, val FROM (
  SELECT *, LAG(val) OVER (ORDER BY id) AS prev FROM t
) x WHERE val = prev;

-- "Median" (Postgres)
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) FROM t;
```

---

## PYTHON / PANDAS — DAILY DRIVERS

```python
import pandas as pd

# Group + aggregate
df.groupby('user_id')['amt'].sum()
df.groupby('user_id').agg(total=('amt','sum'), n=('amt','count'), avg=('amt','mean'))

# Multi-key groupby
df.groupby(['user_id','month']).agg(...)

# Top-N per group
df.sort_values(['dept','sal'], ascending=[True,False]).groupby('dept').head(3)

# Merge (= SQL join)
df.merge(other, on='id', how='left')   # how: left|right|inner|outer
df.merge(other, left_on='a', right_on='b')

# Pivot
df.pivot_table(index='user', columns='month', values='amt', aggfunc='sum', fill_value=0)

# Filter rows
df[df['amt'] > 100]
df[df['col'].isin(['a','b'])]
df[df['col'].str.contains('foo', na=False)]
df.query("amt > 100 and status == 'paid'")

# NULL handling
df['col'].fillna(0); df.dropna(subset=['col']); df['col'].isna()

# New column from condition
df['bucket'] = pd.cut(df['amt'], bins=[0,10,100,1000], labels=['s','m','l'])
df['flag']   = (df['amt'] > 100).astype(int)
import numpy as np
df['x'] = np.where(df['a'] > 0, df['b'], df['c'])

# Date
df['dt'] = pd.to_datetime(df['dt'])
df['month'] = df['dt'].dt.to_period('M')
df.sort_values('dt')

# Window-ish ops
df['cum'] = df.groupby('user')['amt'].cumsum()
df['rk']  = df.groupby('dept')['sal'].rank(method='dense', ascending=False)
df['prev']= df.groupby('user')['amt'].shift(1)
df['roll']= df['amt'].rolling(7).mean()
```

## PYTHON — DSA TEMPLATES (the rusty stuff)

```python
# --- Hashmap counting ---
from collections import Counter, defaultdict
counts = Counter(arr)               # {val: count}
d = defaultdict(list)
for k, v in pairs: d[k].append(v)

# --- Two-sum (hashmap) ---
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen: return [seen[target-x], i]
        seen[x] = i

# --- Two pointers (sorted array) ---
i, j = 0, len(a)-1
while i < j:
    s = a[i] + a[j]
    if s == target: return (i, j)
    elif s < target: i += 1
    else: j -= 1

# --- Sliding window (longest substring w/o repeat) ---
def longest(s):
    seen = {}; left = 0; best = 0
    for right, c in enumerate(s):
        if c in seen and seen[c] >= left:
            left = seen[c] + 1
        seen[c] = right
        best = max(best, right - left + 1)
    return best

# --- Sort with key ---
arr.sort(key=lambda x: (-x[1], x[0]))   # by 2nd desc, 1st asc

# --- Group consecutive ---
from itertools import groupby
for key, grp in groupby(arr): ...   # arr must be sorted by key

# --- Frequency top-K ---
Counter(arr).most_common(k)
```

## PYTHON — QUICK REFS

```python
# Comprehensions
[f(x) for x in xs if cond]
{k: v for k, v in pairs}
{x for x in xs}

# Strings
s.split(','); ','.join(parts); s.strip(); s.lower()
s.startswith('x'); s.endswith('x'); 'x' in s
s[::-1]                       # reverse
s.replace('a','b')

# Slices
a[start:stop:step]; a[-3:]; a[:-1]

# Dict
d.get(k, default); d.setdefault(k, [])
for k, v in d.items(): ...

# Set ops
a & b   # intersection
a | b   # union
a - b   # difference

# Read input on HackerRank stdin style
n = int(input())
arr = list(map(int, input().split()))
```

---

## GOTCHAS — RE-READ BEFORE STARTING

- **SQL:** `COUNT(*)` ≠ `COUNT(col)` (NULLs). `WHERE` before `GROUP BY`, `HAVING` after.
- **SQL:** `NULL = NULL` is NULL (false). Use `IS NULL`.
- **SQL:** integer division — cast: `1.0 * a / b` or `CAST(a AS FLOAT)/b`.
- **SQL:** `LEFT JOIN ... WHERE b.col = x` accidentally turns into INNER. Put the filter in `ON`.
- **pandas:** `df.groupby().agg()` drops grouping cols unless `as_index=False`.
- **pandas:** `merge` default is `how='inner'` — easy to lose rows.
- **pandas:** chained `df[df.x>0]['y'] = ...` silently fails. Use `.loc[mask, 'y'] = ...`.
- **Python:** mutable default args `def f(a=[])` — don't.
- **Python:** `range(n)` is `0..n-1`. Off-by-one is interview kryptonite.

---

## LAST 30 SECONDS BEFORE THEY SHARE THE SCREEN

1. Notebook + pen out. Water in reach.
2. Editor open, scratch file ready, one comment block per problem.
3. Mic check — verbal coding is the play.
4. Smile. Bank the easy ones. You've shipped harder than this at work.
