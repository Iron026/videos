#!/usr/bin/env bash
# Pipeline completo do Episódio 01. Uso: ./montar.sh [--previa]
# Requisitos: node 22, ffmpeg, Chromium/Playwright do ambiente, python3 com kokoro-onnx, faster-whisper, scipy, soundfile.
# Variáveis: KOKORO_MODELO, KOKORO_VOZES, WHISPER_MODELO (caminhos dos modelos; ver README.md).
set -euo pipefail
cd "$(dirname "$0")"
PREVIA=${1:-}
mkdir -p render entrega
if [[ -n "${KOKORO_MODELO:-}" ]]; then
  python3 narracao/gerar_narracao.py --modelo "$KOKORO_MODELO" --vozes "$KOKORO_VOZES"
  python3 ferramentas/alinhar_legendas.py "$WHISPER_MODELO"
fi
python3 audio/gerar_audio.py
if [[ "$PREVIA" == "--previa" ]]; then
  (cd projeto && node render.mjs --saida ../render/previa.mp4 --escala 0.4 --fps 15 --preset veryfast --crf 22)
  VIDEO=render/previa.mp4; SAIDA=render/previa_com_audio.mp4
else
  # Render retomável: segmentos de 2 s em 4 processos; rodar de novo continua de onde parou.
  (cd projeto && for i in 0 1 2 3; do node render.mjs --segmentos ../render/segmentos --dseg 2 --proc $i --nproc 4 --crf 15 --preset slow > ../render/proc_$i.log 2>&1 & done; wait)
  n=$(ls render/segmentos/seg_*.mp4 | grep -v tmp | wc -l); [[ $n -eq 38 ]] || { echo "Segmentos incompletos: $n/38"; exit 1; }
  ls render/segmentos/seg_*.mp4 | grep -v tmp | sort | sed "s#^render/#file '#; s#\$#'#" > render/partes.txt
  ffmpeg -y -loglevel error -f concat -safe 0 -i render/partes.txt -c copy render/video_sem_audio.mp4
  VIDEO=render/video_sem_audio.mp4; SAIDA=entrega/episodio_01_navio_final.mp4
fi
# loudness: -14 LUFS integrado, pico real -1,5 dBTP (2 passagens)
MED=$(ffmpeg -hide_banner -i audio/mix_bruto.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
ii=$(echo "$MED" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
read -r I TP LRA TH OFF <<< "$ii"
ffmpeg -y -loglevel error -i "$VIDEO" -i audio/mix_bruto.wav \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest \
  -metadata title="Como um navio de milhares de toneladas consegue flutuar?" -metadata artist="De Olho no Invisível" -metadata language=por \
  "$SAIDA"
echo "Gerado: $SAIDA"
