#!/bin/bash
# Rodada 9 — montagem da V9 com as decisões aprovadas (registro reprodutível):
#  · COMPOSICAO_R9=1  → composição da V9a (legendas por sentido, áreas seguras, cartões, rótulos com âncora visível)
#  · TRANSICAO_A4=corte → corte seco em 4,87 s (pausa da narração), sem fusão A3 → A4
#  · áudio: som/audio_ep02_r9.wav = mixagem aprovada + SÓ os passos novos do I1 (sem o teto global de −2,0 dB)
#  · cenas da rodada 9 já promovidas a cenas/<id> (V8 preservada em arquivo/cenas_v8.tgz)
# Uso: bash montar_v9.sh [perfil] [saida.mp4]
cd "$(dirname "$0")"
PERFIL=${1:-revisao}; SAIDA=${2:-ep02_v9_revisao.mp4}
COMPOSICAO_R9=1 TRANSICAO_A4=corte AUDIO_EP02=../som/audio_ep02_r9.wav MIXAGEM_EP02=1 python3 montar_ep02.py "$PERFIL" "$SAIDA"
