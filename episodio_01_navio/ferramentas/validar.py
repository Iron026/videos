"""Validação técnica do MP4 final + legendas. Uso: python3 ferramentas/validar.py <video.mp4> <legendas.srt> <modelo_whisper>
Gera entrega/validacao.json e imprime um resumo."""
import sys, json, subprocess, re, os, difflib, unicodedata
import numpy as np

video, srt, modelo = sys.argv[1], sys.argv[2], sys.argv[3]
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = {}
def run(c): return subprocess.run(c, capture_output=True, text=True)

pr = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', video]).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); a = next(s for s in pr['streams'] if s['codec_type'] == 'audio')
num, den = map(int, v['r_frame_rate'].split('/'))
res['video'] = dict(codec=v['codec_name'], perfil=v.get('profile'), largura=v['width'], altura=v['height'], fps=num / den,
                    pix_fmt=v['pix_fmt'], quadros=int(v.get('nb_frames', 0)), duracao=float(v['duration']))
res['audio'] = dict(codec=a['codec_name'], taxa=int(a['sample_rate']), canais=a['channels'], duracao=float(a['duration']))
res['arquivo'] = dict(duracao=float(pr['format']['duration']), tamanho_mb=round(int(pr['format']['size']) / 1e6, 2),
                      taxa_kbps=round(int(pr['format']['bit_rate']) / 1000))

# quadros pretos e congelados
bd = run(['ffmpeg', '-hide_banner', '-i', video, '-vf', 'blackdetect=d=0.05:pix_th=0.06', '-an', '-f', 'null', '-']).stderr
res['quadros_pretos'] = re.findall(r'black_start:\S+ black_end:\S+ black_duration:\S+', bd)
fz = run(['ffmpeg', '-hide_banner', '-i', video, '-vf', 'freezedetect=n=0.0005:d=1.5', '-an', '-f', 'null', '-']).stderr
res['congelamentos'] = re.findall(r'freeze_start: [\d.]+|freeze_duration: [\d.]+', fz)

# loudness
eb = run(['ffmpeg', '-hide_banner', '-i', video, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
summ = eb[eb.rfind('Summary:'):]
res['loudness'] = dict(integrado_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)),
                       lra_lu=float(re.search(r'LRA:\s+(-?[\d.]+) LU', summ).group(1)),
                       pico_real_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1)))

# legendas: ordem, sobreposição, limites e fidelidade ao roteiro
blocos = re.split(r'\n\s*\n', open(srt, encoding='utf-8').read().strip())
def ts(s): h, m, r = s.split(':'); s2, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(s2) + int(ms) / 1000
leg = []
for b in blocos:
    l = b.strip().split('\n'); i, f = [ts(x.strip()) for x in l[1].split('-->')]; leg.append((i, f, ' '.join(l[2:])))
probs = [f'#{k+1}' for k, (i, f, _) in enumerate(leg) if f <= i or (k and i < leg[k - 1][1]) or f > res['arquivo']['duracao']]
def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); return re.sub(r'[^a-z0-9 ]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))
roteiro = open(os.path.join(RAIZ, 'narracao/roteiro.txt'), encoding='utf-8').read()
res['legendas'] = dict(blocos=len(leg), problemas_tempo=probs, texto_identico_ao_roteiro=norm(' '.join(x[2] for x in leg)).split() == norm(roteiro).split(),
                       primeira=leg[0][0], ultima=leg[-1][1])

# integridade da narração: ASR sobre o áudio FINAL mixado
from faster_whisper import WhisperModel
pcm = run(['ffmpeg', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']).stdout if False else None
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
m = WhisperModel(modelo, device='cpu', compute_type='int8')
segs, _ = m.transcribe(audio, language='pt', beam_size=5, vad_filter=False)
hip = ' '.join(s.text.strip() for s in segs)
ref_w, hip_w = norm(roteiro).split(), norm(hip).split()
sm = difflib.SequenceMatcher(a=ref_w, b=hip_w, autojunk=False)
erros = sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal')
res['narracao'] = dict(palavras_roteiro=len(ref_w), wer_percent=round(100 * erros / len(ref_w), 1),
                       diferencas=[(' '.join(ref_w[i1:i2]), ' '.join(hip_w[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal'],
                       transcricao=hip)
json.dump(res, open(os.path.join(RAIZ, 'entrega/validacao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'narracao'}, ensure_ascii=False, indent=1))
print('WER narração:', res['narracao']['wer_percent'], '%', res['narracao']['diferencas'])
