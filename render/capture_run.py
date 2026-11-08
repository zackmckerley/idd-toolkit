"""Run one room generator with capture on and write its views.
Usage: python3 render/capture_run.py bath|mbr|baths|kitchen|beds|living|mud|entry  out.json
The PDF the generator writes is unchanged; the JSON holds every view placed in it."""
import sys, os
sys.path.insert(0, '/home/claude/flrwork'); sys.path.insert(0, '/home/claude/flrwork/rev1'); sys.path.insert(0, '/home/claude/flrwork/render')
os.chdir('/home/claude/flrwork')
import idd_capture
idd_capture.enable()
name, out = sys.argv[1], sys.argv[2]
sys.argv = ['rebuild_one.py', name]
import runpy
runpy.run_path('/home/claude/flrwork/rev1/rebuild_one.py', run_name='__main__')
n = idd_capture.dump(out)
print('views captured:', n)
