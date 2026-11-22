"""A/B dos principais trechos sonoros, com a NARRAÇÃO NO MESMO NÍVEL nos dois lados:
 A = só narração (mesma cópia comprimida da voz, mesmo ganho de master: `som_ep02.py --sem-efeitos` com MASTER_FIXO_DB)
 B = mixagem completa (voz + efeitos + mecanismo + ambiências).
Para cada trecho: um .mp4 com a imagem da V5 tocando A e depois B (rótulo no canto), e medidas por trecho
(LUFS da voz — deve ser igual em A e B —, LUFS total, voz − resto no celular simulado).
Uso: python3 ab_som.py <video_v5.mp4>  → som/ab/*.mp4 + som/ab/ab_trechos.json   (medido, não escutado)"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
A = os.path.dirname(os.path.abspath(__file__)); SR = 48000; OUT = os.path.join(A, 'ab'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, A)
from scipy.signal import lfilter
def lufs(x):  # mesma medida ITU-R BS.1770 de validar_audio.py (copiada: aquele script executa ao ser importado)
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    y = lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0); w = int(0.4 * SR); h = int(0.1 * SR)
    p = np.array([np.mean(y[i:i + w] ** 2, 0).sum() for i in range(0, len(y) - w, h)]); l = -0.691 + 10 * np.log10(p + 1e-12)
    g = l > -70
    if not g.any(): return -99.0
    l1 = -0.691 + 10 * np.log10(p[g].mean() + 1e-12); g2 = g & (l > l1 - 10)
    return -0.691 + 10 * np.log10(p[g2].mean() + 1e-12)
TRECHOS = [('abertura', 0.0, 10.5), ('revelacao', 28.0, 38.5), ('compressor', 74.0, 87.0), ('capilar', 101.8, 107.6),
           ('porta_aberta', 115.0, 124.5), ('final', 145.0, 151.2)]
video = sys.argv[1]
mixB = sf.read(os.path.join(A, 'audio_ep02.wav'))[0]; mixA = sf.read(os.path.join(A, 'audio_ep02_sem_efeitos.wav'))[0]
st = os.path.join(A, 'stems'); voz = sf.read(os.path.join(st, 'ep02_voz.wav'))[0]; vozA = sf.read(os.path.join(st, 'ep02_voz_sem_efeitos.wav'))[0]
resto = sum(sf.read(os.path.join(st, f'ep02_{k}.wav'))[0] for k in ('efeitos', 'mecanismo', 'ambiencias'))
cel = lambda x: sosfiltfilt(butter(4, [350, 7000], 'bandpass', fs=SR, output='sos'), x)
FONTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; res = []
for nome, t0, t1 in TRECHOS:
    i0, i1 = int(t0 * SR), int(t1 * SR); r = dict(trecho=nome, ini=t0, fim=t1)
    r['lufs_voz_A'] = round(lufs(vozA[i0:i1]), 2); r['lufs_voz_B'] = round(lufs(voz[i0:i1]), 2)
    r['lufs_total_A'] = round(lufs(mixA[i0:i1]), 2); r['lufs_total_B'] = round(lufs(mixB[i0:i1]), 2)
    vc, rc = cel(voz[i0:i1].mean(1)), cel(resto[i0:i1].mean(1)); w = int(0.4 * SR); d = []
    for i in range(0, len(vc) - w, w):
        ev = 10 * np.log10((vc[i:i + w] ** 2).mean() + 1e-12); er = 10 * np.log10((rc[i:i + w] ** 2).mean() + 1e-12)
        if ev > -45: d.append(ev - er)
    r['voz_menos_resto_celular_db'] = dict(pior=round(min(d), 1), mediana=round(float(np.median(d)), 1)) if d else None
    r['lufs_resto_B'] = round(lufs(resto[i0:i1]), 2) if np.abs(resto[i0:i1]).max() > 1e-6 else None
    partes = []
    for lado, mix in (('A', mixA), ('B', mixB)):
        wav = os.path.join(OUT, f'_{nome}_{lado}.wav'); sf.write(wav, mix[i0:i1].astype(np.float32), SR, subtype='PCM_24')
        rot = 'A  só narração' if lado == 'A' else 'B  mixagem completa'; mp = os.path.join(OUT, f'_{nome}_{lado}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-t', str(t1 - t0), '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a',
                        '-vf', f"drawbox=x=0:y=0:w=iw:h=44:color=black@0.7:t=fill,drawtext=fontfile={FONTE}:text='{rot}':x=12:y=12:fontsize=22:fontcolor=yellow",
                        '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '256k', '-ar', str(SR), mp], check=True)
        partes.append(mp)
    lst = os.path.join(OUT, f'_{nome}.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in partes))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(OUT, f'ab_{nome}.mp4')], check=True)
    for p in partes + [lst] + [p.replace('.mp4', '.wav') for p in partes]: os.remove(p)
    res.append(r); print(json.dumps(r, ensure_ascii=False))
json.dump(res, open(os.path.join(OUT, 'ab_trechos.json'), 'w'), ensure_ascii=False, indent=1)
