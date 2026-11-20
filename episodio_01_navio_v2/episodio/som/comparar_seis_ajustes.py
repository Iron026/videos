"""Comparativos sonoros ANTES (mixagem aprovada) × DEPOIS (ajustada) dos quatro ajustes de áudio, com a mesma imagem e o
mesmo ganho de master (nenhuma normalização por versão). Uso:
python3 som/comparar_seis_ajustes.py <video_imagem.mp4> <mix_antes.wav> <mix_depois.wav> <saida.mp4>"""
import os, sys, subprocess
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); FONTE = os.path.join(EP, '..', 'fontes', 'Montserrat-800.ttf')
TRECHOS = [(4.4, 10.4, '1 Buzina inicial'), (28.6, 36.6, '2 Fim do estaleiro em 0:30'), (129.9, 134.1, '3 Brilho de cada linha'), (164.4, 168.0, '4 Buzina final')]
video, antes, depois, saida = sys.argv[1:5]; tmp = os.path.join(A, '_cmp6'); os.makedirs(tmp, exist_ok=True); partes = []
for j, (a, b, tit) in enumerate(TRECHOS):
    d = b - a
    for nome, au, cor in (('ANTES', antes, '0xF6F4EC'), ('DEPOIS', depois, '0xF3B544')):
        o = os.path.join(tmp, f'{j}_{nome}.mp4'); txt = f'{nome} · {tit}'
        fo = f',afade=t=out:st={d - 0.12:.3f}:d=0.12' if b < 167.9 else ''
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', video, '-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', au,
                        '-map', '0:v', '-map', '1:a', '-af', f'afade=t=in:d=0.12{fo}',
                        '-vf', f"drawbox=x=0:y=ih-112:w=iw:h=74:color=0x202B57@0.88:t=fill,drawtext=fontfile={FONTE}:text='{txt}':fontcolor={cor}:fontsize=21:x=(w-tw)/2:y=h-88",
                        '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', o], check=True)
        partes.append(o)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
for p in partes: os.remove(p)
os.remove(os.path.join(tmp, 'l.txt')); os.rmdir(tmp); print('ok', saida)
