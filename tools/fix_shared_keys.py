# -*- coding: utf-8 -*-
"""Make proofScriptUrl a shared setting so every device gets it.

Without this the Proof Upload Script URL stays in one browser's
localStorage and the rest of the team never receives it.

Idempotent: running it again does nothing.
"""
import sys

TARGET = 'index.html'
src = open(TARGET, encoding='utf-8').read()

OLD = "'emailDaily','emailNew','emailOverdue'];"
NEW = "'emailDaily','emailNew','emailOverdue','proofScriptUrl'];"

if NEW in src:
    print('SHARED_KEYS already includes proofScriptUrl - nothing to do.')
    sys.exit(0)

if src.count(OLD) != 1:
    print('ERROR: SHARED_KEYS anchor not found exactly once (%d)' % src.count(OLD))
    sys.exit(1)

src = src.replace(OLD, NEW, 1)
open(TARGET, 'w', encoding='utf-8').write(src)
print('SHARED_KEYS updated: proofScriptUrl will now sync to all devices.')
