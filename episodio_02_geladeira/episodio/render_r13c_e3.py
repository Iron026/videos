"""Rodada 13C — re-render LOCALIZADO do E3 com a correção da bobina (cenas/E3_r13c_faces: só m037.bin difere do E3 — saem as 2 faces de contato bobina × estator).
NÃO substitui o definitivo: grava em quadros_final_r13c/E3 (aguarda aprovação do comparativo).
Mesma configuração do definitivo (consulta do manifesto de quadros_final/E3, trocando só a pasta da cena), blocos de 40
quadros, manifesto com checkpoint por quadro (config, hash da cena e do motor, SHA-256, gravação atômica) e verificação de
cada quadro: decodifica, não-preto e semelhança com o quadro definitivo (escala grossa ≥ 0,93 e diferença média ≤ 6).
Uso: python3 render_r13c_e3.py [ini fim]"""
import os, sys, json, hashlib, subprocess, time, shutil
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
CENA = 'E3_r13c_faces'; DEF = os.path.join(A, 'quadros_final', 'E3'); OUT = os.path.join(A, 'quadros_final_r13c', 'E3'); os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
def hcena(d):
    h = hashlib.sha256()
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
md = json.load(open(os.path.join(DEF, '_manifesto_quadros.json')))
consulta = md['reg']['consulta'].replace('/cenas/E3/', f'/cenas/{CENA}/'); assert consulta != md['reg']['consulta']
MOT = sha(os.path.join(MOTOR, 'render3.js'))[:16] + sha(os.path.join(MOTOR, 'render_anim.mjs'))[:8]
reg = dict(consulta=consulta, perfil='final', motor=MOT, cena=hcena(os.path.join(A, 'cenas', CENA)), cena_definitivo=md['reg']['cena'], motor_definitivo=md['reg']['motor'])
EQ = json.load(open(os.path.join(A, '..', 'config', 'producao.json'))).get('motor_equivalente', {})
assert MOT == md['reg']['motor'] or EQ.get(md['reg']['motor'], {}).get('novo') == MOT, 'motor mudou desde o definitivo (sem equivalência registrada)'
reg['motor_equivalencia'] = EQ.get(md['reg']['motor'], {}).get('prova') if MOT != md['reg']['motor'] else None   # rodada 12 (config/producao.json); conferido de novo no E3: base3
mf = os.path.join(OUT, '_manifesto_quadros.json'); man = json.load(open(mf)) if os.path.exists(mf) else dict(reg=reg, quadros={})
assert man['reg'] == reg, 'configuração diferente da do manifesto existente'
def gravar(p, o): tmp = p + '.tmp'; json.dump(o, open(tmp, 'w'), ensure_ascii=False, indent=1); os.replace(tmp, p)
LOG = os.path.join(OUT, '_render.log')
def log(m): l = time.strftime('%H:%M:%S ') + m; print(l, flush=True); open(LOG, 'a').write(l + '\n')
def verificar(f, ref):
    try: im = Image.open(f); im.load()
    except Exception as e: return False, f'não decodifica ({e})', {}
    g = np.asarray(im.convert('L').resize((32, 56)), np.float32); r = np.asarray(Image.open(ref).convert('L').resize((32, 56)), np.float32)
    corr = float(np.corrcoef(g.ravel(), r.ravel())[0, 1]); dm = float(np.abs(g - r).mean())
    ok = g.mean() > 8 and corr >= 0.93 and dm <= 6.0
    return ok, ('ok' if ok else f'fora do limite (corr {corr:.3f}, dif {dm:.2f}, média {g.mean():.1f})'), dict(corr=round(corr, 4), dif=round(dm, 3))
n = len([f for f in os.listdir(DEF) if f.endswith('.jpg')])
ini, fim = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, n - 1)
faltam = [i for i in range(ini, fim + 1) if not (str(i) in man['quadros'] and man['quadros'][str(i)].get('ok')
                                                  and os.path.exists(os.path.join(OUT, f'q{i:04d}.jpg')) and sha(os.path.join(OUT, f'q{i:04d}.jpg')) == man['quadros'][str(i)]['sha256'])]
log(f'E3 r13c: {len(faltam)} quadros a renderizar ({ini}–{fim}); cena {reg["cena"]} (definitivo {reg["cena_definitivo"]}); motor {MOT}')
blocos = []
for i in faltam:
    if blocos and i == blocos[-1][-1] + 1 and len(blocos[-1]) < 40: blocos[-1].append(i)
    else: blocos.append([i])
for b in blocos:
    t = time.time(); tmp = os.path.join(OUT, '_tmp'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    r = subprocess.run(['node', 'render_anim.mjs', consulta, tmp, '1', str(b[0]), str(b[-1])], cwd=MOTOR, capture_output=True, text=True)
    if r.returncode != 0: log(f'PARADA bloco {b[0]}–{b[-1]}: renderizador falhou: {r.stderr[-300:]}'); sys.exit(3)
    for i in b:
        f = os.path.join(tmp, f'q{i:04d}.jpg'); ok, msg, med = verificar(f, os.path.join(DEF, f'q{i:04d}.jpg'))
        if not ok: log(f'PARADA quadro {i}: {msg}'); sys.exit(4)
        dst = os.path.join(OUT, f'q{i:04d}.jpg'); os.replace(f, dst)
        man['quadros'][str(i)] = dict(sha256=sha(dst), ok=True, verificacao=med, quando=time.strftime('%Y-%m-%dT%H:%M:%S')); gravar(mf, man)
    log(f'bloco {b[0]}–{b[-1]} ok em {time.time() - t:.0f} s ({(time.time() - t) / len(b):.1f} s/quadro)')
shutil.rmtree(os.path.join(OUT, '_tmp'), ignore_errors=True)
log(f'FIM: {sum(1 for v in man["quadros"].values() if v.get("ok"))} quadros válidos em {OUT}')
