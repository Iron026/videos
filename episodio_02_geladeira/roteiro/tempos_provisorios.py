"""Tempos PROVISÓRIOS por palavra para o Ep. 02 (sem narração aprovada ainda).
Modelo calibrado na narração REAL do Ep. 01 (mesma voz, Will - Deep; voz/narracao_ep01/trabalho/palavras.json do Ep. 01):
  duração da palavra = 0,0536·letras + 0,1235 s (mínimos quadrados, 384 palavras)
  pausa após '.' 0,37 s · ',' 0,34 s · '?' 0,43 s · ':' 0,41 s (medianas medidas); entre parágrafos +0,15 s.
Ao final, a escala é ajustada para a taxa média medida no Ep. 01 (2,26 palavras/s incluindo pausas).
NÃO é a narração: serve só para decupagem e animatic. Quando o áudio aprovado chegar, este arquivo é substituído
pelo alinhamento real (palavras.json) e toda a montagem passa a seguir os instantes reais."""
import json, re, os
A = os.path.dirname(os.path.abspath(__file__))
PAUSA = {'.': 0.37, ',': 0.34, '?': 0.43, ':': 0.41, '!': 0.37, ';': 0.34}
pars = [l.strip() for l in open(os.path.join(A, 'roteiro_texto.txt')) if l.strip()]
t, out = 0.0, []
for pi, par in enumerate(pars):
    ws = par.split()
    for i, w in enumerate(ws):
        d = 0.0536 * len(re.sub(r'\W', '', w)) + 0.1235
        out.append(dict(palavra=w, inicio=t, fim=t + d, paragrafo=pi)); t += d
        if w[-1] in PAUSA: t += PAUSA[w[-1]]
    t += 0.15
alvo = len(out) / 2.2607                      # mesma taxa média da voz no Ep. 01
k = alvo / out[-1]['fim']
for w in out: w['inicio'] = round(w['inicio'] * k, 3); w['fim'] = round(w['fim'] * k, 3)
json.dump(dict(PROVISORIO=True, nota='tempos estimados; substituir pelo alinhamento da narração aprovada', escala=round(k, 4),
               palavras=out), open(os.path.join(A, 'palavras_provisorio.json'), 'w'), ensure_ascii=False, indent=0)
# frases (para a decupagem)
fr, cur = [], []
for w in out:
    cur.append(w)
    if w['palavra'][-1] in '.?!':
        fr.append(dict(inicio=cur[0]['inicio'], fim=cur[-1]['fim'], texto=' '.join(x['palavra'] for x in cur))); cur = []
json.dump(fr, open(os.path.join(A, 'frases_provisorio.json'), 'w'), ensure_ascii=False, indent=1)
for i, f in enumerate(fr): print(f"F{i+1:02d} {f['inicio']:7.2f}–{f['fim']:7.2f}  {f['texto']}")
print('DURAÇÃO PROVISÓRIA DA FALA', out[-1]['fim'], 's')
