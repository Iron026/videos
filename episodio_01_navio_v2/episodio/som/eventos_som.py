"""Extrai das cenas exportadas os EVENTOS e CURVAS DE MOVIMENTO que dirigem o sound design (tempo global da narração):
contatos (surge: pouso = t0 + dur), velocidades de objetos animados (motores, cabos, quedas), nascimento das faíscas
da solda e tempos físicos da abertura. Saída: som/eventos_som.json. Uso: python3 episodio/som/eventos_som.py"""
import os, json, math, numpy as np
A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, '..', 'cenas')
def cena(s): return json.load(open(os.path.join(C, s, 'cena.json')))
def pos(M): return np.array(M[12:15])
def escala(M): return float(np.linalg.norm(M[0:3]))
def curvas(s, nomes, g0=None):
    c = cena(s); q = c['animacao']['quadros']; fps = c['animacao']['fps']; g0 = c['g0'] if g0 is None else g0
    t = [float(x.get('t', g0 + i / fps)) for i, x in enumerate(q)]
    out = {'t': [round(g0 + i / fps, 4) for i in range(len(q))]}
    for n in nomes:
        P = np.array([pos(x['objetos'][n]) if n in x['objetos'] else [np.nan] * 3 for x in q])
        v = np.r_[0, np.linalg.norm(np.diff(P, axis=0), axis=1) * fps]
        out[n] = dict(z=[round(float(z), 3) for z in P[:, 2]], v=[round(float(x), 3) for x in v])
    return out
ev = {}
# ---- abertura (animatic r2): tempo de cena → global (mesmo mapa da câmera lenta de animatic_r2.py)
a, b = 2.95, 3.45; v0 = 0.35; ts = np.linspace(0.90, 9.0, 40001)
k = np.minimum(np.clip((ts - (a - 0.12)) / 0.12, 0, 1), np.clip(((b + 0.20) - ts) / 0.20, 0, 1)); k = k * k * (3 - 2 * k)
vv = 1 - (1 - v0) * k; gg = np.concatenate([[0], np.cumsum(0.5 * (1 / vv[1:] + 1 / vv[:-1]) * np.diff(ts))])
glob = lambda tc: float(np.interp(tc, ts, gg))
ev['abertura'] = dict(empurrao=glob(1.40), borda=glob(2.30), agua=glob(3.13), leito=glob(3.76), lento=[glob(a - 0.12), glob(b + 0.20)])
# ---- estaleiro: chapas que chegam (pouso), cordões de solda (arcos) e nascimento das faíscas
c = cena('s03'); sv = c['surgir']
ev['chapas'] = sorted(round(x['t0'] + x['dur'], 3) for kk, x in sv.items() if kk.startswith('novo'))
arcos = sorted({(round(x['t0'], 3), round(x['t1'], 3)) for kk, x in sv.items() if kk.startswith('arco_luz')})
ev['solda_cordoes'] = arcos
q = c['animacao']['quadros']; fps = c['animacao']['fps']; nasc = []
nomes = [n for n in q[0]['objetos'] if n.startswith('faisca')]
for n in nomes:
    vivo = False
    for i, x in enumerate(q):
        e = escala(x['objetos'][n]) > 0.01
        if e and not vivo: nasc.append(round(c['g0'] + i / fps, 3))
        vivo = e
ev['faiscas'] = sorted(nasc)
ev['estaleiro_mov'] = curvas('s03', ['carro', 'guincho', 'grupo_carga'])
# ---- porto: pousos dos portêineres e de cada contêiner do time-lapse; movimento de carros e spreaders
c = cena('s09'); sv = c['surgir']
ev['conteineres'] = sorted(round(x['t0'] + x['dur'], 3) for kk, x in sv.items() if kk.startswith('c'))
ev['pousos'] = [101.60, 102.95, 104.45]
ev['porto_mov'] = curvas('s09', ['carro_anc5', 'spreader_anc5', 'carro_anc3', 'spreader_anc3', 'carro_anc7', 'spreader_anc7', 'navio'])
# ---- experimento e conclusão: entrada na água e arfagem do casco
G = 9.81
ev['experimento'] = dict(solto=85.6, agua=85.6 + math.sqrt(2 * 2.0 / G))
ev['experimento_mov'] = curvas('s08b', ['navio', 'cubo_aco'])
ev['retomada'] = dict(borda=74.85 + (2.30 - 1.944), agua=76.13, leito=82.12)
ev['conclusao'] = dict(solto=155.2, agua=155.2 + math.sqrt(4.0 / G))
ev['dique'] = dict(comporta=41.7, jatos_fim=43.6, picadeiros=46.10)
ev['avaria'] = dict(rasgo=134.9, bolhas=[135.0, 136.8], jato=[136.9, 146.4], enche=[137.2, 145.8], hipotese=147.9, divisorias=151.05)
json.dump(ev, open(os.path.join(A, 'eventos_som.json'), 'w'))
print({k: (v if not isinstance(v, (list, dict)) or len(str(v)) < 120 else f'{type(v).__name__}[{len(v)}]') for k, v in ev.items()})
print('chapas', ev['chapas'][:3], '... faíscas', len(ev['faiscas']), 'contêineres', len(ev['conteineres']), ev['conteineres'][:3])
