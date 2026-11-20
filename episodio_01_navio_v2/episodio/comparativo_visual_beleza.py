"""Comparativo visual ANTES × DEPOIS do refinamento de imagem (lado a lado, mesmos instantes, mesmo áudio):
porão da avaria (piso sem sombras serrilhadas, cavernas e longarinas, água nova), qualidade de render final
(antisserrilhado 4×, oclusão ambiente 16 amostras), brilho suave nas luzes fortes e correção de cor.
Uso: python3 episodio/comparativo_visual_beleza.py <antes.mp4> <depois.mp4> <saida.mp4>"""
import os, sys, subprocess
A = os.path.dirname(os.path.abspath(__file__)); FONTE = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
TRECHOS = [(137.0, 142.6, 'Porão da avaria: piso, estrutura e água'), (151.0, 155.0, 'Avaria: divisórias'), (23.4, 26.6, 'Solda: brilho do arco'),
           (8.6, 12.6, 'Navegação: bordas e proa'), (99.0, 104.0, 'Porto: guindastes e contêineres'), (164.4, 168.0, 'Plano final')]
antes, depois, saida = sys.argv[1:4]; tmp = os.path.join(A, '_cmpb'); os.makedirs(tmp, exist_ok=True); partes = []
rot = lambda txt: f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=0xF6F4EC:fontsize=26:box=1:boxcolor=0x202B57@0.9:boxborderw=10:x=(w-tw)/2:y=h-60"
for j, (a, b, tit) in enumerate(TRECHOS):
    o = os.path.join(tmp, f'{j}.mp4'); t = tit.replace(':', '\\:')
    fc = (f"[0:v]scale=540:960,setsar=1,{rot('ANTES')}[l];[1:v]scale=540:960,setsar=1,{rot('DEPOIS')}[r];"
          f"[l][r]hstack=2,pad=1080:1030:0:70:color=0x202B57,drawtext=fontfile={FONTE}:text='{t}':fontcolor=0xF3B544:fontsize=30:x=(w-tw)/2:y=20[v]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{b - a}', '-i', antes, '-ss', f'{a}', '-t', f'{b - a}', '-i', depois, '-filter_complex', fc,
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', o], check=True)
    partes.append(o)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
print('ok', saida)
