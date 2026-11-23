"""Rodada 9: resolve divergências entre o manifesto de render de um plano e a cena atual SEM re-renderizar, só com prova.
Os quadros de um plano dependem só do que o motor lê: cena.json e as malhas mNNN.bin. rotulos2d.json e manometros2d.json são
COMPOSIÇÃO (lidos pela montagem), mas entram no hash da pasta da cena — por isso uma reexportação que só mudou rótulos
(ou só a ordem dos triângulos, que a exportação não garante) faz o manifesto divergir.
Prova exigida (contra a cena de referência, a que foi usada no render — hash igual ao do manifesto):
 · cena.json byte a byte idêntico;
 · cada malha com o MESMO conjunto de triângulos (vértices com posição, normal, cor e atributo; ordem ignorada, 5 casas);
 · nenhum arquivo de render a mais ou a menos.
Passou: o manifesto recebe o hash da cena atual e um registro 'prova_reuso' (hash antigo, novo, arquivos que mudaram).
Uso: python3 reaproveitar_com_prova.py <perfil> <plano> <pasta_da_cena_de_referência>"""
import os, sys, json, hashlib, time
import numpy as np
A = os.path.dirname(os.path.abspath(__file__))
perfil, pid, ref = sys.argv[1], sys.argv[2], sys.argv[3]
atual = os.path.join(A, 'cenas', pid); man = os.path.join(A, f'quadros_{perfil}', pid, '_manifesto.json')
def hcena(d):
    h = hashlib.sha256()
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
def tris(p):
    a = np.round(np.fromfile(p, np.float32).reshape(-1, 3, 12), 5)
    return sorted(tuple(sorted(map(tuple, t))) for t in a)
M = json.load(open(man)); reg = M['reg']
assert hcena(ref) == reg['cena'], f'a cena de referência ({hcena(ref)}) não é a do render ({reg["cena"]})'
render = lambda d: sorted(f for f in os.listdir(d) if f == 'cena.json' or f.endswith('.bin'))
assert render(ref) == render(atual), 'arquivos de render diferentes'
assert open(os.path.join(ref, 'cena.json'), 'rb').read() == open(os.path.join(atual, 'cena.json'), 'rb').read(), 'cena.json diferente'
iguais_bytes, iguais_sem_ordem = 0, []
for f in render(atual):
    if f == 'cena.json': continue
    b1, b2 = open(os.path.join(ref, f), 'rb').read(), open(os.path.join(atual, f), 'rb').read()
    if b1 == b2: iguais_bytes += 1; continue
    assert tris(os.path.join(ref, f)) == tris(os.path.join(atual, f)), f'malha {f} com geometria diferente'
    iguais_sem_ordem.append(f)
comp = [f for f in sorted(set(os.listdir(ref)) | set(os.listdir(atual))) if f not in render(atual)
        and (not os.path.exists(os.path.join(ref, f)) or not os.path.exists(os.path.join(atual, f)) or open(os.path.join(ref, f), 'rb').read() != open(os.path.join(atual, f), 'rb').read())]
prova = dict(quando=time.strftime('%Y-%m-%d %H:%M:%S'), cena_render=reg['cena'], cena_atual=hcena(atual), cena_json='idêntico',
             malhas_identicas_byte=iguais_bytes, malhas_iguais_sem_ordem=iguais_sem_ordem, composicao_mudou=comp)
M.setdefault('provas_reuso', []).append(prova); M['reg']['cena'] = prova['cena_atual']
json.dump(M, open(man, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(prova, ensure_ascii=False))
