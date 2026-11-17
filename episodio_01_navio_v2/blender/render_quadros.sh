#!/bin/bash
# Renderiza os 5 quadros de referência em 1080x1920 (Cycles CPU). Uso: ./render_quadros.sh [amostras] [quadros...]
cd "$(dirname "$0")"
AM=${1:-160}; shift
QS=${@:-1 2 3 4 5}
export PYTHONPATH=${BPY_SITE:-/tmp/claude-0/blender/site}
for q in $QS; do
  python3 quadros.py $q 100 $AM ../etapa_b/quadros/quadro${q}.png 2>&1 | grep -E "MONTAGEM|Traceback|rror:" 
done
echo FIM
