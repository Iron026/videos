"""RENDER DEFINITIVO do Ep. 02 (1080 × 1920, 30 qps) com checkpoints — NÃO executar sem a aprovação do usuário.
Regras do manual (CLAUDE.md, "Render definitivo"), aplicadas aqui:
 · UM processo de render por vez (o renderizador por software não é determinístico em paralelo);
 · blocos de 60 quadros; cada quadro tem entrada no manifesto do plano: configuração, hash da cena (+ cena de sub-quadros
   do obturador), hash do motor, SHA-256 do arquivo, verificação; gravação ATÔMICA (render numa pasta temporária,
   verificação, depois `os.replace` para o destino);
 · retomada segura: um quadro só é reaproveitado se o manifesto bater (configuração + hashes) E o SHA-256 do arquivo
   conferir; quadros reprovados/obsoletos vão para `_descartados/` (nunca apagados);
 · verificação de cada quadro: decodifica, não é preto (luma média ≥ media_min), tamanho ≥ bytes_min, e semelhança com o
   quadro anterior do mesmo plano (escala grossa 32×56: correlação ≥ 0,93 OU diferença média ≤ 6 — limiares do Ep. 01,
   calibrados com texturas repetitivas); reprovado → PARA o processo para investigação (não segue renderizando);
 · obturador (config `obturador`): renderiza os m sub-quadros de cada quadro (cena <plano>_obt) e integra em luz linear.
Uso: python3 render_definitivo.py [--perfil final] [--simular] [planos...]
  --simular: só calcula o plano de trabalho (quadros por plano, blocos, reaproveitáveis), sem renderizar.
Log: quadros_<perfil>/_definitivo.log · manifestos: quadros_<perfil>/<plano>/_manifesto_quadros.json"""
import os, sys, json, hashlib, subprocess, time, shutil
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); MOTOR = os.path.join(RAIZ, 'motor')
args = sys.argv[1:]; PERFIL = 'final'; SIMULAR = '--simular' in args
if '--perfil' in args: PERFIL = args[args.index('--perfil') + 1]
CFG = json.load(open(os.path.join(RAIZ, 'config', 'producao.json'))); P = CFG['perfis'][PERFIL]; VER = CFG['verificacao']; OBT = CFG.get('obturador', {})
BLOCO = 60; CORR_MIN, DIF_MAX = 0.93, 6.0
sys.path.insert(0, os.path.join(RAIZ, 'decupagem')); import planos as PL
ids_arg = [a for a in args if not a.startswith('--') and a != PERFIL]
IDS = ids_arg or [x for p in PL.resolvidos()['planos'] for x in ([p['id']] + ([p['id'] + 'b'] if p['id'] in ('A4', 'J1') else ['G3z'] if p['id'] == 'G3' else []))]
OUT = os.path.join(A, f'quadros_{PERFIL}'); V8REF = os.path.join(A, f'quadros_{PERFIL}_v8'); _fi = os.path.join(A, '..', 'relatorios', 'saltos_investigados_r9.json'); INVEST = json.load(open(_fi)) if os.path.exists(_fi) else []; os.makedirs(OUT, exist_ok=True); LOG = os.path.join(OUT, '_definitivo.log')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
MOT = sha(os.path.join(MOTOR, 'render3.js'))[:16] + sha(os.path.join(MOTOR, 'render_anim.mjs'))[:8]
def log(m):
    l = time.strftime('%H:%M:%S ') + m; print(l, flush=True)
    if not SIMULAR: open(LOG, 'a').write(l + '\n')
def hcena(pid):
    h = hashlib.sha256(); d = os.path.join(A, 'cenas', pid)
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
def gravar_json(p, obj):
    tmp = p + '.tmp'; json.dump(obj, open(tmp, 'w'), ensure_ascii=False, indent=1); os.replace(tmp, p)
EFEITOS = ('uVarre', 'uTermico', 'uRevela', 'corte', 'uFoco', 'uDivide')   # efeitos gravados na cena que MUDAM a imagem de propósito
def quadros_em_transicao(cena, n):
    """Rodada 9: quadros k em que algum efeito da cena muda entre k−1 e k (mesma interpolação smoothstep do motor). Um salto
    nesses quadros é a transição desenhada (ex.: varredura da visão térmica), não defeito; fora deles, o salto continua PARANDO."""
    cv = cena.get('curvas', {}); g0 = cena['g0']; fps = 30
    def val(k_, g):
        k = cv[k_]
        if g <= k[0][0]: return k[0][1]
        for (t0, v0), (t1, v1) in zip(k, k[1:]):
            if g <= t1: u = (g - t0) / max(t1 - t0, 1e-6); return v0 + (v1 - v0) * u * u * (3 - 2 * u)
        return k[-1][1]
    out = set()
    for k in range(1, n):
        if any(e in cv and abs(val(e, g0 + k / fps) - val(e, g0 + (k - 1) / fps)) > 1e-4 for e in EFEITOS): out.add(k)
    return out
def verificar(f, anterior):
    try:
        im = Image.open(f); im.load(); g = np.asarray(im.convert('L').resize((32, 56)), np.float32)
    except Exception as e: return False, f'não decodifica ({e})', None
    if os.path.getsize(f) < VER['bytes_min']: return False, 'arquivo pequeno demais', g
    if g.mean() < VER['media_min']: return False, f'quase preto (média {g.mean():.1f})', g
    if anterior is not None:
        c = float(np.corrcoef(g.ravel(), anterior.ravel())[0, 1]) if g.std() > 1e-3 and anterior.std() > 1e-3 else 1.0; dm = float(np.abs(g - anterior).mean())
        if c < CORR_MIN and dm > DIF_MAX: return False, f'salto em relação ao quadro anterior (corr {c:.3f}, dif {dm:.1f})', g
    return True, 'ok', g
def integrar(src, js, dst):
    lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
    acc = sum(lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in js) / len(js)
    Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(dst, quality=95)
total_render = 0; plano_trabalho = []
for pid in IDS:
    cena = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); n = len(cena['animacao']['quadros'])
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={P['escala']}&{P['consulta']}{CFG['por_plano'].get(pid, '')}"
    reg = dict(consulta=q, perfil=PERFIL, motor=MOT, cena=hcena(pid))
    if pid in OBT: reg['obturador'] = dict(graus=OBT[pid]['graus'], sub=OBT[pid]['sub'], cena_sub=hcena(pid + '_obt'), **({'quadros': OBT[pid]['quadros']} if 'quadros' in OBT[pid] else {}))
    faixa = OBT.get(pid, {}).get('quadros'); em_obt = lambda i: pid in OBT and (faixa is None or faixa[0] <= i <= faixa[1])   # rodada 10: obturador só numa faixa
    d = os.path.join(OUT, pid); os.makedirs(d, exist_ok=True); mf = os.path.join(d, '_manifesto_quadros.json')
    man = json.load(open(mf)) if os.path.exists(mf) else dict(reg=reg, quadros={})
    ob_ant = man.get('reg', {}).get('obturador'); fx_ant = ob_ant.get('quadros') if ob_ant else None
    so_faixa = (man.get('reg') != reg and faixa is not None and {k: v for k, v in man.get('reg', {}).items() if k != 'obturador'} == {k: v for k, v in reg.items() if k != 'obturador'}
                and (ob_ant is None or (fx_ant is not None and {k: v for k, v in ob_ant.items() if k != 'quadros'} == {k: v for k, v in reg['obturador'].items() if k != 'quadros'})))
    if so_faixa:   # rodada 10: SÓ mudou a faixa do obturador (ou ele entrou numa faixa) — só os quadros que entram/saem da faixa são refeitos
        dsc = os.path.join(d, '_descartados', time.strftime('%Y%m%d_%H%M%S') + '_faixa_obturador')
        if not SIMULAR:
            os.makedirs(dsc, exist_ok=True)
            muda = set(range(faixa[0], faixa[1] + 1)) ^ (set(range(fx_ant[0], fx_ant[1] + 1)) if fx_ant else set())
            for i in sorted(muda):
                f = os.path.join(d, f'q{i:04d}.jpg')
                if os.path.exists(f): shutil.move(f, dsc)
                man['quadros'].pop(str(i), None)
            log(f'{pid}: obturador na faixa {faixa[0]}–{faixa[1]} (antes: {fx_ant}) — quadros que mudam {sorted(muda)} vão para {dsc}; os demais seguem válidos (SHA-256)')
            man['reg'] = reg; man.setdefault('historico', []).append(dict(quando=time.strftime('%Y-%m-%dT%H:%M:%S'), mudanca=f'obturador {OBT[pid]["graus"]}° na faixa {faixa}'))
            gravar_json(mf, man)
    # rodada 12: motor alterado com opção DESLIGADA por padrão (ordemtransp): planos que não a usam seguem válidos se o motor
    # anterior estiver em config motor_equivalente (prova numérica registrada lá); nada muda no quadro
    EQ = CFG.get('motor_equivalente', {}); ra = man.get('reg', {})
    if (ra != reg and 'ordemtransp' not in q and EQ.get(ra.get('motor'), {}).get('novo') == MOT
            and {k: v for k, v in ra.items() if k != 'motor'} == {k: v for k, v in reg.items() if k != 'motor'}):
        man['reg'] = reg
        if not SIMULAR:
            man.setdefault('historico', []).append(dict(quando=time.strftime('%Y-%m-%dT%H:%M:%S'), mudanca=f'motor {ra["motor"]} → {MOT}: equivalente com ordemtransp desligado ({EQ[ra["motor"]]["prova"]})'))
            gravar_json(mf, man); log(f'{pid}: motor {ra["motor"]} → {MOT} equivalente (opção nova desligada) — quadros seguem válidos (SHA-256)')
    # rodada 12: mudança de CONFIGURAÇÃO localizada com prova (_prova_reuso_config.json): só os quadros provados iguais ficam
    pc = os.path.join(d, '_prova_reuso_config.json'); pcfg = json.load(open(pc)) if os.path.exists(pc) else None
    if pcfg and pcfg.get('valida') and man.get('reg') == pcfg['reg_anterior'] and reg == pcfg['reg_novo']:
        iguais = set(pcfg['quadros_iguais'])
        if not SIMULAR:
            dsc = os.path.join(d, '_descartados', time.strftime('%Y%m%d_%H%M%S') + '_config_localizada'); os.makedirs(dsc, exist_ok=True)
        for k_ in list(man['quadros']):
            if int(k_) not in iguais:
                f = os.path.join(d, f'q{int(k_):04d}.jpg')
                if os.path.exists(f) and not SIMULAR: shutil.move(f, dsc)
                man['quadros'].pop(k_)
        man['reg'] = reg
        if not SIMULAR:
            man.setdefault('historico', []).append(dict(quando=time.strftime('%Y-%m-%dT%H:%M:%S'), mudanca=f'{pcfg["motivo"]}: {len(iguais)} quadros iguais por prova; refeitos os demais'))
            gravar_json(mf, man); log(f'{pid}: {pcfg["motivo"]} — {len(iguais)} quadros reaproveitados por prova; antigos dos demais em {dsc}')
    pv = os.path.join(d, '_prova_reuso_quadros.json'); prova = json.load(open(pv)) if os.path.exists(pv) else None
    so_cena = (man.get('reg') != reg and prova and prova.get('valida') and {k: v for k, v in man.get('reg', {}).items() if k != 'cena'} == {k: v for k, v in reg.items() if k != 'cena'}
               and man['reg'].get('cena') == prova['cena_atual'] and reg['cena'] == prova['cena_nova'])
    if so_cena and not SIMULAR:   # rodada 10: reexportação LOCALIZADA provada quadro a quadro (provar_quadros_iguais.py) — só os quadros diferentes saem
        dsc = os.path.join(d, '_descartados', time.strftime('%Y%m%d_%H%M%S') + '_cena_localizada'); os.makedirs(dsc, exist_ok=True); iguais = set(prova['quadros_iguais'])
        for k_ in list(man['quadros']):
            if int(k_) not in iguais:
                f = os.path.join(d, f'q{int(k_):04d}.jpg')
                if os.path.exists(f): shutil.move(f, dsc)
                man['quadros'].pop(k_)
        man.setdefault('historico', []).append(dict(quando=time.strftime('%Y-%m-%dT%H:%M:%S'), mudanca=f'cena {prova["cena_atual"]} → {prova["cena_nova"]}: {len(iguais)} quadros iguais por prova; diferentes: {sorted(prova["diferentes"], key=int)}'))
        man['reg'] = reg; gravar_json(mf, man); log(f'{pid}: cena reexportada com prova quadro a quadro — {len(iguais)} quadros reaproveitados; a renderizar: {sorted(prova["diferentes"], key=int)} (antigos em {dsc})')
    if man.get('reg') != reg and not so_faixa and not so_cena:   # configuração/cena/motor mudou: nada é reaproveitado; arquivos antigos vão para _descartados
        if man.get('quadros') and not SIMULAR:
            dsc = os.path.join(d, '_descartados', time.strftime('%Y%m%d_%H%M%S')); os.makedirs(dsc, exist_ok=True)
            for f in os.listdir(d):
                if f.endswith('.jpg'): shutil.move(os.path.join(d, f), dsc)
            log(f'{pid}: configuração mudou — quadros antigos movidos para {dsc}')
        man = dict(reg=reg, quadros={})
    validos = {int(k) for k, v in man['quadros'].items() if v.get('ok') and os.path.exists(os.path.join(d, f'q{int(k):04d}.jpg')) and sha(os.path.join(d, f'q{int(k):04d}.jpg')) == v['sha256']}
    faltam = [i for i in range(n) if i not in validos]
    m = OBT.get(pid, {}).get('sub', 1); total_render += sum(m if em_obt(i) else 1 for i in faltam)
    plano_trabalho.append(dict(plano=pid, quadros=n, reaproveitados=len(validos), a_renderizar=len(faltam), sub_quadros=m, blocos=-(-len(faltam) // BLOCO)))
    if SIMULAR or not faltam:
        if not faltam: log(f'{pid}: completo ({n} quadros conferidos por SHA-256)')
        continue
    blocos = []
    for i in faltam:
        if blocos and i == blocos[-1][-1] + 1 and len(blocos[-1]) < BLOCO and em_obt(i) == em_obt(blocos[-1][-1]): blocos[-1].append(i)
        else: blocos.append([i])
    TRANS = quadros_em_transicao(cena, n)
    for b in blocos:
        t = time.time(); tmp = os.path.join(d, '_tmp'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        if em_obt(b[0]):
            qs = q.replace(f'/cenas/{pid}/', f'/cenas/{pid}_obt/'); tsub = os.path.join(tmp, 'sub')
            r = subprocess.run(['node', 'render_anim.mjs', qs, tsub, '1', str(b[0] * m), str(b[-1] * m + m - 1)], cwd=MOTOR, capture_output=True, text=True)
            if r.returncode == 0:
                for i in b: integrar(tsub, range(i * m, i * m + m), os.path.join(tmp, f'q{i:04d}.jpg'))
        else:
            r = subprocess.run(['node', 'render_anim.mjs', q, tmp, '1', str(b[0]), str(b[-1])], cwd=MOTOR, capture_output=True, text=True)
        if r.returncode != 0: log(f'PARADA {pid} bloco {b[0]}–{b[-1]}: renderizador falhou: {r.stderr[-300:]}'); sys.exit(3)
        ant = None
        if b[0] - 1 in validos or str(b[0] - 1) in man['quadros']:
            fa = os.path.join(d, f'q{b[0] - 1:04d}.jpg'); ant = np.asarray(Image.open(fa).convert('L').resize((32, 56)), np.float32) if os.path.exists(fa) else None
        for i in b:
            ft = os.path.join(tmp, f'q{i:04d}.jpg'); ok, motivo, ant_ = verificar(ft, ant); just = None
            if not ok and motivo.startswith('salto') and i in TRANS:   # transição desenhada na cena (varredura térmica etc.)
                ok, just = True, motivo + ' — justificado: efeito da cena em transição neste quadro'; log(f'{pid} quadro {i}: {just}')
            if not ok and motivo.startswith('salto'):   # o MESMO salto na versão aprovada (V8), com a imagem equivalente à dela
              for nref, dref in ((('V10 aprovada (540, mesma cena)', os.path.join(A, 'quadros_revisao', pid)),) if PERFIL == 'final' else ()) + (('V8 aprovada', os.path.join(V8REF, pid)), ('prévia aprovada da rodada 9', os.path.join(A, 'quadros_previa_r9', pid + '_r9'))):   # rodada 11: no 1080, a referência é a V10 aprovada (comparação em 32×56, independente da resolução)
                fv, fv0 = (os.path.join(dref, f'q{j:04d}.jpg') for j in (i, i - 1))
                if not ok and os.path.exists(fv) and os.path.exists(fv0) and ant is not None:
                    gv, gv0, gn = (np.asarray(Image.open(x).convert('L').resize((32, 56)), np.float32) for x in (fv, fv0, ft))
                    cv = float(np.corrcoef(gv.ravel(), gv0.ravel())[0, 1]); cn = float(np.corrcoef(gn.ravel(), ant.ravel())[0, 1]); cx = float(np.corrcoef(gn.ravel(), gv.ravel())[0, 1])
                    if abs(cn - cv) <= 0.03 and cx >= CORR_MIN:
                        ok, just = True, motivo + f' — justificado: mesmo salto na {nref} (corr ref. {cv:.3f}; novo × ref. {cx:.3f})'; log(f'{pid} quadro {i}: {just}')
            if not ok and motivo.startswith('salto'):   # salto investigado por mim e registrado com evidência (relatorios/saltos_investigados_r9.json)
                for x in INVEST:
                    if x['plano'] == pid and x['quadros'][0] <= i <= x['quadros'][1]:
                        ok, just = True, motivo + ' — justificado: ' + x['motivo']; log(f'{pid} quadro {i}: {just}'); break
            if not ok:
                gravar_json(mf, man); log(f'PARADA {pid} quadro {i}: {motivo} — investigar antes de continuar (arquivo em {tmp})'); sys.exit(4)
            dst = os.path.join(d, f'q{i:04d}.jpg'); os.replace(ft, dst); ant = ant_
            man['quadros'][str(i)] = dict(ok=True, sha256=sha(dst), bytes=os.path.getsize(dst), quando=time.strftime('%Y-%m-%dT%H:%M:%S'), **({'salto_justificado': just} if just else {}), **({'obturador': True} if em_obt(i) else {}))
        gravar_json(mf, man); shutil.rmtree(tmp, ignore_errors=True)
        log(f'{pid}: bloco {b[0]}–{b[-1]} ({len(b)} quadros{f" × {m} sub" if em_obt(b[0]) and m > 1 else ""}) em {time.time() - t:.0f} s')
if SIMULAR:
    print(json.dumps(dict(perfil=PERFIL, planos=len(plano_trabalho), quadros_a_renderizar=sum(p['a_renderizar'] for p in plano_trabalho),
                          renders_de_motor=total_render, detalhes=plano_trabalho), ensure_ascii=False, indent=1))
else: log('FIM: todos os planos completos')
