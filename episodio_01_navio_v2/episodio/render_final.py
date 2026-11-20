"""Render DEFINITIVO do Ep. 01 (1080 × 1920, 30 fps reais), com a qualidade dos testes aprovados.

Configuração (única, registrada no manifesto): escala=1 (1080 × 1920), oclusão ambiente GTAO 16 amostras, MSAA 4×, bloom 0,22,
janoff=1 (prioridade de profundidade das janelas), correção de profundidade da água (oclusor a 0,994, padrão do render2.js).
A correção de cor, os rótulos, os avisos e as legendas entram na montagem (montar_ep01.py final), não aqui.

Regras:
• UM processo de render por vez (nada em paralelo), em blocos de 60 quadros por segmento.
• Checkpoint por quadro no manifesto (quadros_final/_manifesto.json, gravado de forma atômica após cada bloco): retomável.
• Um quadro só é reaproveitado se o manifesto o registrar com a MESMA configuração (consulta + hash do render2.js e do
  render_anim.mjs) e a MESMA cena (hash dos arquivos da cena), e o arquivo tiver o mesmo SHA-256 e decodificar inteiro.
• Cada quadro novo é verificado: decodificação completa, 1080 × 1920, não preto, e semelhança (SSIM, reduzido a 540 × 960) com o
  quadro da revisão aprovada no mesmo índice. Falha → re-render isolado; persistindo → PARA (código 3) para investigação.
• Quadros que estavam em quadros_final/ sem registro compatível são movidos para quadros_final_descartados/ (nada é apagado).
Uso: python3 episodio/render_final.py [segmentos...]      (log: quadros_final/_progresso.log)"""
import os, sys, json, time, shutil, hashlib, subprocess
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motores', 'tempo_real_v2')
SAIDA = os.path.join(A, 'quadros_final'); DESC = os.path.join(A, 'quadros_final_descartados'); MAN = os.path.join(SAIDA, '_manifesto.json'); LOG = os.path.join(SAIDA, '_progresso.log')
SEGS = sys.argv[1:] or ['01', '02', '03', '04', '05', '0607', '0607b', '08a', '08b', '09', '10', '11', '12x', '12', '13']
Q = 'escala=1&aoamostras=16&msaa=4&bloom=0.22&janoff=1'
BLOCO, SSIM_MIN = 60, 0.90
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
CONFIG = dict(consulta=Q, resolucao='1080x1920', fps=30, render2_js=sha(os.path.join(MOTOR, 'render2.js')), render_anim_mjs=sha(os.path.join(MOTOR, 'render_anim.mjs')), three='r170',
              oclusor_agua=0.994, nota='correção de cor, rótulos, avisos e legendas: na montagem (montar_ep01.py final)')
CID = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()[:16]
def log(msg):
    linha = time.strftime('%Y-%m-%d %H:%M:%S ') + msg; print(linha, flush=True); open(LOG, 'a').write(linha + '\n')
def hash_cena(seg):
    d = os.path.join(A, 'cenas', f's{seg}'); h = hashlib.sha256()
    for f in sorted(os.listdir(d)):
        if f == 'cena.json' or f.endswith('.bin'): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
def salvar(man):
    t = MAN + '.tmp'; json.dump(man, open(t, 'w'), ensure_ascii=False); os.replace(t, MAN)
def ssim(a, b):
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2; ma, mb = uniform_filter(a, 7), uniform_filter(b, 7)
    va, vb, cab = uniform_filter(a * a, 7) - ma ** 2, uniform_filter(b * b, 7) - mb ** 2, uniform_filter(a * b, 7) - ma * mb
    return float((((2 * ma * mb + c1) * (2 * cab + c2)) / ((ma ** 2 + mb ** 2 + c1) * (va + vb + c2))).mean())
def verificar(seg, q):
    """→ (ok, info): decodifica inteiro, confere tamanho, não preto, semelhança com a revisão aprovada."""
    p = os.path.join(SAIDA, f's{seg}', f'q{q:04d}.jpg')
    if not os.path.exists(p) or os.path.getsize(p) < 20000: return False, dict(erro='ausente ou incompleto')
    try:
        im = Image.open(p); im.load()
    except Exception as e: return False, dict(erro=f'corrompido: {e}')
    if im.size != (1080, 1920): return False, dict(erro=f'tamanho {im.size}')
    g = np.asarray(im.convert('L').resize((540, 960), Image.LANCZOS)).astype(np.float32)
    if g.mean() < 3: return False, dict(erro='quadro preto')
    info = dict(sha256=sha(p), bytes=os.path.getsize(p), config=CID)
    r = os.path.join(A, 'quadros_revisao', f's{seg}', f'q{q:04d}.jpg')
    if os.path.exists(r):
        s = ssim(g, np.asarray(Image.open(r).convert('L')).astype(np.float32)); info['ssim_revisao'] = round(s, 4)
        if s < SSIM_MIN: return False, dict(info, erro=f'diverge da revisão aprovada (SSIM {s:.3f})')
    return True, info
def render(seg, a, b):
    r = subprocess.run(['node', 'render_anim.mjs', f'cena=../../episodio/cenas/s{seg}/&{Q}', f'../../episodio/quadros_final/s{seg}', '1', str(a), str(b)],
                       cwd=MOTOR, capture_output=True, text=True)
    fim = [l for l in r.stdout.splitlines() if 'FIM' in l or 'ERRO' in l]
    return r.returncode == 0 and any('FIM' in l and 'ERROS' not in l for l in fim), (fim[-1] if fim else r.stderr[-300:])

os.makedirs(SAIDA, exist_ok=True)
man = json.load(open(MAN)) if os.path.exists(MAN) else dict(config=CONFIG, config_id=CID, segmentos={})
if man.get('config_id') != CID:
    log(f'configuração mudou ({man.get("config_id")} → {CID}): nenhum quadro antigo é reaproveitado'); man = dict(config=CONFIG, config_id=CID, segmentos={})
salvar(man)
log(f'INÍCIO · config {CID} · {Q} · segmentos {",".join(SEGS)}')
t_ini = time.time(); feitos = 0
for seg in SEGS:
    n = len(json.load(open(os.path.join(A, 'cenas', f's{seg}', 'cena.json')))['animacao']['quadros'])
    hc = hash_cena(seg); ms = man['segmentos'].get(seg)
    if not ms or ms.get('cena') != hc: ms = man['segmentos'][seg] = dict(cena=hc, n=n, quadros={})
    d = os.path.join(SAIDA, f's{seg}'); os.makedirs(d, exist_ok=True)
    # reaproveitamento: só quadros registrados com a mesma config/cena, mesmo SHA-256 e íntegros; o resto sai da pasta
    validos = set()
    for f in sorted(os.listdir(d)):
        if not f.endswith('.jpg'): continue
        q = int(f[1:5]); reg = ms['quadros'].get(str(q)); p = os.path.join(d, f)
        if reg and reg.get('config') == CID and reg.get('sha256') == sha(p) and verificar(seg, q)[0]: validos.add(q)
        else:
            os.makedirs(os.path.join(DESC, f's{seg}'), exist_ok=True); shutil.move(p, os.path.join(DESC, f's{seg}', f)); ms['quadros'].pop(str(q), None)
    faltam = [q for q in range(n) if q not in validos]
    log(f'SEG s{seg}: {n} quadros · {len(validos)} reaproveitados · {len(faltam)} a renderizar')
    blocos = []
    for q in faltam:
        if blocos and q == blocos[-1][1] + 1 and q - blocos[-1][0] < BLOCO: blocos[-1][1] = q
        else: blocos.append([q, q])
    for a, b in blocos:
        t0 = time.time(); ok, msg = render(seg, a, b)
        if not ok:
            log(f'  s{seg} {a}-{b}: falha do renderizador ({msg}); nova tentativa'); ok, msg = render(seg, a, b)
            if not ok: log(f'PARADA: s{seg} {a}-{b} falhou duas vezes ({msg})'); salvar(man); sys.exit(2)
        ruins = []
        for q in range(a, b + 1):
            ok, info = verificar(seg, q)
            if ok: ms['quadros'][str(q)] = info
            else: ruins.append((q, info))
        for q, info in ruins:   # re-render isolado do quadro problemático
            log(f'  s{seg} q{q}: {info.get("erro")} → re-render isolado'); render(seg, q, q); ok, info2 = verificar(seg, q)
            if ok: ms['quadros'][str(q)] = dict(info2, rerender=info.get('erro'))
            else: log(f'PARADA: s{seg} q{q} continua com defeito ({info2.get("erro")}): investigar antes de continuar'); salvar(man); sys.exit(3)
        salvar(man); feitos += b - a + 1
        ss = [ms['quadros'][str(q)].get('ssim_revisao', 1) for q in range(a, b + 1)]
        log(f'  s{seg} {a}-{b} ok · {(time.time() - t0) / (b - a + 1):.2f} s/quadro · SSIM mín. {min(ss):.3f} · total novo {feitos} · {(time.time() - t_ini) / 3600:.2f} h')
    log(f'SEG s{seg} CONCLUÍDO ({len(ms["quadros"])}/{n})')
tot = sum(len(v['quadros']) for v in man['segmentos'].values())
log(f'FIM_RENDER_FINAL · {tot} quadros registrados · {(time.time() - t_ini) / 3600:.2f} h')
