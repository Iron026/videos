"""Monta o Episódio 01 no tempo GLOBAL da narração real: segmentos renderizados (motor v2), fusões curtas nas
emendas, rótulos da marca projetados por quadro (rotulos2d.json), legendas alinhadas com as palavras reais
(palavras.json), assinatura animada e áudio (audio_ep01.wav) com loudness −14 LUFS / −1,5 dBTP.
Uso: python3 episodio/montar_ep01.py <previa|revisao|final> [saida.mp4]"""
import os, sys, json, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..')
PERFIL = sys.argv[1] if len(sys.argv) > 1 else 'previa'
W, H = {'previa': (540, 960), 'previa30': (540, 960), 'teste': (540, 960), 'revisao': (540, 960), 'final': (1080, 1920)}[PERFIL]
PASSO = 3 if PERFIL == 'previa' else 1
T_INI = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0      # trecho (previa30: amostras a 30 fps)
T_FIM = float(sys.argv[4]) if len(sys.argv) > 4 else None
FPS = 30; DUR = 168.0; ESC = W / 1080   # termina quando o movimento do último plano do navio conclui (sem assinatura)
SAIDA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, f'ep01_{PERFIL}.mp4')
FONTE = os.path.join(RAIZ, 'fontes')
F_LEG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(58 * ESC))
F_ROT = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(47 * ESC))   # rótulos 30% maiores (celular)
F_TAG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), int(26 * ESC))
AZUL, CREME, AMARELO, ESCURO = (32, 43, 87), (246, 244, 236), (243, 181, 68), (16, 22, 46)

# (nome, início, fim) no tempo global; 's01' = plano 1 aprovado do animatic r2; 'ass' = assinatura
SEGS = [('s01', 0.00, 4.40), ('s02', 4.40, 15.10), ('s03', 15.10, 30.30), ('s04', 30.30, 41.55), ('s05', 41.55, 48.00),
        ('s0607', 48.00, 63.10), ('s0607b', 63.10, 65.80), ('s0607_2', 65.80, 74.85), ('s08a', 74.85, 83.85), ('s08b', 83.85, 94.55), ('s09', 94.55, 117.20), ('s10', 117.20, 123.65),
        ('s11', 123.65, 134.00), ('s12x', 134.00, 137.00), ('s12', 137.00, 154.60), ('s13', 154.60, DUR)]
FUSAO = 0.20
FUSOES = {'s04': 0.90}   # passagem de tempo do estaleiro (casco em andamento → navio pronto): fusão mais longa + aviso
# avisos honestos de tempo (canto superior direito)
CHIPS = [(2.05, 3.70, 'Câmera lenta'), (29.95, 32.0, 'Meses depois'), (41.6, 48.0, 'Tempo acelerado'), (76.15, 82.1, 'Câmera lenta'),
         (105.4, 117.2, 'Tempo acelerado'), (137.0, 146.0, 'Tempo acelerado')]


REENQUADRADOS = ['s0607', 's08b', 's11', 's13']   # ajustes finais: segmentos reenquadrados em boa parte (s09 mudou só 2,5 s)
ALIAS = {'s0607_2': ('s0607', 48.00)}   # mesmo segmento renderizado, retomado depois do respiro (base de tempo original)


def pasta(nome):
    nome = ALIAS.get(nome, (nome,))[0]
    if nome == 's01':   # abertura: re-renderizada com o novo aço maciço (o original aprovado fica em animatic/quadros_r2_p1)
        d = os.path.join(A, f'quadros_{"revisao" if PERFIL in ("teste", "previa", "previa30") else PERFIL}', 's01')
        return (d if os.path.isdir(d) and os.listdir(d) else os.path.join(RAIZ, 'animatic', 'quadros_r2_p1')), 1
    if nome == 'ass': return os.path.join(A, 'assinatura_q'), 1
    if PERFIL == 'previa30' and os.path.isdir(os.path.join(A, 'quadros_previa30', nome)): return os.path.join(A, 'quadros_previa30', nome), 1
    if PERFIL == 'teste': return os.path.join(A, 'quadros_revisao', nome), 1
    return os.path.join(A, f'quadros_{"previa" if PERFIL == "previa30" else PERFIL}', nome), PASSO


_cache = {}
GRADE = {}
from grade_ep01 import graduar
GRADE_ON = os.environ.get('GRADE_EP01', '1') == '1'
def nivelar(nome, img):
    nome = ALIAS.get(nome, (nome,))[0]
    if nome in ('s01', 'ass'): return img
    if not GRADE:
        for n_, _, _ in SEGS:
            if n_ in ('s01', 'ass') or n_ in ALIAS: continue
            d = os.path.join(A, 'quadros_previa', n_)   # estatísticas de cor medidas na prévia (mesmas cenas; vale para todos os perfis)
            if not os.path.isdir(d): d, passo = pasta(n_)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))[::8]
            st = [np.asarray(Image.open(os.path.join(d, f)).convert('HSV'), dtype=np.float32).reshape(-1, 3).mean(0) for f in fs]
            GRADE[n_] = np.mean(st, 0)
        GRADE['_alvo'] = np.median(np.array([v for v in GRADE.values()]), 0)
        # ajustes finais: segmentos reenquadrados medem a cor nos quadros novos (o alvo continua o mesmo da versão aprovada)
        for n_ in REENQUADRADOS:
            d = os.path.join(A, 'quadros_revisao', n_)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))[::8] if os.path.isdir(d) else []
            if fs: GRADE[n_] = np.mean([np.asarray(Image.open(os.path.join(d, f)).resize((270, 480)).convert('HSV'), dtype=np.float32).reshape(-1, 3).mean(0) for f in fs], 0)
        print('nivelamento', {k: [round(float(x)) for x in v[1:]] for k, v in GRADE.items()})
    alvo = GRADE['_alvo']
    v = GRADE[nome]
    gv = min(1.12, max(0.9, (alvo[2] / max(v[2], 1)) ** 0.5)); gs = min(1.15, max(0.88, (alvo[1] / max(v[1], 1)) ** 0.5))
    from PIL import ImageEnhance
    return ImageEnhance.Color(ImageEnhance.Brightness(img).enhance(gv)).enhance(gs)


def quadro_seg(nome, g0, g):
    d, passo = pasta(nome)
    if d not in _cache: _cache[d] = sorted(int(f[1:5]) for f in os.listdir(d) if f.endswith('.jpg'))
    g0 = ALIAS.get(nome, (None, g0))[1]
    idx = _cache[d]; f = int(round((g - g0) * FPS)); f = min(max(f, idx[0]), idx[-1])
    f = idx[int(np.searchsorted(idx, f, side='right')) - 1]
    img = nivelar(nome, Image.open(os.path.join(d, f'q{f:04d}.jpg')).convert('RGB').resize((W, H), Image.BICUBIC))
    return graduar(img) if GRADE_ON else img          # correção de cor sutil só na imagem 3D (rótulos e legendas entram depois)


ROT = {}
def rotulos(nome, g0, g):
    if nome in ('s01', 'ass'): return []
    if nome not in ROT:
        p = os.path.join(A, 'cenas', ALIAS.get(nome, (nome,))[0], 'rotulos2d.json'); ROT[nome] = json.load(open(p))['quadros'] if os.path.exists(p) else []
    q = ROT[nome]; g0 = ALIAS.get(nome, (None, g0))[1]; f = int(round((g - g0) * FPS))
    return q[f] if 0 <= f < len(q) else []


def desenhar_rotulo(img, txt, u, v, a, dx, dy):
    if a <= 0.01: return
    camada = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(camada)
    ax, ay = u * W, v * H; bx, by = ax + dx * W, ay + dy * H
    tw = d.textlength(txt, font=F_ROT); pad = 20 * ESC; h = 47 * ESC + 2 * pad * 0.55
    w = tw + 2 * pad
    lx = bx if dx >= 0 else bx - w; lx = min(max(lx, 0.04 * W), 0.96 * W - w)
    ly = min(max(by - h / 2, 0.09 * H), 0.60 * H - h)
    ex = min(max(ax, lx), lx + w); ey = ly + h / 2
    al = int(255 * a)
    d.line([(ax, ay), (ex, ey)], fill=CREME + (al,), width=max(2, int(4 * ESC)))
    r = 11 * ESC; d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=AMARELO + (al,), outline=AZUL + (al,), width=max(1, int(3 * ESC)))
    d.rounded_rectangle([lx, ly, lx + w, ly + h], radius=h / 2, fill=AZUL + (int(240 * a),))
    d.rounded_rectangle([lx + h * 0.3, ly + h - 5 * ESC, lx + w - h * 0.3, ly + h], radius=2, fill=AMARELO + (al,))
    d.text((lx + pad, ly + h / 2), txt, font=F_ROT, fill=CREME + (al,), anchor='lm')
    img.paste(Image.alpha_composite(img.convert('RGBA'), camada).convert('RGB'))


def legendas():
    p = json.load(open(os.path.join(os.environ.get('NARRACAO_EP01_DIR', os.path.join(RAIZ, 'voz', 'narracao_ep01', 'trabalho')), 'palavras.json')))   # legendas seguem a narração usada
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
SEM_LEGENDAS = os.environ.get('SEM_LEGENDAS') == '1'   # master de imagem: legendas entram depois (episodio/trocar_audio.py)


FIM_ESCURO = False   # sem escurecimento final: o vídeo termina no plano do navio
_MASC = Image.open(os.path.join(RAIZ, 'mascote', 'mascote_frente_100.png')).convert('RGBA')
def assinatura_discreta(img, g, t0=166.45):
    """Identificação do canal integrada ao último plano do navio (sem cena própria): mascote pequeno em círculo + nome."""
    if g < t0: return
    a = min(1.0, (g - t0) / 0.8); a = a * a * (3 - 2 * a)
    camada = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(camada)
    f = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), int(36 * ESC)); txt = 'De Olho no Invisível'
    r = int(34 * ESC); tw = d.textlength(txt, font=f); gap = int(14 * ESC); wtot = 2 * r + gap + tw
    x0 = (W - wtot) / 2; yc = int(0.865 * H) - int(6 * ESC * (1 - a))
    d.rounded_rectangle([x0 - 16 * ESC, yc - r - 10 * ESC, x0 + wtot + 22 * ESC, yc + r + 10 * ESC], radius=r + 10 * ESC, fill=AZUL + (int(200 * a),))
    d.ellipse([x0, yc - r, x0 + 2 * r, yc + r], fill=CREME + (int(255 * a),))
    m = _MASC.resize((int(2 * r * 1.25), int(2 * r * 1.25)), Image.LANCZOS); mk = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(mk).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    m = m.crop(((m.width - 2 * r) // 2, int(m.height * 0.06), (m.width - 2 * r) // 2 + 2 * r, int(m.height * 0.06) + 2 * r))
    alfa = Image.fromarray((np.asarray(m.split()[3], dtype=np.float32) * (np.asarray(mk, dtype=np.float32) / 255) * a).astype(np.uint8)); m.putalpha(alfa)
    camada.alpha_composite(m, (int(x0), int(yc - r)))
    d.text((x0 + 2 * r + gap, yc), txt, font=f, fill=CREME + (int(255 * a),), anchor='lm')
    d.rounded_rectangle([x0 + 2 * r + gap, yc + 27 * ESC, x0 + 2 * r + gap + tw * 0.42, yc + 32 * ESC], radius=2, fill=AMARELO + (int(255 * a),))
    img.paste(Image.alpha_composite(img.convert('RGBA'), camada).convert('RGB'))


def compor(g):
    fz = lambda i: FUSOES.get(SEGS[i][0], FUSAO)          # fusão na entrada do segmento i
    fs = lambda i: fz(i + 1) if i + 1 < len(SEGS) else FUSAO  # fusão na saída do segmento i
    ativos = [(n, a, b, fz(i)) for i, (n, a, b) in enumerate(SEGS) if a - fz(i) / 2 <= g < b + fs(i) / 2]
    if len(ativos) == 1: n, a, b, _ = ativos[0]; img = quadro_seg(n, a, g); rots = [(n, a, 1.0)]
    else:
        (n1, a1, b1, _), (n2, a2, b2, f2) = ativos[0], ativos[1]
        k = min(1.0, max(0.0, (g - (a2 - f2 / 2)) / f2)); k = k * k * (3 - 2 * k)
        img = Image.blend(quadro_seg(n1, a1, g), quadro_seg(n2, a2, g), k); rots = [(n1, a1, 1 - k), (n2, a2, k)]
    for (n, a, k) in rots:
        for (txt, u, v, al, dx, dy) in rotulos(n, a, g): desenhar_rotulo(img, txt, u, v, al * k, dx, dy)
    d = ImageDraw.Draw(img)
    for (a, b, txt) in ([] if SEM_LEGENDAS else LEG):
        if a <= g < b:
            d.text((W // 2, int(0.70 * H)), txt, font=F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * ESC)), stroke_fill=ESCURO, anchor='mm')
    for (a, b, txt) in CHIPS:
        if a <= g < b:
            tw = d.textlength(txt, font=F_TAG); x1 = W - int(30 * ESC); x0 = x1 - tw - 36 * ESC; y0 = int(70 * ESC)
            d.rounded_rectangle((x0, y0, x1, y0 + 46 * ESC), radius=23 * ESC, fill=AMARELO)
            d.text((x0 + 18 * ESC, y0 + 23 * ESC), txt, font=F_TAG, fill=AZUL, anchor='lm')
    if FIM_ESCURO and g > DUR - 0.5:   # fim natural: o último plano escurece levemente para o azul da marca
        k = (g - (DUR - 0.5)) / 0.5; img.paste(Image.blend(img, Image.new('RGB', img.size, AZUL), 0.85 * k * k)); d = ImageDraw.Draw(img)
    if True:
        tag = 'VERSÃO DE REVISÃO · não publicar'; x0, y0 = int(30 * ESC), int(70 * ESC); tw = d.textlength(tag, font=F_TAG)
        d.rounded_rectangle((x0, y0, x0 + tw + 36 * ESC, y0 + 46 * ESC), radius=23 * ESC, fill=AZUL)
        d.text((x0 + 18 * ESC, y0 + 23 * ESC), tag, font=F_TAG, fill=CREME, anchor='lm')
    return img


def loudness(au):
    """Ganho + limitador para −14 LUFS e pico verdadeiro ≤ −1,6 dBTP MEDIDOS NO AAC FINAL (a codificação AAC cria picos
    entre amostras: o teto do limitador desce até o pico verdadeiro do arquivo codificado ficar dentro da meta)."""
    tmp = os.path.join(A, f'_teste_{os.getpid()}.m4a')   # nome único: montagens simultâneas não colidem
    def filtro(g, lim): return f'volume={g:.2f}dB,alimiter=limit={lim:.2f}dB:attack=3:release=60:level=disabled:asc=1'
    def medir(g, lim):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', au, '-af', filtro(g, lim), '-c:a', 'aac', '-b:a', '192k', tmp], check=True)
        e = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
        e = e[e.rfind('Summary:'):]
        return float(re.search(r'I:\s+(-?[\d.]+) LUFS', e).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', e).group(1))
    g, lim = 0.0, -2.2
    for _ in range(8):
        i, tp = medir(g, lim)
        if abs(i + 14) < 0.15 and tp <= -1.6: break
        if tp > -1.6: lim -= tp + 1.6 + 0.15
        if abs(i + 14) >= 0.15: g += -14 - i
    os.remove(tmp); print('ganho', round(g, 2), 'dB · teto do limitador', round(lim, 2), 'dB →', i, 'LUFS ·', tp, 'dBTP (AAC)'); return filtro(g, lim)


if __name__ == '__main__':
    au = os.environ.get('AUDIO_EP01', os.path.join(A, 'audio_ep01.wav')); af = loudness(au)   # AUDIO_EP01: outra mixagem (comparações)
    t_fim = T_FIM if T_FIM is not None else DUR
    n = int(round((t_fim - T_INI) * FPS))
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-ss', f'{T_INI:.3f}', '-i', au, '-af', af, '-c:v', 'libx264', '-preset', 'medium', '-crf', os.environ.get('CRF_EP01', '20' if PERFIL != 'final' else '17'),
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                           '-metadata', 'title=De Olho no Invisível · Ep. 01 · versão de revisão (não publicar)', SAIDA], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(compor(T_INI + i / FPS).tobytes())
        if i % 300 == 0: print('quadro', i, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('ok', SAIDA)
