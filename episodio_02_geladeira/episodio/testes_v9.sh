#!/bin/bash
# Rodada 9: bateria de testes de imagem nos planos re-renderizados, V9 × V8 (mesmos scripts, mesmos planos; V8 = quadros_revisao_v8)
cd "$(dirname "$0")"; R=../relatorios/testes_v9; mkdir -p $R
CORTE="C2 C3 C4 D1 D3 D5 G1 G2 G3 H1 H2 J3"; PORTA="C4 G3 H1 H2 J3"
for V in v9:quadros_revisao:cenas v8:quadros_revisao_v8:cenas_v8; do IFS=: read n d c <<< "$V"; export CENAS_DIR=$c
  echo "== $n AO cortes"; nice python3 validar_ao_cortes.py $d $R/ao_cortes_$n.json $CORTE > $R/ao_cortes_$n.txt 2>&1
  echo "== $n porta×vedação"; nice python3 verificar_porta_vedacao.py $R/porta_vedacao_$n.json --quadros $d $PORTA > $R/porta_vedacao_$n.txt 2>&1
  echo "== $n juntas"; nice python3 verificar_juntas.py $d $R/juntas_$n.json $CORTE > $R/juntas_$n.txt 2>&1
done
echo "== cintilação absoluta (todos os planos de cada pasta)"
nice python3 detectar_cintilacao_todos.py quadros_revisao 540 $R/cintilacao_v9.json > $R/cintilacao_v9.txt 2>&1
nice python3 detectar_cintilacao_todos.py quadros_revisao_v8 540 $R/cintilacao_v8.json > $R/cintilacao_v8.txt 2>&1
echo FIM_TESTES
