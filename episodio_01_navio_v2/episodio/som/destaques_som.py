"""Vídeo curto com os momentos-chave do sound design (recortes da versão integral, com título de cada sequência)."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); V = os.path.join(EP, 'ep01_revisao_som.mp4')
TR = [('Bloco de aço e navio', 0.0, 15.1), ('Estaleiro: encaixe e solda', 21.0, 27.5), ('Dique seco', 41.4, 48.2), ('Retomada e experimento', 74.6, 88.6),
      ('Portêineres e contêineres', 97.4, 106.2), ('Avaria e inundação', 133.8, 152.6), ('Conclusão e fim natural', 154.4, 168.0)]
F = ImageFont.truetype(os.path.join(EP, '..', 'fontes', 'Montserrat-800.ttf'), 22); T = os.path.join(EP, 'montagem_som'); os.makedirs(T, exist_ok=True); partes = []
for k, (nome, a, b) in enumerate(TR):
    im = Image.new('RGBA', (540, 44), (32, 43, 87, 230)); ImageDraw.Draw(im).text((14, 10), f'Som {k + 1} · {nome}', font=F, fill=(246, 244, 236)); p = os.path.join(T, f't{k}.png'); im.save(p)
    o = os.path.join(T, f'p{k}.mp4'); af = f'afade=t=in:d=0.08,afade=t=out:st={b - a - 0.25:.2f}:d=0.25'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', V, '-i', p, '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p[v]',
                    '-map', '[v]', '-map', '0:a', '-af', af, '-c:v', 'libx264', '-crf', '19', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', o], check=True); partes.append(o)
open(os.path.join(T, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(T, 'l.txt'), '-c', 'copy', '-movflags', '+faststart', os.path.join(EP, 'ep01_som_destaques.mp4')], check=True)
print('ok')
