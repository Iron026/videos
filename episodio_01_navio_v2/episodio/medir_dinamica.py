"""Mede a dinâmica visual de uma prévia: compara cada quadro com o de 3 s antes (SSIM em tons de cinza, 90×160, área sem
legendas). Janelas com SSIM > 0,80 = 3 s sem mudança visual significativa. Uso: python3 medir_dinamica.py video.mp4"""
import sys, subprocess, numpy as np
from scipy.ndimage import uniform_filter
def ssim(a, b, data_range=255):
    C1, C2 = (0.01 * data_range) ** 2, (0.03 * data_range) ** 2
    ma, mb = uniform_filter(a, 7), uniform_filter(b, 7)
    va = uniform_filter(a * a, 7) - ma * ma; vb = uniform_filter(b * b, 7) - mb * mb; cv = uniform_filter(a * b, 7) - ma * mb
    return float((((2 * ma * mb + C1) * (2 * cv + C2)) / ((ma ** 2 + mb ** 2 + C1) * (va + vb + C2))).mean())
V = sys.argv[1]; w, h, fps = 90, 160, 5
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', V, '-vf', f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
q = np.frombuffer(raw, np.uint8).reshape(-1, h, w)[:, int(h * 0.09):int(h * 0.64), :].astype(float)
lag = 3 * fps; s = np.array([ssim(q[i], q[i - lag], data_range=255) for i in range(lag, len(q))])
t = np.arange(lag, len(q)) / fps
est = t[(s > 0.80) & (t < 166.2)]
blocos = []
for x in est:
    if blocos and x - blocos[-1][1] <= 0.25: blocos[-1][1] = x
    else: blocos.append([x, x])
print(f'{V}: janelas de 3 s sem mudança significativa = {len(est) / fps:.1f} s de {166.2 - 3:.0f} s; SSIM médio 3 s = {s[t < 166.2].mean():.3f}')
print('trechos (fim da janela):', [(round(a - 3, 1), round(b, 1)) for a, b in blocos if b - a >= 0.6])
