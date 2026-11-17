#!/bin/bash
# Renders finais da revisão v3 (quadros 2, 3, 4) e do protótipo do mascote.
cd "$(dirname "$0")"; export PYTHONPATH=${BPY_SITE:-/tmp/claude-0/blender/site}
for q in 2 3 4; do python3 quadros.py $q 100 128 ../etapa_c0/quadros/quadro${q}_v3.png 2>&1 | grep -E "MONTAGEM|Traceback|rror:"; done
python3 mascote.py 100 96 todas 2>&1 | grep -E "OK|Traceback|rror:"
echo FIM
