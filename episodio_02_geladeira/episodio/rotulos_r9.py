"""Rodada 9: rótulos com âncora VISÍVEL (C3, D1, D3, D4, E4, F2). As âncoras da V8 ficavam fora do quadro (rótulo preso à
borda, longe do que nomeia; no D3 a linha apontava para fora da tela).
Sem reexportar nada: a posição 2D de um rótulo é a projeção da âncora 3D pela câmera do quadro, e a câmera de cada quadro
está gravada em cena.json — a mesma projeção do Blender (world_to_camera_view) reproduz os rótulos exportados com erro
≤ 5e-5 (só o arredondamento de 4 casas; verificado em B3, D1, D2, E2, H2). Malhas, câmeras e quadros renderizados NÃO mudam;
os arquivos novos vão para episodio/rotulos_r9/<plano>.json (fora de cenas/, para não mudar o hash das cenas da V8).
Tempos e opacidade de cada rótulo são COPIADOS da V8 (entram no mesmo instante, sincronizados com a palavra).
Âncora 'fixa': ponto do elemento visível no plano inteiro (procurado na superfície do elemento).
Âncora 'trecho': o elemento é um tubo/canal e a câmera anda ao longo dele — a cada quadro, o ponto do tubo cuja projeção cai
mais perto de uma coluna-alvo da tela (o rótulo fica parado na tela, sempre em cima do tubo).
Uso: python3 rotulos_r9.py  → episodio/rotulos_r9/*.json + relatorios/rotulos_r9.json"""
import os, json, math
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(A, 'rotulos_r9'); os.makedirs(OUT, exist_ok=True)
COND_Y = 0.345; ZP = 1.425 - 5 * 0.072
NOVAS = {   # (plano, rótulo): âncora nova  — com linha? (None = mantém o da V8) e deslocamento (dx, dy) da caixa
    ('C3', 'fluido refrigerante'): dict(trecho=((-0.30, COND_Y, ZP), (0.30, COND_Y, ZP)), alvo_u=0.40),
    ('D1', 'Evaporador'): dict(fixa=(0.219, -0.215, 1.365)),
    ('D3', 'fluido mais frio que o ar'): dict(fixa=(-0.20, 0.121, 1.185), dx=0.04, dy=0.07),     # tubo do evaporador no topo; rótulo abaixo, linha curta
    ('D4', 'entra: líquido + vapor'): dict(trecho=((-0.27, -1.30, 1.272), (0.30, -1.30, 1.272)), alvo_u=0.28),
    ('E4', 'ar da cozinha'): dict(fixa=(-0.30, 0.40, 0.525)),
    ('F2', 'entra: vapor quente'): dict(trecho=((-0.27, 1.30, 0.978), (0.30, 1.30, 0.978)), alvo_u=0.28),
}


def proj(cam, P, W=1080, H=1920):
    pos = np.array(cam['pos']); f = np.array(cam['dir'], float); f /= np.linalg.norm(f); r = np.cross(f, cam['up']); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = np.asarray(P, float) - pos; z = d @ f; t = math.tan(math.radians(cam['fov'] / 2))
    return ((d @ r / z) / (t * W / H) + 1) / 2, (1 - (d @ u / z) / t) / 2, z


def ancora(cfg, cam):
    if 'fixa' in cfg: return cfg['fixa']
    a, b = np.array(cfg['trecho'][0]), np.array(cfg['trecho'][1])
    ts = np.linspace(0, 1, 241); us = [proj(cam, a + (b - a) * t)[0] for t in ts]
    k = int(np.argmin([abs(x - cfg['alvo_u']) for x in us])); return tuple(a + (b - a) * ts[k])


rel = {}
for pid in sorted({p for p, _ in NOVAS}):
    c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); r = json.load(open(os.path.join(A, 'cenas', pid, 'rotulos2d.json')))
    Q = c['animacao']['quadros']; novos = []; mud = {}
    for i, q in enumerate(r['quadros']):
        nq = []
        for it in q:
            cfg = NOVAS.get((pid, it[0]))
            if not cfg: nq.append(it); continue
            u, v, z = proj(Q[i]['camera'], ancora(cfg, Q[i]['camera']))
            dx, dy = cfg.get('dx', it[4]), cfg.get('dy', it[5])
            nit = [it[0], round(float(u), 4), round(float(v), 4), it[3], dx, dy] + list(it[6:])   # mesmo tipo (com/sem linha) da V8
            nq.append(nit)
            m = mud.setdefault(it[0], dict(quadros=0, fora_v8=0, fora_r9=0))
            m['quadros'] += 1; m['fora_v8'] += not (0 <= it[1] <= 1 and 0 <= it[2] <= 1); m['fora_r9'] += not (0.02 <= u <= 0.98 and 0.02 <= v <= 0.98)
        novos.append(nq)
    json.dump(dict(g0=r['g0'], fps=r['fps'], quadros=novos, origem='rodada 9: âncoras visíveis; tempos/opacidade da V8'), open(os.path.join(OUT, pid + '.json'), 'w'), ensure_ascii=False)
    rel[pid] = mud; print(pid, mud)
json.dump(dict(ancoras={f'{p}|{n}': v for (p, n), v in NOVAS.items()}, resultado=rel), open(os.path.join(A, '..', 'relatorios', 'rotulos_r9.json'), 'w'), ensure_ascii=False, indent=1)
