#!/bin/bash
# Rodada 13 — montagem DEFINITIVA com as decisões aprovadas pelo usuário (registro reprodutível):
#  · tudo da R11/R12 (montar_r11.sh: COMPOSICAO_R9, corte seco A3→A4, empurrão no A4, aviso do B5)
#  · E3: quadros re-renderizados com a bobina (faces de contato retiradas) e o bloco do cilindro (folga 0,02 mm) corrigidos
#    → quadros_final_r13c2/E3 (cena E3_r13c_v2); os quadros R12 do E3 ficam intactos em quadros_final/E3
#  · ARRED_QUADROS=1: fim dos quadros repetidos por empate de arredondamento (A1, B7, H1, I1)
#  · entrada do E3: fusão atual mantida (CORTE_E3 NÃO é usado)
#  · áudio: som/audio_ep02_r13_r13c_final_r13_teste.wav (mixagem R13C final: 0:33 discreta + porta do C1 mais baixa)
#  · SEM_LEGENDAS=1 no ambiente → master de imagem sem legendas
# Uso: bash montar_r13.sh [perfil] [saida.mp4] [audio.wav]
cd "$(dirname "$0")"
PERFIL=${1:-final}; SAIDA=${2:-ep02_definitivo_r13_1080x1920.mp4}; AUD=${3:-../som/audio_ep02_r13_r13c_final_r13_teste.wav}
QUADROS_R13C=E3=quadros_final_r13c2/E3 ARRED_QUADROS=1 bash montar_r11.sh "$PERFIL" "$SAIDA" "$AUD"
