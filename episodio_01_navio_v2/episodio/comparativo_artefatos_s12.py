"""Comparativo da correção dos artefatos da avaria (137,0–154,6 s): ANTES × DEPOIS lado a lado (do master) e detalhes ampliados
das superfícies corrigidas (dos quadros 3D brutos). Uso: python3 episodio/comparativo_artefatos_s12.py <master_antes.mp4> <master_depois.mp4> <saida.mp4>"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); FONTE = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
antes, depois, saida = sys.argv[1:4]; tmp = os.path.join(A, '_cmps12'); os.makedirs(tmp, exist_ok=True)
AZUL, CREME, OURO = (32, 43, 87), (246, 244, 236), (243, 181, 68)
# detalhes: (quadro do s12, recorte x0, y0, x1, y1, legenda)
DET = [(90, 150, 330, 400, 560, '140,0 s · parede do porão'), (180, 0, 420, 250, 600, '143,0 s · casco junto à água'),
       (270, 180, 380, 440, 600, '146,0 s · parede do porão'), (315, 0, 380, 260, 680, '147,5 s · costado e fundo'),
       (450, 380, 460, 540, 720, '152,0 s · antepara e água'), (510, 0, 380, 260, 640, '154,0 s · compartimento')]
f = lambda s: ImageFont.truetype(FONTE, s)
for k, (q, x0, y0, x1, y1, leg) in enumerate(DET):
    a = Image.open(os.path.join(A, 'quadros_revisao_antes7', 's12', f'q{q:04d}.jpg')).crop((x0, y0, x1, y1))
    b = Image.open(os.path.join(A, 'quadros_revisao', 's12', f'q{q:04d}.jpg')).crop((x0, y0, x1, y1))
    z = min(510 / a.width, 760 / a.height); a = a.resize((int(a.width * z), int(a.height * z)), Image.NEAREST); b = b.resize(a.size, Image.NEAREST)
    W = Image.new('RGB', (1080, 1030), AZUL); d = ImageDraw.Draw(W)
    d.text((540, 40), 'Detalhe ampliado · ' + leg, font=f(30), fill=OURO, anchor='mm')
    for j, (im, t) in enumerate(((a, 'ANTES'), (b, 'DEPOIS'))):
        x = 15 + j * 535 + (510 - im.width) // 2; W.paste(im, (x, 90)); d.text((15 + j * 535 + 255, 90 + im.height + 40), t, font=f(28), fill=CREME, anchor='mm')
    W.save(os.path.join(tmp, f'd{k}.png'))
partes = []
# 1) avaria inteira lado a lado (mesmos instantes, do master)
o = os.path.join(tmp, 'lado.mp4')
rot = lambda txt: f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=0xF6F4EC:fontsize=26:box=1:boxcolor=0x202B57@0.9:boxborderw=10:x=(w-tw)/2:y=h-60"
fc = (f"[0:v]scale=540:960,setsar=1,{rot('ANTES')}[l];[1:v]scale=540:960,setsar=1,{rot('DEPOIS')}[r];"
      f"[l][r]hstack=2,pad=1080:1030:0:70:color=0x202B57,drawtext=fontfile={FONTE}:text='Avaria e inundação (137–154,6 s)':fontcolor=0xF3B544:fontsize=30:x=(w-tw)/2:y=20[v]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '136.8', '-t', '18.0', '-i', antes, '-ss', '136.8', '-t', '18.0', '-i', depois, '-filter_complex', fc,
                '-map', '[v]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p', o], check=True); partes.append(o)
# 2) detalhes ampliados (3,5 s cada)
for k in range(len(DET)):
    o = os.path.join(tmp, f'd{k}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', '3.5', '-i', os.path.join(tmp, f'd{k}.png'), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-r', '30', '-pix_fmt', 'yuv420p', o], check=True); partes.append(o)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
Image.open(os.path.join(tmp, 'd2.png')).save(os.path.join(A, 'ep01_artefatos_s12_detalhe.jpg'), quality=92)
for p in os.listdir(tmp): os.remove(os.path.join(tmp, p))
os.rmdir(tmp); print('ok', saida)
