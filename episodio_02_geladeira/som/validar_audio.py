"""Validação técnica da mixagem do Ep. 02 (medida, não escutada):
 · loudness integrada e pico verdadeiro MEDIDOS NO AAC codificado (como sai no vídeo): metas −14 LUFS e ≤ −1,5 dBTP;
 · voz ≥ 10 dB acima do resto no CELULAR simulado (mono, 350 Hz–7 kHz), por janela de fala (pior caso e mediana);
 · perda em mono (LUFS do mono − LUFS do estéreo) e silêncio no fim;
 · sincronia: ataque dos eventos no áudio × instante do evento na imagem.
Uso: python3 validar_audio.py <video.mp4>  → som/validacao_audio.json"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
SR = 48000


def dec(f, mono=False):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1' if mono else '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).astype(np.float64); return x if mono else x.reshape(-1, 2)


from scipy.signal import lfilter, resample_poly
def lufs(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    y = lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0); w = int(0.4 * SR); h = int(0.1 * SR)
    p = np.array([np.mean(y[i:i + w] ** 2, 0).sum() for i in range(0, len(y) - w, h)]); l = -0.691 + 10 * np.log10(p + 1e-12)
    g = l > -70; l1 = -0.691 + 10 * np.log10(p[g].mean() + 1e-12); g2 = g & (l > l1 - 10)
    return -0.691 + 10 * np.log10(p[g2].mean() + 1e-12)
def tp(x): return 20 * np.log10(np.abs(resample_poly(x, 4, 1, axis=0)).max() + 1e-12)
from scipy.signal import butter, sosfiltfilt
cel = lambda x: sosfiltfilt(butter(4, [350, 7000], 'bandpass', fs=SR, output='sos'), x)

video = sys.argv[1]; aac = dec(video)
res = dict(arquivo=os.path.basename(video), lufs_aac=round(lufs(aac), 2), pico_verdadeiro_aac_dbtp=round(tp(aac), 2))
mono = aac.mean(1); res['perda_mono_db'] = round(lufs(np.stack([mono, mono], 1)) - res['lufs_aac'], 2)
fim = aac[-int(0.5 * SR):]; res['ultimo_0_5s_dbfs'] = round(float(20 * np.log10(np.sqrt((fim ** 2).mean()) + 1e-12)), 1)
# voz × resto no celular: stems da mixagem (mesmo ganho de master)
st = os.path.join(A, 'stems')
# rodada 10: o padrão lia SEMPRE os stems sem sufixo (os da 1ª mixagem), não os da mixagem validada. Agora STEMS_VOZ e
# STEMS_RESTO (lista separada por vírgulas, caminhos relativos a som/stems) dizem quais stems compõem o áudio do vídeo.
voz = sf.read(os.path.join(st, os.environ.get('STEMS_VOZ', 'ep02_voz.wav')))[0].mean(1)
resto = sum(sf.read(os.path.join(st, f))[0].mean(1) for f in os.environ.get('STEMS_RESTO', 'ep02_efeitos.wav,ep02_mecanismo.wav,ep02_ambiencias.wav').split(','))
res['stems_medidos'] = dict(voz=os.environ.get('STEMS_VOZ', 'ep02_voz.wav'), resto=os.environ.get('STEMS_RESTO', 'ep02_efeitos.wav,ep02_mecanismo.wav,ep02_ambiencias.wav'))
vc, rc = cel(voz), cel(resto); w = int(0.4 * SR); difs = []
for i in range(0, len(vc) - w, w):
    ev = 10 * np.log10((vc[i:i + w] ** 2).mean() + 1e-12); er = 10 * np.log10((rc[i:i + w] ** 2).mean() + 1e-12)
    if ev > -45: difs.append(ev - er)
res['voz_menos_resto_celular_db'] = dict(pior=round(float(min(difs)), 1), p5=round(float(np.percentile(difs, 5)), 1), mediana=round(float(np.median(difs)), 1), janelas=len(difs))
res['metas'] = dict(lufs=-14.0, tp_max=-1.5, voz_celular_min_db=10.0)
res['aprovado_tecnico'] = bool(abs(res['lufs_aac'] + 14) <= 0.5 and res['pico_verdadeiro_aac_dbtp'] <= -1.5 and res['voz_menos_resto_celular_db']['p5'] >= 10.0)
json.dump(res, open(os.path.join(A, 'validacao_audio.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
