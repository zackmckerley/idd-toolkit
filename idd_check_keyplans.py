"""Key plan scope check (owner rule 11.07.26): a room section's key plan shows only the area that section designs, plus the
doors and openings into the rooms around it. Every base placed as a key plan must be clipped by keyclip.apply to a
designed-area polygon (keyclip.room_poly for whole rooms, keyclip.area_poly + for_rect for part of an open plan).
    python3 idd_check_keyplans.py            # scans the current generators; exit 1 on a failure
Static check: each generator that places the base (show_pdf_page) must call KC.apply at least once per key plan it places."""
import re, sys, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'rev1')
import importlib.util
_spec = importlib.util.spec_from_file_location('rb', 'rev1/rebuild_one.py'); _src = open('rev1/rebuild_one.py').read()
GENS = [m + '.py' for m in re.findall(r"'\w+': '(build_\w+)'", _src)]      # the room generators in use (rev1/rebuild_one.py MOD)
fail = 0
for f in sorted(GENS):
    s = open(f).read()
    if 'show_pdf_page(' not in s: continue
    helper = re.search(r'def (\w+)\([^)]*\):\n(?:[^\n]*\n){0,6}?[^\n]*show_pdf_page\(', s)
    places = len(re.findall(r'show_pdf_page\(', s))
    if helper: places = places - 1 + len(re.findall(r'(?<!def )\b%s\(sh' % helper.group(1), s))
    clips = len(re.findall(r'KC\.apply\(', s))
    ok = clips >= places
    fail += not ok
    print('%-24s key plans %d, clipped %d  %s' % (f, places, clips, 'PASS' if ok else 'FAIL: clip every key plan to its designed area'))
sys.exit(1 if fail else 0)
