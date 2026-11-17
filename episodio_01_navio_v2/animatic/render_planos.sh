#!/bin/bash
# Renderiza os planos 1 e 2/3 do animatic em 1080×1920 (Three.js v2: GTAO 8 amostras, MSAA 4×). Retomável por plano.
cd "$(dirname "$0")/../motores/tempo_real_v2"
for c in p1 p23; do
  [ -f ../../animatic/quadros_$c/.completo ] && continue
  node render_anim.mjs "cena=../../animatic/cena_$c/&escala=1&aoamostras=8&msaa=4" ../../animatic/quadros_$c 1 && touch ../../animatic/quadros_$c/.completo
done
echo FIM_RENDER
