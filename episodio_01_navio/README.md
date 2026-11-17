# De Olho no Invisível — Episódio 01
**Como um navio de milhares de toneladas consegue flutuar?** · 75 s · 1080×1920 · 30 fps · pt-BR

Produção 100% procedural e local: modelagem, animação, água, legendas, efeitos sonoros e música
são gerados por código. Nenhum recurso pago ou crédito externo foi usado.

## Estrutura

| Pasta / arquivo | Função |
|---|---|
| `narracao/roteiro.txt` | Texto aprovado (preservado integralmente) |
| `narracao/gerar_narracao.py` | Síntese de voz (Kokoro-82M, voz `pm_alex`) com cada frase ancorada ao storyboard → `narracao.wav`, `frases.json` |
| `ferramentas/alinhar_legendas.py` | Alinhamento palavra a palavra com Whisper → `palavras.json`, `legendas.json`, `entrega/episodio_01_legendas.srt` (o texto é sempre o do roteiro; o ASR só fornece tempos) |
| `projeto/src/casco.js` | Forma do casco (uma única função `meiaBoca(x,y)`), hidrostática (volume × calado, centro de carena) e malhas |
| `projeto/src/fisica.js` | Simulação determinística do calado: carga de contêineres (30 t cada) e alagamento dos porões |
| `projeto/src/agua.js` | Oceano “diorama”: ondas analíticas, face de corte, leito, céu, tingimento subaquático |
| `projeto/src/roteiro.js` · `camera.js` | Linha do tempo das cenas e trilha de câmera (Hermite / Catmull-Rom) |
| `projeto/src/sobreposicao.js` | Rótulos, cartões, painel de densidade, legendas queimadas e assinatura |
| `projeto/src/main.js` | Montagem da cena; `window.quadro(t)` renderiza qualquer instante (ordem livre) |
| `projeto/render.mjs` | Chromium headless (WebGL) → FFmpeg. Modo vídeo ou quadros isolados |
| `audio/gerar_audio.py` | Efeitos, ambiente e música originais sintetizados; ducking sob a narração |
| `ferramentas/validar.py` | Validação do MP4 (formato, quadros pretos/congelados, loudness, legendas, ASR da narração) |
| `montar.sh` | Pipeline completo (`--previa` para baixa resolução) |

## Como reproduzir
```bash
cd projeto && npm install && cd ..
# modelos (baixados via npm, sem HuggingFace):
#   Kokoro: npm pack kokoro-q8-shards kokoro-js  → concatenar kokoro-q8.part0..5.bin em kokoro-q8.onnx
#           e converter voices/*.bin (float32 510×1×256) num voices.npz
#   Whisper small (CTranslate2): npm pack @skillninja/shortmovie-telop-model-p0..p3 → concatenar model.bin.part0..3
export KOKORO_MODELO=.../kokoro-q8.onnx KOKORO_VOZES=.../voices.npz WHISPER_MODELO=.../whisper-small-ct2
pip install kokoro-onnx faster-whisper scipy soundfile
./montar.sh --previa      # ~10 min
./montar.sh               # final 1080×1920
python3 ferramentas/validar.py entrega/episodio_01_navio_final.mp4 entrega/episodio_01_legendas.srt $WHISPER_MODELO
```

## Reutilização para próximos episódios
- Trocar `narracao/roteiro.txt` e os alvos `ALVOS` em `gerar_narracao.py` (tempo de início de cada frase).
- `render.mjs`, `sobreposicao.js` (estilo de legendas, rótulos, cartões, assinatura), `agua.js`, `camera.js`,
  `audio/gerar_audio.py` e `ferramentas/` são genéricos; `casco.js`/`fisica.js` são específicos do tema.
- Paleta da marca: `#202B57`, `#F6F4EC`, `#F3B544`. Fonte: Montserrat (OFL, via `@fontsource`).

## Licenças dos componentes
Three.js (MIT) · Montserrat (SIL OFL 1.1) · Kokoro-82M e vozes (Apache-2.0) · Whisper (MIT, só para alinhamento/validação) ·
FFmpeg (ferramenta local). Música e efeitos: síntese original deste projeto.
