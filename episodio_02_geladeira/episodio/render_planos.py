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
for pid in IDS:
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={P['escala']}&{P['consulta']}{CFG['por_plano'].get(pid, '')}"
    reg = dict(consulta=q, passo=P['passo'], motor=MOT, cena=hcena(pid)); d = os.path.join(OUT, pid); man = os.path.join(d, '_manifesto.json')
    n = len(json.load(open(os.path.join(A, 'cenas', pid, 'cena.json')))['animacao']['quadros'])
    esperados = list(range(0, n, P['passo']))
    if os.path.exists(man) and json.load(open(man)).get('reg') == reg and all(os.path.exists(os.path.join(d, f'q{i:04d}.jpg')) for i in esperados):
        log(f'{pid} já renderizado com a mesma configuração'); continue
    t = time.time(); r = subprocess.run(['node', 'render_anim.mjs', q, d, str(P['passo'])], cwd=MOTOR, capture_output=True, text=True)
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
