"""Folha de contato dos planos: 3 quadros por plano (2 %, 50 %, 98 % do plano), resolução baixa. Uso:
python3 folha_contato.py <escala> <saida.jpg> [planos...]   (renderiza em quadros_contato/)"""
import os, sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
esc = float(sys.argv[1]); saida = sys.argv[2]
sys.path.insert(0, os.path.join(A, '..', 'decupagem')); import planos as PL
P = PL.resolvidos()['planos']; ids = sys.argv[3:] or [p['id'] for p in P]
fonte = ImageFont.truetype(os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf'), 18)
tiles = []
for p in P:
    if p['id'] not in ids: continue
    cena = os.path.join(A, 'cenas', p['id']); m = json.load(open(os.path.join(cena, 'cena.json')))
    g0 = m['g0']; idx = [int(round((p['t0'] + (p['t1'] - p['t0']) * f - g0) * 30)) for f in (0.02, 0.5, 0.98)]
    out = os.path.join(A, 'quadros_contato', p['id'])
    if not all(os.path.exists(os.path.join(out, f'q{i:04d}.jpg')) for i in idx) or os.environ.get('REFAZER'):
        passo = max(1, (idx[2] - idx[0]) // 2)
        r = subprocess.run(['node', 'render_anim.mjs', f"cena=/episodio_02_geladeira/episodio/cenas/{p['id']}/&escala={esc}&aoamostras=8&msaa=4",
                            out, str(passo), str(idx[0]), str(idx[0] + 2 * passo)], cwd=MOTOR, capture_output=True, text=True)
        print(p['id'], r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-400:], flush=True)
        idx = [idx[0], idx[0] + passo, idx[0] + 2 * passo]
    ims = [Image.open(os.path.join(out, f'q{i:04d}.jpg')) for i in idx]
    w, h = ims[0].size; t = Image.new('RGB', (3 * w + 8, h + 30), (20, 22, 30))
    for k, im in enumerate(ims): t.paste(im, (k * (w + 4), 30))
    ImageDraw.Draw(t).text((6, 4), f"{p['id']}  {p['t0']:.1f}–{p['t1']:.1f}s  {p['narrado'][:48]}", font=fonte, fill=(246, 244, 236))
    tiles.append(t)
cols = 4; W, H = tiles[0].size; rows = (len(tiles) + cols - 1) // cols
folha = Image.new('RGB', (cols * W, rows * H), (10, 10, 14))
for i, t in enumerate(tiles): folha.paste(t, ((i % cols) * W, (i // cols) * H))
folha.save(saida, quality=85); print('folha', saida, folha.size)
