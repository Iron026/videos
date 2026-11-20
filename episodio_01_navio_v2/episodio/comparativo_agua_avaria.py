"""Comparativo visual ANTES × DEPOIS da água dentro do navio na avaria (lado a lado, mesmos instantes, mesmo áudio).
Uso: python3 episodio/comparativo_agua_avaria.py <antes.mp4> <depois.mp4> <saida.mp4>"""
import os, sys, subprocess
A = os.path.dirname(os.path.abspath(__file__)); FONTE = os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf')
antes, depois, saida = sys.argv[1:4]; a, b = 134.6, 155.0
rot = lambda txt: f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=0xF6F4EC:fontsize=26:box=1:boxcolor=0x202B57@0.9:boxborderw=10:x=(w-tw)/2:y=h-60"
fc = (f"[0:v]scale=540:960,setsar=1,{rot('ANTES')}[l];[1:v]scale=540:960,setsar=1,{rot('DEPOIS')}[r];"
      f"[l][r]hstack=2,pad=1080:1030:0:70:color=0x202B57,drawtext=fontfile={FONTE}:text='Água dentro do navio (avaria)':fontcolor=0xF3B544:fontsize=30:x=(w-tw)/2:y=20[v]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a}', '-t', f'{b - a}', '-i', antes, '-ss', f'{a}', '-t', f'{b - a}', '-i', depois, '-filter_complex', fc,
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', saida], check=True)
print('ok', saida)
