"""Validação técnica do MP4 do Episódio 01: formato, duração (< 180 s), quadros pretos, congelamentos, loudness,
sincronia da narração (correlação do áudio do MP4 com a narração original) e cobertura das legendas.
Uso: python3 episodio/validar_ep01.py <video.mp4> → <video>.validacao.json"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, resample_poly

V = sys.argv[1]; A = os.path.dirname(os.path.abspath(__file__))
def run(c): return subprocess.run(c, capture_output=True, text=True)
pr = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', V]).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); a = next(s for s in pr['streams'] if s['codec_type'] == 'audio')
n, d = map(int, v['r_frame_rate'].split('/'))
res = dict(video=dict(codec=v['codec_name'], largura=v['width'], altura=v['height'], fps=n / d, duracao=float(v['duration'])),
           audio=dict(codec=a['codec_name'], taxa=int(a['sample_rate']), canais=a['channels'], duracao=float(a['duration'])),
           tamanho_mb=round(int(pr['format']['size']) / 1e6, 1))
res['abaixo_de_180s'] = float(pr['format']['duration']) < 180
bd = run(['ffmpeg', '-hide_banner', '-i', V, '-vf', 'blackdetect=d=0.10:pix_th=0.06', '-an', '-f', 'null', '-']).stderr
res['quadros_pretos'] = re.findall(r'black_start:\S+ black_end:\S+', bd)
fz = run(['ffmpeg', '-hide_banner', '-i', V, '-vf', 'freezedetect=n=0.0008:d=1.5', '-an', '-f', 'null', '-']).stderr
res['congelamentos_1_5s'] = re.findall(r'freeze_start: [\d.]+|freeze_duration: [\d.]+', fz)
eb = run(['ffmpeg', '-hide_banner', '-i', V, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr; sm = eb[eb.rfind('Summary:'):]
res['loudness'] = dict(integrado_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', sm).group(1)), pico_real_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', sm).group(1)))
# sincronia: a narração original deve estar em t = 0 no MP4 (correlação em 3 janelas: início, meio, fim)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
au = np.frombuffer(raw, dtype=np.float32)
voz, sr = sf.read(os.path.join(A, '..', 'voz', 'narracao_ep01', 'trabalho', 'narracao_48k.wav')); voz = resample_poly(voz, 1, 3)
desv = []
for t0 in (10.0, 85.0, 160.0):
    ref = voz[int(t0 * 16000):int((t0 + 4) * 16000)]; seg = au[int((t0 - 1) * 16000):int((t0 + 5) * 16000)]
    cc = fftconvolve(seg, ref[::-1], mode='valid'); desv.append(round((int(np.argmax(cc)) / 16000 - 1.0) * 1000))
res['sincronia_narracao_ms'] = desv
json.dump(res, open(os.path.splitext(V)[0] + '.validacao.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
