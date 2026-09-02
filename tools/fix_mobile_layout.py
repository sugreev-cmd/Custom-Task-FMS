# -*- coding: utf-8 -*-
"""Make the task detail modal fit properly on every phone.

Problems this fixes on small screens:
  * detail fields stacked one per row, so the modal was ~1.7 screens tall
  * "Take Photo" / "Choose Photo" only 34px tall - too small to tap
  * footer buttons wrapped onto two lines and got squashed
  * the floating "Synced" pill sat on top of the Mark Done button

Idempotent: running it again does nothing.
"""
import sys

TARGET = 'index.html'
src = open(TARGET, encoding='utf-8').read()

MARK = 'PHONE FIT - task detail modal'
if MARK in src:
    print('Mobile layout fix already applied - nothing to do.')
    sys.exit(0)

CSS = """
/* ============ %s ============
   Ye block jaan-boojh kar sabse aakhir me hai taaki upar wale
   mobile rules ko override kar sake. */
@media(max-width:680px){

  /* Detail fields do-do karke - modal chhota, scroll kam */
  .task-detail-grid{grid-template-columns:1fr 1fr;gap:8px}
  .tdg-item{padding:8px 10px}
  .tdg-lbl{font-size:7.5px;margin-bottom:3px}
  .tdg-val{font-size:11.5px;line-height:1.35}

  /* Camera buttons - ungli se aaram se dabein (46px) */
  .tf-cam-wrap{gap:8px}
  .tf-btn{flex:1 1 0;min-width:0;justify-content:center;min-height:46px;
          font-size:13px;padding:10px 6px}
  .tf-count{flex:1 0 100%%;order:3;margin-left:0;text-align:right}
  .tf-grid{grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:7px}

  /* Footer buttons ek hi line me, text toote nahi */
  .mf{gap:6px;padding:12px;flex-wrap:nowrap;align-items:stretch}
  .mf .bp,.mf .bs,.mf .bd2b{flex:1 1 0;min-width:0;white-space:nowrap;
                            padding:12px 6px;font-size:11px;text-align:center}
  .mf .bd2b{flex:0 0 auto;padding:12px 10px}

  /* "Synced" pill Mark Done button ke upar na aaye */
  .sync-dot{bottom:auto;top:10px;right:10px}
}

@media(max-width:380px){
  .mf .bp,.mf .bs,.mf .bd2b{font-size:10px;padding:12px 4px}
  .mf{gap:4px;padding:10px 8px}
  .tf-btn{font-size:12px;min-height:44px}
  .tf-grid{grid-template-columns:repeat(auto-fill,minmax(84px,1fr))}
  .tdg-val{font-size:11px}
}
</style>""" % MARK

if src.count('</style>') != 1:
    print('ERROR: </style> not found exactly once (%d)' % src.count('</style>')); sys.exit(1)

src = src.replace('</style>', CSS, 1)
open(TARGET, 'w', encoding='utf-8').write(src)
print('Mobile layout fix applied.')
