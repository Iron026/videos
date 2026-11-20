"""Comparativo ANTES × DEPOIS do vazamento do mar no experimento casco × bloco (s08b, ~86–90,5 s): trecho lado a lado (master)
e detalhe ampliado do fundo duplo no pico do vazamento (quadros brutos). Uso: python3 episodio/comparativo_s08b.py <antes.mp4> <depois.mp4> <saida.mp4>"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); FONTE = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
antes, depois, saida = sys.argv[1:4]; tmp = os.path.join(A, '_cmps08b'); os.makedirs(tmp, exist_ok=True)
rot = lambda txt: f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=0xF6F4EC:fontsize=26:box=1:boxcolor=0x202B57@0.9:boxborderw=10:x=(w-tw)/2:y=h-60"
fc = (f"[0:v]scale=540:960,setsar=1,{rot('ANTES')}[l];[1:v]scale=540:960,setsar=1,{rot('DEPOIS')}[r];"
      f"[l][r]hstack=2,pad=1080:1030:0:70:color=0x202B57,drawtext=fontfile={FONTE}:text='Casco × bloco (85,5–91 s)':fontcolor=0xF3B544:fontsize=30:x=(w-tw)/2:y=20[v]")
o1 = os.path.join(tmp, 'lado.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '85.5', '-t', '5.5', '-i', antes, '-ss', '85.5', '-t', '5.5', '-i', depois, '-filter_complex', fc,
                '-map', '[v]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p', o1], check=True)
f = lambda s: ImageFont.truetype(FONTE, s); partes = [o1]
for k, q in enumerate((120, 150, 180)):   # 87,85 / 88,85 / 89,85 s
    box = (150, 520, 470, 640)
    a = Image.open(os.path.join(A, 'quadros_revisao_antes8', 's08b', f'q{q:04d}.jpg')).crop(box); b = Image.open(os.path.join(A, 'quadros_revisao', 's08b', f'q{q:04d}.jpg')).crop(box)
    z = 1050 / a.width; a = a.resize((1050, int(a.height * z)), Image.NEAREST); b = b.resize(a.size, Image.NEAREST)
    W = Image.new('RGB', (1080, 1030), (32, 43, 87)); d = ImageDraw.Draw(W)
    d.text((540, 40), f'Detalhe ampliado · fundo duplo · {83.85 + q / 30:.2f} s'.replace('.', ','), font=f(30), fill=(243, 181, 68), anchor='mm')
    W.paste(a, (15, 90)); d.text((540, 90 + a.height + 30), 'ANTES', font=f(26), fill=(246, 244, 236), anchor='mm')
    y2 = 90 + a.height + 60; W.paste(b, (15, y2)); d.text((540, y2 + b.height + 30), 'DEPOIS', font=f(26), fill=(246, 244, 236), anchor='mm')
    p = os.path.join(tmp, f'd{k}.png'); W.save(p)
    if k == 1: W.save(os.path.join(A, 'ep01_s08b_detalhe.jpg'), quality=92)
    o = os.path.join(tmp, f'd{k}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', '3.5', '-i', p, '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-r', '30', '-pix_fmt', 'yuv420p', o], check=True); partes.append(o)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
for p in os.listdir(tmp): os.remove(os.path.join(tmp, p))
os.rmdir(tmp); print('ok', saida)
