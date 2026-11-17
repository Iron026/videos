#!/bin/bash
# Testes de validação em qualidade de REVISÃO (540×960, GTAO 4, 30 fps reais), gravados direto em quadros_revisao/
# (os quadros são reaproveitados no render integral). Formato: segmento:quadro_ini:quadro_fim
cd "$(dirname "$0")/../motores/tempo_real_v2"
for spec in "$@"; do
  IFS=: read s a b <<< "$spec"
  node render_anim.mjs "cena=../../episodio/cenas/s$s/&escala=0.5&aoamostras=4&msaa=0" ../../episodio/quadros_revisao/s$s 1 $a $b 2>&1 | grep -E "FIM|rror"
done
echo FIM_TRECHOS
