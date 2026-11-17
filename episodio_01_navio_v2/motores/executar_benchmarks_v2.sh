#!/bin/bash
# Benchmarks v2 em sequência (um motor por vez, CPU dedicada). Resultados em motores/resultados_v2/
cd "$(dirname "$0")/tempo_real_v2"; R=../resultados_v2; mkdir -p $R
for q in 2 3; do
  for v in "ref:ao=1&aoamostras=16&msaa=4" "cache:ao=1&aoamostras=16&msaa=4&cache=1" "ao8:ao=1&aoamostras=8&msaa=4&cache=1" \
           "msaa2:ao=1&aoamostras=8&msaa=2&cache=1" "e075:escala=0.75&ao=1&aoamostras=8&msaa=4&cache=1" "semao:ao=0&msaa=4&cache=1"; do
    nome=${v%%:*}; qs=${v#*:}; esc=1; [[ $qs == *escala=* ]] || qs="escala=1&$qs"
    timeout 1500 node bench2.mjs "cena=../cena2_q$q/&$qs" 4 $R/rt_q${q}_$nome.png 2>&1 | tail -1 > $R/rt_q${q}_$nome.json
    echo "RT q$q $nome $(python3 -c "import json;d=json.load(open('$R/rt_q${q}_$nome.json'));print(round(d['render_mediana_ms']))") ms"
  done
done
cd ../../blender; export PYTHONPATH=${BPY_SITE:-/tmp/claude-0/blender/site}
python3 bench_cycles2.py 3 50 ../motores/resultados_v2/cycles_q3 '[{"nome":"ref128","amostras":128},{"nome":"s64","amostras":64},{"nome":"s32","amostras":32,"quadros":2},{"nome":"s16","amostras":16},{"nome":"s32_lim05","amostras":32,"limiar":0.05},{"nome":"s32_saltos","amostras":32,"saltos":[4,2,2,4]},{"nome":"s32_p35","amostras":32,"pct":35},{"nome":"s32_persist","amostras":32,"quadros":2,"persistente":true}]' 2>&1 | grep -E "^VAR|rror"
echo FIM
