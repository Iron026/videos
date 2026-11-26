"""Verificação palavra a palavra da narração APROVADA com o modelo OFICIAL do Whisper (openai/whisper-large-v3, licença MIT),
rodando 100 % local: o áudio não sai da máquina (HF_HUB_OFFLINE=1 na transcrição). Nada é gerado nem alterado no áudio.

1. Converte os pesos oficiais (safetensors) para CTranslate2 localmente (uma vez).
2. Transcreve com tempos por palavra (faster-whisper, CPU, float32), SEM prompt de roteiro (para não induzir o resultado).
3. Casa a transcrição com o roteiro oficial (difflib, palavras normalizadas) e relata divergências.
4. Grava roteiro/palavras_whisper.json: as palavras do ROTEIRO com os instantes medidos (as não casadas são interpoladas
   entre vizinhas casadas e marcadas). O original palavras.json não é tocado aqui.
Uso: PYTHONPATH=/home/user/whisper_site python3 verificar_whisper.py <audio.mp3>"""
import os, sys, json, re, subprocess, unicodedata, difflib, hashlib, time
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'roteiro')
OFICIAL = '/home/user/modelos/whisper-large-v3-oficial'; CT2 = '/home/user/modelos/whisper-large-v3-ct2'
audio = sys.argv[1]
if not os.path.exists(os.path.join(CT2, 'model.bin')):
    t = time.time()
    subprocess.run([sys.executable, '-m', 'ctranslate2.converters.transformers', '--model', OFICIAL, '--output_dir', CT2,
                    '--copy_files', 'tokenizer.json', 'preprocessor_config.json', '--quantization', 'float16'], check=True)
    print(f'convertido em {time.time() - t:.0f} s', flush=True)
os.environ['HF_HUB_OFFLINE'] = '1'
from faster_whisper import WhisperModel
t = time.time()
modelo = WhisperModel(CT2, device='cpu', compute_type='float32')
import numpy as np   # decodificação pelo ffmpeg (16 kHz mono float), sem tocar no arquivo original
pcm = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
segs, info = modelo.transcribe(pcm, language='pt', word_timestamps=True, beam_size=5, vad_filter=False, condition_on_previous_text=True)
ww = [dict(palavra=w.word.strip(), inicio=round(w.start, 3), fim=round(w.end, 3), prob=round(w.probability, 3)) for s in segs for w in s.words]
print(f'transcrito em {time.time() - t:.0f} s · {len(ww)} palavras', flush=True)

def norm(w):
    w = unicodedata.normalize('NFKD', w.lower()); w = ''.join(c for c in w if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', w)
rot = [w for l in open(os.path.join(R, 'roteiro_texto.txt')) if l.strip() for w in l.split()]
a, b = [norm(w) for w in rot], [norm(w['palavra']) for w in ww]
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
casa = {}; diverg = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal':
        for k in range(i2 - i1): casa[i1 + k] = j1 + k
    else:
        diverg.append(dict(tipo=op, roteiro=' '.join(rot[i1:i2]), ouvido=' '.join(w['palavra'] for w in ww[j1:j2]),
                           instante=ww[j1]['inicio'] if j1 < len(ww) else None))
        if op == 'replace' and i2 - i1 == j2 - j1:          # troca 1 a 1 (ex.: grafia de número): tempos ainda valem
            for k in range(i2 - i1): casa[i1 + k] = j1 + k
out = []
for i, w in enumerate(rot):
    if i in casa: x = ww[casa[i]]; out.append(dict(palavra=w, inicio=x['inicio'], fim=x['fim'], prob=x['prob']))
    else: out.append(dict(palavra=w, inicio=None, fim=None, interpolado=True))
for i, w in enumerate(out):      # interpola as não casadas entre vizinhas casadas
    if w['inicio'] is None:
        p = next(j for j in range(i - 1, -2, -1) if j < 0 or out[j]['inicio'] is not None)
        n = next(j for j in range(i + 1, len(out) + 1) if j == len(out) or out[j]['inicio'] is not None)
        t0 = out[p]['fim'] if p >= 0 else 0.0; t1 = out[n]['inicio'] if n < len(out) else t0 + 0.4
        k = (i - p) / (n - p); w['inicio'] = round(t0 + (t1 - t0) * (k - 0.5 / (n - p)), 3); w['fim'] = round(t0 + (t1 - t0) * k, 3)
sha = hashlib.sha256(open(audio, 'rb').read()).hexdigest()
rel = dict(modelo='openai/whisper-large-v3 (pesos oficiais, convertidos localmente para CTranslate2 float16; inferência float32 em CPU)',
           audio=os.path.basename(audio), audio_sha256=sha, idioma=info.language, prob_idioma=round(info.language_probability, 3),
           palavras_roteiro=len(rot), palavras_ouvidas=len(ww), casadas=len(casa), divergencias=diverg,
           prob_media=round(sum(w['prob'] for w in ww) / len(ww), 3), prob_baixa=[w for w in ww if w['prob'] < 0.5])
json.dump(dict(metodo=rel['modelo'], palavras=out), open(os.path.join(R, 'palavras_whisper.json'), 'w'), ensure_ascii=False, indent=0)
json.dump(dict(rel, transcricao=ww), open(os.path.join(A, 'verificacao_whisper.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in rel.items() if k != 'prob_baixa'}, ensure_ascii=False, indent=1)); print('prob < 0,5:', rel['prob_baixa'])
