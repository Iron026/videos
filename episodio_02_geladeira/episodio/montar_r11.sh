#!/bin/bash
# Rodada 11 — montagem DEFINITIVA com as decisões aprovadas (registro reprodutível):
#  · tudo da V9/V10 (COMPOSICAO_R9=1, corte seco A3→A4 em 4,87 s)
#  · TRANSICAO_A4_INTERNA=empurrao → Opção C aprovada: rosto → interior azul em 5,737 s, empurrão lateral de 0,3 s com
#    desfoque de movimento de 180° CENTRADO; quadros-ponte quadros_pontes_r11/<perfil>/A4_rosto_c (câmera aprovada continuada)
#    e A4_interior (câmera fixa do interior, igual à aprovada no q34)
#  · GARRAFA_B5=1 → aviso "Tempo acelerado" só depois do pouso da garrafa (a cena B5 aprovada já tem a garrafa entrando)
#  · áudio: som/audio_ep02_r11_final.wav = V10 (efeitos aprovados) + Spice Intrigue + pouso da garrafa + "pop" nas 5
#    apresentações de componentes (−9 dB da voz), correção local de pico em 85,9 s (ver relatorios/manifesto_producao_r11.json)
#  · SEM_LEGENDAS=1 no ambiente → master de imagem sem legendas
# Uso: bash montar_r11.sh [perfil] [saida.mp4] [audio.wav]
cd "$(dirname "$0")"
PERFIL=${1:-final}; SAIDA=${2:-ep02_final.mp4}; AUD=${3:-../som/audio_ep02_r11_final.wav}
COMPOSICAO_R9=1 TRANSICAO_A4=corte TRANSICAO_A4_INTERNA=empurrao GARRAFA_B5=1 AUDIO_EP02="$AUD" MIXAGEM_EP02=1 python3 montar_ep02.py "$PERFIL" "$SAIDA"
