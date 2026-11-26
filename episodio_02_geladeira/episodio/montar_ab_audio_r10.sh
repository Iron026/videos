#!/bin/bash
# Rodada 10: versões de áudio sobre a MESMA imagem (V10; vídeo copiado bit a bit) + trechos A/B.
#  A = mixagem V9 aprovada · B1 = V9 + efeitos novos · B2 = V9 + trilha · B = V9 + efeitos novos + trilha
# Uso: bash montar_ab_audio_r10.sh  (precisa de ep02_v10_revisao_audio_v9.mp4)
set -e; cd "$(dirname "$0")"; V=ep02_v10_revisao_audio_v9.mp4; P=previas_r10; mkdir -p $P
./trocar_audio_r10.sh $V ../som/audio_ep02_r10_efeitos.wav ep02_v10_revisao_efeitos.mp4
./trocar_audio_r10.sh $V ../som/audio_ep02_r10_musica.wav ep02_v10_revisao_trilha.mp4
./trocar_audio_r10.sh $V ../som/audio_ep02_r10_completo.wav ep02_v10_revisao_efeitos_e_trilha.mp4
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
TRECHOS="0:6:abertura 31.5:7:revelacao 74:9:compressor_valvulas 115.3:6:puxador_e_leite 133:18.2:conclusao"
ab $V "A · audio V9 aprovado" ep02_v10_revisao_efeitos_e_trilha.mp4 "B · efeitos novos + trilha" ab_audio_v9_x_nova.mp4
# só a contribuição da TRILHA: efeitos novos sem trilha × efeitos novos com trilha (mesmos efeitos dos dois lados)
ab ep02_v10_revisao_efeitos.mp4 "B1 · efeitos novos, sem trilha" ep02_v10_revisao_efeitos_e_trilha.mp4 "B · efeitos novos + trilha" ab_so_trilha.mp4
# só a contribuição dos EFEITOS: V9 × V9 + efeitos novos (sem trilha)
TRECHOS="0:3:puxador_A1 73.8:9.5:valvulas_E2_E3 116.8:3.2:puxador_e_leite_I1"
ab $V "A · audio V9 aprovado" ep02_v10_revisao_efeitos.mp4 "B1 · V9 + efeitos novos" ab_so_efeitos.mp4
echo ok
