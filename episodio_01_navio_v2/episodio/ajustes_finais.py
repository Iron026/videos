"""Ajustes finais de direção do Ep01: (1) montagem curta só com os trechos corrigidos e (2) comparativo antes/depois
(lado a lado, mesmo áudio), a partir da versão de revisão anterior (ep01_revisao.mp4) e da nova (ep01_revisao_ajustes.mp4).
Uso: python3 episodio/ajustes_finais.py"""
import os, subprocess, io
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__))
ANTES, DEPOIS = os.path.join(A, 'ep01_revisao.mp4'), os.path.join(A, 'ep01_revisao_ajustes.mp4')
TRECHOS = [('1 · Empuxo', 56.4, 75.0), ('2 · Experimento bloco × casco', 83.7, 94.6), ('3 · Porto: guindaste', 96.9, 101.9),
           ('4 · Marcas do costado', 123.5, 134.0), ('5 · Conclusão', 154.4, 171.0)]
F = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
TMP = os.path.join(A, 'montagem_ajustes'); os.makedirs(TMP, exist_ok=True)
def run(*a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *a], check=True)
def tag(txt, w):   # faixa de título (PNG) sobreposta no topo
    im = Image.new('RGBA', (w, 44), (32, 43, 87, 230)); d = ImageDraw.Draw(im); f = ImageFont.truetype(F, 22)
    d.text((14, 10), txt, font=f, fill=(246, 244, 236)); p = os.path.join(TMP, f'tag_{abs(hash((txt, w)))}.png'); im.save(p); return p
curtos, comps = [], []
for k, (nome, t0, t1) in enumerate(TRECHOS):
    d = t1 - t0
    c = os.path.join(TMP, f'curto_{k}.mp4'); tg = tag(f'Ajuste {nome}  ·  {t0:.1f}–{t1:.1f} s', 540)
    run('-ss', f'{t0}', '-t', f'{d}', '-i', DEPOIS, '-i', tg, '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p[v]', '-map', '[v]', '-map', '0:a',
        '-c:v', 'libx264', '-crf', '19', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', c); curtos.append(c)
    m = os.path.join(TMP, f'comp_{k}.mp4'); ta, td = tag('ANTES', 540), tag('DEPOIS', 540)
    run('-ss', f'{t0}', '-t', f'{d}', '-i', ANTES, '-ss', f'{t0}', '-t', f'{d}', '-i', DEPOIS, '-i', ta, '-i', td, '-i', tg,
        '-filter_complex', '[0:v][2:v]overlay=0:0[a];[1:v][3:v]overlay=0:0[b];[a][b]hstack,pad=1080:1004:0:44:color=0x202B57[h];[h][4:v]overlay=270:0,format=yuv420p[v]',
        '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', m); comps.append(m)
for lista, saida in ((curtos, 'ep01_ajustes_finais_trechos.mp4'), (comps, 'comparativo_ajustes_finais.mp4')):
    txt = os.path.join(TMP, 'lista.txt'); open(txt, 'w').write(''.join(f"file '{p}'\n" for p in lista))
    run('-f', 'concat', '-safe', '0', '-i', txt, '-c', 'copy', '-movflags', '+faststart', os.path.join(A, saida)); print('ok', saida)
# folha antes/depois (JPG): instantes-chave de cada ajuste
ts = [57.5, 60.5, 68.0, 72.5, 84.5, 86.8, 88.0, 91.5, 98.3, 99.7, 126.8, 132.5, 155.3, 157.2, 160.5, 163.3, 165.5]
w, h = 180, 320; W = Image.new('RGB', (len(ts) * w, 2 * h + 60), (32, 43, 87)); dr = ImageDraw.Draw(W); f = ImageFont.truetype(F, 16)
for i, t in enumerate(ts):
    for j, src in enumerate((ANTES, DEPOIS)):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', src, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        W.paste(Image.open(io.BytesIO(raw)).resize((w, h)), (i * w, 30 + j * (h + 30)))
    dr.text((i * w + 4, 6), f'{t:.1f} s', font=f, fill=(246, 244, 236))
dr.text((4, h + 36), 'ANTES ↑   DEPOIS ↓', font=f, fill=(243, 181, 68))
W.save(os.path.join(A, 'comparativo_ajustes_finais.jpg'), quality=88); print('ok folha')
