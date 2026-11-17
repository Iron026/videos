"""Validação técnica do animatic. Uso: python3 animatic/validar_animatic.py → animatic/validacao_animatic.json"""
import json, os, re, subprocess
import numpy as np

A = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(A, 'animatic_ep01.mp4')
def run(c): return subprocess.run(c, capture_output=True, text=True)
pr = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', V]).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); a = next(s for s in pr['streams'] if s['codec_type'] == 'audio')
n, d = map(int, v['r_frame_rate'].split('/'))
res = dict(video=dict(codec=v['codec_name'], largura=v['width'], altura=v['height'], fps=n / d, quadros=int(v.get('nb_frames', 0)), duracao=float(v['duration'])),
           audio=dict(codec=a['codec_name'], taxa=int(a['sample_rate']), canais=a['channels'], duracao=float(a['duration'])),
           tamanho_mb=round(int(pr['format']['size']) / 1e6, 2))
bd = run(['ffmpeg', '-hide_banner', '-i', V, '-vf', 'blackdetect=d=0.05:pix_th=0.06', '-an', '-f', 'null', '-']).stderr
res['quadros_pretos'] = re.findall(r'black_start:\S+ black_end:\S+', bd)
fz = run(['ffmpeg', '-hide_banner', '-i', V, '-vf', 'freezedetect=n=0.0005:d=1.0', '-an', '-f', 'null', '-']).stderr
res['congelamentos'] = re.findall(r'freeze_start: [\d.]+|freeze_duration: [\d.]+', fz)
eb = run(['ffmpeg', '-hide_banner', '-i', V, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr; sm = eb[eb.rfind('Summary:'):]
res['loudness'] = dict(integrado_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', sm).group(1)), pico_real_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', sm).group(1)))
# sincronia da voz real: palavras da amostra no áudio final (previsto: "De" em 15,20 s; "O invisível" em 17,10 s)
from faster_whisper import WhisperModel
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
au = np.frombuffer(raw, dtype=np.float32)
segs, _ = WhisperModel(os.environ.get('WHISPER_MODELO', '/tmp/claude-0/asr/m'), device='cpu', compute_type='int8').transcribe(au, language='pt', beam_size=5, word_timestamps=True)
pal = [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for s in segs for w in s.words]
res['voz'] = dict(transcricao=' '.join(p[0] for p in pal), palavras=pal)
ini = next((p[1] for p in pal if p[0].lower().startswith('de')), None)
res['voz']['inicio_detectado_s'] = ini; res['voz']['inicio_previsto_s'] = 15.20
res['voz']['desvio_ms'] = None if ini is None else round((ini - 15.20) * 1000)
json.dump(res, open(os.path.join(A, 'validacao_animatic.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
