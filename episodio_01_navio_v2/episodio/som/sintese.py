"""Biblioteca de síntese ORIGINAL para o sound design (nenhuma amostra de terceiros): impactos metálicos por síntese modal,
respingos em camadas, bolhas (modelo de Minnaert), atrito aço × concreto, motores elétricos, cabos sob tensão, solda,
fluxo de água, ambiências e respostas ao impulso sintéticas para reverberação por ambiente."""
import math, numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

SR = 48000
rng = np.random.default_rng(20261119)
_SOS = {}


def _sos(tipo, f, o=4):
    k = (tipo, f if not isinstance(f, list) else tuple(f), o)
    if k not in _SOS:
        fn = [min(max(x, 10.0), SR / 2 * 0.98) for x in (f if isinstance(f, (list, tuple)) else [f])]
        _SOS[k] = butter(o, fn if len(fn) > 1 else fn[0], tipo, fs=SR, output='sos')
    return _SOS[k]


def lp(x, f, o=4): return sosfilt(_sos('lowpass', f, o), x)
def hp(x, f, o=4): return sosfilt(_sos('highpass', f, o), x)
def bp(x, lo, hi, o=4): return sosfilt(_sos('bandpass', [lo, hi], o), x)
def lpz(x, f, o=2): return sosfiltfilt(_sos('lowpass', f, o), x, axis=0)
def hpz(x, f, o=2): return sosfiltfilt(_sos('highpass', f, o), x, axis=0)
def n_(s): return max(1, int(round(s * SR)))
def tt(n): return np.arange(n) / SR
def ruido(n): return rng.standard_normal(n)
def db(v): return 10 ** (v / 20)


def rosa(n):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); f[0] = f[1]
    x = np.fft.irfft(X / np.sqrt(f), n); return x / (np.std(x) + 1e-12)


def marrom(n):
    x = np.cumsum(rng.standard_normal(n)); x = hp(x, 18, 2); return x / (np.std(x) + 1e-12)


def lento_lfo(n, f=0.5, prof=0.5, oitavas=2):
    """Modulação lenta e irregular (0..1) para turbulência, ondas, vento."""
    m = np.zeros(n)
    for k in range(oitavas):
        c = max(2, int(n / SR * f * 2 ** k) + 3)
        m += np.interp(np.arange(n), np.linspace(0, n, c), rng.standard_normal(c)) / 2 ** k
    m = (m - m.min()) / (np.ptp(m) + 1e-9); return 1 - prof + prof * m


def janela(n, a=0.01, r=0.1):
    t = tt(n); d = n / SR; return np.clip(t / max(a, 1e-4), 0, 1) * np.clip((d - t) / max(r, 1e-4), 0, 1)


def chirp(f0, f1, n, curva=1.0):
    k = np.linspace(0, 1, n) ** curva; f = f0 + (f1 - f0) * k; return np.sin(2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6.28))


# ------------------------------------------------------------------------------------------------ metal
def modal(dur, modos, golpe=0.003, ruido_golpe=0.4, brilho_golpe=1500):
    """Síntese modal: soma de modos amortecidos (f, tau, amp) + excitação curta (golpe)."""
    n = n_(dur); t = tt(n); x = np.zeros(n)
    for (f, tau, a) in modos:
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    k = n_(golpe); x[:k] += ruido_golpe * hp(ruido(k), brilho_golpe) * np.linspace(1, 0, k)
    x[:n_(0.0008)] *= np.linspace(0, 1, n_(0.0008)); return x


def impacto_aco(massa=1.0, dur=1.4, brilho=1.0, sem=None):
    """Aço maciço batendo em concreto/aço: corpo grave (pesado), modos inarmônicos médios curtos, estalo de contato."""
    r = np.random.default_rng(sem) if sem is not None else rng
    f0 = 52 / massa ** 0.25
    modos = [(f0, 0.18 * massa ** 0.3, 1.0), (f0 * 1.9, 0.11, 0.45)]
    for k, rel in enumerate((3.9, 6.6, 9.8, 14.1, 19.7, 27.3)):
        modos.append((f0 * rel * r.uniform(0.96, 1.04), 0.06 + 0.12 * r.random() / (1 + k * 0.4), 0.30 * brilho / (1 + 0.5 * k)))
    x = modal(dur, modos, golpe=0.004, ruido_golpe=0.8 * brilho, brilho_golpe=900)
    n = len(x); t = tt(n); x += 0.35 * lp(ruido(n), 260) * np.exp(-t / 0.10)          # massa de ar deslocada no impacto
    return x


def clank_chapa(tam=1.0, sem=None, rattle=2):
    """Chapa de aço (contato/encaixe): modos de placa + pequenos repiques de acomodação."""
    r = np.random.default_rng(sem)
    base = 95 / tam ** 0.5
    modos = [(base * m * r.uniform(0.95, 1.05), r.uniform(0.08, 0.35), a) for m, a in ((1, 0.9), (2.3, 0.6), (3.8, 0.45), (5.9, 0.35), (8.7, 0.25), (12.4, 0.18), (17.0, 0.12))]
    x = modal(1.2, modos, golpe=0.003, ruido_golpe=0.6)
    for k in range(rattle):
        d = n_(r.uniform(0.03, 0.14) * (k + 1)); y = modal(0.5, [(f * r.uniform(0.98, 1.02), tau * 0.5, a * 0.4) for (f, tau, a) in modos[2:]], ruido_golpe=0.2)
        m = min(len(y), len(x) - d); x[d:d + m] += y[:m] * r.uniform(0.2, 0.45)
    return x


def conteiner_pouso(peso=1.0, sem=None):
    """Contêiner (caixa de aço de ~20 t) assentando: baque grave da caixa, tinido dos cantos (castings) e trepidação curta."""
    r = np.random.default_rng(sem)
    n = n_(1.3); t = tt(n)
    f0 = r.uniform(58, 74)
    corpo = np.sin(2 * np.pi * np.cumsum(f0 * (1 - 0.25 * np.minimum(t / 0.2, 1))) / SR) * np.exp(-t / (0.16 * peso ** 0.3))
    caixa = modal(1.3, [(f * r.uniform(0.95, 1.05), tau, a) for f, tau, a in ((118, 0.14, 0.6), (187, 0.11, 0.45), (263, 0.09, 0.35), (342, 0.07, 0.25))], ruido_golpe=0.3)
    cantos = modal(1.3, [(f * r.uniform(0.93, 1.07), tau, a) for f, tau, a in ((640, 0.09, 0.5), (1130, 0.07, 0.4), (1790, 0.05, 0.3), (2620, 0.04, 0.22), (3900, 0.03, 0.12))], ruido_golpe=0.5, brilho_golpe=2500)
    x = 1.0 * corpo + 0.7 * caixa + 0.55 * cantos
    for k in range(r.integers(1, 4)):                                   # segundo canto e acomodação
        d = n_(r.uniform(0.012, 0.18)); x[d:] += 0.35 * cantos[:n - d] * r.uniform(0.3, 0.8)
    trep = lp(ruido(n), 140) * np.exp(-t / 0.35) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t))   # trepidação da pilha/convés
    return (x + 0.4 * trep) * peso


def rangido(dur, f0=180, desliza=0.25, rugosidade=60, sem=None):
    """Rangido metálico (stick-slip): pulsos de atrito em taxa variável excitando ressonâncias que deslizam."""
    r = np.random.default_rng(sem); n = n_(dur); t = tt(n)
    taxa = rugosidade * (0.7 + 0.6 * lento_lfo(n, 3.0, 1.0))
    fase = np.cumsum(taxa / SR); imp = np.diff(np.floor(fase), prepend=0) * r.lognormal(0, 0.4, n)
    from scipy.signal import lfilter
    x = np.zeros(n)
    for k, rel in enumerate((1.0, 1.63, 2.41, 3.7)):
        f = f0 * rel * (1 + desliza * (t / dur - 0.5)); bw = 6.0 + 3 * k          # largura de banda (Hz) da ressonância
        rr = np.exp(-np.pi * bw / SR); y = np.zeros(n); zi = np.zeros(2)
        for i0 in range(0, n, 512):                    # ressonador de 2 polos com frequência deslizante, em blocos
            w = 2 * np.pi * f[i0] / SR
            y[i0:i0 + 512], zi = lfilter([1.0 - rr], [1.0, -2 * rr * np.cos(w), rr * rr], imp[i0:i0 + 512], zi=zi)
        x += y / (1 + k)
    return x / (np.abs(x).max() + 1e-9) * janela(n, 0.05, 0.15)


# ------------------------------------------------------------------------------------------------ água
def bolhas(dur, taxa, rmin=0.0008, rmax=0.006, sobe=0.25, sem=None):
    """Bolhas (Minnaert: f ≈ 3,26/r Hz, r em m), cada uma um seno amortecido com leve subida de altura."""
    r = np.random.default_rng(sem); n = n_(dur); x = np.zeros(n)
    k = r.poisson(max(taxa * dur, 0))
    for _ in range(k):
        rr = math.exp(r.uniform(math.log(rmin), math.log(rmax))); f = 3.26 / rr
        d = 0.004 + rr * 9.0; m = n_(d * 3); t = tt(m)
        ph = 2 * np.pi * np.cumsum(f * (1 + sobe * t / (d * 3))) / SR
        y = np.sin(ph) * np.exp(-t / d) * (rr / rmax) ** 0.35 * r.uniform(0.4, 1.0)
        i = r.integers(0, max(1, n - m)); x[i:i + m] += y[:max(0, min(m, n - i))]
    return x


def respingo(escala=1.0, lento=1.0, denso=1.0, sem=None):
    """Respingo em camadas, estéreo: (1) baque do impacto, (2) lençol/coroa de água, (3) colapso da cavidade (whoomp),
    (4) gotas caindo de volta, (5) lavagem. lento > 1 = câmera lenta (mais longo e mais grave). denso > 1 = objeto pesado/compacto."""
    r = np.random.default_rng(sem); L = lento
    n = n_(2.6 * L * max(escala, 0.6) + 0.4); t = tt(n)
    thump = np.sin(2 * np.pi * np.cumsum((90 - 45 * np.minimum(t / (0.12 * L), 1)) / L ** 0.8) / SR) * np.exp(-t / (0.10 * L * denso ** 0.5))
    lencol = bp(ruido(n), 260 / L ** 0.7, 5200 / L ** 0.6) * np.minimum(1, t / (0.006 * L)) * np.exp(-t / (0.22 * L * escala ** 0.5)) * lento_lfo(n, 18 / L, 0.5)
    k0 = n_(0.10 * L); cav = np.zeros(n); m = n_(0.45 * L); tc = tt(m)
    cav[k0:k0 + m] = (lp(ruido(m), 320 / L ** 0.5) * np.sin(np.pi * tc / (0.45 * L)) ** 2 + 0.6 * np.sin(2 * np.pi * np.cumsum(70 - 25 * tc / tc[-1]) / L / SR) * np.sin(np.pi * tc / (0.45 * L)) ** 3)[:n - k0]
    lav = bp(ruido(n), 350 / L ** 0.5, 2600 / L ** 0.5) * np.clip((t - 0.35 * L) / (0.3 * L), 0, 1) * np.exp(-np.maximum(t - 0.6 * L, 0) / (0.5 * L * escala))
    out = np.zeros((n, 2))
    nucleo = 0.9 * denso * thump + 0.75 * lencol + 0.8 * denso * cav + 0.35 * escala * lav
    for c in range(2):
        g = bolhas(n / SR, 70 * escala / L, 0.0015 * L ** 0.5, 0.007 * L ** 0.5, sem=None if sem is None else sem + c)
        g *= np.clip((t - 0.12 * L) / (0.1 * L), 0, 1) * np.exp(-t / (0.9 * L * escala))
        out[:, c] = nucleo + 0.45 * g
    return out * janela(n, 0.0005, 0.3)[:, None]


def fluxo_agua(dur, intens=None, lo=180, hi=2800, turb=8.0, sem=None):
    """Água correndo/jorrando: ruído em banda com turbulência; 'intens' = curva 0..1 (array do tamanho do trecho)."""
    n = n_(dur); x = bp(ruido(n), lo, hi) * lento_lfo(n, turb, 0.55, 3)
    x += 0.5 * lp(ruido(n), lo * 1.4) * lento_lfo(n, turb / 3, 0.6)
    if intens is not None: x *= intens
    return x


def marulho(dur, taxa=1.2, sem=None):
    """Água batendo no casco/cais: pancadas curtas e irregulares."""
    r = np.random.default_rng(sem); n = n_(dur); x = np.zeros(n)
    for _ in range(r.poisson(taxa * dur)):
        m = n_(r.uniform(0.25, 0.7)); t = tt(m)
        y = bp(ruido(m), r.uniform(180, 300), r.uniform(900, 1800)) * np.minimum(1, t / 0.02) * np.exp(-t / r.uniform(0.08, 0.2))
        y += 0.4 * bolhas(m / SR, 40, 0.001, 0.004) * np.exp(-t / 0.25)
        i = r.integers(0, max(1, n - m)); x[i:i + m] += y[:n - i] * r.uniform(0.4, 1.0)
    return x


def mar(n, ondas=0.16, vento=0.0):
    """Mar aberto: ondas (massa grave + espuma das cristas) e vento."""
    o = lp(rosa(n), 700) * lento_lfo(n, ondas, 0.75, 2)
    cr = bp(ruido(n), 900, 4500) * lento_lfo(n, ondas * 1.3, 0.92, 2) ** 3
    x = o + 0.35 * cr
    if vento: x += vento * bp(rosa(n), 250, 1800) * lento_lfo(n, 0.08, 0.8, 3)
    return x


# ------------------------------------------------------------------------------------------------ máquinas
def motor_eletrico(v, f0=55.0, f1=420.0, engrenagem=0.5):
    """Motor/redutor de guindaste: zumbido harmônico que sobe com a velocidade v (0..1, por amostra) + engrenagens."""
    f = f0 + (f1 - f0) * v; ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(a * np.sin(k * ph) for k, a in ((1, 1.0), (2, 0.5), (3, 0.32), (5, 0.18), (7, 0.1)))
    eng = bp(ruido(len(v)), 400, 2500) * (0.55 + 0.45 * np.sin(ph * 0.25)) * engrenagem
    amp = np.clip(v, 0, 1) ** 0.6
    return (lp(x, 1600) + eng) * amp


def guincho(v, catraca=14.0):
    """Tambor do guincho: estalos da catraca em taxa ∝ velocidade + ronco do tambor."""
    n = len(v); fase = np.cumsum(catraca * np.clip(v, 0, 1) / SR); imp = np.diff(np.floor(fase), prepend=0)
    cl = bp(imp * rng.lognormal(0, 0.3, n), 1200, 5000) * 6
    return cl + lp(ruido(n), 180) * np.clip(v, 0, 1) * 0.8


def cabo_cantando(tensao):
    """Cabo de aço sob tensão: leve 'canto' agudo e tremido, proporcional à tensão (0..1)."""
    n = len(tensao); x = bp(ruido(n), 950, 1350, 2) * lento_lfo(n, 6, 0.6)
    x += 0.3 * np.sin(2 * np.pi * np.cumsum(1100 + 60 * lento_lfo(n, 0.7, 1.0)) / SR)
    return x * np.clip(tensao, 0, 1)


def arco_solda(env, crepita=900):
    """Arco elétrico: zumbido de 100 Hz retificado + fritura densa (micro-estalos agudos), modulados pela intensidade
    LUMINOSA do arco (env, por amostra — a mesma tremulação do shader)."""
    n = len(env); t = tt(n)
    zum = np.abs(np.sin(2 * np.pi * 50 * t)) - 0.63; zum = bp(zum, 90, 3000) * 0.6
    taxa = crepita * env; fase = np.cumsum(taxa / SR); imp = np.diff(np.floor(fase), prepend=0) * rng.lognormal(0, 0.5, n)
    fritura = bp(imp, 2200, 9000) * 3.0 + 0.25 * bp(ruido(n), 3000, 9000) * env
    return (zum * env + fritura) * np.clip(env * 1.4, 0, 1)


def estalo_faisca(sem=None):
    r = np.random.default_rng(sem); m = n_(r.uniform(0.03, 0.09)); t = tt(m)
    return hp(ruido(m), 3500) * np.exp(-t / r.uniform(0.006, 0.02)) * r.uniform(0.4, 1.0)


def atrito_aco_concreto(dur, intens=None, peso=1.0, sem=None):
    """Aço arrastado no concreto: grânulos de atrito, corpo de raspagem, ronco grave e leve guincho."""
    r = np.random.default_rng(sem); n = n_(dur); t = tt(n)
    taxa = 700 * (0.6 + 0.8 * lento_lfo(n, 6, 1.0)); fase = np.cumsum(taxa / SR)
    imp = np.diff(np.floor(fase), prepend=0) * r.lognormal(0, 0.6, n)
    gr = bp(imp, 600, 4200) * 4.0
    corpo = bp(ruido(n), 160, 1100) * lento_lfo(n, 12, 0.6)
    ronco = lp(ruido(n), 110) * peso * lento_lfo(n, 4, 0.5)
    guin = bp(ruido(n), 2050, 2350, 2) * lento_lfo(n, 2.5, 1.0) ** 4 * 0.5
    x = 0.8 * gr + 0.7 * corpo + 0.9 * ronco + guin
    if intens is not None: x *= intens
    return x * janela(n, 0.03, 0.06)


def passagem_ar(dur, f0=300, f1=1400, sem=None):
    """Deslocamento de ar (queda, objeto passando): ruído em banda que sobe."""
    n = n_(dur); t = tt(n); x = np.zeros(n); k = np.linspace(0, 1, n)
    for i0 in range(0, n, 2400):
        seg = slice(i0, min(n, i0 + 2400)); fc = f0 + (f1 - f0) * k[i0]
        x[seg] = bp(ruido(seg.stop - seg.start + 800), fc * 0.6, fc * 1.6)[800:]
    return x * np.sin(np.pi * k) ** 1.5


def baque_submerso(massa=1.0, sem=None):
    """Impacto abafado no leito: grave, sem brilho, com nuvem de sedimento."""
    n = n_(2.2); t = tt(n)
    x = np.sin(2 * np.pi * np.cumsum(48 - 18 * np.minimum(t / 0.3, 1)) / SR) * np.exp(-t / (0.22 * massa ** 0.3))
    x += 0.6 * lp(ruido(n), 280) * np.exp(-t / 0.18)
    sed = lp(ruido(n), 650) * np.clip(t / 0.15, 0, 1) * np.exp(-t / 0.9) * lento_lfo(n, 5, 0.5)
    return x + 0.5 * sed


# ------------------------------------------------------------------------------------------------ reverberação
AMBIENTES = {   # rt (s), atraso (ms), reflexões iniciais (ms, ganho), corte agudo, modos (Hz) e coloração
    'ext':   dict(rt=0.7, pre=8, er=[(23, 0.25), (61, 0.12)], lp0=6000, lp1=2500, modos=[], ganho=0.35),
    'ind':   dict(rt=2.4, pre=18, er=[(37, 0.5), (71, 0.4), (118, 0.35), (190, 0.22)], lp0=7000, lp1=2200, modos=[(310, 0.12), (520, 0.1), (870, 0.08)], ganho=0.55),
    'porto': dict(rt=1.3, pre=12, er=[(48, 0.35), (96, 0.28), (170, 0.16)], lp0=6500, lp1=2400, modos=[], ganho=0.45),
    'dique': dict(rt=1.6, pre=14, er=[(29, 0.45), (58, 0.3), (102, 0.25)], lp0=5000, lp1=1800, modos=[], ganho=0.5),
    'int':   dict(rt=1.9, pre=6, er=[(9, 0.6), (17, 0.5), (26, 0.4), (41, 0.3)], lp0=6000, lp1=2600, modos=[(78, 0.35), (131, 0.3), (196, 0.25), (262, 0.2)], ganho=0.6),
    'sub':   dict(rt=1.1, pre=3, er=[(7, 0.6), (15, 0.5)], lp0=1300, lp1=500, modos=[(62, 0.3), (95, 0.25)], ganho=0.7),
}


def resposta_impulso(nome, sem=7):
    p = AMBIENTES[nome]; r = np.random.default_rng(sem); n = n_(p['rt'] * 1.25 + 0.05); t = tt(n)
    ir = np.zeros((n, 2))
    for c in range(2):
        z = r.standard_normal(n) * np.exp(-6.9 * t / p['rt'])
        # escurece com o tempo: mistura de duas versões filtradas
        a = lp(z, p['lp0']); b = lp(z, p['lp1']); k = np.clip(t / p['rt'], 0, 1)
        y = a * (1 - k) + b * k
        for (f, g) in p['modos']: y += g * bp(z, f * 0.97, f * 1.03, 2) * 4
        y[:n_(p['pre'] / 1000)] = 0
        for (ms, g) in p['er']:
            i = n_((ms + r.uniform(-3, 3)) / 1000)
            if i < n: y[i] += g * (1 if r.random() > 0.3 else -1) * 3
        ir[:, c] = y
    ir /= np.sqrt((ir ** 2).sum() / 2) + 1e-9
    return ir * p['ganho']
