#!/bin/bash
# Full pipeline for the Casa Grove interior design set. Every step is deterministic from the base PDFs and the configs.
set -e
cd "$(dirname "$0")"
python3 build_model.py > logs_model.txt 2>&1          # room model from the base plans
python3 idd_electrical.py > logs_elec.txt              # rule-based lighting, switching, power, data
python3 build_elev.py                                  # interior elevations ID-7xx + elev_index.json
python3 build.py > logs_fp.txt 2>&1                   # flooring base edits (Rev1)
python3 compose.py | tail -1                           # flooring plans ID-101/102
python3 build_base.py | tail -1                        # neutral bases
python3 build_wf.py > logs_wf.txt 2>&1                # wall finish base edits
python3 compose_wf.py | tail -1                        # wall finish plans ID-201/202 with markers
python3 compose_plans.py | tail -1                     # RCP, lighting, power, furniture
python3 build_details.py | tail -1                     # ID-801
python3 build_cover.py | tail -1                       # ID-000 / ID-001 (needs every other sheet first)
python3 build_takeoff.py | tail -1
python3 "$(ls -d /root/.claude/skills/synced/*/xlsx | head -1)/scripts/recalc.py" 261101.HD102.Takeoff.xlsx 60 | head -3
for f in CoverSchedules FlooringPlans WallFinishPlans RCPPlans LightingPlans PowerDataPlans FurniturePlans InteriorElevations Details; do
  python3 idd_qa.py sheets 261101.HD102.$f.pdf | grep -E "overlaps [1-9]|soft_hyphens': [1-9]|em_dashes': [1-9]|double_hyphens': [1-9]|replacement_glyphs': [1-9]" | sed "s/^/$f: /" || true
done
python3 idd_checks.py | tail -3
python3 assemble_set.py
