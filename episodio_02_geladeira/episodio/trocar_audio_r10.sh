#!/bin/bash
# Rodada 10: troca SÓ o áudio de um vídeo montado (imagem copiada bit a bit, -c:v copy), com o MESMO tratamento de áudio da
# montagem (fade de 50 ms no último quadro, AAC 192 kb/s, 48 kHz, duração = último quadro). Uso: trocar_audio_r10.sh video.mp4 audio.wav saida.mp4
set -e; V=$1; AU=$2; OUT=$3
N=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 "$V"); DUR=$(python3 -c "print(f'{$N/30:.4f}')"); ST=$(python3 -c "print(f'{$N/30-0.05:.4f}')")
ffmpeg -y -v error -i "$V" -i "$AU" -map 0:v -map 1:a -c:v copy -af "afade=t=out:st=$ST:d=0.05" -c:a aac -b:a 192k -ar 48000 -t $DUR -movflags +faststart "$OUT"
echo "ok $OUT ($N quadros, $DUR s)"
