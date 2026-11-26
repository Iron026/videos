"""Renderiza os planos do Ep. 02 num perfil de config/producao.json. UM processo de render por vez (lição do Ep. 01:
lotes paralelos no renderizador por software não são determinísticos). Manifesto por plano com a configuração e o hash da
cena e do motor; um plano só é pulado se tudo bater e todos os quadros existirem e decodificarem.
Uso: python3 render_planos.py <perfil> [planos...]   (log: quadros_<perfil>/_progresso.log)"""
import os, sys, json, hashlib, subprocess, time
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); MOTOR = os.path.join(RAIZ, 'motor')
CFG = json.load(open(os.path.join(RAIZ, 'config', 'producao.json'))); PERFIL = sys.argv[1]; P = CFG['perfis'][PERFIL]
sys.path.insert(0, os.path.join(RAIZ, 'decupagem')); import planos as PL
IDS = sys.argv[2:] or [x for p in PL.resolvidos()['planos'] for x in ([p['id']] + ([p['id'] + 'b'] if p['id'] in ('A4', 'J1') else ['G3z'] if p['id'] == 'G3' else []))]
OUT = os.path.join(A, f'quadros_{PERFIL}'); os.makedirs(OUT, exist_ok=True); LOG = os.path.join(OUT, '_progresso.log')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
MOT = sha(os.path.join(MOTOR, 'render3.js'))[:16] + sha(os.path.join(MOTOR, 'render_anim.mjs'))[:8]
def log(m): l = time.strftime('%H:%M:%S ') + m; print(l, flush=True); open(LOG, 'a').write(l + '\n')
def hcena(pid):
    h = hashlib.sha256(); d = os.path.join(A, 'cenas', pid)
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
import numpy as np
def integrar(src, dst_f, js):
    """Obturador: média em luz LINEAR dos sub-quadros js (mesma integração de obturador.py, validada na rodada 7)."""
    lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
    acc = sum(lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in js) / len(js)
    tmp = dst_f + '.tmp.jpg'; Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(tmp, quality=95); os.replace(tmp, dst_f)
OBT = CFG.get('obturador', {})
for pid in IDS:
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={P['escala']}&{P['consulta']}{CFG['por_plano'].get(pid, '')}"
    reg = dict(consulta=q, passo=P['passo'], motor=MOT, cena=hcena(pid)); d = os.path.join(OUT, pid); man = os.path.join(d, '_manifesto.json')
    if pid in OBT: reg['obturador'] = dict(OBT[pid], cena_sub=hcena(pid + '_obt'))
    n = len(json.load(open(os.path.join(A, 'cenas', pid, 'cena.json')))['animacao']['quadros'])
    esperados = list(range(0, n, P['passo']))
    if os.path.exists(man) and json.load(open(man)).get('reg') == reg and all(os.path.exists(os.path.join(d, f'q{i:04d}.jpg')) for i in esperados):
        log(f'{pid} já renderizado com a mesma configuração'); continue
    t = time.time()
    if pid in OBT:   # rodada 8: obturador de 180° — renderiza os m sub-quadros de cada quadro e integra em luz linear
        m = OBT[pid]['sub']; qs = q.replace(f'/cenas/{pid}/', f'/cenas/{pid}_obt/'); dsub = os.path.join(OUT, pid + '_obt')
        r = subprocess.run(['node', 'render_anim.mjs', qs, dsub, '1', str(esperados[0] * m), str(esperados[-1] * m + m - 1)], cwd=MOTOR, capture_output=True, text=True)
        os.makedirs(d, exist_ok=True)
        if r.returncode == 0:
            for i in esperados: integrar(dsub, os.path.join(d, f'q{i:04d}.jpg'), range(i * m, i * m + m))
    else: r = subprocess.run(['node', 'render_anim.mjs', q, d, str(P['passo'])], cwd=MOTOR, capture_output=True, text=True)
    ruins = []
    for i in esperados:
        f = os.path.join(d, f'q{i:04d}.jpg')
        try:
            im = Image.open(f); im.load(); g = im.convert('L')
            if os.path.getsize(f) < CFG['verificacao']['bytes_min'] or sum(g.resize((32, 56)).getdata()) / (32 * 56) < CFG['verificacao']['media_min']: ruins.append(i)
        except Exception: ruins.append(i)
    erro = 'ERROS' in r.stdout or r.returncode != 0
    json.dump(dict(reg=reg, quadros=len(esperados), ruins=ruins, segundos=round(time.time() - t, 1), saida=r.stdout.strip().splitlines()[-1:] if r.stdout else r.stderr[-300:]),
              open(man, 'w'), ensure_ascii=False, indent=1)
    log(f'{pid}: {len(esperados)} quadros em {time.time()-t:.0f} s · ruins {ruins[:5]}{" · ERRO " + r.stderr[-200:] if erro else ""}')
    if ruins or erro: log(f'PARADA em {pid}: investigar antes de continuar'); sys.exit(3)
