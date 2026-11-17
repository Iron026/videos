"""Integra um arquivo de narração da voz oficial (ElevenLabs · Will - Deep) ao projeto.

Uso:  python3 voz/preparar_narracao.py <audio_original> "<texto de referência>" <pasta_saida> [modelo_whisper]

O original NUNCA é alterado. Na pasta de saída são gerados:
  narracao_48k.wav   – versão de trabalho (48 kHz, mono, 24 bits), normalizada para −16 LUFS (fala)
  palavras.json      – cada palavra do TEXTO DE REFERÊNCIA com início/fim (s); o reconhecimento de fala só fornece tempos
  legendas.srt       – blocos curtos para legenda
  verificacao.json   – transcrição automática, diferenças em relação ao texto, ritmo, loudness, pico
Não gera nem regenera áudio: nenhuma chamada à ElevenLabs, nenhuma voz substituta.
"""
import sys, os, json, re, subprocess, difflib, unicodedata
import numpy as np

orig, texto, saida = sys.argv[1], sys.argv[2], sys.argv[3]
modelo = sys.argv[4] if len(sys.argv) > 4 else os.environ.get('WHISPER_MODELO', '/tmp/claude-0/asr/m')
os.makedirs(saida, exist_ok=True)


def run(c): return subprocess.run(c, capture_output=True, text=True)


def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); w = re.sub(r'\s+', ' ', w)
    return re.sub(r'[^a-z0-9 ]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


# 1) versão de trabalho normalizada (loudnorm em duas passagens)
wav = os.path.join(saida, 'narracao_48k.wav')
m1 = run(['ffmpeg', '-hide_banner', '-i', orig, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-']).stderr
j = json.loads(m1[m1.rfind('{'):m1.rfind('}') + 1])
run(['ffmpeg', '-y', '-v', 'error', '-i', orig, '-af',
     f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
     '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', wav])

# 2) reconhecimento com tempos por palavra
from faster_whisper import WhisperModel
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', orig, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
segs, _ = WhisperModel(modelo, device='cpu', compute_type='int8').transcribe(audio, language='pt', beam_size=5, word_timestamps=True)
asr = [(w.word.strip(), w.start, w.end, w.probability) for s in segs for w in s.words]

# 3) alinhamento: palavras do roteiro recebem os tempos das palavras reconhecidas correspondentes
ref = texto.split(); rn = [norm(w) for w in ref]; hn = [norm(w[0]) for w in asr]
sm = difflib.SequenceMatcher(a=rn, b=hn, autojunk=False)
tempos = [None] * len(ref)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal':
        for k in range(i2 - i1): tempos[i1 + k] = (asr[j1 + k][1], asr[j1 + k][2], asr[j1 + k][3])
    elif op == 'replace' and j2 > j1:          # divide o trecho reconhecido proporcionalmente
        t0, t1 = asr[j1][1], asr[j2 - 1][2]; n = i2 - i1
        for k in range(n): tempos[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n, None)
for i in range(len(ref)):                      # palavras sem correspondência: interpola entre vizinhas
    if tempos[i] is None:
        a = next((tempos[k][1] for k in range(i - 1, -1, -1) if tempos[k]), 0.0)
        b = next((tempos[k][0] for k in range(i + 1, len(ref)) if tempos[k]), a + 0.3)
        tempos[i] = (a, max(b, a + 0.05), None)
palavras = [dict(palavra=w, inicio=round(t[0], 3), fim=round(t[1], 3), confianca=None if t[2] is None else round(t[2], 2)) for w, t in zip(ref, tempos)]
json.dump(palavras, open(os.path.join(saida, 'palavras.json'), 'w'), ensure_ascii=False, indent=1)

# 4) legendas: quebra em fim de frase ou a cada ~28 caracteres
def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}'
blocos, atual = [], []
for p in palavras:
    atual.append(p)
    txt = ' '.join(x['palavra'] for x in atual)
    if p['palavra'][-1] in '.?!' or len(txt) >= 28: blocos.append(atual); atual = []
if atual: blocos.append(atual)
with open(os.path.join(saida, 'legendas.srt'), 'w', encoding='utf-8') as f:
    for i, b in enumerate(blocos, 1):
        f.write(f"{i}\n{ts(b[0]['inicio'])} --> {ts(b[-1]['fim'])}\n{' '.join(x['palavra'] for x in b)}\n\n")

# 5) verificação
eb = run(['ffmpeg', '-hide_banner', '-i', orig, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr; sm_ = eb[eb.rfind('Summary:'):]
dur = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', orig]).stdout)
erros = sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal')
fala = sum(p['fim'] - p['inicio'] for p in palavras)
ver = dict(original=os.path.abspath(orig), duracao_s=round(dur, 3), transcricao=' '.join(w[0] for w in asr),
           diferencas=[(' '.join(ref[i1:i2]), ' '.join(w[0] for w in asr[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal'],
           wer_percent=round(100 * erros / max(1, len(ref)), 1), palavras_por_min=round(len(ref) / max(asr[-1][2] - asr[0][1], 1e-3) * 60, 1),
           loudness_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', sm_).group(1)), pico_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', sm_).group(1)))
json.dump(ver, open(os.path.join(saida, 'verificacao.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(ver, ensure_ascii=False, indent=1))
