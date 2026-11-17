#!/bin/bash
# Revisão r2: renderiza os planos 1 e 2/3 em 1080×1920 (Three.js v2: GTAO 8 amostras, MSAA 4×) e a assinatura curta.
cd "$(dirname "$0")/../motores/tempo_real_v2"
for c in p1 p23; do
  [ -f ../../animatic/quadros_r2_$c/.completo ] && continue
  node render_anim.mjs "cena=../../animatic/cena_r2_$c/&escala=1&aoamostras=8&msaa=4" ../../animatic/quadros_r2_$c 1 && touch ../../animatic/quadros_r2_$c/.completo
done
cd ../../assinatura && [ -f ../animatic/quadros_r2_p4/.completo ] || { node captura_anim.mjs ../animatic/quadros_r2_p4 96 curto && touch ../animatic/quadros_r2_p4/.completo; }
echo FIM_RENDER_R2
