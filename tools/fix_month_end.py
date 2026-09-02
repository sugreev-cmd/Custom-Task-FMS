# -*- coding: utf-8 -*-
"""Fix the month-end date bug that stops 30-day months from loading.

The app built the range end as  <month> + '-31'.  For September, April,
June and November that produces an impossible date (e.g. 2026-09-31),
Postgres rejects the whole query, and NO tasks load for that month.

Also raises loadMonth's row limit so a busy month is never truncated.

Idempotent: running it again does nothing.
"""
import sys

TARGET = 'index.html'
src = open(TARGET, encoding='utf-8').read()

if 'function monthEnd(' in src:
    print('Month-end fix already applied - nothing to do.')
    sys.exit(0)

changed = 0

# 1. helper - last real day of the month
HELPER_ANCHOR = "var allTasks = [];      // global cache"
HELPER = """var allTasks = [];      // global cache

/* Last REAL day of a month, e.g. monthEnd('2026-09') -> '2026-09-30'.
   Building the end date as <ym>+'-31' made Postgres reject the whole
   query for 30-day months, so nothing loaded at all. */
function monthEnd(ym){
  var p = String(ym).split('-');
  var y = parseInt(p[0],10), m = parseInt(p[1],10);
  if(!y || !m) return ym + '-28';
  var d = new Date(y, m, 0).getDate();
  return ym + '-' + String(d).padStart(2,'0');
}"""
if src.count(HELPER_ANCHOR) != 1:
    print('ERROR: helper anchor not found exactly once (%d)' % src.count(HELPER_ANCHOR)); sys.exit(1)
src = src.replace(HELPER_ANCHOR, HELPER, 1); changed += 1

# 2. loadMonth
A_OLD = "  var to   = ym + '-31';"
A_NEW = "  var to   = monthEnd(ym);"
if src.count(A_OLD) != 1:
    print('ERROR: loadMonth anchor not found exactly once (%d)' % src.count(A_OLD)); sys.exit(1)
src = src.replace(A_OLD, A_NEW, 1); changed += 1

# 3. loadData
B_OLD = "  var to   = curYM  + '-31';"
B_NEW = "  var to   = monthEnd(curYM);"
if src.count(B_OLD) != 1:
    print('ERROR: loadData anchor not found exactly once (%d)' % src.count(B_OLD)); sys.exit(1)
src = src.replace(B_OLD, B_NEW, 1); changed += 1

# 4. a busy month must not be silently truncated
C_OLD = "&due_date=lte.'+to+'&limit=2000'"
C_NEW = "&due_date=lte.'+to+'&limit=5000'"
if src.count(C_OLD) == 1:
    src = src.replace(C_OLD, C_NEW, 1); changed += 1

open(TARGET, 'w', encoding='utf-8').write(src)
print('Month-end fix applied (%d edits). 30-day months will now load.' % changed)
