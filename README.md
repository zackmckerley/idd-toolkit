# idd-toolkit

The code behind HELIOS interior design drawing sets: plans in, a coordinated drawing set out, then photoreal rendered elevations and inspiration-driven finish options. The interior-design-drawings skill describes the method. This repository holds the code.

The worked example is Casa Grove (HD102, 3350 Thomas Ave): the `build_*_rev1.py` room generators and `rev1/`. Those files are project code. Read them for the patterns, then copy and rename them for a new project instead of editing them in place.

## Setup in a fresh session

```bash
git clone https://github.com/zackmckerley/idd-toolkit.git /home/claude/flrwork   # the scripts assume this path
cd /home/claude/flrwork
pip install --break-system-packages pymupdf shapely fonttools numpy openpyxl colour-science scikit-learn pillow ezdxf
apt-get install -y fonts-inter fonts-liberation        # Inter Medium/Bold for drawing text, Liberation Serif for titles
# Blender for renders: the bpy module in its own Python 3.11 venv
python3.11 -m venv /home/claude/rendervenv && /home/claude/rendervenv/bin/pip install bpy==4.2.0 numpy pillow
python3 render/fetch_assets.py                          # CC0 textures and HDRIs from Poly Haven (about 50 MB)
python3 render/calibrate.py                             # exposure calibration for the drawing-style renders
```

The input files (the architect's plans, base PDFs) are not stored here. They come from the project. Keep the clone at `/home/claude/flrwork`: about a dozen scripts hard-code that path.

## From what to what

| Start from | Run | Gets you |
|---|---|---|
| An architect's vector PDF plan | `idd_ingest` / `build_model.py` (configure FLOORS) | `model_f{n}.json` room model |
| A DXF/DWG | `idd_ingest.from_dxf` | the same |
| A scan or photo of a plan | `idd_ingest.from_image` (calibrate on two dimensions) | the same, dimensions marked as scaled |
| A concept: a sketch, a napkin, a verbal brief | write a plan spec, then `python3 idd_planspec.py spec.json OUT` (example in `examples/concept/`) | a clean vector base plan PDF on the standard layers, plus the exact room model |
| A room model | `make_set.sh` (generated set), `build_elev.py` | finish plans, RCP, lighting, power, furniture, elevations, details, schedules, takeoff |
| A room to design | a study sheet (`build_study.py` pattern), the owner picks, then a room generator (`build_*_rev1.py` pattern) using `idd_components` / `idd_kitchen` | the designed room sheets (key plan, elevations, compartments) |
| Designed sheets | `build_review_set.py` | the owner review set, full size and 11x17 |
| A designed room | `render/capture_run.py ROOM views.json`, then `render/photoreal.py views.json IDX out.png` | photoreal rendered elevations (`--preview` for a quick look) |
| An inspiration image | `render/inspiration.py IMAGE OUT --neutral x,y,w,h --neutral-is HEX --source "..."` | palette, Sherwin-Williams and Benjamin Moore candidates by CIEDE2000, LRV, confidence, the design-read template |

## Checks

`idd_qa.py sheets`, `idd_checks.py`, and `idd_check_keyplans.py` (every key plan is clipped to the area its section designs). Then an independent review with `references/reviewer-brief.md` from the skill.
