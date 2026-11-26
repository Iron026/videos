"""Verificação do vídeo montado: quadros consecutivos quase idênticos (congelamento / fps efetivo baixo) e trechos com
padrão alternado (repete, avança 2) — assinatura de arredondamento de empate. Uso: python3 detectar_quadros_repetidos.py <video.mp4>
Cena realmente parada também aparece: conferir os trechos listados (o padrão ALTERNADO é o que indica defeito)."""
import sys, subprocess
import numpy as np
f = sys.argv[1]; W, H = 270, 480
r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
a = np.frombuffer(r, np.uint8).reshape(-1, H, W).astype(np.float32); d = np.abs(np.diff(a, axis=0)).reshape(len(a) - 1, -1).mean(1)
rep = d < 0.15; print(f'{len(a)} quadros; pares quase idênticos: {int(rep.sum())}')
k = 0; alt = []
while k < len(rep) - 6:
    w = rep[k:k + 6]
    if w.sum() == 3 and (all(w[0::2]) and not any(w[1::2]) or all(w[1::2]) and not any(w[0::2])):
        j = k
        while j < len(rep) - 2 and rep[j] != rep[j + 1]: j += 1
        alt.append((k, j)); k = j + 1
    else: k += 1
for s, e in alt: print(f'  padrão ALTERNADO (repete/avança) nos quadros {s}–{e + 1} ({s / 30:.2f}–{(e + 1) / 30:.2f} s)')
print(f'{len(alt)} trecho(s) com padrão alternado')
