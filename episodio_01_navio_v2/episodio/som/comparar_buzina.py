"""Comparativo curto SEM × COM buzina (versão refinada), mesma imagem e narração no mesmo nível.
Uso: python3 som/comparar_buzina.py <video_revisao.mp4> <saida.mp4>"""
import os, sys, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_ep01 import lufs, pico_verdadeiro, db
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); SR = 48000
TRECHOS = [(3.4, 11.4, 'Abertura'), (160.0, 168.0, 'Conclusão')]
VERS = [('SEM BUZINA', 'refinado'), ('COM BUZINA', 'refinado_buzina')]
video, saida = sys.argv[1], sys.argv[2]; tmp = os.path.join(A, '_cmp_buz'); os.makedirs(tmp, exist_ok=True)
m0 = json.load(open(os.path.join(A, 'mix_refinado.json')))['master_db']
aj = {v: m0 - json.load(open(os.path.join(A, f'mix_{v}.json')))['master_db'] for _, v in VERS}   # narração no mesmo nível
partes, med = [], []
for j, (a, b, tit) in enumerate(TRECHOS):
    for nome, v in VERS:
        x = sf.read(os.path.join(EP, f'audio_ep01_{v}.wav'))[0][int(a * SR):int(b * SR)] * db(aj[v]); k = int(0.15 * SR)
        x[:k] *= np.linspace(0, 1, k)[:, None]
        if b < 167.9: x[-k:] *= np.linspace(1, 0, k)[:, None]
        w = os.path.join(tmp, f'{j}_{v}.wav'); sf.write(w, x, SR, subtype='PCM_24')
        vz = sf.read(os.path.join(EP, 'stems', f'ep01_narracao_{v}.wav'))[0][int(a * SR):int(b * SR)] * db(aj[v])
        med.append(dict(trecho=tit, versao=nome, mix_lufs=round(lufs(x), 1), pico_dbtp=round(pico_verdadeiro(x), 1), narracao_lufs=round(lufs(vz), 2)))
        m = os.path.join(tmp, f'{j}_{v}.mp4'); txt = f'{nome} · {tit}'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', video, '-i', w, '-map', '0:v', '-map', '1:a',
                        '-vf', f"drawbox=x=0:y=ih-112:w=iw:h=74:color=0x202B57@0.88:t=fill,drawtext=fontfile={EP}/../fontes/Montserrat-800.ttf:text='{txt}':fontcolor={'0xF6F4EC' if 'SEM' in nome else '0xF3B544'}:fontsize=24:x=(w-tw)/2:y=h-90",
                        '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', m], check=True)
        partes.append(m)
open(os.path.join(tmp, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in partes))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'l.txt'), '-c', 'copy', saida], check=True)
json.dump(med, open(os.path.join(A, 'comparativo_buzina_medidas.json'), 'w'), ensure_ascii=False, indent=1)
for x in med: print(x)
