#!/bin/bash
# Rodada 13.1 — igual à R13 (montar_r13.sh) + avisos retirados a pedido do usuário: "Visão térmica", "Corte ilustrativo",
# "Tempo acelerado", "Fluxo desacelerado" e "Câmera lenta". Ficam "Canal ampliado (esquema)" (D4, F2) e o aviso da lupa (G3).
# Só o DESENHO dos avisos muda; posições de rótulos e cartões continuam calculadas como antes.
cd "$(dirname "$0")"
PERFIL=${1:-final}; SAIDA=${2:-ep02_definitivo_r13_1_1080x1920.mp4}; AUD=${3:-../som/audio_ep02_r13_r13c_final_r13_teste.wav}
AVISOS_OCULTOS="Visão térmica,Corte ilustrativo,Tempo acelerado,Fluxo desacelerado,Câmera lenta" bash montar_r13.sh "$PERFIL" "$SAIDA" "$AUD"
