#!/bin/bash
# Rodada 11 (Secret Garden): A = efeitos novos sem música × B = efeitos novos + Secret Garden, sobre a MESMA imagem (V10; vídeo copiado bit a bit) + trechos A/B.
#  A = mixagem V9 aprovada · B1 = V9 + efeitos novos · B2 = V9 + trilha · B = V9 + efeitos novos + trilha
# Uso: bash montar_ab_audio_r10.sh  (precisa de ep02_v10_revisao_audio_v9.mp4)
set -e; cd "$(dirname "$0")"; V=ep02_v10_revisao_audio_v9.mp4; P=previas_r10; mkdir -p $P
F=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
# ab <A.mp4> <rótulo A> <B.mp4> <rótulo B> <saída>: cada trecho toca A e depois B, com o rótulo na tela
ab() {
  local partes=() i=0
  for t in $TRECHOS; do IFS=: read ini dur nome <<< "$t"
    for lado in A B; do
      if [ $lado = A ]; then src=$1; rot=$2; else src=$3; rot=$4; fi
      out=$P/_ab_$i.mp4; i=$((i+1)); partes+=($out)
      ffmpeg -y -v error -ss $ini -t $dur -i $src -vf "drawtext=fontfile=$F:text='$rot · $nome':x=(w-tw)/2:y=h*0.12:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10" \
        -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 $out
    done
  done
  printf "file '%s'\n" "${partes[@]##*/}" > $P/_lista.txt
  (cd $P && ffmpeg -y -v error -f concat -safe 0 -i _lista.txt -c copy $5 && rm -f _ab_*.mp4 _lista.txt)
}
TRECHOS="0:8:abertura 31.5:7:revelacao 48.3:7:evaporador 74:9:compressor 86.9:8:condensador 101:7:capilar 115.8:8:porta_aberta 133:18.2:conclusao"
ab ep02_v10_revisao_efeitos.mp4 "A · efeitos novos, sem musica" ep02_v10_revisao_efeitos_e_secret_garden.mp4 "B · efeitos novos + Secret Garden" ab_secret_garden.mp4
echo ok
