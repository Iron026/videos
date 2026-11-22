"""Sound design do Ep. 02 — primeira mixagem (sistema modular herdado do Ep. 01: stems separados, reverberação por
ambiente, ducking multibanda sob a voz, loudness medido no AAC). GRAVAÇÕES REAIS (Freesound, CC0) para tudo o que é
físico; nenhuma síntese nesta versão. O MP3 da narração é só LIDO (decodificado para 48 kHz em memória).

Regras (CLAUDE.md): todo som tem origem e função; mecanismos seguem o estado real e a DISTÂNCIA real da câmera (posição
por quadro, de cena.json); nada de whoosh em cortes, visão térmica, feixes ou rótulos; ambiente contínuo (é a mesma
cozinha o tempo todo); a voz tem prioridade; silêncio no fim.

Eventos ancorados nas cenas e nas palavras verificadas:
 · porta abre (A1, I1) no ângulo da porta; porta fecha (C1) quando o ângulo chega a zero;
 · passos do personagem nos instantes de pouso calculados pela encenação (I1) e, fora de quadro, no recuo de A3;
 · compressor: ligado o episódio inteiro (a serpentina está quente desde a abertura); nível pela distância da câmera ao
   compressor, abafado quando o gabinete fica entre os dois; em E3 (câmera lenta) a gravação desce de tom;
 · evaporador: gorgolejo do fluido evaporando nos planos do evaporador (D), pela distância;
 · capilar: chiado da expansão em G3, crescendo quando a lupa chega ao ponto em que o líquido começa a evaporar.
Uso: python3 som_ep02.py [--sem-efeitos]   → som/stems/*.wav, som/audio_ep02.wav, som/mix_ep02.json, som/usos_ep02.json"""
import os, sys, json, math, subprocess
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, resample_poly
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..')
sys.path.insert(0, os.path.join(RAIZ, '..', 'episodio_01_navio_v2', 'episodio', 'som'))
import sintese as S                                     # só importado (Ep. 01 não é alterado)
from sintese import SR, n_, lpz, hpz, bp, db
S.AMBIENTES['cozinha'] = dict(rt=0.42, lp0=9000, lp1=2600, modos=[(165, 0.08), (290, 0.05)], pre=3,
                               er=[(6, 0.45), (11, 0.32), (17, 0.22), (26, 0.14)], ganho=1.0)
sys.path.insert(0, os.path.join(RAIZ, 'decupagem')); import planos as PL
R = PL.resolvidos(); DUR = R['duracao']; N = int(round(DUR * SR)); PLAN = {p['id']: p for p in R['planos']}
PAL = json.load(open(os.path.join(RAIZ, 'roteiro', 'palavras.json')))
FONTES = {x['id']: x for x in json.load(open(os.path.join(A, 'fontes_freesound.json')))}
ESC = json.load(open(os.path.join(A, 'escolhas.json')))           # papel → id + trecho (escolhido por medição)
MP3 = os.path.join(RAIZ, 'voz', 'ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3')
STEMS = {k: np.zeros((N, 2)) for k in ('efeitos', 'mecanismo', 'ambiencias')}
ENVIO = {k: np.zeros(N) for k in STEMS}
USOS = []
COMP = np.array([0.0, 0.18, 0.14]); EVAP = np.array([0.0, 0.0, 1.30]); CAPS = np.array([-0.15, 0.25, 1.42])


def T(p, apos=0.0): return next(w['inicio'] for w in PAL if w['palavra'].strip('.,:;?!').lower() == p and w['inicio'] >= apos)


# ------------------------------------------------------------------ gravações
_C = {}
def carregar(i):
    if i not in _C:
        f = os.path.join(A, 'bib', 'freesound', f'{i}.mp3')
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 's16le', '-'],
                                         capture_output=True, check=True).stdout, np.int16).astype(np.float64) / 32768
        _C[i] = x.reshape(-1, 2)
    return _C[i]


def trecho(i, ini, dur, fi=0.005, fo=0.08, tom=1.0, uso=''):
    a = carregar(i); i0 = int(ini * SR); i1 = min(len(a), i0 + int(dur * SR / tom)); x = a[i0:i1].copy()
    if tom != 1.0:
        from fractions import Fraction
        fr = Fraction(1 / tom).limit_denominator(60); x = resample_poly(x, fr.numerator, fr.denominator, axis=0)
    k1, k2 = min(len(x), n_(fi)), min(len(x), n_(fo))
    if k1: x[:k1] *= np.linspace(0, 1, k1)[:, None]
    if k2: x[-k2:] *= np.linspace(1, 0, k2)[:, None]
    pk = np.abs(x).max() + 1e-9
    USOS.append(dict(id=i, titulo=FONTES[i]['titulo'], ini=round(ini, 3), dur=round(len(x) / SR, 3), tom=tom, uso=uso))
    return x / pk


def laco(i, dur, ini=0.0, fim=None, xf=0.6, tom=1.0, uso=''):
    """Cama contínua: trechos [ini, fim] da gravação emendados por fusão de igual potência."""
    a = carregar(i); fim = fim or len(a) / SR - 0.05; seg = trecho(i, ini, fim - ini, 0.0, 0.0, tom, uso)
    k = n_(xf); out = seg.copy()
    while len(out) < dur * SR + k:
        w = np.linspace(0, 1, k)[:, None]
        out = np.concatenate([out[:-k], out[-k:] * np.cos(w * np.pi / 2) + seg[:k] * np.sin(w * np.pi / 2), seg[k:]])
    return out[:int(dur * SR)]


def por(t, x, ganho_db, stem='efeitos', pan=0.0, envio=0.25, env=None):
    i0 = int(round(t * SR)); i1 = min(N, i0 + len(x))
    if i1 <= max(0, i0): return
    y = x[max(0, -i0): i1 - i0] * db(ganho_db)
    if env is not None: y = y * env[max(0, i0):i1, None]
    g = np.array([math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)]) * math.sqrt(2)
    STEMS[stem][max(0, i0):i1] += y * g; ENVIO[stem][max(0, i0):i1] += y.mean(1) * envio


# ------------------------------------------------------------------ geometria: distância real da câmera, por quadro
_cam = {}
def cam_pos(g):
    """Posição da câmera do plano ativo no instante g (cena.json, 30 qps); planos de lupa/canal usam o plano principal."""
    p = next((q for q in R['planos'] if q['t0'] <= g < q['t1']), R['planos'][-1]); pid = p['id']
    if pid not in _cam:
        c = json.load(open(os.path.join(RAIZ, 'episodio', 'cenas', pid, 'cena.json'))); _cam[pid] = (c['g0'], np.array([q['camera']['pos'] for q in c['animacao']['quadros']]))
    g0, P = _cam[pid]; return P[max(0, min(len(P) - 1, int(round((g - g0) * 30))))], pid


def curva_distancia(alvo, ref=1.0, minimo_db=-30.0, oclusao=None):
    """Ganho (linear, por amostra) ∝ ref/d, suavizado (0,25 s); oclusao(pid) → dB extra quando algo fica no caminho."""
    ts = np.arange(0, DUR, 1 / 30); gs = []
    for t in ts:
        p, pid = cam_pos(t); d = max(0.25, float(np.linalg.norm(p - alvo))); gdb = max(minimo_db, 20 * math.log10(ref / d))
        if oclusao: gdb += oclusao(pid)
        gs.append(gdb)
    gs = np.convolve(np.array(gs), np.ones(8) / 8, mode='same')
    return db(np.interp(np.arange(N) / SR, ts, gs))


SEM_FX = '--sem-efeitos' in sys.argv
CORTE = set('CDEFGH') ; TECN = lambda pid: pid[0] in CORTE or pid == 'J3'     # planos em corte: nada entre câmera e mecanismo
COZ = lambda pid: not TECN(pid)


def ambiencia():
    e = ESC['cozinha']; x = laco(e['id'], DUR + 0.2, e.get('ini', 0.0), e.get('fim'), uso='ambiência da cozinha (tom do cômodo)')
    k = n_(1.2); x[-k:] *= np.linspace(1, 0, k)[:, None]                    # silêncio no fim
    por(0.0, x, e.get('db', -6.0), 'ambiencias', 0.0, 0.10)


def compressor():
    """Zumbido real do compressor, ligado o episódio todo; nível pela distância da câmera; abafado (gabinete no caminho)
    nos planos de cozinha; em E3, câmera lenta: a mesma gravação 0,75× (mais grave e mais lenta)."""
    e = ESC['zumbido']; x = laco(e['id'], DUR + 0.2, e.get('ini', 0.0), e.get('fim'), uso='zumbido do compressor (ligado)')[:N]
    k_ = n_(1.2); x[-k_:] *= np.linspace(1, 0, k_)[:, None]                                    # silêncio no fim
    ocl = lambda pid: -9.0 if COZ(pid) else 0.0
    g = curva_distancia(COMP, ref=0.6, minimo_db=-24, oclusao=ocl)
    coz = np.interp(np.arange(N) / SR, np.arange(0, DUR, 1 / 30), np.convolve([1.0 if COZ(cam_pos(t)[1]) else 0.0 for t in np.arange(0, DUR, 1 / 30)], np.ones(8) / 8, 'same'))
    abaf = lpz(x, 700, 2); x = x * (1 - coz[:len(x), None]) + abaf * coz[:len(x), None]       # gabinete no caminho: só graves
    t0, t1 = PLAN['E3']['t0'], PLAN['E3']['t1']; k = n_(0.25)
    lento = laco(e['id'], t1 - t0 + 0.6, e.get('ini', 0.0), e.get('fim'), tom=0.75, uso='zumbido em câmera lenta (E3)')
    w = np.zeros(N); i0, i1 = int(t0 * SR), int(t1 * SR); w[i0:i1] = 1; w = np.convolve(w, np.ones(k) / k, 'same')
    x = x * (1 - w[:len(x), None]); xl = np.zeros_like(x); xl[i0 - k // 2: i0 - k // 2 + len(lento)] = lento[:len(xl) - (i0 - k // 2)]
    x = x + xl * w[:len(x), None]
    por(0.0, x, e.get('db', -10.0), 'mecanismo', 0.0, 0.12, env=g)


def porta():
    e = ESC['porta_abre']; f = ESC['porta_fecha']
    for t_ang, onde in ((0.20, 'A1'), (T('deixa') - 0.13, 'I1')):
        x = trecho(e['id'], e['ini'], e['dur'], uso=f'porta abrindo ({onde}) — vedação descola no início do giro')
        por(t_ang + 0.04 - e.get('ataque', 0.0), x, e.get('db', -8.0), 'efeitos', 0.15, 0.25)
    t_fecha = PLAN['C1']['t0'] + 0.02 * (PLAN['C1']['t1'] - PLAN['C1']['t0']) + 1.0     # ângulo chega a zero
    x = trecho(f['id'], f['ini'], f['dur'], uso='porta fechando (C1) — batida no instante em que o ângulo chega a zero')
    por(t_fecha - f.get('ataque', 0.0), x, f.get('db', -8.0), 'efeitos', 0.2, 0.25)


def passos():
    e = ESC['passos']; pousos = []
    t0, t1 = 115.55, 116.95; pousos += [(t0 + (k + 1) * (t1 - t0) / 3, -10.0, 'entrada (I1)') for k in range(3)]
    # rodada 8: no I1 ele dá um passo à frente, pega o leite e sai pela esquerda (mesmos tempos de encenacao02.tempos_passos_i1)
    pousos += [(118.40, -12.0, 'passo à frente (I1)')] + [(118.80 + (119.70 - 118.80) * k / 2, -12.0, 'saída com o leite (I1)') for k in (1, 2)]
    pousos += [(3.05 + (k + 1) * (4.20 - 3.05) / 3, -22.0, 'recuo fora de quadro (A3)') for k in range(3)]
    amostra = list(range(len(pousos) - 3)) + [5, 6, 7]   # rodada 8: A3 mantém as MESMAS amostras da mixagem aprovada (5, 6, 7)
    for j, (t, gdb, onde) in enumerate(pousos):
        a = e['passos'][amostra[j] % len(e['passos'])]
        x = trecho(e['id'], a - 0.03, 0.32, fi=0.003, fo=0.12, uso=f'passo — {onde}')
        por(t - 0.03, x, e.get('db', -12.0) + gdb + 10, 'efeitos', -0.2, 0.3)


def evaporador():
    e = ESC['gorgolejo']; t0, t1 = PLAN['D1']['t0'], PLAN['D5']['t1']
    x = laco(e['id'], t1 - t0 + 0.5, e.get('ini', 0.0), e.get('fim'), uso='gorgolejo do fluido evaporando (planos do evaporador)')
    k = n_(0.8); x[:k] *= np.linspace(0, 1, k)[:, None]; x[-k:] *= np.linspace(1, 0, k)[:, None]
    g = curva_distancia(EVAP, ref=0.5, minimo_db=-20)
    por(t0 - 0.2, x, e.get('db', -14.0), 'mecanismo', -0.1, 0.15, env=g)


def capilar():
    """SÍNTESE (única desta mixagem, declarada): chiado da expansão no capilar — ruído na banda 2,5–7 kHz, levemente
    irregular, crescendo quando a lupa chega ao ponto em que o líquido começa a evaporar. Não há gravação real adequada."""
    e = ESC['chiado']; t0, t1 = PLAN['G3']['t0'], PLAN['G3']['t1']; tp = T('parte', apos=t0 - 0.5)
    n = int((t1 - t0 + 0.4) * SR); r = np.random.default_rng(2026)                     # gerador isolado (não muda outros sons)
    base = bp(r.standard_normal((n, 2)), 2500, 7000, 4); mod = 1 + 0.25 * np.convolve(r.standard_normal(n), np.ones(n_(0.08)) / n_(0.08) * 6, 'same')
    x = base * mod[:, None]; x /= np.abs(x).max() + 1e-9
    USOS.append(dict(id='sintese', titulo='chiado sintetizado (ruído filtrado)', ini=0, dur=round(n / SR, 3), tom=1.0, uso='chiado da expansão no capilar (G3) — SÍNTESE'))
    tt = np.arange(n) / SR + t0
    env = np.clip((tt - (tp - 0.6)) / 0.8, 0.25, 1.0); env[-n_(0.5):] *= np.linspace(1, 0, n_(0.5))
    por(t0, x * env[:, None], e.get('db', -18.0), 'mecanismo', 0.1, 0.1)


# ------------------------------------------------------------------ medidas (copiadas do Ep. 01 para não importar o mixer dele)
def k_weight(x):
    from scipy.signal import lfilter
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)


def lufs(x):
    y = k_weight(x if x.ndim == 2 else np.stack([x, x], 1)); w = int(0.4 * SR); h = int(0.1 * SR)
    p = np.array([np.mean(y[i:i + w] ** 2, 0).sum() for i in range(0, len(y) - w, h)]); l = -0.691 + 10 * np.log10(p + 1e-12)
    g = l > -70
    if not g.any(): return -99.0
    l1 = -0.691 + 10 * np.log10(p[g].mean() + 1e-12); g2 = g & (l > l1 - 10)
    return -0.691 + 10 * np.log10(p[g2].mean() + 1e-12)


def pico_verdadeiro(x): return 20 * np.log10(np.abs(resample_poly(x, 4, 1, axis=0)).max() + 1e-12)


def limitador(x, teto_db=-1.8, liberacao=0.08):
    from scipy.ndimage import minimum_filter1d
    up = np.abs(resample_poly(x, 4, 1, axis=0)).max(1); pk = up[: len(x) * 4].reshape(-1, 4).max(1)[:len(x)]
    g = np.minimum(1.0, db(teto_db) / (pk + 1e-12)); g = minimum_filter1d(g, size=2 * n_(0.0015) + 1)
    B = 8; m = -(-len(g) // B); gb = np.pad(g, (0, m * B - len(g)), constant_values=1).reshape(m, B).min(1)
    a = math.exp(-B / (liberacao * SR)); out = np.empty(m); cur = 1.0
    for i, v in enumerate(gb): cur = v if v < cur else cur * a + v * (1 - a); out[i] = cur
    out = np.minimum(np.repeat(out, B)[:len(g)], g); return x * out[:, None], float(20 * np.log10(out.min()))


def mixar(master_fixo_db=None, ganhos_fixos_db=None, sufixo=''):
    voz = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', MP3, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                                       capture_output=True, check=True).stdout, np.int16).astype(np.float64) / 32768
    v = np.zeros(N); v[:min(N, len(voz))] = voz[:N]
    # compressão SUAVE da cópia de mixagem da voz: a narração tem 20 dB entre pico e loudness (−21,7 LUFS, −1,7 dBTP) e a
    # meta é 12,5 dB (−14 LUFS, −1,5 dBTP), então ~7,5 dB de pico precisam sair. Limiar = percentil 90 do nível (5 ms) da
    # PRÓPRIA fala, razão 2:1: só os 10 % mais fortes são tocados; o resto do trabalho fica com o limitador. (Versão anterior,
    # −26 dBFS 2,5:1, comprimia > 75 % da fala até −11 dB: descartada.) O MP3 não muda.
    w5 = n_(0.005); nv = np.sqrt(np.convolve(v ** 2, np.ones(w5) / w5, 'same')) + 1e-9; ndb = 20 * np.log10(nv)
    LIM_V = float(np.percentile(ndb[ndb > -45], 90)); RAZ = 2.0
    gr = np.minimum(0.0, -(ndb - LIM_V) * (1 - 1 / RAZ)); gr = np.where(ndb > LIM_V, gr, 0.0)
    a_at, a_lb = math.exp(-1 / (0.005 * SR / 16)), math.exp(-1 / (0.12 * SR / 16)); gd = gr[::16]; sm_ = np.empty_like(gd); cur = 0.0
    for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); sm_[i] = cur
    gcv = np.repeat(sm_, 16)[:N]; v = v * db(gcv); COMP_VOZ = float(sm_.min()); COMP_MED = float(gcv[ndb > -45].mean())
    VOZ = np.stack([v, v], 1)
    ir = S.resposta_impulso('cozinha')
    for k in STEMS:
        for c in range(2): STEMS[k][:, c] += fftconvolve(ENVIO[k], ir[:, c])[:N]
        STEMS[k] = hpz(STEMS[k], 30, 2)
    Lv = lufs(VOZ); alvo = dict(ambiencias=Lv - 22.0, mecanismo=Lv - 15.0, efeitos=Lv - 9.0)    # níveis relativos à voz
    GK = {}
    for k in STEMS:
        if not np.abs(STEMS[k]).max(): GK[k] = 0.0; continue
        GK[k] = ganhos_fixos_db[k] if ganhos_fixos_db else alvo[k] - lufs(STEMS[k]); STEMS[k] *= db(GK[k])
    # ducking multibanda pela voz (mesmo princípio do Ep. 01): na banda 200 Hz–5 kHz o conjunto fica ≥ 13 dB abaixo da fala
    w = n_(0.03); mm = lambda x: np.convolve(x, np.ones(w) / w, 'same')
    ativa = np.clip(lpz((np.sqrt(mm(v ** 2)) > db(-42)).astype(float), 3.0), 0, 1); vm = np.sqrt(mm(bp(v, 200, 4000) ** 2)) + 1e-6
    meio = {k: STEMS[k] - lpz(STEMS[k], 200, 4) - hpz(STEMS[k], 5000, 4) for k in STEMS}; tot = sum(meio.values())
    sm = np.sqrt(mm((tot ** 2).mean(1))) + 1e-9; g = np.minimum(1.0, vm * db(-13.0) / sm); g = np.maximum(g, db(-18.0)); g = 1 - (1 - g) * ativa
    a_at, a_lb = math.exp(-1 / (0.010 * SR / 16)), math.exp(-1 / (0.45 * SR / 16)); gd = g[::16]; out = np.empty_like(gd); cur = 1.0
    for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); out[i] = cur
    gs = np.repeat(out, 16)[:N]
    for k in STEMS: STEMS[k] = STEMS[k] - meio[k] + meio[k] * gs[:, None]
    soma = VOZ + sum(STEMS.values())
    mg = master_fixo_db if master_fixo_db is not None else (-14.0 - lufs(soma))
    mix, red = limitador(soma * db(mg), -1.8)
    os.makedirs(os.path.join(A, 'stems'), exist_ok=True)
    for k in STEMS: sf.write(os.path.join(A, 'stems', f'ep02_{k}{sufixo}.wav'), (STEMS[k] * db(mg)).astype(np.float32), SR, subtype='PCM_24')
    sf.write(os.path.join(A, 'stems', f'ep02_voz{sufixo}.wav'), (VOZ * db(mg)).astype(np.float32), SR, subtype='PCM_24')
    sf.write(os.path.join(A, f'audio_ep02{sufixo}.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
    return dict(compressao_voz_max_db=round(COMP_VOZ, 1), compressao_voz_limiar_dbfs=round(LIM_V, 1), compressao_voz_razao=RAZ, compressao_voz_media_na_fala_db=round(COMP_MED, 2), master_db=round(mg, 2), ganhos_stems_db={k: round(v_, 2) for k, v_ in GK.items()}, ducking_max_db=round(float(20 * np.log10(gs.min())), 1),
                limitador_max_db=round(red, 2), lufs_wav=round(lufs(mix), 2), tp_wav=round(pico_verdadeiro(mix), 2))


if __name__ == '__main__':
    if not SEM_FX:
        ambiencia(); compressor(); porta(); passos(); evaporador(); capilar()
    ref = None
    if os.environ.get('MASTER_FIXO_DB'): ref = float(os.environ['MASTER_FIXO_DB'])
    gk = json.loads(os.environ['GANHOS_FIXOS']) if os.environ.get('GANHOS_FIXOS') else None
    rel = mixar(ref, gk, '_sem_efeitos' if SEM_FX else '')
    json.dump(rel, open(os.path.join(A, 'mix_ep02' + ('_sem_efeitos' if SEM_FX else '') + '.json'), 'w'), ensure_ascii=False, indent=1)
    if not SEM_FX: json.dump(USOS, open(os.path.join(A, 'usos_ep02.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rel, ensure_ascii=False))
