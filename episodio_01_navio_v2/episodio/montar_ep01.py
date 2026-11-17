"""Monta o Episódio 01 no tempo GLOBAL da narração real: segmentos renderizados (motor v2), fusões curtas nas
emendas, rótulos da marca projetados por quadro (rotulos2d.json), legendas alinhadas com as palavras reais
(palavras.json), assinatura animada e áudio (audio_ep01.wav) com loudness −14 LUFS / −1,5 dBTP.
Uso: python3 episodio/montar_ep01.py <previa|revisao|final> [saida.mp4]"""
import os, sys, json, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..')
PERFIL = sys.argv[1] if len(sys.argv) > 1 else 'previa'
W, H = {'previa': (540, 960), 'revisao': (1080, 1920), 'final': (1080, 1920)}[PERFIL]
PASSO = 3 if PERFIL == 'previa' else 1
FPS = 30; DUR = 171.0; ESC = W / 1080
SAIDA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, f'ep01_{PERFIL}.mp4')
FONTE = os.path.join(RAIZ, 'fontes')
F_LEG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(58 * ESC))
F_ROT = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(36 * ESC))
F_TAG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), int(26 * ESC))
AZUL, CREME, AMARELO, ESCURO = (32, 43, 87), (246, 244, 236), (243, 181, 68), (16, 22, 46)

# (nome, início, fim) no tempo global; 's01' = plano 1 aprovado do animatic r2; 'ass' = assinatura
SEGS = [('s01', 0.00, 4.40), ('s02', 4.40, 15.10), ('s03', 15.10, 30.30), ('s04', 30.30, 41.55), ('s05', 41.55, 48.00),
        ('s0607', 48.00, 74.85), ('s08a', 74.85, 83.85), ('s08b', 83.85, 94.55), ('s09', 94.55, 117.20), ('s10', 117.20, 123.65),
        ('s11', 123.65, 134.00), ('s12', 134.00, 154.60), ('s13', 154.60, 166.30), ('ass', 166.20, DUR)]
FUSAO = 0.20


def pasta(nome):
    if nome == 's01': return os.path.join(RAIZ, 'animatic', 'quadros_r2_p1'), 1
    if nome == 'ass': return os.path.join(A, 'assinatura_q'), 1
    return os.path.join(A, f'quadros_{PERFIL}', nome), PASSO


_cache = {}
def quadro_seg(nome, g0, g):
    d, passo = pasta(nome)
    if d not in _cache: _cache[d] = sorted(int(f[1:5]) for f in os.listdir(d) if f.endswith('.jpg'))
    idx = _cache[d]; f = int(round((g - g0) * FPS)); f = min(max(f, idx[0]), idx[-1])
    f = idx[int(np.searchsorted(idx, f, side='right')) - 1]
    return Image.open(os.path.join(d, f'q{f:04d}.jpg')).convert('RGB').resize((W, H), Image.BICUBIC)


ROT = {}
def rotulos(nome, g0, g):
    if nome in ('s01', 'ass'): return []
    if nome not in ROT:
        p = os.path.join(A, 'cenas', nome, 'rotulos2d.json'); ROT[nome] = json.load(open(p))['quadros'] if os.path.exists(p) else []
    q = ROT[nome]; f = int(round((g - g0) * FPS))
    return q[f] if 0 <= f < len(q) else []


def desenhar_rotulo(img, txt, u, v, a, dx, dy):
    if a <= 0.01: return
    camada = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(camada)
    ax, ay = u * W, v * H; bx, by = ax + dx * W, ay + dy * H
    tw = d.textlength(txt, font=F_ROT); pad = 16 * ESC; h = 36 * ESC + 2 * pad * 0.55
    w = tw + 2 * pad
    lx = bx if dx >= 0 else bx - w; lx = min(max(lx, 0.04 * W), 0.96 * W - w)
    ly = min(max(by - h / 2, 0.09 * H), 0.60 * H - h)
    ex = min(max(ax, lx), lx + w); ey = ly + h / 2
    al = int(255 * a)
    d.line([(ax, ay), (ex, ey)], fill=CREME + (al,), width=max(2, int(4 * ESC)))
    r = 9 * ESC; d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
    d.rounded_rectangle([lx, ly, lx + w, ly + h], radius=h / 2, fill=AZUL + (int(240 * a),))
    d.rounded_rectangle([lx + h * 0.3, ly + h - 5 * ESC, lx + w - h * 0.3, ly + h], radius=2, fill=AMARELO + (al,))
    d.text((lx + pad, ly + h / 2), txt, font=F_ROT, fill=CREME + (al,), anchor='lm')
    img.paste(Image.alpha_composite(img.convert('RGBA'), camada).convert('RGB'))


def legendas():
    p = json.load(open(os.path.join(RAIZ, 'voz', 'narracao_ep01', 'trabalho', 'palavras.json')))
    blocos, cur = [], []
    for i, w in enumerate(p):
        cur.append(w)
        txt = ' '.join(x['palavra'] for x in cur); fim_frase = w['palavra'][-1] in '.?!:;,'
        prox = p[i + 1] if i + 1 < len(p) else None
        pausa = prox is not None and prox['inicio'] - w['fim'] > 0.30
        longo = (prox is not None and len(txt + ' ' + prox['palavra']) > 26) or (w['fim'] - cur[0]['inicio']) > 2.2
        if prox is None or fim_frase or pausa or longo:
            blocos.append([cur[0]['inicio'], w['fim'], txt]); cur = []
    for i in range(len(blocos)):
        nxt = blocos[i + 1][0] if i + 1 < len(blocos) else DUR
        blocos[i][1] = min(blocos[i][1] + 0.25, nxt)
        blocos[i][2] = re.sub(r'[.,:;]+$', '', blocos[i][2])
    return [b for b in blocos if b[0] < 166.3]
LEG = legendas()


def compor(g):
    ativos = [(n, a, b) for n, a, b in SEGS if a - FUSAO / 2 <= g < b + FUSAO / 2]
    if len(ativos) == 1: n, a, b = ativos[0]; img = quadro_seg(n, a, g); rots = [(n, a, 1.0)]
    else:
        (n1, a1, b1), (n2, a2, b2) = ativos[0], ativos[1]
        k = min(1.0, max(0.0, (g - (a2 - FUSAO / 2)) / FUSAO))
        img = Image.blend(quadro_seg(n1, a1, g), quadro_seg(n2, a2, g), k); rots = [(n1, a1, 1 - k), (n2, a2, k)]
    for (n, a, k) in rots:
        for (txt, u, v, al, dx, dy) in rotulos(n, a, g): desenhar_rotulo(img, txt, u, v, al * k, dx, dy)
    d = ImageDraw.Draw(img)
    for (a, b, txt) in LEG:
        if a <= g < b:
            d.text((W // 2, int(0.70 * H)), txt, font=F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * ESC)), stroke_fill=ESCURO, anchor='mm')
    if g < 166.2:
        tag = 'VERSÃO DE REVISÃO · não publicar'; x0, y0 = int(30 * ESC), int(70 * ESC); tw = d.textlength(tag, font=F_TAG)
        d.rounded_rectangle((x0, y0, x0 + tw + 36 * ESC, y0 + 46 * ESC), radius=23 * ESC, fill=AZUL)
        d.text((x0 + 18 * ESC, y0 + 23 * ESC), tag, font=F_TAG, fill=CREME, anchor='lm')
    return img


def loudness(au):
    tmp = os.path.join(A, '_teste.m4a')
    def filtro(g): return f'volume={g:.2f}dB,alimiter=limit=-2.2dB:attack=3:release=60:level=disabled:asc=1'
    def medir(g):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', au, '-af', filtro(g), '-c:a', 'aac', '-b:a', '192k', tmp], check=True)
        e = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
        return float(re.search(r'I:\s+(-?[\d.]+) LUFS', e[e.rfind('Summary:'):]).group(1))
    g = 0.0
    for _ in range(4):
        i = medir(g)
        if abs(i + 14) < 0.15: break
        g += -14 - i
    os.remove(tmp); print('ganho', round(g, 2), 'dB →', i, 'LUFS'); return filtro(g)


if __name__ == '__main__':
    au = os.path.join(A, 'audio_ep01.wav'); af = loudness(au)
    n = int(round(DUR * FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', au, '-af', af, '-c:v', 'libx264', '-preset', 'medium', '-crf', '20' if PERFIL != 'final' else '17',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                           '-metadata', 'title=De Olho no Invisível · Ep. 01 · versão de revisão (não publicar)', SAIDA], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(compor(i / FPS).tobytes())
        if i % 300 == 0: print('quadro', i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', SAIDA)
