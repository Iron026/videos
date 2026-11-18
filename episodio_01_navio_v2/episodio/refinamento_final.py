"""Refinamento final do Ep01: comparativo antes/depois (lado a lado) dos trechos corrigidos e montagem curta.
Antes = ep01_revisao_ajustes.mp4 (com tela de assinatura, 171 s) · Depois = ep01_revisao_refinada.mp4 (169,5 s).
Uso: python3 episodio/refinamento_final.py"""
import os, subprocess, io
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__))
ANTES, DEPOIS = os.path.join(A, 'ep01_revisao_ajustes.mp4'), os.path.join(A, 'ep01_revisao_refinada.mp4')
# (nome, início, fim antes, fim depois)
TRECHOS = [('1 · Aço do bloco (abertura)', 0.0, 4.4, 4.4), ('2 · Soldagem', 23.3, 26.2, 26.2),
           ('3 · Empuxo: transição contínua', 56.4, 63.2, 63.2), ('4 · Retomada do bloco', 74.4, 84.0, 84.0),
           ('5 · Final sem tela de assinatura', 159.0, 171.0, 169.5)]
F = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
TMP = os.path.join(A, 'montagem_refinamento'); os.makedirs(TMP, exist_ok=True)
def run(*a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *a], check=True)
def tag(txt, w, nome):
    im = Image.new('RGBA', (w, 44), (32, 43, 87, 230)); d = ImageDraw.Draw(im); d.text((14, 10), txt, font=ImageFont.truetype(F, 22), fill=(246, 244, 236))
    p = os.path.join(TMP, nome + '.png'); im.save(p); return p
ta, td = tag('ANTES', 540, 'antes'), tag('DEPOIS', 540, 'depois')
curtos, comps = [], []
for k, (nome, t0, t1a, t1d) in enumerate(TRECHOS):
    da, dd = t1a - t0, t1d - t0; dmax = max(da, dd)
    tg = tag(f'{nome}  ·  {t0:.1f}–{t1d:.1f} s', 540, f't{k}')
    c = os.path.join(TMP, f'curto_{k}.mp4')
    run('-ss', f'{t0}', '-t', f'{dd}', '-i', DEPOIS, '-i', tg, '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p[v]', '-map', '[v]', '-map', '0:a',
        '-c:v', 'libx264', '-crf', '19', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', c); curtos.append(c)
    m = os.path.join(TMP, f'comp_{k}.mp4')
    run('-ss', f'{t0}', '-t', f'{da}', '-i', ANTES, '-ss', f'{t0}', '-t', f'{dd}', '-i', DEPOIS, '-i', ta, '-i', td, '-i', tg,
        '-filter_complex', f'[0:v]tpad=stop_mode=clone:stop_duration={dmax - da + 0.05:.3f}[a0];[1:v]tpad=stop_mode=add:color=0x202B57:stop_duration={dmax - dd + 0.05:.3f}[b0];'
        f'[a0][2:v]overlay=0:0[a];[b0][3:v]overlay=0:0[b];[a][b]hstack,pad=1080:1004:0:44:color=0x202B57[h];[h][4:v]overlay=270:0,trim=duration={dmax:.3f},format=yuv420p[v];'
        f'[1:a]apad,atrim=duration={dmax:.3f}[au]',
        '-map', '[v]', '-map', '[au]', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', m); comps.append(m)
for lista, saida in ((curtos, 'ep01_refinamento_trechos.mp4'), (comps, 'comparativo_refinamento.mp4')):
    txt = os.path.join(TMP, 'lista.txt'); open(txt, 'w').write(''.join(f"file '{p}'\n" for p in lista))
    run('-f', 'concat', '-safe', '0', '-i', txt, '-c', 'copy', '-movflags', '+faststart', os.path.join(A, saida)); print('ok', saida)
# folha antes/depois
ts = [(1.2, 1.2), (3.0, 3.0), (24.0, 24.0), (24.9, 24.9), (57.6, 57.6), (58.9, 58.9), (59.6, 59.6), (61.4, 61.4), (74.95, 74.95), (75.6, 75.6),
      (76.3, 76.3), (77.5, 77.5), (166.8, 166.8), (168.0, 168.0), (169.2, 169.2)]
w, h = 180, 320; W = Image.new('RGB', (len(ts) * w, 2 * h + 60), (32, 43, 87)); dr = ImageDraw.Draw(W); f = ImageFont.truetype(F, 16)
for i, (t, t2) in enumerate(ts):
    for j, (src, tt) in enumerate(((ANTES, t), (DEPOIS, t2))):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(tt), '-i', src, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        W.paste(Image.open(io.BytesIO(raw)).resize((w, h)), (i * w, 30 + j * (h + 30)))
    dr.text((i * w + 4, 6), f'{t:.1f} s', font=f, fill=(246, 244, 236))
dr.text((4, h + 36), 'ANTES ↑   DEPOIS ↓', font=f, fill=(243, 181, 68))
W.save(os.path.join(A, 'comparativo_refinamento.jpg'), quality=88); print('ok folha')
