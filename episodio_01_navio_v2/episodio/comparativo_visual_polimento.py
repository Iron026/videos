"""Comparativo visual ANTES × DEPOIS do polimento (lado a lado, mesmos instantes, com o áudio da versão nova).
Antes = montagem de revisão anterior (ep01_revisao_som.mp4); depois = nova montagem.
Uso: python3 episodio/comparativo_visual_polimento.py <antes.mp4> <depois.mp4> <saida.mp4>"""
import os, sys, subprocess
A = os.path.dirname(os.path.abspath(__file__)); FONTE = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
TRECHOS = [(8.9, 13.8, 'Espuma e onda de proa'), (29.2, 32.0, 'Salto da superestrutura: passagem de tempo'),
           (49.6, 54.0, 'Face subaquática do diorama'), (77.0, 82.2, 'Água em 1:19 (77–82 s)'),
           (143.2, 148.2, 'Leitura da inclinação (proa × popa)'), (155.5, 160.5, 'Conclusão: vista submersa')]
antes, depois, saida = sys.argv[1:4]; tmp = os.path.join(A, '_cmpv'); os.makedirs(tmp, exist_ok=True); partes = []
for j, (a, b, tit) in enumerate(TRECHOS):
    o = os.path.join(tmp, f'{j}.mp4'); d = b - a
    rot = lambda txt, x: f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=0xF6F4EC:fontsize=26:box=1:boxcolor=0x202B57@0.9:boxborderw=10:x={x}:y=h-60"
    fc = (f"[0:v]scale=540:960,setsar=1,{rot('ANTES', '(w-tw)/2')}[l];[1:v]scale=540:960,setsar=1,{rot('DEPOIS', '(w-tw)/2')}[r];"
          f"[l][r]hstack=2,pad=1080:1030:0:70:color=0x202B57,drawtext=fontfile={FONTE}:text='{tit.replace(":", "\\:")}':fontcolor=0xF3B544:fontsize=30:x=(w-tw)/2:y=20[v]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{d}', '-i', antes, '-ss', f'{a}', '-t', f'{d}', '-i', depois, '-filter_complex', fc,
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', o], check=True)
    partes.append(o)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
print('ok', saida)
