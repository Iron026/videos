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
CAIXAS = [] if os.environ.get('CAIXAS_EP02') == '1' else None   # rodada 7: registro das caixas desenhadas (testes de sobreposição)
def _cx(tipo, nome, caixa):
    if CAIXAS is not None: CAIXAS.append((tipo, nome, [float(c) for c in caixa]))


def faixa(a, b, txt): return (PL_T[a][0], PL_T[b][1], txt)
PL_T = {p['id']: (p['t0'], p['t1']) for p in PLANOS}
CHIPS = [faixa('A3', 'A3', 'Corte ilustrativo'),
         faixa('B5', 'B7', 'Tempo acelerado'), faixa('C2', 'H2', 'Corte ilustrativo'), faixa('D4', 'D4', 'Fluxo desacelerado'),
         faixa('F2', 'F2', 'Fluxo desacelerado'), faixa('D4', 'D4', 'Canal ampliado (esquema)'), faixa('F2', 'F2', 'Canal ampliado (esquema)'), faixa('G3', 'G3', 'Fluxo desacelerado'), faixa('G3', 'G3', 'Lupa: canal ampliado (esquema)'), faixa('E3', 'E3', 'Câmera lenta'),
         faixa('I3', 'I4', 'Corte ilustrativo'), faixa('J3', 'J3', 'Corte ilustrativo')]
# v4: avisos que dependem do MODO ativo (visão térmica; parede em corte só na metade traseira da tela dividida) são
# calculados das curvas gravadas em cada cena (mesma interpolação smoothstep do motor), não por plano inteiro
_curvas = {}
def curva_cena(pid, nome, g, padrao=0.0):
    if pid not in _curvas:
        f = os.path.join(A, 'cenas', pid, 'cena.json'); _curvas[pid] = json.load(open(f)).get('curvas', {}) if os.path.exists(f) else {}
    k = _curvas[pid].get(nome)
    if not k: return padrao
    if g <= k[0][0]: return k[0][1]
    for (t0, v0), (t1, v1) in zip(k, k[1:]):
        if g <= t1: u = (g - t0) / max(t1 - t0, 1e-6); return v0 + (v1 - v0) * u * u * (3 - 2 * u)
    return k[-1][1]
def termico_visivel(pid, g):
    ativo = lambda q: curva_cena(q, 'uTermico', g) > 0.01 and curva_cena(q, 'uVarre', g, 1.0) > 0.01
    if pid in DIVIDIDA: return ativo(pid) or (k_divisao(pid, g) > 0.02 and ativo(DIVIDIDA[pid]))
    return ativo(pid)
def chips_dinamicos(g):
    vivos = [p['id'] for p in PLANOS if p['t0'] <= g < p['t1']]
    out = []
    if any(termico_visivel(q, g) for q in vivos): out.append('Visão térmica (ilustrativa)')
    if any(q in DIVIDIDA and k_divisao(q, g) > 0.02 for q in vivos): out.append('Corte ilustrativo')   # metade traseira: parede em corte
    return out


def pasta(pid): return os.path.join(A, f'quadros_{PERFIL}', pid)
_idx = {}; _meta = {}
def meta(pid):
    if pid not in _meta:
        c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); _meta[pid] = c['g0']
    return _meta[pid]


DIVIDIDA = {'A4': 'A4b', 'J1': 'J1b'}
def k_divisao(pid, g):
    t0, t1 = PL_T[pid]; k = min(1.0, max(0.0, (g - t0 - 0.10 * (t1 - t0)) / 0.8)); k = k * k * (3 - 2 * k)
    if pid == 'A4': k *= 1.0 - min(1.0, max(0.0, (g - t0 - 0.80 * (t1 - t0)) / 0.6))   # A4 volta à frente inteira no fim
    return k
def quadro(pid, g):
    if pid in DIVIDIDA and os.path.isdir(pasta(DIVIDIDA[pid])):
        a, b = quadro_simples(pid, g), quadro_simples(DIVIDIDA[pid], g)
        k = k_divisao(pid, g)
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
        p = os.path.join(A, 'cenas', pid, arq)
        p9 = os.path.join(A, 'rotulos_r9', pid + '.json')   # rodada 9: âncoras visíveis (mesmos tempos; ver rotulos_r9.py)
        if arq == 'rotulos2d.json' and os.environ.get('COMPOSICAO_R9', '0') == '1' and os.path.exists(p9): p = p9
        _dados[k] = json.load(open(p)) if os.path.exists(p) else dict(g0=0, quadros=[])
    d = _dados[k]; f = int(round((g - d['g0']) * FPS)); q = d['quadros']
    return q[f] if 0 <= f < len(q) else []


def caixa_rotulo(txt, u, v, dx, dy, linha=True):
    ax, ay = u * W, v * H; bx, by = ax + dx * W, ay + dy * H
    tw = F_ROT.getlength(txt); pad = 20 * ESC; h = 44 * ESC + 2 * pad * 0.55; w = tw + 2 * pad
    if linha: lx = bx if dx >= 0 else bx - w; ly = by - h / 2
    else: lx = ax - w / 2; ly = ay - h - 10 * ESC          # rodada 8: sem linha — o rótulo encosta no próprio elemento
    if R9: lx = min(max(lx, ZONA['esquerda'] * ESC), W - ZONA['direita'] * ESC - w); ly = min(max(ly, (ZONA['topo'] + 8) * ESC), 0.62 * H - h)
    else: lx = min(max(lx, 0.04 * W), 0.96 * W - w); ly = min(max(ly, 0.09 * H), 0.62 * H - h)
    return lx, ly, w, h
LUPA_AVISO = 'Lupa: canal ampliado (esquema)'
def avisos_topo(g):
    vs = chips_dinamicos(g) + [t for (a, b, t) in CHIPS if a <= g < b]
    return [t for t in vs if not (R9 and t == LUPA_AVISO)]
def caixas_avisos(g):
    y = (ZONA['topo'] + 12) * ESC if R9 else 70 * ESC; out = []
    for txt in avisos_topo(g):
        tw = F_TAG.getlength(txt); x1 = W - int(30 * ESC); x0 = x1 - tw - 36 * ESC; out.append((x0, y, x1, y + 46 * ESC)); y += int(56 * ESC)
    return out
def separar_rotulos(rs, g=None):
    """Rodada 9: rótulos do mesmo quadro que se encostam (ex.: depois de sair da coluna de botões) — o que está mais abaixo
    sobe acima do outro (ajusta v da âncora só para a caixa; a linha de chamada, se houver, continua na âncora real)."""
    out, caixas = [], []
    fixas = caixas_avisos(g) if g is not None else []
    for r in sorted(rs, key=lambda r: -r[2]):
        txt, u, v, a, dx, dy, ln = r
        lx, ly, w, h = caixa_rotulo(txt, u, v, dx, dy, ln); dv = 0.0
        for c in fixas:   # rótulo que encosta num aviso desce para baixo da pilha de avisos (rótulos não entram na faixa superior)
            if not (lx + w + 8 * ESC <= c[0] or c[2] + 8 * ESC <= lx or ly + h + 6 * ESC <= c[1] or c[3] + 6 * ESC <= ly):
                dv = (max(f[3] for f in fixas) + 10 * ESC + h + 10 * ESC - v * H) / H if not ln else dv
                if ln: dv = (max(f[3] for f in fixas) + 10 * ESC + h / 2 - (v * H + dy * H)) / H
                lx, ly, w, h = caixa_rotulo(txt, u, v + dv, dx, dy, ln) if not ln else caixa_rotulo(txt, u, v, dx, dy + dv, ln)
                break
        for _ in range(6):
            bate = [c for c in caixas if not (lx + w + 8 * ESC <= c[0] or c[2] + 8 * ESC <= lx or ly + h + 6 * ESC <= c[1] or c[3] + 6 * ESC <= ly)]
            if not bate or ln: break
            dv -= (h + 12 * ESC) / H; lx, ly, w, h = caixa_rotulo(txt, u, v + dv, dx, dy, ln)
        caixas.append((lx, ly, lx + w, ly + h)); out.append([txt, u, v + dv, a, dx, dy, ln] if not ln else [txt, u, v, a, dx, dy + dv, ln])
    return out
def _rot(r):   # [txt, u, v, a, dx, dy(, linha)] — o 7º campo (0) marca rótulo SEM linha de chamada
    return r[:6] + [len(r) < 7 or bool(r[6])]


def rotulo(img, txt, u, v, a, dx, dy, linha=True):
    if a <= 0.01: return
    cam = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam)
    ax, ay = u * W, v * H; pad = 20 * ESC
    if linha and R9 and not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0): linha = False   # rodada 9: nunca uma linha para fora da tela
    lx, ly, w, h = caixa_rotulo(txt, u, v, dx, dy, linha)
    ex = min(max(ax, lx), lx + w); ey = ly + h / 2; al = int(255 * a)
    if linha:   # rodada 8: linha de chamada só para elementos pequenos, detalhes ampliados ou fora do quadro
        d.line([(ax, ay), (ex, ey)], fill=CREME + (al,), width=max(2, int(4 * ESC)))
        r = 11 * ESC; d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
        _cx('ligacao_rotulo', txt, (ax, ay, ex, ey))
    d.rounded_rectangle([lx, ly, lx + w, ly + h], radius=h / 2, fill=AZUL + (int(240 * a),)); _cx('rotulo', txt, (lx, ly, lx + w, ly + h))
    d.rounded_rectangle([lx + h * 0.3, ly + h - 5 * ESC, lx + w - h * 0.3, ly + h], radius=2, fill=AMARELO + (al,))
    d.text((lx + pad, ly + h / 2), txt, font=F_ROT, fill=CREME + (al,), anchor='lm')
    img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB'))


MAN_LEG = os.environ.get('MANOMETRO_LEGIVEL', '1') == '1'   # rodada 7: PADRÃO (aprovado): mostrador 25 % maior, textos de 30 px fora do anel; '0' = versão anterior
F_MAN2 = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(30 * ESC))
F_CART_T = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(38 * ESC))   # rodada 9: título do cartão (hierarquia)
F_CART_E = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), int(29 * ESC))   # rodada 9: extremos da escala
G_ATUAL = [0.0]
def centro_manometro(u, v, lado):
    R_ = (80 if MAN_LEG else 64) * ESC; cx = min(max(u * W + lado * 150 * ESC, R_ + 12 * ESC), W - R_ - 12 * ESC); cy = min(max(v * H - 110 * ESC, R_ + 120 * ESC), 0.62 * H)
    return R_, cx, cy


# ---- rodada 7: POSICIONAMENTO dos manômetros legíveis (MAN_LEG). Candidatos em volta da âncora; o primeiro sem colisão com
# bordas, lupa, faixa da legenda, avisos, rótulos e o outro mostrador; histerese (fica no lugar enquanto couber) e
# escolha no plano inteiro com o mínimo de trocas; troca inevitável vira fusão curta. Pares (baixa/alta) lado a lado, na ordem horizontal das âncoras.
MAN_CARTAO = os.environ.get('MANOMETRO_CARTAO', '1') == '1'   # rodada 8: manômetro como CARTÃO de pressão (linguagem dos rótulos)
CW, CH = 250 * ESC, 200 * ESC
def _caixa_cartao(cx, cy): return (cx - CW / 2, cy - CH / 2, cx + CW / 2, cy + CH / 2)
def _textos_man(cx, cy, R_):
    """Posições (centro) dos textos do mostrador legível: 'pressão' no topo; 'baixa'/'alta' nas LATERAIS do anel, na altura
    das pontas da escala (220° e −40°) — a parte de baixo fica livre para a linha de ligação."""
    yb = cy + 0.62 * R_; m = 8 * ESC
    return {'pressão': (cx, cy - R_ - 28 * ESC), 'baixa': (cx - R_ - m - F_MAN2.getlength('baixa') / 2, yb), 'alta': (cx + R_ + m + F_MAN2.getlength('alta') / 2, yb)}
def _caixas_textos_man(cx, cy, R_):
    if MAN_CARTAO: return {'cartao': _caixa_cartao(cx, cy)}
    out = {}
    for t, (x, y) in _textos_man(cx, cy, R_).items():
        w = F_MAN2.getlength(t) / 2 + 5 * ESC; out[t] = (x - w, y - 20 * ESC, x + w, y + 20 * ESC)
    return out
def _extensao_man(cx, cy, R_):
    if MAN_CARTAO: return _caixa_cartao(cx, cy)
    cs = list(_caixas_textos_man(cx, cy, R_).values()) + [(cx - R_, cy - R_, cx + R_, cy + R_)]
    return (min(c[0] for c in cs), min(c[1] for c in cs), max(c[2] for c in cs), max(c[3] for c in cs))
def _ponto_ligacao(cx, cy, R_, ax, ay):
    if MAN_CARTAO:   # ponto da borda do cartão mais próximo da âncora
        x0, y0, x1, y1 = _caixa_cartao(cx, cy); return (min(max(ax, x0), x1), min(max(ay, y0), y1))
    vx, vy = ax - cx, ay - cy; nv = max(1e-6, math.hypot(vx, vy)); return (cx + vx / nv * R_, cy + vy / nv * R_)
def _seg_cruza(p, q, c):
    for k in range(1, 40):
        t = k / 40; x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if c[0] < x < c[2] and c[1] < y < c[3]: return True
    return False
class _Obs(list): textos = ()
def _obstaculos(pid, g):
    if R9:   # rodada 9: a legenda do instante (posição escolhida por bloco) e a faixa superior/inferior das plataformas
        cl = caixa_legenda_em(g); ob = _Obs([cl] if cl else []); ob.textos = ([cl] if cl else []) + caixas_avisos(g)   # linhas de ligação não cruzam texto
        ob += [(0, 0, W, ZONA['topo'] * ESC), (0, H - ZONA['base'] * ESC, W, H)]
    else: ob = [(0, 0.74 * H - 50 * ESC, W, 0.74 * H + 50 * ESC)]                               # faixa da legenda
    if R9:
        ob += caixas_avisos(g) + [(W - ZONA['direita'] * ESC, ZONA['direita_desde'] * H, W, H)]   # avisos + coluna de botões
        if pid in INSET and PL_T[pid][0] - 0.05 <= g <= PL_T[pid][1] + 0.4: ob.append(caixa_aviso_lupa(INSET[pid]))
    else:
        nchips = len(chips_dinamicos(g) + [t for (a, b, t) in CHIPS if a <= g < b])
        if nchips: ob.append((W - 640 * ESC, 0, W, 70 * ESC + nchips * 56 * ESC))           # avisos (canto superior direito)
    if PERFIL != 'final': ob.append((0, H - 95 * ESC, W, H))                                      # selo da prévia
    rs = list(map(_rot, dados(pid, 'rotulos2d.json', g)))
    for (txt, u, v, a, dx, dy, ln) in (separar_rotulos(rs, g) if R9 else rs):
        if a > 0.05: lx, ly, w, h = caixa_rotulo(txt, u, v, dx, dy, ln); ob.append((lx, ly, lx + w, ly + h))
    circ = []
    if pid in INSET:
        c = INSET[pid]; t0, t1 = PL_T[pid]
        if t0 - 0.05 <= g <= t1 + 0.4: circ.append((c['cx'] * W, c['cy'] * H, c['r'] * W + 10 * ESC))
    return ob, circ
def _colide(ext, ob, circ):
    m = 12 * ESC
    if ext[0] < m or ext[1] < m or ext[2] > W - m or ext[3] > H - m: return True
    for o in ob:
        if not (ext[2] <= o[0] or o[2] <= ext[0] or ext[3] <= o[1] or o[3] <= ext[1]): return True
    for (cx, cy, r) in circ:
        nx, ny = min(max(cx, ext[0]), ext[2]), min(max(cy, ext[1]), ext[3])
        if (nx - cx) ** 2 + (ny - cy) ** 2 < r * r: return True
    return False
_LAYOUT = {}
TROCA_Q = 9          # quadros da fusão quando o mostrador precisa mudar de lugar (0,3 s)
def layout_manometros(pid):
    """Para o plano inteiro: em cada quadro, os candidatos VÁLIDOS; escolha por programação dinâmica que minimiza o número de
    trocas (custo de troca alto, leve preferência pela ordem dos candidatos). Posição = âncora + deslocamento do candidato
    (segue a âncora suavemente). Troca inevitável → fusão de TROCA_Q quadros (some num lugar, aparece no outro)."""
    if pid in _LAYOUT: return _LAYOUT[pid]
    dados(pid, 'manometros2d.json', 0.0); dd = _dados[(pid, 'manometros2d.json')]; g0 = dd['g0']; Q = dd['quadros']
    R_ = (CH / 2 if MAN_CARTAO else 80 * ESC); FIX = [(fx * W, fy * H) for fy in (0.16, 0.26, 0.36, 0.46, 0.56, 0.64) for fx in (0.22, 0.5, 0.78)]
    NC = 10 + len(FIX); um = {}
    for q in Q:
        for m in q: um.setdefault(m[0], []).append(m[1])
    ORD = {n: sum(v) / len(v) for n, v in um.items()}       # ordem horizontal FIXA no plano (média das âncoras)
    ext0 = _extensao_man(0, 0, R_); larg = ext0[2] - ext0[0] + 24 * ESC
    def pos(ms, k):
        anc = [(m[1] * W, m[2] * H) for m in ms]; n = len(ms)
        mx = sum(a[0] for a in anc) / n; top, bot = min(a[1] for a in anc), max(a[1] for a in anc)
        dy_up = -(R_ + (70 if MAN_CARTAO else 130) * ESC); dy_dn = R_ + (80 if MAN_CARTAO else 150) * ESC; lado = larg * 0.5 + R_ * 0.3
        base = ([(mx, top + dy_up), (mx + lado, top + dy_up), (mx - lado, top + dy_up), (mx, top + dy_up * 1.6),
                 (mx + larg, (top + bot) / 2), (mx - larg, (top + bot) / 2), (mx, bot + dy_dn), (mx + lado, bot + dy_dn),
                 (mx - lado, bot + dy_dn), (mx, bot + dy_dn * 1.5)] + FIX)[k]     # 10 relativos à âncora + posições FIXAS na tela
        x0 = base[0] - larg * (n - 1) / 2; x0 = min(max(x0, -ext0[0] + 12 * ESC), W - 12 * ESC - ext0[2] - larg * (n - 1))
        return [(x0 + j * larg, base[1]) for j in range(n)], anc
    quadros = []
    for i, q in enumerate(Q):
        ms = sorted(q, key=lambda m: ORD[m[0]])
        if not ms: quadros.append(None); continue
        ob, circ = _obstaculos(pid, i / FPS + g0)
        lupa = (INSET[pid], [m for m in ms if m[0] == INSET[pid]['ancora']]) if pid in INSET else None
        val = []
        for k in range(NC):
            c, anc = pos(ms, k); val.append(valido(c, ob, circ, anc, lupa and lupa[1] and (lupa[0], [cc for m, cc in zip(ms, c) if m[0] == lupa[0]['ancora']][0])))
        quadros.append((ms, val))
    # programação dinâmica sobre os quadros com manômetro
    idx = [i for i, x in enumerate(quadros) if x]; esc = {}
    if idx:
        INF = 1e9; custo = [[0.0] * NC]; trilha = []
        for j, i in enumerate(idx):
            val = quadros[i][1]; loc = [(0.0 if val[k] else 1000.0) + 0.01 * k for k in range(NC)]
            if j == 0: custo = [loc]; continue
            ant = custo[-1]; novo, tr = [], []
            for k in range(NC):
                best = min(range(NC), key=lambda kk: ant[kk] + (0 if kk == k else 30.0)); novo.append(ant[best] + (0 if best == k else 30.0) + loc[k]); tr.append(best)
            custo.append(novo); trilha.append(tr)
        k = min(range(NC), key=lambda kk: custo[-1][kk]); seq = [k]
        for tr in reversed(trilha): k = tr[k]; seq.append(k)
        seq.reverse(); esc = {i: k for i, k in zip(idx, seq)}
    out = []
    for i, x in enumerate(quadros):
        if not x: out.append({}); continue
        ms, _ = x; k = esc[i]; c, _a = pos(ms, k); ent = {m[0]: [(cc[0], cc[1], 1.0)] for m, cc in zip(ms, c)}
        # fusão: se houver troca nos próximos/últimos TROCA_Q/2 quadros, mistura as duas posições
        for j in range(1, TROCA_Q // 2 + 1):
            for viz, lado in ((i + j, 1), (i - j, -1)):
                if viz in esc and esc[viz] != k and all(esc.get(i + lado * t, k) == k for t in range(1, j)):
                    w = 0.5 - 0.5 * j / (TROCA_Q // 2 + 1)                 # 0,5 na troca → 0 longe dela
                    c2, _b = pos(ms, esc[viz])
                    for m, cc, cc2 in zip(ms, c, c2): ent[m[0]] = [(cc[0], cc[1], 1.0 - w), (cc2[0], cc2[1], w)]
        out.append(ent)
    _LAYOUT[pid] = (g0, out); return _LAYOUT[pid]
def valido(centros, ob, circ, anc, lupa=None):
    """Candidato válido: nenhum mostrador/texto colide com bordas/legenda/avisos/rótulos/lupa nem entre si; nenhuma linha de
    ligação cruza um texto (de qualquer mostrador do grupo)."""
    R_ = (CH / 2 if MAN_CARTAO else 80 * ESC); exts = [_extensao_man(cx, cy, R_) for (cx, cy) in centros]
    if any(_colide(e, ob, circ) for e in exts): return False
    for a in range(len(exts)):
        for b in range(a + 1, len(exts)):
            e1, e2 = exts[a], exts[b]
            if not (e1[2] + 10 * ESC <= e2[0] or e2[2] + 10 * ESC <= e1[0] or e1[3] <= e2[1] or e2[3] <= e1[1]): return False
    textos = [c for (cx, cy) in centros for c in _caixas_textos_man(cx, cy, R_).values()]
    for (cx, cy), (ax, ay) in zip(centros, anc):
        p = _ponto_ligacao(cx, cy, R_, ax, ay)
        if any(_seg_cruza((ax, ay), p, c) for c in textos): return False
        if any(_seg_cruza((ax, ay), p, c) for c in getattr(ob, 'textos', ())): return False   # rodada 9: nem sobre a legenda/avisos
        for (cx2, cy2) in centros:   # a ligação não atravessa o OUTRO mostrador
            if (cx2, cy2) != (cx, cy) and _seg_cruza((ax, ay), p, _extensao_man(cx2, cy2, R_)): return False
    if lupa:   # a linha da lupa (borda do círculo → topo do mostrador) não cruza textos nem mostradores
        c, (mx, my) = lupa; lx, ly, lr = c['cx'] * W, c['cy'] * H, c['r'] * W
        fim = (mx, my - R_ - (4 if MAN_CARTAO else 50) * ESC); vx, vy = fim[0] - lx, fim[1] - ly; nv = max(1e-6, math.hypot(vx, vy))
        if nv <= lr + 8 * ESC: return False
        ini = (lx + vx / nv * lr, ly + vy / nv * lr)
        if any(_seg_cruza(ini, fim, t) for t in textos): return False
        if any(_seg_cruza(ini, fim, _extensao_man(cx, cy, R_)) for (cx, cy) in centros if not MAN_CARTAO): return False
    return True
def posicoes_manometro(pid, nome, g):
    g0, L = layout_manometros(pid); f = int(round((g - g0) * FPS))
    return L[f].get(nome, []) if 0 <= f < len(L) else []
def posicao_manometro(pid, nome, g):
    ps = posicoes_manometro(pid, nome, g); return max(ps, key=lambda p: p[2])[:2] if ps else None


def manometro(img, nome, u, v, a, val, lado, pid=None, pp=None):
    """Mostrador neutro (creme/azul da marca): ponteiro de 'baixa' a 'alta' pressão. Sem números (comparação relativa)."""
    if a <= 0.01: return
    if MAN_LEG and pid and pp is None:   # rodada 7: posições resolvidas (uma, ou duas durante a fusão de uma troca)
        for (px, py, w) in posicoes_manometro(pid, nome, G_ATUAL[0]): manometro(img, nome, u, v, a * w, val, lado, pid, (px, py))
        return
    cam = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam); al = int(255 * a)
    R_, cx, cy = centro_manometro(u, v, lado)
    if MAN_CARTAO and pp and R9:   # rodada 9: mesmo cartão, só visual — hierarquia (título > extremos), escala com 3 marcas,
        # arco preenchido até o valor + marcador maior (lê melhor nos extremos que uma agulha), fundo opaco, ligação mais fina.
        # Valor e ângulo: MESMA fórmula da R8 (ang = 180 + 180·valor).
        cx, cy = pp; x0, y0, x1, y1 = _caixa_cartao(cx, cy); ax, ay = u * W, v * H; fim = _ponto_ligacao(cx, cy, R_, ax, ay)
        if math.hypot(ax - fim[0], ay - fim[1]) > 30 * ESC:
            d.line([(ax, ay), fim], fill=CREME + (int(200 * a),), width=max(1, int(3 * ESC)))
        rr_ = 8 * ESC; d.ellipse([ax - rr_, ay - rr_, ax + rr_, ay + rr_], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
        d.rounded_rectangle([x0, y0, x1, y1], radius=28 * ESC, fill=AZUL + (int(252 * a),))
        d.rounded_rectangle([x0 + 0.2 * CW, y1 - 6 * ESC, x1 - 0.2 * CW, y1], radius=2, fill=AMARELO + (al,))
        d.text((cx, y0 + 36 * ESC), 'pressão', font=F_CART_T, fill=CREME + (al,), anchor='mm')
        Rg, esp = 66 * ESC, max(3, int(14 * ESC)); gc = (cx, y0 + 146 * ESC); bb = [gc[0] - Rg, gc[1] - Rg, gc[0] + Rg, gc[1] + Rg]
        vv = max(0.0, min(1.0, val)); ang = 180 + 180 * vv
        d.arc(bb, start=180, end=360, fill=(246, 244, 236, int(90 * a)), width=esp)                    # escala (trilho)
        if vv > 0.004: d.arc(bb, start=180, end=ang, fill=AMARELO + (al,), width=esp)                   # preenchido até o valor
        for f_ in (0.0, 0.5, 1.0):                                                                     # 3 marcas por fora: baixa · meio · alta
            t_ = math.radians(180 + 180 * f_); r1, r2 = Rg + 5 * ESC, Rg + 15 * ESC
            d.line([(gc[0] + r1 * math.cos(t_), gc[1] + r1 * math.sin(t_)), (gc[0] + r2 * math.cos(t_), gc[1] + r2 * math.sin(t_))], fill=CREME + (int(200 * a),), width=max(1, int(3 * ESC)))
        rm = Rg - esp / 2; kx, ky = gc[0] + rm * math.cos(math.radians(ang)), gc[1] + rm * math.sin(math.radians(ang)); kr = 15 * ESC
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=CREME + (al,), outline=AZUL + (al,), width=max(1, int(5 * ESC)))   # marcador (ponteiro)
        for txt, xx in (('baixa', gc[0] - Rg), ('alta', gc[0] + Rg)):
            d.text((xx, y0 + 180 * ESC), txt, font=F_CART_E, fill=CREME + (int(215 * a),), anchor='mm')
        _cx('mostrador', nome, (x0, y0, x1, y1)); _cx('ligacao_man', nome, (ax, ay) + fim); _cx('texto_man', nome + ':cartao', (x0, y0, x1, y1))
        _cx('ponteiro', nome, (val, ang, 0, 0)); img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB')); return
    if MAN_CARTAO and pp:   # rodada 8: CARTÃO de pressão — mesma linguagem dos rótulos (cápsula azul + sublinhado amarelo)
        cx, cy = pp; x0, y0, x1, y1 = _caixa_cartao(cx, cy); ax, ay = u * W, v * H; fim = _ponto_ligacao(cx, cy, R_, ax, ay)
        if math.hypot(ax - fim[0], ay - fim[1]) > 30 * ESC:   # ponto de medição num tubo fino: linha curta até o cartão
            d.line([(ax, ay), fim], fill=CREME + (al,), width=max(2, int(4 * ESC)))
        rr_ = 11 * ESC; d.ellipse([ax - rr_, ay - rr_, ax + rr_, ay + rr_], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
        d.rounded_rectangle([x0, y0, x1, y1], radius=28 * ESC, fill=AZUL + (int(240 * a),))
        d.rounded_rectangle([x0 + 0.2 * CW, y1 - 6 * ESC, x1 - 0.2 * CW, y1], radius=2, fill=AMARELO + (al,))
        d.text((cx, y0 + 36 * ESC), 'pressão', font=F_MAN2, fill=CREME + (al,), anchor='mm')
        Rg, esp = 72 * ESC, max(3, int(15 * ESC)); gc = (cx, y0 + 148 * ESC); bb = [gc[0] - Rg, gc[1] - Rg, gc[0] + Rg, gc[1] + Rg]
        vv = max(0.0, min(1.0, val)); ang = 180 + 180 * vv
        d.arc(bb, start=180, end=360, fill=(246, 244, 236, int(70 * a)), width=esp)                    # trilho da escala
        if vv > 0.004: d.arc(bb, start=180, end=ang, fill=AMARELO + (al,), width=esp)                   # preenchido até o valor
        kx, ky = gc[0] + Rg * math.cos(math.radians(ang)), gc[1] + Rg * math.sin(math.radians(ang)); kr = 12 * ESC
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=CREME + (al,), outline=AZUL + (al,), width=max(1, int(4 * ESC)))
        for txt, xx in (('baixa', gc[0] - Rg), ('alta', gc[0] + Rg)):
            d.text((xx, y0 + 178 * ESC), txt, font=F_MAN2, fill=CREME + (al,), anchor='mm')
        _cx('mostrador', nome, (x0, y0, x1, y1)); _cx('ligacao_man', nome, (ax, ay) + fim); _cx('texto_man', nome + ':cartao', (x0, y0, x1, y1))
        _cx('ponteiro', nome, (val, ang, 0, 0)); img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB')); return
    if pp:   # rodada 7: posição resolvida; a ligação sai da âncora e chega ao anel no ponto voltado para ela
        cx, cy = pp; fim = _ponto_ligacao(cx, cy, R_, u * W, v * H)
        d.line([(u * W, v * H), fim], fill=CREME + (al,), width=max(2, int(3 * ESC)))
    else: d.line([(u * W, v * H), (cx, cy + R_)], fill=CREME + (al,), width=max(2, int(3 * ESC)))
    d.ellipse([cx - R_, cy - R_, cx + R_, cy + R_], fill=CREME + (al,), outline=AZUL + (al,), width=max(2, int(5 * ESC)))
    _cx('mostrador', nome, (cx - R_, cy - R_, cx + R_, cy + R_)); _cx('ligacao_man', nome, (u * W, v * H) + (fim if pp else (cx, cy + R_)))
    a0, a1 = math.radians(220), math.radians(-40)
    for k in range(11):
        t = a0 + (a1 - a0) * k / 10; r1, r2 = R_ * 0.78, R_ * (0.62 if k % 5 == 0 else 0.70)
        d.line([(cx + r1 * math.cos(t), cy - r1 * math.sin(t)), (cx + r2 * math.cos(t), cy - r2 * math.sin(t))], fill=AZUL + (al,), width=max(1, int(3 * ESC)))
    if MAN_LEG:   # fora do anel, nas laterais à altura das pontas da escala, com contorno (legível sobre qualquer fundo)
        for txt, pt in _textos_man(cx, cy, R_).items():
            if txt == 'pressão': continue
            d.text(pt, txt, font=F_MAN2, fill=CREME + (al,), anchor='mm', stroke_width=max(2, int(5 * ESC)), stroke_fill=ESCURO + (al,))
            _cx('texto_man', nome + ':' + txt, d.textbbox(pt, txt, font=F_MAN2, anchor='mm', stroke_width=max(2, int(5 * ESC))))
    else:
        d.text((cx - R_ * 0.55, cy + R_ * 0.45), 'baixa', font=F_MAN, fill=AZUL + (al,), anchor='mm')
        d.text((cx + R_ * 0.55, cy + R_ * 0.45), 'alta', font=F_MAN, fill=AZUL + (al,), anchor='mm')
        _cx('texto_man_interno', nome + ':baixa', d.textbbox((cx - R_ * 0.55, cy + R_ * 0.45), 'baixa', font=F_MAN, anchor='mm'))
        _cx('texto_man_interno', nome + ':alta', d.textbbox((cx + R_ * 0.55, cy + R_ * 0.45), 'alta', font=F_MAN, anchor='mm'))
    t = a0 + (a1 - a0) * (0.1 + 0.8 * max(0.0, min(1.0, val)))
    d.line([(cx, cy), (cx + R_ * 0.72 * math.cos(t), cy - R_ * 0.72 * math.sin(t))], fill=(200, 60, 40, al), width=max(2, int(5 * ESC)))
    rr = 7 * ESC; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=AZUL + (al,))
    d.text((cx, cy - R_ - (28 if MAN_LEG else 16) * ESC), 'pressão', font=F_MAN2 if MAN_LEG else F_MAN, fill=CREME + (al,), anchor='mm', stroke_width=max(1, int((5 if MAN_LEG else 3) * ESC)), stroke_fill=ESCURO + (al,))
    _cx('texto_man', nome + ':pressão', d.textbbox((cx, cy - R_ - (28 if MAN_LEG else 16) * ESC), 'pressão', font=F_MAN2 if MAN_LEG else F_MAN, anchor='mm', stroke_width=max(1, int((5 if MAN_LEG else 3) * ESC))))
    t_ = a0 + (a1 - a0) * (0.1 + 0.8 * max(0.0, min(1.0, val))); _cx('ponteiro', nome, (val, math.degrees(t_), 0, 0))
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


# ---- rodada 9 (COMPOSICAO_R9=1; '0' = V8 idêntica): legendas por unidades de sentido, posição escolhida por bloco fora
# das zonas de interface e longe de rosto/mecanismo/rótulos; avisos abaixo da faixa superior das plataformas
R9 = os.environ.get('COMPOSICAO_R9', '0') == '1'
# zonas de interface (aprox., em px de 1080 × 1920; guias de terceiros — Shorts: topo 120, base 300, coluna direita ~96;
# Reels: topo ~250, base ~340 (atribuído à Meta), coluna direita ~120). Usamos a UNIÃO (o mais restritivo de cada lado).
ZONA = dict(topo=250, base=340, direita=120, direita_desde=0.40, esquerda=60)
ZONA_BASE_CONSERVADORA = 670          # número mais conservador citado para Reels (só relatado; penalidade leve)
LH_LEG = 70 * ESC                     # altura de linha da legenda
Y_LEG_CAND = [0.74, 0.71, 0.68, 0.65, 0.62, 0.59]   # centros candidatos (fração da altura); escolha por bloco
def _proj(cam, P):
    pos = np.array(cam['pos']); f = np.array(cam['dir'], float); f /= np.linalg.norm(f); r = np.cross(f, cam['up']); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = np.asarray(P, float) - pos; z = d @ f; t = math.tan(math.radians(cam['fov'] / 2))
    return ((d @ r / z) / (t * W / H) + 1) / 2 * W, (1 - (d @ u / z) / t) / 2 * H, z, t
_rosto_cache = {}
def rosto(pid, g):
    """Caixa do rosto do personagem no quadro (projeção da cabeça exportada); None se não houver personagem à vista."""
    if pid not in _rosto_cache:
        f = os.path.join(A, 'cenas', pid, 'cena.json'); c = json.load(open(f)) if os.path.exists(f) else {}
        _rosto_cache[pid] = (c.get('g0', 0), c.get('animacao', {}).get('quadros', []))
    g0, Q = _rosto_cache[pid]; i = int(round((g - g0) * FPS))
    if not (0 <= i < len(Q)) or 'pers_cabeca' not in Q[i]['objetos']: return None
    m = Q[i]['objetos']['pers_cabeca']; P = (m[12], m[13], m[14] + 0.12)
    x, y, z, t = _proj(Q[i]['camera'], P)
    if z <= 0.05: return None
    rr = 0.17 / (z * t) * H / 2
    b = (x - rr, y - rr, x + rr, y + rr)
    return b if b[2] > 0 and b[0] < W and b[3] > 0 and b[1] < H else None
# mecanismos (coordenadas do modelo, as mesmas dos rótulos do H2 e da caixa do evaporador): só contam quando o circuito está
# revelado (uRevela) — antes disso estão escondidos atrás das paredes e a projeção não diria nada sobre o que se vê
MECS = [((-0.10, 0.12, 0.12), (0.06, 0.26, 0.30)),          # compressor (carcaça; caixa justa — a projeção da caixa 3D já infla o retângulo)
        ((-0.215, -0.235, 1.185), (0.215, 0.205, 1.405)),   # evaporador (caixa do congelador)
        ((0.20, 0.22, 0.20), (0.27, 0.29, 0.30))]           # capilar (trecho junto ao compressor)
def mecanismos(pid, g):
    if curva_cena(pid, 'uRevela', g, 0.0) < 0.5: return []
    if pid not in _rosto_cache: rosto(pid, g)
    g0, Q = _rosto_cache[pid]; i = int(round((g - g0) * FPS))
    if not (0 <= i < len(Q)): return []
    cam = Q[i]['camera']; out = []
    pts = [MECS[k] for k in range(len(MECS))] + [((m[12] - 0.04, m[13] - 0.04, m[14] - 0.04), (m[12] + 0.04, m[13] + 0.04, m[14] + 0.04))
                                                for n_, m in Q[i]['objetos'].items() if n_.startswith('mec_') and n_.endswith('pivo')]
    for (a, b) in pts:
        cs = [_proj(cam, (x, y, z)) for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])]
        if any(c[2] <= 0.05 for c in cs): continue
        xs = [c[0] for c in cs]; ys = [c[1] for c in cs]; bb = (max(0, min(xs)), max(0, min(ys)), min(W, max(xs)), min(H, max(ys)))
        if bb[2] > bb[0] and bb[3] > bb[1]: out.append(bb)
    return out
def _linhas_leg(b): return b['linhas']
def caixa_legenda(b, yc):
    hl = len(b['linhas']) * LH_LEG; wl = max(F_LEG.getlength(l) for l in b['linhas']) + 2 * 7 * ESC
    return (W / 2 - wl / 2, yc - hl / 2 - 6 * ESC, W / 2 + wl / 2, yc + hl / 2 + 6 * ESC)
def _sobrepoe(a, b, m=0):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])
def _custo_posicao(b, yf):
    """Custo de um centro candidato para o bloco inteiro (amostras a cada 3 quadros): zonas de interface, rosto, âncoras de
    rótulos e pressão (o que o rótulo aponta é mecanismo), caixas de rótulos, lupa; leve preferência pelo terço inferior."""
    yc = yf * H; cx = caixa_legenda(b, yc); s = 1080 / W
    c = 0.0
    if cx[3] > H - ZONA['base'] / s: c += 500
    if cx[3] > H - ZONA_BASE_CONSERVADORA / s: c += 3
    if cx[2] > W - ZONA['direita'] / s and cx[3] > ZONA['direita_desde'] * H: c += 200
    if cx[1] < ZONA['topo'] / s: c += 500
    c += 2.0 * abs(yf - 0.68) / 0.03 + (12.0 * (0.68 - yf) / 0.03 if yf < 0.68 else 0.0)   # prefere o terço inferior; subir para o centro (onde fica a ação) só com motivo forte
    fixo, c, n = c, 0.0, 0
    for k in np.arange(b['t0'], b['t1'], 0.1):
        vivos = [p['id'] for p in PLANOS if p['t0'] <= k < p['t1']]; n += 1
        for pid in vivos:
            r = rosto(pid, k)
            if r and _sobrepoe(cx, r, 8 * ESC): c += 40
            fr = 0.0
            for mb in mecanismos(pid, k):   # fração da caixa da legenda que cobre o mecanismo (a maior, não a soma: peças do mesmo compressor)
                ix = max(0, min(cx[2], mb[2]) - max(cx[0], mb[0])) * max(0, min(cx[3], mb[3]) - max(cx[1], mb[1]))
                fr = max(fr, ix / ((cx[2] - cx[0]) * (cx[3] - cx[1])))
            c += 20 * fr
            for (txt, u, v, a, dx, dy, ln) in map(_rot, dados(pid, 'rotulos2d.json', k)):
                if a < 0.05: continue
                lx, ly, w, h = caixa_rotulo(txt, u, v, dx, dy, ln)
                if _sobrepoe(cx, (lx, ly, lx + w, ly + h), 6 * ESC): c += 30
                if 0 <= u <= 1 and 0 <= v <= 1 and cx[0] - 10 * ESC <= u * W <= cx[2] + 10 * ESC and cx[1] - 10 * ESC <= v * H <= cx[3] + 10 * ESC: c += 25
            for (nome, u, v, a, val) in dados(pid, 'manometros2d.json', k):
                if a > 0.05 and cx[0] - 10 * ESC <= u * W <= cx[2] + 10 * ESC and cx[1] - 10 * ESC <= v * H <= cx[3] + 10 * ESC: c += 25
                if a > 0.05 and cx[3] < v * H < cx[3] + CH + 110 * ESC and cx[0] - 100 * ESC < u * W < cx[2] + 100 * ESC: c += 30   # âncora logo ABAIXO da legenda sem espaço para o cartão entre as duas: a ligação cruzaria o texto
            if pid in INSET:
                L_ = INSET[pid]; lc = (L_['cx'] * W, L_['cy'] * H, L_['r'] * W)
                nx, ny = min(max(lc[0], cx[0]), cx[2]), min(max(lc[1], cx[1]), cx[3])
                if (nx - lc[0]) ** 2 + (ny - lc[1]) ** 2 < (lc[2] + 8 * ESC) ** 2: c += 40
    return fixo + (c / n * 10 if n else 0.0)             # parte dinâmica: média das amostras (escala ×10)
LEG9, POS9 = [], []
if R9:
    import legendas_r9
    LEG9 = legendas_r9.blocos(lambda s: F_LEG.getlength(s) + 14 * ESC, (1080 - 2 * ZONA['direita']) * ESC, DUR)   # simétrica: fora da coluna de botões
POSICAO_LEG_FIXA = float(os.environ['LEGENDA_Y']) if os.environ.get('LEGENDA_Y') else None   # testes: posição única
def posicoes_legenda():
    """Programação dinâmica sobre os blocos: custo de cada posição + custo de MUDAR de altura entre blocos seguidos (a legenda
    não deve pular à toa)."""
    if POS9 or not LEG9: return POS9
    if POSICAO_LEG_FIXA is not None: POS9.extend([POSICAO_LEG_FIXA] * len(LEG9)); return POS9
    K = len(Y_LEG_CAND); cs = [[_custo_posicao(b, y) for y in Y_LEG_CAND] for b in LEG9]
    tot = [cs[0][:]]; tr = []
    for i in range(1, len(LEG9)):
        colado = LEG9[i]['t0'] - LEG9[i - 1]['t1'] < 0.4; troca = 60.0 if colado else 15.0   # a legenda só muda de altura com motivo forte
        row, back = [], []
        for k in range(K):
            j = min(range(K), key=lambda jj: tot[-1][jj] + (0 if jj == k else troca))
            row.append(tot[-1][j] + (0 if j == k else troca) + cs[i][k]); back.append(j)
        tot.append(row); tr.append(back)
    k = min(range(K), key=lambda kk: tot[-1][kk]); seq = [k]
    for back in reversed(tr): k = back[k]; seq.append(k)
    seq.reverse(); POS9.extend(Y_LEG_CAND[k] for k in seq); return POS9
def legenda_r9(d, g):
    ps = posicoes_legenda()
    for b, yf in zip(LEG9, ps):
        if not (b['t0'] <= g < b['t1']): continue
        visiveis = min([m for (t, m) in b['revela'] if g < t] + [len(b['palavras'])])   # pausa longa: o resto entra no ataque
        yc = yf * H; y0 = yc - (len(b['linhas']) - 1) * LH_LEG / 2; usadas = 0
        for q, lin in enumerate(b['linhas']):
            ws = lin.split(); mostra = ws[:max(0, min(len(ws), visiveis - usadas))]; usadas += len(ws)
            x0 = W / 2 - F_LEG.getlength(lin) / 2; y = y0 + q * LH_LEG
            if mostra: d.text((x0, y), ' '.join(mostra), font=F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * ESC)), stroke_fill=ESCURO, anchor='lm')
        _cx('legenda', ' / '.join(b['linhas']), caixa_legenda(b, yc))
def caixa_legenda_em(g):
    for b, yf in zip(LEG9, posicoes_legenda()):
        if b['t0'] <= g < b['t1']: return caixa_legenda(b, yf * H)
    return None


# polimento: LUPA — ampliação didática localizada (plano renderizado à parte, composto num círculo) ligada por uma linha
# ao marcador do plano principal (manômetro que percorre o capilar real no mesmo ponto)
INSET = {'G3': dict(plano='G3z', cx=0.50, cy=0.255, r=0.31, ancora='capilar')}
if os.environ.get('COMPOSICAO_R9', '0') == '1': INSET['G3'].update(cx=0.46, cy=0.32)   # rodada 9: topo abaixo da faixa superior e livre dos avisos (mesmo tamanho)
def caixa_aviso_lupa(c):
    tw = F_TAG.getlength(LUPA_AVISO); x0 = c['cx'] * W - tw / 2 - 18 * ESC; yb = c['cy'] * H + c['r'] * W
    return (x0, yb - 23 * ESC, x0 + tw + 36 * ESC, yb + 23 * ESC)
def lupa(img, pid, g, k):
    c = INSET[pid]; z = c['plano']
    if not os.path.isdir(pasta(z)): return
    t0, t1 = PL_T[pid]; a = k * min(1.0, max(0.0, (g - t0) / 0.35), max(0.0, (t1 + 0.1 - g) / 0.3))
    if a <= 0.01: return
    sub = quadro_simples(z, g); top = (H - W) // 2; quad = sub.crop((0, top, W, top + W))
    D = int(2 * c['r'] * W); cx, cy = int(c['cx'] * W), int(c['cy'] * H); quad = quad.resize((D, D), Image.LANCZOS)
    m4 = Image.new('L', (4 * D, 4 * D), 0); ImageDraw.Draw(m4).ellipse((0, 0, 4 * D - 1, 4 * D - 1), fill=int(255 * a)); mask = m4.resize((D, D), Image.LANCZOS)
    # linha de ligação: do marcador (manômetro no capilar real) até a borda do círculo
    anc = next(((u, v) for (nome, u, v, aa, val) in dados(pid, 'manometros2d.json', g) if nome == c['ancora']), None)
    cam = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam); al = int(230 * a)
    if anc:
        # rodada 6: a linha termina no TOPO do manômetro (acima de "pressão"), que tem a própria ligação até o capilar; antes ela
        # descia até a âncora e atravessava o mostrador (cortava "pressão" — visto no teste em 1080)
        R_m, mx, my = centro_manometro(anc[0], anc[1], 0)
        pp = posicao_manometro(pid, c['ancora'], g) if MAN_LEG else None
        if pp: mx, my = pp
        ax, ay = mx, my - ((CH / 2 + 4 * ESC) if MAN_CARTAO else R_m + (50 if MAN_LEG else 34) * ESC)
        vx, vy = ax - cx, ay - cy; n = max(1e-6, (vx * vx + vy * vy) ** 0.5)
        if n > D / 2 + 8: ex, ey = cx + vx / n * D / 2, cy + vy / n * D / 2; _cx('ligacao_lupa', pid, (ex, ey, ax, ay)); d.line((ex, ey, ax, ay), fill=(16, 22, 46, al), width=max(3, int(7 * ESC))); d.line((ex, ey, ax, ay), fill=(246, 244, 236, al), width=max(1, int(3 * ESC)))
    img.paste(Image.alpha_composite(img.convert('RGBA'), cam).convert('RGB'))
    img.paste(quad, (cx - D // 2, cy - D // 2), mask); _cx('lupa', pid, (cx - D // 2, cy - D // 2, cx + D // 2, cy + D // 2))
    anel = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(anel).ellipse((cx - D // 2, cy - D // 2, cx + D // 2, cy + D // 2), outline=(246, 244, 236, int(255 * a)), width=max(2, int(6 * ESC)))
    img.paste(Image.alpha_composite(img.convert('RGBA'), anel).convert('RGB'))
    if R9:   # rodada 9: o aviso da lupa fica preso ao anel (descreve a própria lupa), fora da pilha do canto
        b = caixa_aviso_lupa(c); sel = Image.new('RGBA', img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sel)
        ds.rounded_rectangle(b, radius=23 * ESC, fill=AMARELO + (int(255 * a),)); ds.text((b[0] + 18 * ESC, (b[1] + b[3]) / 2), LUPA_AVISO, font=F_TAG, fill=AZUL + (int(255 * a),), anchor='lm')
        img.paste(Image.alpha_composite(img.convert('RGBA'), sel).convert('RGB')); _cx('aviso_lupa', LUPA_AVISO, b)
    # rótulos do canal, levados para dentro do círculo
    for (txt, u, v, aa, dx, dy, _ln) in map(_rot, dados(z, 'rotulos2d.json', g)):
        X = cx + (u * W - W / 2) / W * D; Y = cy + (v * H - (top + W / 2)) / W * D
        if (X - cx) ** 2 + (Y - cy) ** 2 < (D / 2) ** 2:
            ddy = -0.035
            if R9:   # rodada 9: rótulo da lupa que encostaria num aviso vai para baixo do ponto
                lx, ly, w, h = caixa_rotulo(txt, X / W, Y / H, 0.03, ddy, True)
                if any(not (lx + w <= b[0] or b[2] <= lx or ly + h <= b[1] or b[3] <= ly) for b in caixas_avisos(g)): ddy = 0.035
            rotulo(img, txt, X / W, Y / H, aa * a, 0.03, ddy)


def compor(g):
    fz = lambda i: FUSOES.get(PLANOS[i]['id'], FUSAO); fs = lambda i: fz(i + 1) if i + 1 < len(PLANOS) else FUSAO
    ativos = [(p['id'], fz(i)) for i, p in enumerate(PLANOS) if p['t0'] - fz(i) / 2 <= g < p['t1'] + fs(i) / 2]
    if len(ativos) == 1: img = quadro(ativos[0][0], g); camadas = [(ativos[0][0], 1.0)]
    else:
        (p1, _), (p2, f2) = ativos[0], ativos[1]; t0 = PL_T[p2][0]
        k = min(1.0, max(0.0, (g - (t0 - f2 / 2)) / f2)); k = k * k * (3 - 2 * k)
        img = Image.blend(quadro(p1, g), quadro(p2, g), k); camadas = [(p1, 1 - k), (p2, k)]
    for (pid, k) in camadas:
        rs = list(map(_rot, dados(pid, 'rotulos2d.json', g)))
        if R9: rs = separar_rotulos(rs, g)
        for (txt, u, v, a, dx, dy, ln) in rs: rotulo(img, txt, u, v, a * k, dx, dy, ln)
        ms = dados(pid, 'manometros2d.json', g)
        G_ATUAL[0] = g
        for j, (nome, u, v, a, val) in enumerate(ms): manometro(img, nome, u, v, a * k, val, (-1 if j % 2 == 0 else 1) if len(ms) > 1 else 0, pid)
        if pid in INSET: lupa(img, pid, g, k)
    d = ImageDraw.Draw(img)
    if R9: legenda_r9(d, g)
    else:
        for (a, b, txt) in LEG:
            if a <= g < b: d.text((W // 2, int(0.74 * H)), txt, font=F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * ESC)), stroke_fill=ESCURO, anchor='mm'); _cx('legenda', txt, d.textbbox((W // 2, int(0.74 * H)), txt, font=F_LEG, anchor='mm', stroke_width=max(2, int(7 * ESC))))
    y = int((ZONA['topo'] + 12) * ESC) if R9 else int(70 * ESC)   # rodada 9: avisos abaixo da faixa superior das plataformas
    for txt in avisos_topo(g):
        if True:
            tw = d.textlength(txt, font=F_TAG); x1 = W - int(30 * ESC); x0 = x1 - tw - 36 * ESC
            d.rounded_rectangle((x0, y, x1, y + 46 * ESC), radius=23 * ESC, fill=AMARELO); _cx('aviso', txt, (x0, y, x1, y + 46 * ESC)); d.text((x0 + 18 * ESC, y + 23 * ESC), txt, font=F_TAG, fill=AZUL, anchor='lm')
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
    n = int(round(DUR * FPS)); DUR_V = n / FPS     # rodada 6: a trilha termina no ÚLTIMO QUADRO (antes passava 7 ms do vídeo)
    # JANELA_EP02="t0,t1": monta só esse trecho (testes curtos em 1080); quadros da janela, áudio recortado no mesmo trecho
    jan = [float(x) for x in os.environ['JANELA_EP02'].split(',')] if os.environ.get('JANELA_EP02') else None
    q0, q1 = (int(round(jan[0] * FPS)), int(round(jan[1] * FPS))) if jan else (0, n)
    entrada_audio = (['-ss', f'{q0 / FPS:.4f}'] if jan and au else []) + (['-i', au] if au else ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'])
    # MIXAGEM_EP02=1: o áudio já é a mixagem masterizada (−14 LUFS, pico verdadeiro medido) — entra SEM renormalizar
    filtro_audio = ((['-af', f'afade=t=out:st={DUR_V - 0.05:.4f}:d=0.05'] if not jan else []) if os.environ.get('MIXAGEM_EP02')   # fim sem clique (ambiente a −45 dBFS)
                    else (['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000'] if au else []))   # animatic: só a voz, nivelada
    titulo = 'De Olho no Invisível · Ep. 02 · ' + ('animatic (não publicar)' if PERFIL == 'animatic' else 'versão de revisão (não publicar)' if PERFIL != 'final' else 'Como a geladeira esfria sem produzir frio?')
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', *entrada_audio,
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17' if PERFIL == 'final' else '21', '-pix_fmt', 'yuv420p',
                           *filtro_audio, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{(q1 - q0) / FPS:.4f}', '-movflags', '+faststart', '-metadata', f'title={titulo}', SAIDA], stdin=subprocess.PIPE)
    for i in range(q0, q1):
        ff.stdin.write(compor(i / FPS).tobytes())
        if i % 600 == 0: print('quadro', i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', SAIDA)
