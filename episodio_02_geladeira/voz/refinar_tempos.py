"""Tempos FINAIS das palavras: identidade e ordem pelo Whisper oficial (verificado 384/384 contra o roteiro) + ataque acústico
medido. Motivo: o Whisper erra o INÍCIO das palavras que vêm depois de uma pausa (põe ~0,3 s antes, dentro do silêncio);
a envoltória de energia mede esse ataque com resolução de 10 ms. Regra (ver comentário no código): cada pausa detectada
(≥ 0,12 s, mesmo detector de alinhar_por_pausas.py) é atribuída à fronteira de palavras mais compatível com os tempos do
Whisper; a palavra seguinte passa a começar no FIM da pausa e a anterior termina no COMEÇO dela. As demais palavras
(fala contínua) mantêm os tempos do Whisper.
Saída: roteiro/palavras.json (tempos usados pela decupagem e legendas). Cópia da v1: roteiro/palavras_v1_pausas.json.
Uso: python3 refinar_tempos.py <audio.mp3>"""
import os, sys, json, shutil, subprocess
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'roteiro')
sr = 16000; x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                                              capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
hop = 160; n = len(x) // hop
db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)); db = np.convolve(db, np.ones(3) / 3, mode='same')
fala = db > np.percentile(db, 95) - 32
pausas = []; k = 0
while k < n:
    if not fala[k]:
        j = k
        while j < n and not fala[j]: j += 1
        if (j - k) * 0.01 >= 0.12: pausas.append((k * 0.01, j * 0.01))
        k = j
    else: k += 1
wh = json.load(open(os.path.join(R, 'palavras_whisper.json')))['palavras']
out = [dict(palavra=w['palavra'], inicio=w['inicio'], fim=w['fim']) for w in wh]
ajustes = []
# Critério único: cada PAUSA (a, b) vai para a fronteira de palavras i cujo início Whisper, corrigido pelo viés medido
# (VIES = +0,28 s: o Whisper começa as palavras pós-pausa dentro do silêncio), fica mais perto do fim b da pausa.
# Custo = |b − (início_i + VIES)| − 0,20 s se o roteiro tem pontuação antes da palavra i; aceito se custo < 0,45 s.
# Atribuição em ordem (monotônica) e sem repetir pausa nem fronteira.
VIES = 0.28; ultimo = 0
for (a, b) in pausas:
    custos = [(abs(b - (w['inicio'] + VIES)) - 0.20 * (wh[i - 1]['palavra'][-1] in '.,?!:;'), i) for i, w in enumerate(wh) if i > ultimo]
    if not custos: continue
    c, i = min(custos)
    if c >= 0.45: continue
    ultimo = i; w = wh[i]
    out[i]['inicio'] = round(b, 3); out[i]['fim'] = round(max(w['fim'], b + 0.06), 3)
    out[i - 1]['fim'] = round(max(min(a, out[i - 1]['fim']) if out[i - 1]['fim'] > a else out[i - 1]['fim'], out[i - 1]['inicio'] + 0.02), 3)
    for j in range(i + 1, len(out)):          # Whisper adiantado também nas seguintes: não podem começar antes do ataque
        if out[j]['inicio'] < out[j - 1]['fim']: out[j]['inicio'] = out[j - 1]['fim']; out[j]['fim'] = round(max(out[j]['fim'], out[j]['inicio'] + 0.06), 3)
        else: break
    ajustes.append(dict(palavra=w['palavra'], whisper=w['inicio'], ataque=round(b, 3), delta=round(b - w['inicio'], 3)))
# fala inicial: o ataque da primeira palavra
ini = next(i for i in range(n) if fala[i]) * 0.01
if abs(ini - out[0]['inicio']) < 0.5: ajustes.append(dict(palavra=out[0]['palavra'], whisper=out[0]['inicio'], ataque=ini, delta=round(ini - out[0]['inicio'], 3))); out[0]['inicio'] = round(ini, 3)
# fim da fala: o último instante com energia de fala (medido), não o fim estimado pelo Whisper
fim_fala = (max(i for i in range(n) if fala[i]) + 1) * 0.01
out[-1]['fim'] = round(max(out[-1]['fim'], fim_fala), 3)
# passada final de coerência: inícios em ordem estrita (≥ 20 ms entre palavras) e cada fim limitado ao início da seguinte
for a_, b_ in zip(out, out[1:]):
    if b_['inicio'] < a_['inicio'] + 0.02: b_['inicio'] = round(a_['inicio'] + 0.02, 3)
for a_, b_ in zip(out, out[1:]):
    a_['fim'] = round(min(max(a_['fim'], a_['inicio']), b_['inicio']), 3)
for a, b in zip(out, out[1:]): assert a['inicio'] <= a['fim'] <= b['inicio'] + 1e-6, (a, b)   # o Whisper dá duração 0 a algumas palavras átonas
v1 = os.path.join(R, 'palavras_v1_pausas.json')
if not os.path.exists(v1): shutil.copy(os.path.join(R, 'palavras.json'), v1)
json.dump(out, open(os.path.join(R, 'palavras.json'), 'w'), ensure_ascii=False, indent=0)
d = np.array([a['delta'] for a in ajustes])
rel = dict(pausas_detectadas=len(pausas), palavras_ajustadas_ao_ataque=len(ajustes), delta_medio_s=round(float(d.mean()), 3),
           delta_min_s=round(float(d.min()), 3), delta_max_s=round(float(d.max()), 3), ajustes=ajustes)
json.dump(rel, open(os.path.join(A, 'refino_tempos.json'), 'w'), ensure_ascii=False, indent=1)
print({k: v for k, v in rel.items() if k != 'ajustes'})
