"""Alinhamento PROVISÓRIO da narração por pausas (sem reconhecimento de fala).

Por que existe: o modelo Whisper local não pôde ser baixado nesta sessão. Sem ele, NÃO é possível verificar as palavras.
O que faz: detecta as pausas do áudio (envoltória de energia) e as associa, em ordem, às fronteiras de pontuação do roteiro
oficial (programação dinâmica). Entre fronteiras casadas, as palavras são distribuídas pelo modelo de duração calibrado no
Ep. 01. Resultado: tempos de FRASE confiáveis quando as pausas casam bem; tempos de PALAVRA aproximados.
O que NÃO faz: não confirma que cada palavra foi dita, nem detecta troca de palavras dentro de uma frase.
Saída: roteiro/palavras_pausas.json (+ relatório). O original nunca é alterado.
Uso: python3 alinhar_por_pausas.py <audio.mp3>"""
import os, sys, json, re, subprocess
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'roteiro')
audio = sys.argv[1]
sr = 16000
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
hop = 160; n = len(x) // hop
rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12); db = 20 * np.log10(rms)
db = np.convolve(db, np.ones(3) / 3, mode='same')
ref = np.percentile(db, 95); fala = db > ref - 32          # quadros de fala (10 ms)
t = np.arange(n) * hop / sr
idx = np.where(fala)[0]; ini, fim = t[idx[0]], t[idx[-1]] + 0.01
# pausas: trechos sem fala ≥ 0,12 s dentro da fala
pausas = []; k = idx[0]
while k < idx[-1]:
    if not fala[k]:
        j = k
        while j < n and not fala[j]: j += 1
        if (j - k) * 0.01 >= 0.12: pausas.append(((k + j) / 2 * 0.01, (j - k) * 0.01, k * 0.01, j * 0.01))
        k = j
    else: k += 1
# roteiro: palavras e fronteiras de pontuação
pars = [l.strip() for l in open(os.path.join(R, 'roteiro_texto.txt')) if l.strip()]
ws = [w for p in pars for w in p.split()]
dur = np.array([0.0536 * len(re.sub(r'\W', '', w)) + 0.1235 for w in ws])
PESO = {'.': 1.0, '?': 1.0, '!': 1.0, ':': 0.8, ',': 0.6, ';': 0.6}
fronteiras = [i for i, w in enumerate(ws) if w[-1] in PESO and i < len(ws) - 1]
# tempos esperados das fronteiras (fala sem pausas, escalada para caber entre o início e o fim medidos)
pausa_esp = np.array([0.30 if i in fronteiras else 0.0 for i in range(len(ws))])
cum = np.concatenate([[0], np.cumsum(dur + pausa_esp)]); esc = (fim - ini) / (cum[-1] - pausa_esp[-1])
esp = {i: ini + (cum[i + 1] - pausa_esp[i] * 0.5) * esc for i in fronteiras}
# programação dinâmica: casar fronteiras (em ordem) com pausas (em ordem)
F, P = fronteiras, pausas; nf, npz = len(F), len(P)
INF = 1e9; D = np.full((nf + 1, npz + 1), INF); D[0, :] = 0; D[:, 0] = np.arange(nf + 1) * 0; bk = {}
D[0, 0] = 0
for a in range(nf + 1):
    for b in range(npz + 1):
        if a == 0 and b == 0: continue
        best = INF; arg = None
        if a > 0 and b > 0:   # casa fronteira a-1 com pausa b-1
            dt = abs(esp[F[a - 1]] - P[b - 1][0]); c = D[a - 1, b - 1] + (dt / 1.2) ** 2 - 0.6 * min(P[b - 1][1], 0.6) * PESO[ws[F[a - 1]][-1]]
            if c < best: best, arg = c, ('m', a - 1, b - 1)
        if a > 0:             # fronteira sem pausa (vírgula falada sem parar)
            c = D[a - 1, b] + 0.9 * PESO[ws[F[a - 1]][-1]] ** 2
            if c < best: best, arg = c, ('f', a - 1, b)
        if b > 0:             # pausa sem fronteira (respiração dentro da frase)
            c = D[a, b - 1] + 0.35 + 1.5 * max(P[b - 1][1] - 0.25, 0)
            if c < best: best, arg = c, ('p', a, b - 1)
        D[a, b] = best; bk[(a, b)] = arg
a, b = nf, npz; casadas = {}
while (a, b) != (0, 0):
    op, a2, b2 = bk[(a, b)]
    if op == 'm': casadas[F[a2]] = P[b2]
    a, b = a2, b2
# âncoras: início, fronteiras casadas (fim da palavra = começo da pausa; próxima palavra = fim da pausa), fim
anc = [(-1, ini)]   # (índice da última palavra antes da âncora, tempo de início da próxima)
fins = {}
for i in sorted(casadas): fins[i] = casadas[i][2]; anc.append((i, casadas[i][3]))
palavras = []; pos = 0; t0 = ini
lim = sorted(casadas) + [len(ws) - 1]
for k, i_fim in enumerate(lim):
    bloco = list(range(pos, i_fim + 1)); tf = fins.get(i_fim, fim)
    d = dur[bloco] + np.array([0.25 * (ws[j][-1] in PESO) for j in bloco]); d[-1] -= 0.25 * (ws[bloco[-1]][-1] in PESO)
    s = (tf - t0) / d.sum(); tt = t0
    for j, dj in zip(bloco, d):
        w_d = dur[j] * s; palavras.append(dict(palavra=ws[j], inicio=round(tt, 3), fim=round(tt + w_d, 3))); tt += dj * s
    pos = i_fim + 1; t0 = casadas[i_fim][3] if i_fim in casadas else tf
frases = [i for i in fronteiras if ws[i][-1] in '.?!']
casadas_frases = [i for i in frases if i in casadas]
resid = [casadas[i][0] - esp[i] for i in fronteiras if i in casadas]
rel = dict(METODO='alinhamento por pausas (sem reconhecimento de fala): NÃO verifica as palavras', audio=os.path.basename(audio),
           fala_inicio=round(ini, 3), fala_fim=round(fim, 3), pausas_detectadas=len(P), fronteiras_roteiro=len(F),
           fronteiras_casadas=len(casadas), fins_de_frase=len(frases), fins_de_frase_casados=len(casadas_frases),
           fins_de_frase_sem_pausa=[' '.join(ws[max(0, i - 3):i + 1]) for i in frases if i not in casadas],
           pausas_sem_fronteira=[round(p[0], 2) for p in P if p not in casadas.values()],
           residuo_medio_s=round(float(np.mean(np.abs(resid))), 3), residuo_max_s=round(float(np.max(np.abs(resid))), 3),
           escala_fala_vs_ep01=round(float(esc), 4))
json.dump(dict(PROVISORIO=True, metodo=rel['METODO'], palavras=palavras), open(os.path.join(R, 'palavras_pausas.json'), 'w'), ensure_ascii=False, indent=0)
json.dump(rel, open(os.path.join(A, 'alinhamento_pausas.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(rel, ensure_ascii=False, indent=1))
