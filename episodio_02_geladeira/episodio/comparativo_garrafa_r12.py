"""Rodada 12 — comparativo ANTES (definitivo R11) × DEPOIS (definitivo R12) da garrafa nas emendas em que a ordem de
desenho dos transparentes trocava (H2 em 1:53 = o defeito relatado; C4 e H1 = mesmo mecanismo, achados pela varredura).
Lê os quadros dos MP4 MONTADOS (o que o espectador vê). Gera:
  previas_r12/garrafa_antes_depois_r12.png  → recortes 1:1 em volta da garrafa, 4 quadros por emenda (2 antes, 2 depois
                                               da troca), linha R11 × linha R12, com o brilho médio da água em cada quadro
  previas_r12/ab_garrafa_1m53_r11_x_r12.mp4 → lado a lado (esq. R11, dir. R12): quadro inteiro em tempo real
                                               (111,9–114,3 s) e depois o recorte ampliado 2× em câmera lenta 4× (112,8–113,5 s); sem áudio
Uso (em episodio/): python3 comparativo_garrafa_r12.py <r11.mp4> <r12.mp4>"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1080, 1920, 30
R11, R12 = sys.argv[1], sys.argv[2]; OUT = os.path.join(A, 'previas_r12'); os.makedirs(OUT, exist_ok=True)
FONTE = os.path.join(A, '..', 'fontes') if os.path.isdir(os.path.join(A, '..', 'fontes')) else None
fonte = lambda t, s: ImageFont.truetype(os.path.join(FONTE, f'Montserrat-{t}.ttf'), s) if FONTE else ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
# emenda = 1º quadro do VÍDEO que mostra o quadro da cena com a ordem nova; recorte 280 × 460 centrado na garrafa
# (caixas projetadas da malha garrafa_agua/garrafa_pet com a câmera exportada); água = miolo da garrafa
EMENDAS = [dict(nome='H2 · 1:53,1 (defeito relatado)', q=3393, rec=(139, 862, 419, 1322), agua=(258, 1080, 302, 1200)),
           dict(nome='C4 · 0:44,4', q=1332, rec=(127, 893, 407, 1353), agua=(245, 1060, 290, 1190)),
           dict(nome='H1 · 1:49,6', q=3287, rec=(47, 1460, 327, 1920), agua=(150, 1650, 215, 1760))]


def quadros(f, q0, n):
    """n quadros a partir do quadro q0 do vídeo (busca exata: -ss antes da entrada decodifica do quadro-chave e descarta)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{q0 / FPS - 0.001:.4f}', '-i', f, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H, W, 3)


def tc(q):
    t = q / FPS; return f'{int(t // 60)}:{t % 60:05.2f}'.replace('.', ',')


# ---------------------------------------------------------------- folha de recortes
rw, rh = 280, 460; mx, cab, rot = 24, 70, 150
folha = Image.new('RGB', (rot + 4 * (rw + mx) + mx, sum(cab + 2 * (rh + 40) + mx for _ in EMENDAS) + 110), (24, 28, 36))
d = ImageDraw.Draw(folha); F1, F2, F3 = fonte(800, 34), fonte(700, 24), fonte(700, 20)
d.text((mx, 30), 'Garrafa: definitivo R11 (antes) × R12 (depois) — recortes 1:1 do vídeo montado', font=F1, fill=(245, 240, 230))
y = 110; medidas = {}
for e in EMENDAS:
    a, b = quadros(R11, e['q'] - 2, 4), quadros(R12, e['q'] - 2, 4)
    d.text((mx, y + 18), e['nome'] + '  —  a troca de ordem acontecia entre a 2ª e a 3ª coluna', font=F2, fill=(255, 214, 90)); y += cab
    medidas[e['nome']] = {}
    for lin, (V, nome) in enumerate(((a, 'R11\nantes'), (b, 'R12\ndepois'))):
        d.multiline_text((mx, y + rh // 2 - 30), nome, font=F2, fill=(245, 240, 230), spacing=6)
        for k in range(4):
            x0, y0, x1, y1 = e['rec']; im = Image.fromarray(V[k][y0:y1, x0:x1]); X = rot + k * (rw + mx)
            folha.paste(im, (X, y)); ax0, ay0, ax1, ay1 = e['agua']
            lum = float(V[k][ay0:ay1, ax0:ax1].astype(np.float32).mean()); medidas[e['nome']].setdefault(nome.split()[0], []).append(round(lum, 1))
            d.text((X, y + rh + 6), f'{tc(e["q"] - 2 + k)}  água {lum:5.1f}', font=F3, fill=(200, 205, 215))
            if lin == 0: d.rectangle((X - 2, y - 2, X + rw + 1, y + rh + 1), outline=(70, 76, 90))
        y += rh + 40
    y += mx
folha.save(os.path.join(OUT, 'garrafa_antes_depois_r12.png'), optimize=True)

# ---------------------------------------------------------------- vídeo lado a lado do 1:53
q0, q1 = int(round(111.9 * FPS)), int(round(114.3 * FPS)); z0, z1 = int(round(112.8 * FPS)), int(round(113.5 * FPS))
a, b = quadros(R11, q0, q1 - q0), quadros(R12, q0, q1 - q0)
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x960', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, 'ab_garrafa_1m53_r11_x_r12.mp4')], stdin=subprocess.PIPE)
FT = fonte(800, 30); FS = fonte(700, 22)


def placa(img, esq, dir_, sub):
    dd = ImageDraw.Draw(img)
    for x, t in ((20, esq), (560, dir_)):
        dd.rounded_rectangle((x, 16, x + dd.textlength(t, font=FT) + 28, 62), radius=22, fill=(255, 214, 90)); dd.text((x + 14, 39), t, font=FT, fill=(20, 40, 80), anchor='lm')
    dd.text((540, 944), sub, font=FS, fill=(245, 240, 230), anchor='ms', stroke_width=2, stroke_fill=(0, 0, 0))
    dd.line((540, 0, 540, 960), fill=(245, 240, 230), width=3)


for i in range(q1 - q0):   # tempo real, quadro inteiro reduzido a 540 × 960 de cada lado
    im = Image.new('RGB', (1080, 960)); im.paste(Image.fromarray(a[i]).resize((540, 960), Image.LANCZOS), (0, 0)); im.paste(Image.fromarray(b[i]).resize((540, 960), Image.LANCZOS), (540, 0))
    placa(im, 'R11 · antes', 'R12 · depois', f'tempo real  ·  {tc(q0 + i)}'); ff.stdin.write(im.tobytes())
x0, y0, x1, y1 = EMENDAS[0]['rec']; cw, ch = 540, int(round(540 * (y1 - y0) / (x1 - x0)))
for i in range(z0 - q0, z1 - q0):   # recorte ampliado, cada quadro repetido 4× (câmera lenta 4×)
    im = Image.new('RGB', (1080, 960), (24, 28, 36))
    for j, V in enumerate((a, b)):
        c = Image.fromarray(V[i][y0:y1, x0:x1]).resize((cw, ch), Image.LANCZOS).crop((0, max(0, (ch - 960) // 2), cw, max(0, (ch - 960) // 2) + min(ch, 960)))
        im.paste(c, (540 * j, max(0, (960 - c.size[1]) // 2)))
    placa(im, 'R11 · antes', 'R12 · depois', f'recorte ampliado, câmera lenta 4×  ·  {tc(q0 + i)}')
    for _ in range(4): ff.stdin.write(im.tobytes())
ff.stdin.close(); ff.wait()
json.dump(dict(brilho_medio_agua=medidas, emendas=EMENDAS), open(os.path.join(OUT, 'garrafa_antes_depois_r12.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(medidas, ensure_ascii=False, indent=1))
