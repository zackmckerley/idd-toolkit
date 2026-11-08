"""Rebuild one room set without importing the others (so a drafter mid-edit on one generator cannot break another's build).
Usage: python3 rev1/rebuild_one.py bath|mbr|baths|kitchen|beds|living|mud|entry|finish|study2"""
import sys, importlib, os
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1')
os.chdir('/home/claude/flrwork')
import idd_std, idd_sheet
name = sys.argv[1]
idd_std.PROJECT['base'] = 'FOR ARCHITECTURE CO., REV 1 10.23.26'
idd_sheet.EXTRA_REVS[:] = [('1', '11.05.26', 'BASE PLAN TO FOR REV 1')]
MOD = {'bath': 'build_mbath_rev1', 'mbr': 'build_mbr_rev1', 'baths': 'build_baths_rev1', 'kitchen': 'build_kitchen_rev1',
       'beds': 'build_beds_rev1', 'living': 'build_great_rev1b', 'mud': 'build_mud', 'entry': 'build_entry'}
if name == 'study2':                      # the fireplace wall options for the review set, ID-235 and ID-236
    import build_great_s2 as m; m.build_review()
elif name == 'finish':
    os.chdir('/home/claude/flrwork/rev1'); import runpy; runpy.run_path('build_finish_rev1.py', run_name='__main__')
elif name in ('mud', 'entry'):
    import runpy; runpy.run_path(MOD[name] + '.py', run_name='__main__')
else:
    m = importlib.import_module(MOD[name])
    if name == 'living': idd_std.PROJECT['date'] = m.ISSUE
    m.build()
