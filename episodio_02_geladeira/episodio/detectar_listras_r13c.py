"""Detector de listras horizontais (z-fighting bobina × estator) em tons de cobre/amarelo: energia de 2ª diferença
VERTICAL muito maior que a HORIZONTAL (listras são linhas horizontais de 1–2 px), só em pixels cor de cobre/tampa."""
import sys, os, json, numpy as np
from PIL import Image
def medir(f):
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]; L = 0.3 * R + 0.59 * G + 0.11 * B
    cor = (R > 100) & (B < 0.55 * R) & (G < 0.9 * R)
    v = np.abs(2 * L[1:-1, 1:-1] - L[:-2, 1:-1] - L[2:, 1:-1]); h = np.abs(2 * L[1:-1, 1:-1] - L[1:-1, :-2] - L[1:-1, 2:])
    m = cor[1:-1, 1:-1] & cor[:-2, 1:-1] & cor[2:, 1:-1] & (v > 10) & (v > 3 * h + 4)
    # só conta linhas horizontais: pelo menos 4 pixels vizinhos na mesma linha também marcados
    k = np.ones(5); run = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 1, m.astype(np.float32))
    return int(((run >= 4) & m).sum())
alvos = sys.argv[1:]
res = {}
for p in alvos:
    fs = [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith('.jpg')] if os.path.isdir(p) else [p]
    for f in fs: res[f] = medir(f)
print(json.dumps(res))
