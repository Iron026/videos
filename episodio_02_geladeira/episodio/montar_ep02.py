"""Monta o Ep. 02 no tempo GLOBAL: planos renderizados (motor render3.js), fusões nas emendas, rótulos da marca
(rotulos2d.json), manômetros (manometros2d.json), avisos honestos, legendas pelas palavras (narração aprovada ou, sem ela,
tempos PROVISÓRIOS) e correção de cor sutil (grade.py, herdada do Ep. 01).
Perfis: animatic (270×480, 1 quadro a cada 2) · revisao (540×960) · final (1080×1920, CRF 17).
Sem narração aprovada: trilha silenciosa e selo "tempos provisórios". Uso: python3 montar_ep02.py <perfil> [saida.mp4]"""
import os, sys, json, re, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..')
sys.path.insert(0, os.path.join(RAIZ, 'decupagem')); import planos as PL
from grade import graduar
PERFIL = sys.argv[1] if len(sys.argv) > 1 else 'animatic'
W, H = {'animatic': (540, 960), 'revisao': (540, 960), 'final': (1080, 1920)}[PERFIL]   # animatic: quadros 270×480 ampliados
PASSO = 2 if PERFIL == 'animatic' else 1
FPS = 30; ESC = W / 1080
R = PL.resolvidos(); PLANOS = R['planos']; DUR = R['duracao']; PROVISORIO = 'aprovada' not in R['origem']
SAIDA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, f'ep02_{PERFIL}.mp4')
FONTE = os.path.join(RAIZ, 'fontes')
F_LEG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(58 * ESC))
F_ROT = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(44 * ESC))
F_TAG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), int(26 * ESC))
F_MAN = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), int(22 * ESC))
AZUL, CREME, AMARELO, ESCURO = (32, 43, 87), (246, 244, 236), (243, 181, 68), (16, 22, 46)
FUSAO = 0.20
FUSOES = {'B1': 0.30, 'C1': 0.30, 'C2': 0.0, 'D1': 0.30, 'E1': 0.30, 'F1': 0.30, 'I1': 0.30, 'J1': 0.30, 'J4': 0.40}   # fusão na ENTRADA do plano   # v3: C2 em corte SECO no ataque de "Escondido"
# avisos honestos (canto superior direito), por plano
def faixa(a, b, txt): return (PL_T[a][0], PL_T[b][1], txt)
PL_T = {p['id']: (p['t0'], p['t1']) for p in PLANOS}
CHIPS = [faixa('A2', 'A4', 'Visão térmica (ilustrativa)'), faixa('A3', 'A4', 'Corte ilustrativo'), faixa('B4', 'B7', 'Visão térmica (ilustrativa)'),
         faixa('B5', 'B7', 'Tempo acelerado'), faixa('C2', 'H2', 'Corte ilustrativo'), faixa('D4', 'D4', 'Fluxo desacelerado'),
         faixa('F2', 'F2', 'Fluxo desacelerado'), faixa('D4', 'D4', 'Canal ampliado (esquema)'), faixa('F2', 'F2', 'Canal ampliado (esquema)'), faixa('G3', 'G3', 'Fluxo desacelerado'), faixa('E3', 'E3', 'Câmera lenta'),
         faixa('I3', 'I4', 'Corte ilustrativo'), faixa('J1', 'J1', 'Visão térmica (ilustrativa)'), faixa('J3', 'J3', 'Corte ilustrativo')]


def pasta(pid): return os.path.join(A, f'quadros_{PERFIL}', pid)
_idx = {}; _meta = {}
def meta(pid):
    if pid not in _meta:
        c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); _meta[pid] = c['g0']
    return _meta[pid]


DIVIDIDA = {'A4': 'A4b', 'J1': 'J1b'}
def quadro(pid, g):
    if pid in DIVIDIDA and os.path.isdir(pasta(DIVIDIDA[pid])):
        a, b = quadro_simples(pid, g), quadro_simples(DIVIDIDA[pid], g)
        t0, t1 = PL_T[pid]; k = min(1.0, max(0.0, (g - t0 - 0.10 * (t1 - t0)) / 0.8)); k = k * k * (3 - 2 * k)
        if pid == 'A4': k *= 1.0 - min(1.0, max(0.0, (g - t0 - 0.80 * (t1 - t0)) / 0.6))   # A4 volta à frente inteira no fim
        x = int(W - (W / 2) * k)
        if x >= W: return a
        im = Image.new('RGB', (W, H)); la = W // 2 - x // 2; lb = W // 2 - (W - x) // 2   # cada metade mostra o CENTRO da sua imagem
        im.paste(a.crop((la, 0, la + x, H)), (0, 0)); im.paste(b.crop((lb, 0, lb + (W - x), H)), (x, 0))
        ImageDraw.Draw(im).rectangle([x - max(1, int(3 * ESC)), 0, x + max(1, int(3 * ESC)), H], fill=CREME)
        return im
    return quadro_simples(pid, g)


def quadro_simples(pid, g):
    d = pasta(pid)
    if d not in _idx: _idx[d] = sorted(int(f[1:5]) for f in os.listdir(d) if f.endswith('.jpg'))
    idx = _idx[d]; f = int(round((g - meta(pid)) * FPS)); f = idx[max(0, int(np.searchsorted(idx, f, side='right')) - 1)]
    img = Image.open(os.path.join(d, f'q{f:04d}.jpg')).convert('RGB').resize((W, H), Image.BICUBIC)
    return graduar(img)


_dados = {}
def dados(pid, arq, g):
    k = (pid, arq)
    if k not in _dados:
        p = os.path.join(A, 'cenas', pid, arq); _dados[k] = json.load(open(p)) if os.path.exists(p) else dict(g0=0, quadros=[])
    d = _dados[k]; f = int(round((g - d['g0']) * FPS)); q = d['quadros']
    return q[f] if 0 <= f < len(q) else []


def rotulo(img, txt, u, v, a, dx, dy):
    if a <= 0.01: return
    cam = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam)
    ax, ay = u * W, v * H; bx, by = ax + dx * W, ay + dy * H
    tw = d.textlength(txt, font=F_ROT); pad = 20 * ESC; h = 44 * ESC + 2 * pad * 0.55; w = tw + 2 * pad
    lx = bx if dx >= 0 else bx - w; lx = min(max(lx, 0.04 * W), 0.96 * W - w); ly = min(max(by - h / 2, 0.09 * H), 0.62 * H - h)
    ex = min(max(ax, lx), lx + w); ey = ly + h / 2; al = int(255 * a)
    d.line([(ax, ay), (ex, ey)], fill=CREME + (al,), width=max(2, int(4 * ESC)))
    r = 11 * ESC; d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
    d.rounded_rectangle([lx, ly, lx + w, ly + h], radius=h / 2, fill=AZUL + (int(240 * a),))
    d.rounded_rectangle([lx + h * 0.3, ly + h - 5 * ESC, lx + w - h * 0.3, ly + h], radius=2, fill=AMARELO + (al,))
    d.text((lx + pad, ly + h / 2), txt, font=F_ROT, fill=CREME + (al,), anchor='lm')
    img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB'))


def manometro(img, nome, u, v, a, val, lado):
    """Mostrador neutro (creme/azul da marca): ponteiro de 'baixa' a 'alta' pressão. Sem números (comparação relativa)."""
    if a <= 0.01: return
    cam = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam); al = int(255 * a)
    R_ = 64 * ESC; cx = min(max(u * W + lado * 150 * ESC, R_ + 12 * ESC), W - R_ - 12 * ESC); cy = min(max(v * H - 110 * ESC, R_ + 120 * ESC), 0.62 * H)
    d.line([(u * W, v * H), (cx, cy + R_)], fill=CREME + (al,), width=max(2, int(3 * ESC)))
    d.ellipse([cx - R_, cy - R_, cx + R_, cy + R_], fill=CREME + (al,), outline=AZUL + (al,), width=max(2, int(5 * ESC)))
    a0, a1 = math.radians(220), math.radians(-40)
    for k in range(11):
        t = a0 + (a1 - a0) * k / 10; r1, r2 = R_ * 0.78, R_ * (0.62 if k % 5 == 0 else 0.70)
        d.line([(cx + r1 * math.cos(t), cy - r1 * math.sin(t)), (cx + r2 * math.cos(t), cy - r2 * math.sin(t))], fill=AZUL + (al,), width=max(1, int(3 * ESC)))
    d.text((cx - R_ * 0.55, cy + R_ * 0.45), 'baixa', font=F_MAN, fill=AZUL + (al,), anchor='mm')
    d.text((cx + R_ * 0.55, cy + R_ * 0.45), 'alta', font=F_MAN, fill=AZUL + (al,), anchor='mm')
    t = a0 + (a1 - a0) * (0.1 + 0.8 * max(0.0, min(1.0, val)))
    d.line([(cx, cy), (cx + R_ * 0.72 * math.cos(t), cy - R_ * 0.72 * math.sin(t))], fill=(200, 60, 40, al), width=max(2, int(5 * ESC)))
    rr = 7 * ESC; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=AZUL + (al,))
    d.text((cx, cy - R_ - 16 * ESC), 'pressão', font=F_MAN, fill=CREME + (al,), anchor='mm', stroke_width=max(1, int(3 * ESC)), stroke_fill=ESCURO + (al,))
    img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB'))


def legendas():
    p = PL.carregar_palavras()[0]; blocos, cur = [], []
    for i, w in enumerate(p):
        cur.append(w); txt = ' '.join(x['palavra'] for x in cur); prox = p[i + 1] if i + 1 < len(p) else None
        fim = w['palavra'][-1] in '.?!:;,'; pausa = prox is not None and prox['inicio'] - w['fim'] > 0.30
        longo = (prox is not None and len(txt + ' ' + prox['palavra']) > 26) or (w['fim'] - cur[0]['inicio']) > 2.2
        if prox is None or fim or pausa or longo: blocos.append([cur[0]['inicio'], w['fim'], txt]); cur = []
    for i in range(len(blocos)):
        nxt = blocos[i + 1][0] if i + 1 < len(blocos) else DUR
        blocos[i][1] = min(blocos[i][1] + 0.25, nxt); blocos[i][2] = re.sub(r'[.,:;]+$', '', blocos[i][2])
    return blocos
LEG = legendas()


def compor(g):
    fz = lambda i: FUSOES.get(PLANOS[i]['id'], FUSAO); fs = lambda i: fz(i + 1) if i + 1 < len(PLANOS) else FUSAO
    ativos = [(p['id'], fz(i)) for i, p in enumerate(PLANOS) if p['t0'] - fz(i) / 2 <= g < p['t1'] + fs(i) / 2]
    if len(ativos) == 1: img = quadro(ativos[0][0], g); camadas = [(ativos[0][0], 1.0)]
    else:
        (p1, _), (p2, f2) = ativos[0], ativos[1]; t0 = PL_T[p2][0]
        k = min(1.0, max(0.0, (g - (t0 - f2 / 2)) / f2)); k = k * k * (3 - 2 * k)
        img = Image.blend(quadro(p1, g), quadro(p2, g), k); camadas = [(p1, 1 - k), (p2, k)]
    for (pid, k) in camadas:
        for (txt, u, v, a, dx, dy) in dados(pid, 'rotulos2d.json', g): rotulo(img, txt, u, v, a * k, dx, dy)
        ms = dados(pid, 'manometros2d.json', g)
        for j, (nome, u, v, a, val) in enumerate(ms): manometro(img, nome, u, v, a * k, val, (-1 if j % 2 == 0 else 1) if len(ms) > 1 else 0)
    d = ImageDraw.Draw(img)
    for (a, b, txt) in LEG:
        if a <= g < b: d.text((W // 2, int(0.74 * H)), txt, font=F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * ESC)), stroke_fill=ESCURO, anchor='mm')
    y = int(70 * ESC)
    for (a, b, txt) in CHIPS:
        if a <= g < b:
            tw = d.textlength(txt, font=F_TAG); x1 = W - int(30 * ESC); x0 = x1 - tw - 36 * ESC
            d.rounded_rectangle((x0, y, x1, y + 46 * ESC), radius=23 * ESC, fill=AMARELO); d.text((x0 + 18 * ESC, y + 23 * ESC), txt, font=F_TAG, fill=AZUL, anchor='lm')
            y += int(56 * ESC)
    if PERFIL != 'final':
        tag = ('ANIMATIC · tempos provisórios · não publicar' if PROVISORIO else 'ANIMATIC · não publicar' if PERFIL == 'animatic' else 'VERSÃO DE REVISÃO · não publicar')
        x0, y0 = int(30 * ESC), int(H - 80 * ESC); tw = d.textlength(tag, font=F_TAG)
        d.rounded_rectangle((x0, y0, x0 + tw + 36 * ESC, y0 + 46 * ESC), radius=23 * ESC, fill=AZUL); d.text((x0 + 18 * ESC, y0 + 23 * ESC), tag, font=F_TAG, fill=CREME, anchor='lm')
        pid = next((p['id'] for p in PLANOS if p['t0'] <= g < p['t1']), PLANOS[-1]['id'])
        d.text((W - int(30 * ESC), y0 + 23 * ESC), f'{pid} · {g:6.2f} s', font=F_TAG, fill=CREME, anchor='rm', stroke_width=max(1, int(3 * ESC)), stroke_fill=ESCURO)
    return img


if __name__ == '__main__':
    au = os.environ.get('AUDIO_EP02')
    n = int(round(DUR * FPS))
    entrada_audio = ['-i', au] if au else ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    filtro_audio = ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000'] if au else []   # animatic: só a voz, nivelada para escuta
    titulo = 'De Olho no Invisível · Ep. 02 · ' + ('animatic (não publicar)' if PERFIL == 'animatic' else 'versão de revisão (não publicar)' if PERFIL != 'final' else 'Como a geladeira esfria sem produzir frio?')
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', *entrada_audio,
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17' if PERFIL == 'final' else '21', '-pix_fmt', 'yuv420p',
                           *filtro_audio, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{DUR:.3f}', '-movflags', '+faststart', '-metadata', f'title={titulo}', SAIDA], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(compor(i / FPS).tobytes())
        if i % 600 == 0: print('quadro', i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', SAIDA)
