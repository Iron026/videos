"""Pré-visualização rápida de câmera: exporta os planos pedidos e renderiza 4 quadros de cada (10/37/63/90 %) em 270×480.
Barata (sem render completo) e com a MESMA configuração do animatic. Uso:
python3 prever.py <saida.jpg> [--sem-exportar] PLANO [PLANO ...]"""
import os, sys, json, subprocess, time
from PIL import Image, ImageDraw
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); MOTOR = os.path.join(RAIZ, 'motor')
saida = sys.argv[1]; args = sys.argv[2:]; exportar = '--sem-exportar' not in args; ids = [a for a in args if not a.startswith('--')]
if exportar:
    t = time.time(); env = dict(os.environ, PYTHONPATH='/home/user/bpy_site')
    r = subprocess.run(['python3', os.path.join(RAIZ, 'blender', 'episodio02.py')] + ids, env=env, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2500:]); sys.exit(1)
    print(f'exportação {time.time() - t:.0f} s', flush=True)
tmp = os.path.join(os.path.dirname(os.path.abspath(saida)), '_prev'); linhas = []
for pid in ids:
    c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); n = len(c['animacao']['quadros'])
    idx = [int(n * f) for f in (0.10, 0.37, 0.63, 0.90)]; out = os.path.join(tmp, pid); os.makedirs(out, exist_ok=True)
    q = f'cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala=0.25&aoamostras=8&msaa=4'
    ims = []; passo = idx[1] - idx[0]; idx = [idx[0] + k * passo for k in range(4)]
    subprocess.run(['node', 'render_anim.mjs', q, out, str(passo), str(idx[0]), str(idx[3])], cwd=MOTOR, capture_output=True, text=True)
    for i in idx:
        im = Image.open(os.path.join(out, f'q{i:04d}.jpg')).convert('RGB'); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 14], fill=(0, 0, 0)); d.text((3, 1), f"{pid} {c['g0'] + i / 30:.1f}s", fill=(255, 255, 0)); ims.append(im)
    w, h = ims[0].size; row = Image.new('RGB', (4 * w + 6, h), (40, 40, 40))
    for k, im in enumerate(ims): row.paste(im, (k * (w + 2), 0))
    linhas.append(row); print(pid, 'ok', flush=True)
W, H = linhas[0].size; cols = 2 if len(linhas) > 2 else 1; rows = (len(linhas) + cols - 1) // cols
folha = Image.new('RGB', (cols * W + (cols - 1) * 12, rows * H), (90, 90, 90))
for i, r in enumerate(linhas): folha.paste(r, ((i % cols) * (W + 12), (i // cols) * H))
folha.save(saida, quality=85); print('folha', saida, folha.size)
