"""Teste curto em 540 × 960 NATIVOS (mesma configuração do perfil 'revisao': AO 16, MSAA 4×, bloom 0,18) em instantes
escolhidos (segundos do episódio). Para avaliar materiais, detalhes e antisserrilhado sem render extenso.
Uso: python3 teste_nativo.py <saida.jpg> PLANO:t1,t2,... [PLANO:t ...]   (exporte a cena antes, se mudou)"""
import os, sys, json, subprocess
from PIL import Image, ImageDraw
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
saida = sys.argv[1]; tiles = []
tmp = os.path.join(os.path.dirname(os.path.abspath(saida)), '_nativo')
for spec in sys.argv[2:]:
    pid, ts = spec.split(':'); c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); g0 = c['g0']; n = len(c['animacao']['quadros'])
    for t in [float(x) for x in ts.split(',')]:
        i = max(0, min(n - 1, int(round((t - g0) * 30)))); out = os.path.join(tmp, pid)
        subprocess.run(['node', 'render_anim.mjs', f'cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala=0.5&aoamostras=16&msaa=4&bloom=0.18',
                        out, '1', str(i), str(i)], cwd=MOTOR, capture_output=True)
        im = Image.open(os.path.join(out, f'q{i:04d}.jpg')).convert('RGB'); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 120, 18], fill=(0, 0, 0)); d.text((4, 3), f'{pid} {t:.2f}s', fill=(255, 255, 0)); tiles.append(im)
w, h = tiles[0].size; cols = min(4, len(tiles)); rows = (len(tiles) + cols - 1) // cols
folha = Image.new('RGB', (cols * (w + 4), rows * (h + 4)), (40, 40, 40))
for k, im in enumerate(tiles): folha.paste(im, ((k % cols) * (w + 4), (k // cols) * (h + 4)))
folha.save(saida, quality=88); print('folha', saida, folha.size)
