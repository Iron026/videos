"""Conferência das legendas contra a narração (Ep. 02). Recalcula os blocos com a MESMA regra de montar_ep02.legendas()
(importada do próprio módulo) a partir de roteiro/palavras.json (Whisper oficial verificado + ataque acústico) e mede:
  1. cobertura: toda palavra fica na tela durante todo o intervalo em que é falada;
  2. antecipação: quanto cada bloco aparece ANTES do ataque acústico da sua 1ª palavra (energia do áudio, 10 ms);
  3. atraso: quanto cada bloco aparece DEPOIS desse ataque;
  4. comparação com as legendas da v1 (palavras_v1_pausas.json): deslocamento dos blocos.
Uso: python3 conferir_legendas.py → imprime e grava relatorios/conferencia_legendas_v2.json"""
import os, sys, json, subprocess, importlib
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..')
sys.argv = ['montar_ep02.py', 'animatic']; sys.path.insert(0, A)
M = importlib.import_module('montar_ep02')                       # a regra de blocos é a da montagem, não uma cópia
P = json.load(open(os.path.join(RAIZ, 'roteiro', 'palavras.json')))
blocos = M.legendas()
audio = os.path.join(RAIZ, 'voz', 'ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3')
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
n = len(x) // 160; db = 20 * np.log10(np.sqrt(np.mean(x[:n * 160].reshape(n, 160) ** 2, axis=1) + 1e-12)); db = np.convolve(db, np.ones(3) / 3, mode='same')
fala = db > np.percentile(db, 95) - 32
def ataque(t):   # fim do silêncio (≥ 0,12 s) mais próximo de t, numa janela de ±0,5 s; None se a fala é contínua ali
    melhor = None
    for k in range(max(1, int((t - 0.5) * 100)), min(n, int((t + 0.5) * 100))):
        if fala[k] and not fala[k - 1]:
            j = k - 1
            while j > 0 and not fala[j]: j -= 1
            if (k - 1 - j) * 0.01 >= 0.12 and (melhor is None or abs(k * 0.01 - t) < abs(melhor - t)): melhor = k * 0.01
    return melhor
descob, ant, atr = [], [], []
for (a, b, txt) in blocos:
    ws = [w for w in P if a - 1e-6 <= w['inicio'] < b]
    for w in ws:
        if w['fim'] > b + 1e-6: descob.append(dict(palavra=w['palavra'], fala=[w['inicio'], w['fim']], tela=[round(a, 3), round(b, 3)]))
    t_at = ataque(a)
    if t_at is None: continue           # bloco no meio de fala contínua: vale o início Whisper da palavra
    d = a - t_at
    (ant if d < 0 else atr).append(dict(bloco=txt, tela=round(a, 3), ataque=round(t_at, 3), d=round(d, 3)))
quadro = 1 / 30
res = dict(blocos=len(blocos), palavras=len(P), blocos_apos_pausa_medidos=len(ant + atr),
           palavras_fora_da_tela_enquanto_faladas=descob,
           blocos_antes_do_ataque=dict(n=len([z for z in ant if z['d'] < -quadro]), max_s=min([z['d'] for z in ant], default=0), lista=[z for z in ant if z['d'] < -quadro]),
           blocos_depois_do_ataque=dict(n=len([z for z in atr if z['d'] > quadro]), max_s=max([z['d'] for z in atr], default=0), lista=[z for z in atr if z['d'] > quadro]),
           desvio_abs_medio_s=round(float(np.mean([abs(z['d']) for z in ant + atr])), 3))
# v1: mesma regra sobre os tempos antigos
M.PL.carregar_palavras = lambda: (json.load(open(os.path.join(RAIZ, 'roteiro', 'palavras_v1_pausas.json'))), 'v1')
b1 = M.legendas()
z1 = [(a - t) for (a, b, _) in b1 for t in [ataque(a)] if t is not None]
P1 = json.load(open(os.path.join(RAIZ, 'roteiro', 'palavras_v1_pausas.json')))
cob1 = sum(1 for (a, b, _) in b1 for w in P1 if a - 1e-6 <= w['inicio'] < b and w['fim'] > b + 1e-6)
res['v1'] = dict(blocos=len(b1), blocos_apos_pausa_medidos=len(z1), desvio_abs_medio_s=round(float(np.mean(np.abs(z1))), 3),
                 max_antes_s=round(float(min(z1)), 3), max_depois_s=round(float(max(z1)), 3), fora_de_1_quadro=sum(1 for z in z1 if abs(z) > quadro),
                 palavras_fora_da_tela=cob1, nota='a v1 tinha palavras com instantes errados dentro das frases (ex.: E2 "É aqui que entra o compressor" comprimido em 0,15 s); a cobertura acima usa os tempos da própria v1 e não revela isso')
json.dump(res, open(os.path.join(RAIZ, 'relatorios', 'conferencia_legendas_v2.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k not in ('blocos_antes_do_ataque', 'blocos_depois_do_ataque') else {kk: vv for kk, vv in v.items() if kk != 'lista'}) for k, v in res.items()}, ensure_ascii=False, indent=1))
