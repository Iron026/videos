#!/bin/bash
# Renderiza os segmentos do Ep01 no motor v2.  Uso: render_segmentos.sh <perfil: previa|revisao|final> [segmentos...]
#   previa : 270×480, sem AO/MSAA, 1 a cada 3 quadros (10 fps)   — checagem de sincronia e narrativa
#   revisao: 540×960, GTAO 4 amostras, sem MSAA, 30 fps           — versão de revisão
#   final  : 1080×1920, GTAO 8, MSAA 4×, 30 fps                   — NÃO executar sem aprovação
P=${1:-previa}; shift
SEGS=${@:-02 03 04 05 0607 08a 08b 09 10 11 12 13}
case $P in
  previa)  Q="escala=0.25&ao=0&msaa=0"; PASSO=3 ;;
  revisao) Q="escala=0.5&aoamostras=4&msaa=0"; PASSO=1 ;;
  final)   Q="escala=1&aoamostras=8&msaa=4"; PASSO=1 ;;
esac
cd "$(dirname "$0")/../motores/tempo_real_v2"
for s in $SEGS; do
  OUT=../../episodio/quadros_${P}/s$s
  [ -f $OUT/.completo ] && continue
  node render_anim.mjs "cena=../../episodio/cenas/s$s/&$Q" $OUT $PASSO && touch $OUT/.completo
  echo "SEG $s ok"
done
echo FIM_$P
