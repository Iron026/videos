  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#!/bin/bash
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*# Rodada 11 — montagem DEFINITIVA com as decisões aprovadas (registro reprodutível):
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#  · tudo da V9/V10 (COMPOSICAO_R9=1, corte seco A3→A4 em 4,87 s)
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#  · TRANSICAO_A4_INTERNA=empurrao → Opção C aprovada: rosto → interior azul em 5,737 s, empurrão lateral de 0,3 s com
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#    desfoque de movimento de 180° CENTRADO; quadros-ponte quadros_pontes_r11/<perfil>/A4_rosto_c (câmera aprovada continuada)
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#    e A4_interior (câmera fixa do interior, igual à aprovada no q34)
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#  · áudio: som/audio_ep02_r11_spice_intrigue.wav (V10 efeitos aprovados + Spice Intrigue, correção local de pico em 85,9 s)
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*#  · SEM_LEGENDAS=1 no ambiente → master de imagem sem legendas
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*# Uso: bash montar_r11.sh [perfil] [saida.mp4] [audio.wav]
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*cd "$(dirname "$0")"
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*PERFIL=${1:-final}; SAIDA=${2:-ep02_final.mp4}; AUD=${3:-../som/audio_ep02_r11_final.wav}
  · áudio: som/audio_ep02_r11_spice_intrigue.wav.*COMPOSICAO_R9=1 TRANSICAO_A4=corte TRANSICAO_A4_INTERNA=empurrao GARRAFA_B5=1 AUDIO_EP02="$AUD" MIXAGEM_EP02=1 python3 montar_ep02.py "$PERFIL" "$SAIDA"
