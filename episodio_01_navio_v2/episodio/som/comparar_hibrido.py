"""Comparação sonora ANTES × DEPOIS (mesmas imagens, mesmo nível): para cada trecho, toca o som anterior e depois o
híbrido. 'Antes' = o que foi entregue por último naquele trecho (demo Mixkit onde ela existia; síntese no resto).
Cada trecho de cada versão é igualado em −16 LUFS para comparar o som e não o volume.
Uso: python3 som/comparar_hibrido.py <video_revisao.mp4> <saida.mp4>"""
import os, sys, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_ep01 import lufs, pico_verdadeiro, db

A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); SR = 48000
TRECHOS = [  # (início, fim, título, arquivo "antes")
    (0.0, 15.1, 'Abertura: arrasto do bloco', 'audio_ep01_real.wav'),
    (15.1, 33.0, 'Estaleiro: pórtico, encaixe, solda, passagem de tempo', 'audio_ep01_real.wav'),
    (33.0, 48.0, 'Corte do casco e dique (antes: síntese)', 'audio_ep01.wav'),
    (94.55, 123.65, 'Porto e carregamento (antes: síntese)', 'audio_ep01.wav'),
    (149.0, 155.0, 'Divisórias estanques', 'audio_ep01_real.wav'),
    (154.6, 168.0, 'Conclusão (antes: síntese)', 'audio_ep01.wav'),
]


def cortar(arq, a, b):
    x, sr = sf.read(os.path.join(EP, arq), always_2d=True); assert sr == SR
    y = x[int(a * SR):int(b * SR)].copy(); k = int(0.25 * SR)
    y[:k] *= np.linspace(0, 1, k)[:, None]; y[-k:] *= np.linspace(1, 0, k)[:, None]
    return y * db(-16 - lufs(y))


if __name__ == '__main__':
    video, saida = sys.argv[1], sys.argv[2]; tmp = os.path.join(A, '_cmp'); os.makedirs(tmp, exist_ok=True)
    partes, med = [], []
    for j, (a, b, tit, antes) in enumerate(TRECHOS):
        for v, arq in (('ANTES', antes), ('DEPOIS (híbrido)', 'audio_ep01_hibrido.wav')):
            y = cortar(arq, a, b); w = os.path.join(tmp, f'{j}_{v[:5]}.wav'); sf.write(w, y, SR, subtype='PCM_24')
            med.append(dict(trecho=tit, versao=v, lufs=round(lufs(y), 1), pico_dbtp=round(pico_verdadeiro(y), 1)))
            m = os.path.join(tmp, f'{j}_{v[:5]}.mp4'); txt = f'{v} · {tit}'.replace(':', '\\:').replace("'", '')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', video, '-i', w, '-map', '0:v', '-map', '1:a',
                            '-vf', f"drawbox=x=0:y=ih-110:w=iw:h=70:color=0x202B57@0.85:t=fill,drawtext=fontfile={EP}/../fontes/Montserrat-800.ttf:text='{txt}':fontcolor=0xF3B544:fontsize=22:x=(w-tw)/2:y=h-90",
                            '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', m], check=True)
            partes.append(m)
    lista = os.path.join(tmp, 'lista.txt'); open(lista, 'w').write(''.join(f"file '{p}'\n" for p in partes))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista, '-c', 'copy', saida], check=True)
    json.dump(med, open(os.path.join(A, 'comparativo_hibrido_medidas.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(med, ensure_ascii=False))
