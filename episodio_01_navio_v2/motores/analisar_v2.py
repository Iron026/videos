"""Analisa os benchmarks v2: SSIM de cada variante contra a referência de qualidade máxima do mesmo motor,
tabela de tempos e projeções, e folhas de comparação visual Cycles × tempo real (inteiro + detalhes).
Uso: python3 motores/analisar_v2.py
"""
import json, os, glob
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(AQUI, 'resultados_v2'); RAIZ = os.path.dirname(AQUI)
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; F2 = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
AZUL, BRANCO, AMARELO = (32, 43, 87), (246, 244, 236), (243, 181, 68)


def carregar(p, tam=None):
    im = Image.open(p).convert('RGB')
    if tam and im.size != tam: im = im.resize(tam, Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255.0


def ssim(a, b):
    """SSIM (Wang et al. 2004) na luminância, janela gaussiana σ = 1,5."""
    ya = a @ [0.299, 0.587, 0.114]; yb = b @ [0.299, 0.587, 0.114]
    C1, C2 = 0.01 ** 2, 0.03 ** 2; g = lambda x: gaussian_filter(x, 1.5)
    ma, mb = g(ya), g(yb); va = g(ya * ya) - ma ** 2; vb = g(yb * yb) - mb ** 2; cab = g(ya * yb) - ma * mb
    return float((((2 * ma * mb + C1) * (2 * cab + C2)) / ((ma ** 2 + mb ** 2 + C1) * (va + vb + C2))).mean())


def tabela_rt():
    linhas = []
    for q in (2, 3):
        ref = os.path.join(R, f'rt_q{q}_ref_ultimo.png')
        if not os.path.exists(ref): continue
        A = carregar(ref)
        for f in sorted(glob.glob(os.path.join(R, f'rt_q{q}_*.json'))):
            d = json.load(open(f)); nome = os.path.basename(f)[len(f'rt_q{q}_'):-5]
            img = f.replace('.json', '_ultimo.png')
            s = ssim(A, carregar(img, (A.shape[1], A.shape[0])))
            linhas.append(dict(quadro=q, variante=nome, ms=d['render_mediana_ms'], primeiro_ms=d['primeiro_ms'], ssim=s, W=d['info']['W'], H=d['info']['H']))
    return linhas


def tabela_cycles():
    p = os.path.join(R, 'cycles_q3', 'cycles.json')
    if not os.path.exists(p): return []
    d = json.load(open(p)); ref = carregar(os.path.join(R, 'cycles_q3', 'ref128.png')); out = []
    for v in d:
        img = os.path.join(R, 'cycles_q3', v['nome'] + '.png')
        out.append(dict(variante=v['nome'], tempos=v['tempos_s'], ssim=ssim(ref, carregar(img, (ref.shape[1], ref.shape[0]))), W=v['W'], H=v['H']))
    return out


def folha(q, cycles_png, rt_png, saida, recortes):
    w, h = 540, 960; fn = ImageFont.truetype(F, 26); fs = ImageFont.truetype(F2, 21)
    a = Image.open(cycles_png).convert('RGB'); b = Image.open(rt_png).convert('RGB').resize(a.size, Image.LANCZOS)
    nr = len(recortes); cw = 2 * w + 10
    tot_h = 80 + h + 20 + nr * (60 + int(w * 0.75)) + 20
    c = Image.new('RGB', (cw + 20, tot_h), AZUL); d = ImageDraw.Draw(c)
    for i, (im, t, sub) in enumerate(((a, 'Cycles · 128 amostras', 'referência de qualidade'), (b, 'Tempo real v2 · Three.js', 'mesma cena, câmera e luz'))):
        x = 10 + i * (w + 10); c.paste(im.resize((w, h), Image.LANCZOS), (x, 80)); d.text((x + 4, 8), t, font=fn, fill=BRANCO); d.text((x + 4, 44), sub, font=fs, fill=AMARELO)
    y = 80 + h + 20
    for (titulo, caixa) in recortes:
        d.text((14, y + 14), 'Detalhe ampliado · ' + titulo, font=fn, fill=BRANCO); y += 60
        for i, im in enumerate((a, b)):
            cr = im.crop(caixa).resize((w, int(w * 0.75)), Image.LANCZOS); c.paste(cr, (10 + i * (w + 10), y))
        y += int(w * 0.75)
    c.save(saida, quality=90)


if __name__ == '__main__':
    rt = tabela_rt(); cy = tabela_cycles()
    json.dump(dict(tempo_real=rt, cycles=cy), open(os.path.join(R, 'analise.json'), 'w'), indent=1)
    for l in rt: print(f"RT  Q{l['quadro']} {l['variante']:8s} {l['W']}x{l['H']}  {l['ms']/1000:6.2f} s/quadro  SSIM {l['ssim']:.4f}")
    for l in cy: print(f"CY  Q3 {l['variante']:12s} {l['W']}x{l['H']}  {l['tempos']} s  SSIM {l['ssim']:.4f}")
    finais = {2: os.path.join(RAIZ, 'etapa_c0', 'quadros', 'quadro2_v3.png'), 3: os.path.join(RAIZ, 'etapa_c1', 'quadros', 'quadro3_v3b.png')}
    recortes = {2: [('proa e cavernas', (0, 900, 640, 1380)), ('pórtico, cabo e painel', (560, 380, 1080, 770)), ('chão e sombras', (120, 1450, 760, 1930))],
                3: [('linha d\'água e porão', (60, 860, 700, 1340)), ('água e leito', (420, 1050, 1080, 1545)), ('superfície do mar', (0, 330, 640, 810))]}
    for q in (2, 3):
        rtp = os.path.join(R, f'rt_q{q}_ref.png')
        if os.path.exists(rtp): folha(q, finais[q], rtp, os.path.join(R, f'comparacao_q{q}.jpg'), recortes[q]); print('folha', q)
