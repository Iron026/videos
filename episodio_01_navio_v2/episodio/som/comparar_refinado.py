"""Comparativo de som ANTERIOR (som_hibrido) × REFINADO (som_refinado), com a MESMA imagem (revisão aprovada) e a MESMA
narração. Níveis comparáveis: as duas mixagens já estão a −14 LUFS; a refinada é corrigida pela pequena diferença de
master (dB) para que a NARRAÇÃO fique exatamente no mesmo nível nas duas — o que muda entre elas é só o som da cena.
Uso: python3 som/comparar_refinado.py <video_revisao.mp4> <saida.mp4>"""
import os, sys, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_ep01 import lufs, pico_verdadeiro, db

A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); SR = 48000
TRECHOS = [(0.0, 15.1, '1 · Abertura e bloco na água'), (40.8, 64.0, '2 · Dique e empuxo'), (15.1, 30.6, '3a · Guindaste e solda (estaleiro)'),
           (94.55, 118.0, '3b · Guindastes e carregamento'), (134.0, 154.7, '4 · Avaria e inundação'), (154.6, 168.0, '5 · Conclusão')]
VERS = [('SOM ANTERIOR', 'hibrido'), ('SOM REFINADO', 'refinado')]


def cortar(arq, a, b, g_db):
    x, sr = sf.read(os.path.join(EP, arq), always_2d=True); assert sr == SR
    y = x[int(a * SR):int(b * SR)].copy() * db(g_db); k = int(0.2 * SR)
    y[:k] *= np.linspace(0, 1, k)[:, None]; y[-k:] *= np.linspace(1, 0, k)[:, None]
    return y


if __name__ == '__main__':
    video, saida = sys.argv[1], sys.argv[2]; tmp = os.path.join(A, '_cmp_ref'); os.makedirs(tmp, exist_ok=True)
    mh, mr = (json.load(open(os.path.join(A, f'mix_{v}.json')))['master_db'] for v in ('hibrido', 'refinado'))
    ajuste = {'hibrido': 0.0, 'refinado': mh - mr}                   # narração no mesmo nível nas duas versões
    vh, vr = (sf.read(os.path.join(EP, 'stems', f'ep01_narracao_{v}.wav'))[0] for v in ('hibrido', 'refinado'))
    partes, med = [], []
    for j, (a, b, tit) in enumerate(TRECHOS):
        for nome, v in VERS:
            y = cortar(f'audio_ep01_{v}.wav', a, b, ajuste[v]); w = os.path.join(tmp, f'{j}_{v}.wav'); sf.write(w, y, SR, subtype='PCM_24')
            fundo = sum(sf.read(os.path.join(EP, 'stems', f'ep01_{s}_{v}.wav'))[0][int(a * SR):int(b * SR)] for s in ('efeitos', 'ambiencias')) * db(ajuste[v])
            med.append(dict(trecho=tit, versao=nome, mix_lufs=round(lufs(y), 1), pico_dbtp=round(pico_verdadeiro(y), 1), efeitos_e_ambiencias_lufs=round(lufs(fundo), 1)))
            m = os.path.join(tmp, f'{j}_{v}.mp4'); txt = f'{nome} · {tit}'.replace(':', '\\:').replace("'", '')
            cor = '0xF6F4EC' if v == 'hibrido' else '0xF3B544'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', video, '-i', w, '-map', '0:v', '-map', '1:a',
                            '-vf', f"drawbox=x=0:y=ih-112:w=iw:h=74:color=0x202B57@0.88:t=fill,drawtext=fontfile={EP}/../fontes/Montserrat-800.ttf:text='{txt}':fontcolor={cor}:fontsize=19:x=(w-tw)/2:y=h-87",
                            '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', m], check=True)
            partes.append(m)
    lista = os.path.join(tmp, 'lista.txt'); open(lista, 'w').write(''.join(f"file '{p}'\n" for p in partes))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista, '-c', 'copy', saida], check=True)
    json.dump(dict(ajuste_refinado_db=round(ajuste['refinado'], 3), narracao_lufs=dict(hibrido=round(lufs(vh), 2), refinado=round(lufs(vr * db(ajuste['refinado'])), 2)), trechos=med),
              open(os.path.join(A, 'comparativo_refinado_medidas.json'), 'w'), ensure_ascii=False, indent=1)
    for x in med: print(x)
