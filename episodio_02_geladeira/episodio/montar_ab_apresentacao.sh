#!/bin/bash
# Rodada 11 (teste): sons de APRESENTAÇÃO dos componentes — mesma imagem (V10, vídeo copiado), três áudios por trecho:
#  A = Spice Intrigue aprovada (sem som de apresentação) · B = + "madeira" (Freesound 551921) · C = + "pop" (Freesound 776443)
set -e; cd "$(dirname "$0")"; P=previas_r11; F=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf; partes=(); i=0
TRECHOS="39.8:3.6:fluido_refrigerante 47.9:3.6:evaporador 73.8:3.6:compressor 86.6:3.6:condensador 99.5:3.6:capilar"
for t in $TRECHOS; do IFS=: read ini dur nome <<< "$t"
  for lado in A B C; do
    case $lado in A) src=ep02_v10_revisao_efeitos_e_spice_intrigue.mp4; rot="A · sem som de apresentacao";; B) src=$P/_v10_si_g_mad.mp4; rot="B · madeira";; C) src=$P/_v10_si_g_pop.mp4; rot="C · pop";; esac
    out=$P/_ab_$i.mp4; i=$((i+1)); partes+=($out)
    ffmpeg -y -v error -ss $ini -t $dur -i $src -vf "drawtext=fontfile=$F:text='$rot · $nome':x=(w-tw)/2:y=h*0.12:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10" \
      -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 $out
  done
done
printf "file '%s'\n" "${partes[@]##*/}" > $P/_lista.txt
(cd $P && ffmpeg -y -v error -f concat -safe 0 -i _lista.txt -c copy ab_apresentacao_componentes.mp4 && rm -f _ab_*.mp4 _lista.txt)
echo ok
