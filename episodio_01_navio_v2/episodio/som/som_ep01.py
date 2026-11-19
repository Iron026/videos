"""Sound design cinematográfico do Ep. 01 (pós-produção; nenhum render 3D depende disto).
Gera 4 stems separados — narração, efeitos, ambiências, música — sincronizados com a narração real e com os eventos
extraídos das cenas (som/eventos_som.json), aplica reverberação por ambiente, ducking dinâmico multibanda sob a voz,
fade final natural e masterização (−14 LUFS integrados, pico verdadeiro ≤ −1,8 dBTP antes do AAC).
Saídas: episodio/stems/*.wav (24 bits), episodio/audio_ep01.wav (mix), som/mix_ep01.json (níveis e verificações).
Uso: python3 episodio/som/som_ep01.py"""
import os, sys, json, math, numpy as np, soundfile as sf
from scipy.signal import fftconvolve, resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sintese as S
from sintese import SR, n_, tt, ruido, rosa, marrom, lp, hp, bp, lpz, hpz, db, janela, lento_lfo

A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..')
DUR = 168.0; N = int(round(DUR * SR))
EV = json.load(open(os.path.join(A, 'eventos_som.json')))
STEMS = {k: np.zeros((N, 2)) for k in ('efeitos', 'ambiencias', 'musica')}
SENDS = {}                     # (stem, ambiente) -> envio mono para a reverberação daquele ambiente
LISTA = []                     # registro de efeitos por sequência (relatório)


def soma(*xs):
    """Soma sons de durações diferentes (os mais curtos completados com silêncio)."""
    m = max(len(x) for x in xs); out = np.zeros(m)
    for x in xs: out[:len(x)] += x
    return out


def pan_g(p):
    th = (p + 1) * math.pi / 4; return math.cos(th) * math.sqrt(2), math.sin(th) * math.sqrt(2)


def por(t, x, dB=0.0, pan=0.0, amb='ext', envio=0.25, stem='efeitos', sub=False, nome=None):
    """Coloca o som x (mono ou estéreo) no tempo global t. sub=True: ouvido debaixo d'água (abafado)."""
    if x.ndim == 1: x = np.stack([x, x], 1)
    if sub: x = lpz(x, 900, 2) * 1.3
    i0 = int(round(t * SR)); a = max(0, i0); b = min(N, i0 + len(x))
    if b <= a: return
    seg = x[a - i0:b - i0] * db(dB); gl, gr = pan_g(pan)
    STEMS[stem][a:b, 0] += seg[:, 0] * gl; STEMS[stem][a:b, 1] += seg[:, 1] * gr
    if envio > 0:
        k = (stem, 'sub' if sub else amb); SENDS.setdefault(k, np.zeros(N)); SENDS[k][a:b] += seg.mean(1) * envio
    if nome: LISTA.append((round(t, 2), nome))


def curva(tempos, valores, t0, n):
    """Curva amostrada por amostra a partir de (tempos, valores) globais, para um trecho que começa em t0 com n amostras."""
    return np.interp(t0 + tt(n), tempos, valores)


def media_movel(x, k):
    """Média móvel centrada (cumsum, O(n)) — 1D ou por coluna."""
    k = max(1, int(k)); c = np.cumsum(np.concatenate([np.zeros((1,) + x.shape[1:]), x]), axis=0)
    i = np.arange(len(x)); a = np.clip(i - k // 2, 0, len(x)); b = np.clip(i + (k - k // 2), 0, len(x))
    return (c[b] - c[a]) / np.maximum(b - a, 1).reshape((-1,) + (1,) * (x.ndim - 1))


def suav(x, s): return media_movel(x, s * SR)


# =============================================================================================== AMBIÊNCIAS
# camada -> lista de (t0, t1, dB) ; trocas suaves (0,35 s) entre trechos
AMB = {
    'mar':        [(0.0, 2.75, -31), (4.4, 15.1, -23), (15.1, 30.3, -42), (48.0, 49.3, -29), (63.1, 65.8, -32), (74.85, 76.2, -31),
                   (83.85, 88.6, -26), (88.6, 94.55, -33), (94.55, 134.0, -37), (134.0, 137.0, -29), (154.6, 156.4, -27), (156.4, 164.35, -32), (164.35, DUR, -24)],
    'vento':      [(0.0, 2.75, -36), (4.4, 15.1, -29), (83.85, 88.6, -31), (94.55, 117.2, -38), (154.6, 156.4, -33), (164.35, DUR, -29)],
    'marulho':    [(0.0, 2.75, -31), (74.85, 76.2, -27), (94.55, 104.9, -33), (104.9, 109.6, -25), (109.6, 123.65, -31), (123.65, 134.0, -26), (88.6, 94.55, -31)],
    'motor_navio': [(4.4, 15.1, -29)],
    'estaleiro':  [(15.1, 30.3, -27), (30.3, 35.0, -31), (35.0, 41.55, -41), (41.55, 48.0, -37)],
    'porao':      [(35.0, 41.55, -30), (137.0, 154.6, -29)],
    'dique':      [(41.55, 48.0, -29)],
    'sub':        [(2.75, 4.4, -25), (49.3, 63.1, -24), (63.1, 65.8, -32), (65.8, 74.85, -25), (76.2, 83.85, -23), (88.6, 94.55, -34),
                   (134.0, 137.0, -32), (156.4, 164.35, -29)],
    'porto':      [(94.55, 117.2, -26), (117.2, 123.65, -30), (123.65, 134.0, -33)],
}


def envelope_camada(trechos):
    g = np.zeros(N)
    for (a, b, d) in trechos: g[int(a * SR):int(b * SR)] = db(d)
    return suav(g, 0.35)


def gerar_camada(nome):
    if nome == 'mar': x = S.mar(N, 0.15, 0.0); amb = 'ext'
    elif nome == 'vento': x = S.bp(rosa(N), 220, 1900) * lento_lfo(N, 0.07, 0.85, 3); amb = 'ext'
    elif nome == 'marulho': x = S.marulho(DUR, 1.3, sem=11); amb = 'ext'
    elif nome == 'motor_navio':     # diesel distante: harmônicos graves com pulsação de ignição (acima de 40 Hz)
        t = tt(N); x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((47, 1), (94, .6), (141, .4), (188, .25))) * (0.7 + 0.3 * np.sin(2 * np.pi * 7.8 * t))
        x = hp(lp(x + 0.3 * lp(ruido(N), 300), 420), 40); amb = 'ext'
    elif nome == 'estaleiro':       # base industrial: zumbido, máquinas distantes, pancadas longínquas
        x = 0.6 * lp(rosa(N), 300) + 0.25 * S.motor_eletrico(0.25 + 0.1 * lento_lfo(N, 0.2, 1.0), 70, 300) + 0.15 * bp(rosa(N), 1500, 5000) * lento_lfo(N, 0.3, 0.8)
        r = np.random.default_rng(31)
        for t0 in np.sort(r.uniform(15.1, 48, 26)):
            k = int(t0 * SR); y = S.clank_chapa(r.uniform(1.5, 3), sem=int(t0 * 100), rattle=1) * 0.25
            x[k:k + len(y)] += y[:N - k]
        amb = 'ind'
    elif nome == 'porao':           # compartimento de aço: ar parado, ronco grave, estalos térmicos raros
        x = 0.8 * lp(marrom(N), 140) + 0.12 * bp(rosa(N), 2000, 6000); r = np.random.default_rng(41)
        for t0 in r.uniform(35, 154, 40):
            k = int(t0 * SR); y = S.modal(0.4, [(r.uniform(900, 2400), 0.05, 1)], ruido_golpe=0.2) * 0.08; x[k:k + len(y)] += y[:N - k]
        amb = 'int'
    elif nome == 'dique': x = 0.5 * lp(rosa(N), 500) + 0.2 * S.marulho(DUR, 0.6, sem=12); amb = 'dique'
    elif nome == 'sub':             # debaixo d'água: pressão grave, ondulação lenta, bolhas distantes
        x = lp(marrom(N), 380) * lento_lfo(N, 0.12, 0.5) + 0.25 * lp(S.bolhas(DUR, 3, 0.002, 0.01, sem=13), 1200); amb = 'sub'
    elif nome == 'porto':           # porto: máquinas e veículos distantes, ronco de geradores, pancadas longínquas
        x = 0.5 * lp(rosa(N), 450) + 0.2 * S.motor_eletrico(0.18 + 0.08 * lento_lfo(N, 0.15, 1.0), 60, 240) + 0.1 * bp(rosa(N), 1800, 5000)
        r = np.random.default_rng(51)
        for t0 in np.sort(r.uniform(94.5, 134, 18)):
            k = int(t0 * SR); y = S.conteiner_pouso(0.25, sem=int(t0 * 10)) * 0.4; x[k:k + len(y)] += y[:N - k]
        amb = 'porto'
    x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * db(-20)
    return x, amb


# =============================================================================================== EFEITOS POR SEQUÊNCIA
def abertura():
    e = EV['abertura']
    x = S.atrito_aco_concreto(e['borda'] - e['empurrao'] + 0.05, intens=np.linspace(0.6, 1.0, n_(e['borda'] - e['empurrao'] + 0.05)), peso=1.0, sem=1)
    por(e['empurrao'], x, -17, 0.15, 'ext', 0.25, nome='atrito do bloco de aço no concreto do cais')
    por(e['borda'] - 0.02, soma(S.impacto_aco(0.8, brilho=0.5, sem=2), 0.6 * S.atrito_aco_concreto(0.22, sem=3)), -15, 0.15, 'ext', 0.3, nome='bloco tomba na borda: raspão e baque grave')
    por(e['borda'], S.passagem_ar(e['agua'] - e['borda'], 180, 700), -30, 0.1, nome='queda (ar deslocado, em câmera lenta)')
    por(e['agua'], S.respingo(1.1, lento=2.0, denso=1.7, sem=4), -11, 0.1, 'ext', 0.3, nome='impacto pesado na água (câmera lenta): baque, lençol, cavidade, gotas')
    por(e['agua'] + 0.08, S.bolhas(1.4, 70, 0.003, 0.016, sem=5), -20, 0.1, sub=True, nome='bolhas do bloco afundando (ouvidas debaixo d\'água)')
    por(e['agua'] + 0.1, lp(ruido(n_(1.3)), 260) * np.sin(np.linspace(0, np.pi, n_(1.3))), -24, sub=True, nome='água deslocada pela descida')
    por(e['leito'], S.baque_submerso(1.0), -14, 0.1, sub=True, nome='impacto no leito com sedimento (abafado)')


def navio_navegando():
    por(4.40, S.passagem_ar(0.9, 250, 900), -33, nome='rajada de vento no corte para o mar aberto')
    t = tt(n_(2.2)); apito = sum(a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5 * t)) for a, f in ((1, 73.4), (0.6, 146.8), (0.35, 220.2)))
    por(5.0, lp(apito, 900) * np.minimum(1, t / 0.25) * np.clip((2.2 - t) / 0.5, 0, 1), -27, -0.2, 'ext', 0.6, nome='apito grave e distante do navio')
    n = n_(4.5); k = np.linspace(0, 1, n); intens = np.sin(np.pi * np.clip(k * 1.2, 0, 1)) ** 1.2
    por(9.0, S.fluxo_agua(4.5, intens, 220, 3200, 10, sem=6), -20, 0.25, 'ext', 0.2, nome='água empurrada pela proa (onda de proa)')
    por(11.0, S.bp(ruido(n_(2.5)), 2500, 8000) * janela(n_(2.5), 0.4, 1.0) * lento_lfo(n_(2.5), 12, 0.6), -27, 0.3, nome='espuma e borrifo da proa')
    por(8.4, lp(ruido(n_(2.6)), 220) * np.sin(np.linspace(0, np.pi, n_(2.6))) ** 2, -24, -0.3, nome='massa do costado passando (travelling)')
    n = n_(2.0); por(13.3, S.fluxo_agua(2.0, np.linspace(1, 0.2, n), 600, 5000, 14, sem=7), -25, -0.4, nome='esteira se formando e se afastando')


def estaleiro():
    m = EV['estaleiro_mov']; tg = np.array(m['t'])
    def vel(nome, vmax):
        v = np.clip(np.array(m[nome]['v']) / vmax, 0, 1); return np.convolve(v, np.ones(5) / 5, 'same')
    a, b = 15.1, 30.3; n = n_(b - a)
    vc = curva(tg, vel('carro', 3.05), a, n); vg = curva(tg, vel('grupo_carga', 3.97), a, n)
    por(a, S.motor_eletrico(vc, 60, 380, 0.6), -23, -0.2, 'ind', 0.45, nome='motor do carro do pórtico (acelera e freia com o movimento)')
    por(a, S.guincho(vg, 16) + 0.6 * S.motor_eletrico(vg, 90, 520, 0.4), -24, 0.1, 'ind', 0.45, nome='guincho baixando a chapa (catraca e tambor)')
    tens = np.clip(vg * 1.4 + 0.25 * (vg > 0.02), 0, 1)
    por(a, S.cabo_cantando(tens), -33, 0.05, 'ind', 0.3, nome='cabos de aço sob tensão')
    vf = vel('grupo_carga', 3.97); acel = np.abs(np.gradient(vf))                        # arrancadas e freadas do içamento (por quadro)
    picos = [tg[i] for i in range(1, len(acel) - 1) if acel[i] > 0.02 and acel[i] >= acel[i - 1] and acel[i] >= acel[i + 1]]
    ult = -9
    for t0 in picos:
        if t0 - ult > 1.0: por(t0, S.rangido(0.7, 230, 0.2, 70, sem=int(t0 * 10)), -27, 0.1, 'ind', 0.5, nome='rangido dos cabos ao arrancar/frear'); ult = t0
    for t0, f in ((18.4, 160), (20.6, 210), (22.4, 140)):
        por(t0, S.rangido(0.9, f, 0.3, 45, sem=int(t0)), -31, -0.3, 'ind', 0.6, nome='rangido metálico sutil da estrutura')
    por(23.60, soma(S.clank_chapa(2.6, sem=8), 0.7 * S.impacto_aco(2.0, brilho=0.6, sem=9)), -11, 0.0, 'ind', 0.55, nome='ENCAIXE da chapa no casco (contato pesado)')
    nv = n_(1.2); por(23.62, lp(ruido(nv), 90) * np.exp(-tt(nv) / 0.35) * (1 + 0.5 * np.sin(2 * np.pi * 11 * tt(nv))), -17, 0.0, 'ind', 0.2, nome='vibração estrutural após o encaixe')
    # solda: arco com a MESMA tremulação luminosa do shader (por quadro, 30 Hz) e um estalo para cada faísca que nasce
    def tremor(g, sem, tr=0.5):
        q = np.floor(g * 30 + 0.5).astype(np.float32)
        def h(x): return np.mod(np.sin(x * np.float32(12.9898) + np.float32(sem * 78.233)).astype(np.float32) * np.float32(43758.5453), 1.0)
        return 1 - tr + tr * (0.6 * h(q) + 0.4 * h(q * np.float32(0.5) + np.float32(3.1)))
    cordoes = [((23.75, 24.55), 0.25, -13, 0.1), ((24.68, 25.25), 1.25, -13, 0.1), ((24.0, 24.7), 3.25, -22, 0.25), ((24.85, 25.4), 4.25, -22, 0.25),
               ((24.9, 26.4), 6.25, -29, -0.3), ((25.1, 26.4), 9.25, -30, -0.4)]
    for (ta, tb), sem, g_, p_ in cordoes:
        n = n_(tb - ta + 0.12); g = ta + tt(n); env = tremor(g, sem).astype(float) * np.clip((g - ta) / 0.06, 0, 1) * np.clip((tb + 0.12 - g) / 0.12, 0, 1)
        por(ta, S.arco_solda(env), g_, p_, 'ind', 0.35, nome='arco de solda (zumbido elétrico + crepitação) sincronizado com o brilho')
    for t0 in EV['faiscas']:
        macro = t0 < 25.3
        por(t0, S.estalo_faisca(sem=int(t0 * 1000)), -21 if macro else -31, 0.1 + 0.4 * (np.random.default_rng(int(t0 * 1000)).random() - 0.5), 'ind', 0.2)
    LISTA.append((23.75, f'{len(EV["faiscas"])} estalos de faíscas, um no nascimento de cada faísca'))
    r = np.random.default_rng(10)
    for t0 in EV['chapas']:
        por(t0, S.clank_chapa(r.uniform(1.0, 1.8), sem=int(t0 * 1000), rattle=1), r.uniform(-29, -24), r.uniform(-0.6, 0.6), 'ind', 0.55)
    LISTA.append((EV['chapas'][0], f'{len(EV["chapas"])} contatos de chapas chegando ao costado e à proa'))


def corte_casco():
    por(33.15, S.rangido(1.8, 90, -0.2, 35, sem=14) * 0.8 + lp(ruido(n_(1.8)), 160) * janela(n_(1.8), 0.3, 0.6), -19, 0.2, 'ind', 0.5, nome='proa se separando: deslizamento pesado de aço')
    for t0 in (37.0, 39.2):
        n = n_(1.0); por(t0, bp(ruido(n), 2500, 7000) * np.sin(np.linspace(0, np.pi, n)) ** 2, -36, 0.0, 'int', 0.4, nome='células acendendo (brilho sutil, sem bipe)')
    por(39.6, S.rangido(1.4, 120, 0.1, 25, sem=15), -34, -0.2, 'int', 0.6, nome='estalo térmico no porão vazio')


def dique():
    e = EV['dique']
    por(e['comporta'] - 0.05, soma(S.impacto_aco(2.2, brilho=0.4, sem=16), 0.5 * S.rangido(0.6, 110, 0.0, 60, sem=17)), -15, -0.3, 'dique', 0.5, nome='válvulas/comporta abrindo (baque metálico grave)')
    n = n_(0.7); por(e['comporta'], bp(ruido(n), 1200, 7000) * np.linspace(0, 1, n) ** 2, -22, -0.3, 'dique', 0.3, nome='sopro de pressão antes da água')
    n = n_(3.2); k = np.linspace(0, 1, n); intens = np.clip(k / 0.15, 0, 1) * (1 - 0.35 * k)
    por(e['comporta'] + 0.3, S.fluxo_agua(3.2, intens, 150, 3200, 9, sem=18), -11, -0.25, 'dique', 0.45, nome='jatos de água entrando no dique (fluxo forte)')
    n = n_(4.6); k = np.linspace(0, 1, n)
    por(43.4, S.fluxo_agua(4.6, (0.6 + 0.4 * np.sin(np.pi * k)) * (1 - 0.6 * k), 90, 1100, 5, sem=19), -19, -0.2, 'dique', 0.5, nome='enchimento contínuo, cada vez mais grave e profundo')
    por(42.25, S.marulho(3.8, 2.8, sem=20), -22, 0.1, 'dique', 0.4, nome='água alcançando o casco e os picadeiros')
    por(e['picadeiros'] - 0.05, S.rangido(1.4, 65, 0.25, 22, sem=21), -21, 0.0, 'dique', 0.4, nome='estrutura alivia quando o peso deixa os picadeiros (discreto)')
    por(e['picadeiros'], S.impacto_aco(3.5, brilho=0.08, sem=22), -27, 0.0, 'dique', 0.3, nome='leve desprendimento da quilha')
    por(46.4, S.marulho(1.6, 1.5, sem=23), -27, 0.2, 'dique', 0.4, nome='casco livre: água ao redor')


def empuxo():
    n = n_(1.0); por(49.0, S.respingo(0.45, 1.0, 0.6, sem=24), -24, 0.0, 'ext', 0.2, nome='câmera entra na água')
    por(49.15, S.bolhas(0.9, 140, 0.001, 0.006, sem=25), -23, 0.0, sub=True, nome='bolhas da entrada; o mundo fica abafado')
    n = n_(2.6); por(50.75, (lp(ruido(n), 130) + 0.5 * np.sin(2 * np.pi * 55 * tt(n))) * np.sin(np.linspace(0, np.pi, n)) ** 2, -27, sub=True, nome='mapa de pressão: ondulação grave')
    por(51.0, S.rangido(2.6, 62, 0.15, 22, sem=26), -31, 0.0, sub=True, nome='casco sob pressão (um único som para o grupo de setas)')
    n = n_(0.4)
    for p in (-0.6, 0.6): por(57.35, np.sin(2 * np.pi * np.cumsum(np.linspace(75, 55, n)) / SR) * np.exp(-tt(n) / 0.12), -25, p, 'sub', 0.3)
    LISTA.append((57.35, 'os dois lados empurram juntos (pulso grave, um de cada lado)'))
    n = n_(0.9)
    for p in (-0.7, 0.7):   # cada lado desliza para o centro e se anula
        x = bp(ruido(n), 250, 1400) * np.sin(np.linspace(0, np.pi, n)) ** 2; xs = np.stack([x * (1 - 0.5 * (1 + p) * np.linspace(1, 0, n)), x * (1 - 0.5 * (1 - p) * np.linspace(1, 0, n))], 1)
        por(58.35, xs, -29, 0.0, 'sub', 0.3)
    LISTA.append((58.35, 'laterais se anulam: sopro que converge ao centro'))
    por(59.8, S.passagem_ar(1.8, 180, 850), -27, 0.0, 'sub', 0.4, nome='componentes verticais convergem (ar subindo, sutil)')
    n = n_(1.1); tt_ = tt(n); bloom = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.minimum(tt_ / 0.8, 1)) / SR) * np.sin(np.pi * tt_ / 1.1) ** 1.5
    por(61.3, bloom + 0.4 * lp(ruido(n), 200) * np.sin(np.pi * tt_ / 1.1), -21, 0.0, 'sub', 0.4, nome='empuxo se forma (impulso grave para cima)')
    n = n_(2.4); k = np.linspace(0, 1, n)
    por(63.2, S.fluxo_agua(2.4, np.sin(np.pi * k) ** 1.2, 120, 900, 6, sem=27) + 0.4 * S.bolhas(2.4, 50, 0.002, 0.008, sem=28), -24, 0.0, 'ext', 0.3, nome='volume deslocado se enche (água deslocada)')
    n = n_(0.9); por(65.6, bp(ruido(n), 2500, 6000) * np.sin(np.linspace(0, np.pi, n)) ** 2, -36, nome='área deslocada destacada (brilho sutil)')
    n = n_(0.6); por(67.2, np.sin(2 * np.pi * 70 * tt(n)) * np.exp(-tt(n) / 0.15), -30, 0.15, sub=True, nome='peso da água deslocada (pulso grave)')
    n = n_(1.0); por(71.15, np.sin(2 * np.pi * np.cumsum(np.linspace(80, 55, n)) / SR) * np.sin(np.pi * tt(n) / 1.0) ** 2, -26, sub=True, nome='peso do navio = empuxo (equilíbrio)')


def retomada():
    e = EV['retomada']
    x = S.atrito_aco_concreto(e['borda'] - 74.85 + 0.05, intens=np.linspace(0.8, 1.0, n_(e['borda'] - 74.85 + 0.05)), peso=1.0, sem=29)
    por(74.85, x, -17, 0.15, 'ext', 0.25, nome='retomada: o mesmo atrito do bloco no cais (variação)')
    por(e['borda'] - 0.02, soma(S.impacto_aco(0.8, brilho=0.55, sem=30), 0.6 * S.atrito_aco_concreto(0.2, sem=31)), -15, 0.15, 'ext', 0.3, nome='bloco deixa a borda (variação)')
    por(e['borda'], S.passagem_ar(e['agua'] - e['borda'], 200, 760), -30, 0.1)
    por(e['agua'], S.respingo(1.0, lento=1.5, denso=1.7, sem=32), -12, 0.1, 'ext', 0.3, nome='impacto na água coerente com a abertura (outra variação de camadas)')
    n = n_(1.0); x = lp(ruido(n), 500) * np.linspace(0, 1, n) ** 2 * np.exp(-np.maximum(tt(n) - 0.7, 0) / 0.1)
    por(e['agua'] - 0.4, x, -30, nome='transição suave para a câmera lenta')
    n = n_(5.7); por(76.3, lp(ruido(n), 140) * np.linspace(0.5, 1, n) * janela(n, 0.6, 0.4), -22, sub=True, nome='mundo em câmera lenta: deslocamento grave')
    por(76.25, S.bolhas(5.6, 22, 0.006, 0.022, sobe=0.1, sem=33), -21, 0.1, sub=True, nome='bolhas grandes e lentas (câmera lenta)')
    por(e['leito'], S.baque_submerso(1.2), -12, 0.05, sub=True, nome='impacto no leito (tempo volta ao normal)')
    n = n_(1.8); por(e['leito'] + 0.05, lp(ruido(n), 520) * np.clip(tt(n) / 0.2, 0, 1) * np.exp(-tt(n) / 0.8), -21, sub=True, nome='sedimento se espalhando (abafado)')


def experimento():
    e = EV['experimento']; m = EV['experimento_mov']
    for p in (-0.4, 0.3): por(e['solto'], S.passagem_ar(e['agua'] - e['solto'], 160, 600), -31, p)
    por(e['agua'], S.respingo(1.3, 1.0, 1.9, sem=34), -12, -0.35, 'ext', 0.3, nome='bloco maciço entra na água (compacto, pesado)')
    por(e['agua'] + 0.012, S.respingo(2.3, 1.35, 0.9, sem=35), -13, 0.3, 'ext', 0.35, nome='casco entra na água (largo: grande massa de água deslocada)')
    n = n_(1.8); por(e['agua'] + 0.05, lp(ruido(n), 210) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, -17, 0.3, 'ext', 0.3, nome='onda de deslocamento do casco')
    por(e['agua'] + 0.2, S.bolhas(3.0, 45, 0.003, 0.014, sem=36), -24, -0.35, sub=True, nome='bolhas do bloco afundando (abafadas)')
    tg = np.array(m['t']); z = np.array(m['navio']['z']); vz = np.gradient(z)
    ext = [tg[i] for i in range(1, len(vz) - 1) if tg[i] > e['agua'] + 0.4 and np.sign(vz[i]) != np.sign(vz[i - 1])]
    for k, t0 in enumerate(ext[:5]):
        por(t0, S.marulho(0.8, 6, sem=40 + k), -18 - 4 * k, 0.3, 'ext', 0.3)
    LISTA.append((ext[0] if ext else 0, f'água batendo no casco a cada inversão da arfagem ({min(5, len(ext))} vezes, cada vez mais fraca)'))
    n = n_(1.5); por(89.9, S.fluxo_agua(1.5, np.sin(np.linspace(0, np.pi, n)), 120, 800, 5, sem=37), -30, nome='volume deslocado destacado')
    n = n_(1.0); por(91.0, np.sin(2 * np.pi * np.cumsum(np.linspace(60, 80, n)) / SR) * np.sin(np.linspace(0, np.pi, n)) ** 2, -29, nome='empuxo = peso (pulso grave)')


def porto():
    m = EV['porto_mov']; tg = np.array(m['t'])
    def vel(nome, vmax):
        v = np.array(m[nome]['v']); v[v > 12] = 0; v = np.clip(v / vmax, 0, 1); return np.convolve(v, np.ones(7) / 7, 'same')
    a, b = 94.55, 117.2; n = n_(b - a)
    for k, p in ((5, 0.0), (3, -0.5), (7, 0.5)):
        vc = curva(tg, vel(f'carro_anc{k}', 4.0), a, n)
        z = np.array(m[f'spreader_anc{k}']['z']); vz = np.abs(np.gradient(z) * 30); vz[vz > 12] = 0
        vs = curva(tg, np.convolve(np.clip(vz / 5.0, 0, 1), np.ones(7) / 7, 'same'), a, n)
        g0 = -24 if k == 5 else -29
        por(a, S.motor_eletrico(vc, 55, 340, 0.6), g0, p, 'porto', 0.4)
        por(a, S.guincho(vs, 18) + 0.6 * S.motor_eletrico(vs, 85, 560, 0.4), g0 - 1, p, 'porto', 0.4)
        por(a, S.cabo_cantando(np.clip(vs * 1.5 + vc * 0.6, 0, 1)), g0 - 11, p, 'porto', 0.3)
    LISTA.append((97.6, 'motores, guinchos e cabos dos 3 portêineres seguindo a velocidade real do carro e do spreader'))
    for i, t0 in enumerate(EV['pousos']):
        por(t0, S.conteiner_pouso(1.0, sem=60 + i), -12, (-0.1, -0.3, 0.3)[i], 'porto', 0.45)
        por(t0 - 0.9, S.rangido(0.8, 260, -0.15, 60, sem=63 + i), -29, 0.0, 'porto', 0.4)
    LISTA.append((101.6, 'pouso de cada contêiner no instante exato do contato (101,60 · 102,95 · 104,45): baque, cantos, trepidação'))
    r = np.random.default_rng(70)
    for t0 in EV['conteineres']:
        por(t0, S.conteiner_pouso(0.32, sem=int(t0 * 1000)), r.uniform(-33, -27), r.uniform(-0.7, 0.7), 'porto', 0.35)
    LISTA.append((105.45, f'{len(EV["conteineres"])} contatos de contêineres no time-lapse (cada um no seu instante de pouso)'))
    z = np.array(m['navio']['z']); vz = np.abs(np.gradient(z) * 30)
    intens = curva(tg, np.convolve(np.clip(vz / 0.25, 0, 1), np.ones(15) / 15, 'same'), a, n)
    por(a, S.fluxo_agua(b - a, intens, 150, 1400, 4, sem=71), -24, 0.2, 'porto', 0.3, nome='água se movendo ao redor do casco conforme o calado aumenta')
    por(118.9, S.marulho(2.0, 2.5, sem=72), -29, 0.1, nome='cota do calado sobe (marulho junto à quilha)')
    for i in range(5):
        n = n_(0.08); por(130.5 + 0.55 * i, S.modal(0.15, [(1800 + 120 * i, 0.03, 1)], ruido_golpe=0.1), -37, 0.0, 'ext', 0.1)
    LISTA.append((130.5, 'marcas: toques muito discretos quando cada linha acende'))


def avaria():
    e = EV['avaria']
    x = soma(S.impacto_aco(0.7, brilho=1.3, sem=80), 0.8 * S.rangido(0.55, 230, 0.35, 140, sem=81), 0.5 * bp(ruido(n_(0.4)), 600, 4000) * np.exp(-tt(n_(0.4)) / 0.08))
    por(e['rasgo'], x, -11, 0.2, 'ext', 0.25, nome='ruptura metálica localizada no costado')
    n = n_(1.9); por(e['bolhas'][0], S.bolhas(1.9, 160, 0.002, 0.012, sem=82) + 0.6 * S.fluxo_agua(1.9, np.linspace(0.3, 1, n), 150, 1100, 10, sem=83), -18, 0.2, sub=True,
                     nome='bolhas sugadas pelo rombo')
    a, b = e['jato']; n = n_(b - a); k = tt(n)
    intens = np.clip(k / 0.6, 0, 1) * np.where(a + k < 143.5, 1.0, np.clip(1 - (a + k - 143.5) / 3.0, 0.15, 1))
    jato = 0.6 * S.fluxo_agua(b - a, intens, 300, 4500, 14, sem=84) + 1.0 * S.fluxo_agua(b - a, intens, 60, 500, 6, sem=85)   # corpo grave forte, chiado contido
    por(a, jato, -14, 0.15, 'int', 0.55, nome='água entrando sob pressão pelo rombo (jato que diminui quando é coberto)')
    c0, c1 = e['enche']; n = n_(c1 - c0 + 2.0); k = tt(n) / (c1 - c0)
    por(c0, S.fluxo_agua(c1 - c0 + 2.0, np.clip(k, 0, 1) ** 0.7 * np.clip((c1 - c0 + 2 - tt(n)) / 2.0, 0, 1), 70, 700, 3, sem=86) + 0.4 * S.bolhas(c1 - c0 + 2, 35, 0.003, 0.015, sem=87),
        -19, 0.0, 'int', 0.6, nome='porão enchendo: turbulência grave e bolhas, crescendo')
    r = np.random.default_rng(88)
    for t0 in np.sort(r.uniform(137.4, 142.0, 9)):
        por(t0, S.respingo(0.35, 1.0, 0.6, sem=int(t0 * 100)), r.uniform(-27, -22), r.uniform(-0.6, 0.6), 'int', 0.6)
    LISTA.append((137.4, '9 golpes de água nas estruturas internas (anteparas, piso)'))
    for i, (t0, f, g) in enumerate(((139.5, 150, -27), (142.3, 120, -25), (144.9, 105, -24), (146.8, 95, -23), (148.4, 85, -22), (149.7, 80, -23))):
        por(t0, S.rangido(1.3, f, -0.2, 30, sem=90 + i), g, (-0.4, 0.3, -0.2, 0.4, -0.3, 0.2)[i], 'int', 0.6)
    LISTA.append((139.5, '6 rangidos do casco sob carga crescente (mais graves e próximos)'))
    n = n_(17.6); t = tt(n); g = 137.0 + t
    nivel = np.interp(g, [137, 146, 147.9, 150.6, 151.05, 154.6], [0.15, 0.6, 1.0, 1.0, 0.85, 0.0])
    drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 58.3 * t) + 0.3 * lp(ruido(n), 120)) * nivel
    por(137.0, drone, -22, 0.0, 'int', 0.3, nome='tensão grave crescente; alivia gradualmente após as divisórias')
    por(e['divisorias'], S.impacto_aco(2.5, brilho=0.3, sem=95), -22, 0.0, 'int', 0.5, nome='divisórias estanques: baque firme e calmo (controle)')


def conclusao():
    e = EV['conclusao']
    por(e['solto'], S.passagem_ar(e['agua'] - e['solto'], 150, 520), -29, 0.25)
    por(e['agua'], S.respingo(2.6, 1.25, 2.0, sem=96), -11, 0.25, 'ext', 0.35, nome='bloco de 17 m entra na água (impacto enorme, camadas)')
    n = n_(1.6); por(e['agua'] + 0.05, lp(ruido(n), 180) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, -16, 0.25, nome='massa de água deslocada')
    por(e['agua'] + 0.4, S.bolhas(2.6, 60, 0.004, 0.02, sem=97), -21, 0.25, sub=True, nome='bolhas e descida do bloco (abafadas)')
    n = n_(2.4); por(156.3, lp(ruido(n), 200) * np.sin(np.linspace(0, np.pi, n)) ** 2, -24, sub=True)
    n = n_(1.4); por(159.6, S.fluxo_agua(1.4, np.sin(np.linspace(0, np.pi, n)), 120, 700, 5, sem=98), -30, nome='volume deslocado sob o casco')
    n = n_(1.0); por(161.4, np.sin(2 * np.pi * np.cumsum(np.linspace(60, 82, n)) / SR) * np.sin(np.linspace(0, np.pi, n)) ** 2, -29, nome='peso = empuxo (pulso grave)')
    por(164.35, S.marulho(3.6, 1.2, sem=99), -30, -0.1, nome='plano final: mar natural ao redor do navio')


# =============================================================================================== MÚSICA (original, discreta)
def musica():
    NOT = {'D': 146.83, 'E': 164.81, 'F#': 185.0, 'G': 196.0, 'A': 220.0, 'B': 246.94, 'C': 130.81}
    def acorde(r, menor=False): f = NOT[r]; return [f, f * 2 ** ((3 if menor else 4) / 12), f * 1.5]
    SEC = [(0.0, 15.1, [('B', 1), ('G', 0), ('D', 0), ('A', 0)]), (15.1, 48.0, [('D', 0), ('A', 0), ('B', 1), ('G', 0)]),
           (48.0, 94.55, [('E', 1), ('C', 0), ('G', 0), ('D', 0)]), (94.55, 134.0, [('D', 0), ('G', 0), ('A', 0), ('B', 1)]),
           (134.0, 154.6, [('B', 1), ('F#', 1), ('G', 0), ('E', 1)]), (154.6, 165.6, [('G', 0), ('D', 0), ('A', 0)]), (165.6, DUR, [('D', 0)])]
    M = np.zeros((N, 2))
    for (a, b, prog) in SEC:
        t0 = a; i = 0
        while t0 < b - 0.05:
            t1 = min(b, t0 + 4.0); n = int((t1 - t0 + 1.2) * SR); t = tt(n); r, mn = prog[i % len(prog)]; fs = acorde(r, mn); v = np.zeros(n)
            for f in fs + [fs[0] / 2]:
                for det in (-0.12, 0.12):
                    ph = 2 * np.pi * f * (1 + det / 100) * t; v += 0.5 * (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.25 + np.sin(ph) * 0.35
            pad = lp(v, 900) * np.minimum(1, t / 0.9) * np.clip((t1 - t0 + 1.2 - t) / 1.2, 0, 1)
            i0 = int(t0 * SR); j0 = min(N, i0 + n)
            M[i0:j0, 0] += pad[:j0 - i0]; M[i0:j0, 1] += pad[:j0 - i0]                    # sem atraso entre canais (seguro em mono)
            t0 = t1; i += 1
    for (a, b) in ((97.6, 117.0), (154.6, 165.6)):
        passo = 60 / 92 / 2; k = 0; t0 = a
        while t0 < b:
            sec = next(s for s in SEC if s[0] <= t0 < s[1]); r, mn = sec[2][int((t0 - sec[0]) // 4.0) % len(sec[2])]
            f = acorde(r, mn)[k % 3] * 2; n = n_(0.5); t = tt(n)
            nota = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * S.janela(n, 0.004, 0.45) * np.exp(-t / 0.18) * min(1, (t0 - a) / 2.0) * 0.6
            i0 = int(t0 * SR); j0 = min(N, i0 + n); M[i0:j0, 0] += nota[:j0 - i0] * (0.8 + 0.2 * (k % 2)); M[i0:j0, 1] += nota[:j0 - i0] * (1.0 - 0.2 * (k % 2))
            t0 += passo; k += 1
    STEMS['musica'] += M


# =============================================================================================== LOUDNESS (BS.1770-4)
def k_weight(x):
    from scipy.signal import lfilter
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)


def lufs(x, curto=False):
    y = k_weight(x if x.ndim == 2 else np.stack([x, x], 1)); w = int(0.4 * SR); h = int(0.1 * SR)
    p = np.array([np.mean(y[i:i + w] ** 2, 0).sum() for i in range(0, len(y) - w, h)]); l = -0.691 + 10 * np.log10(p + 1e-12)
    if curto: return l
    g = l > -70; l1 = -0.691 + 10 * np.log10(p[g].mean() + 1e-12); g2 = g & (l > l1 - 10)
    return -0.691 + 10 * np.log10(p[g2].mean() + 1e-12)


def pico_verdadeiro(x):
    up = resample_poly(x, 4, 1, axis=0); return 20 * np.log10(np.abs(up).max() + 1e-12)


LIM = {}


def limitador(x, teto_db=-1.8, liberacao=0.08):
    """Limitador de pico verdadeiro (detecção com sobreamostragem 4×, antecipação de 1,5 ms)."""
    up = np.abs(resample_poly(x, 4, 1, axis=0)).max(1); pk = up[: len(x) * 4].reshape(-1, 4).max(1)[:len(x)]
    teto = db(teto_db); g = np.minimum(1.0, teto / (pk + 1e-12))
    from scipy.ndimage import minimum_filter1d
    la = n_(0.0015); g = minimum_filter1d(g, size=2 * la + 1)          # antecipação: o ganho já desce antes do pico
    B = 8; m = -(-len(g) // B); gb = np.pad(g, (0, m * B - len(g)), constant_values=1).reshape(m, B).min(1)
    a = math.exp(-B / (liberacao * SR)); out = np.empty(m); cur = 1.0
    for i, v in enumerate(gb):
        cur = v if v < cur else cur * a + v * (1 - a); out[i] = cur
    out = np.minimum(np.repeat(out, B)[:len(g)], g)
    LIM['reducoes'] = [(round(i / SR, 2), round(float(20 * np.log10(out[i])), 1)) for i in range(0, len(out), SR // 10) if out[i:i + SR // 10].min() < db(-1.5)]
    return x * out[:, None], float(20 * np.log10(out.min()))


# =============================================================================================== MONTAGEM
def gerar_sintetico():
    for nome, trechos in AMB.items():
        x, amb = gerar_camada(nome); g = envelope_camada(trechos)
        if nome == 'sub': x = lpz(x, 700)
        y = x * g
        if nome in ('mar', 'vento', 'estaleiro', 'porto'): yr = gerar_camada(nome)[0] * g * (1.0 if nome != 'sub' else 1.0)   # segundo canal: realização independente (largura, sem atraso)
        else: yr = y
        STEMS['ambiencias'] += np.stack([y, yr], 1)
        k = ('ambiencias', amb); SENDS.setdefault(k, np.zeros(N)); SENDS[k] += y * 0.25
    for f in (abertura, navio_navegando, estaleiro, corte_casco, dique, empuxo, retomada, experimento, porto, avaria, conclusao): f()
    musica()


def mixar(saida='audio_ep01.wav', stems_dir='stems', sufixo='', relatorio='mix_ep01.json', efeitos_rel=-2.0, amb_rel=-16.0):
    # reverberação por ambiente (envios → convolução com a resposta ao impulso daquele ambiente)
    for (stem, amb), s in SENDS.items():
        ir = S.resposta_impulso(amb)
        for c in range(2): STEMS[stem][:, c] += fftconvolve(s, ir[:, c])[:N]
    # narração (cópia de montagem): sem a fala de assinatura; o MP3 e o WAV de trabalho NÃO são alterados
    voz, sr = sf.read(os.path.join(EP, '..', 'voz', 'narracao_ep01', 'trabalho', 'narracao_48k.wav')); assert sr == SR
    v = np.zeros(N); v[:min(N, len(voz))] = (voz if voz.ndim == 1 else voz.mean(1))[:N]
    corte = int(166.36 * SR); v[corte:] = 0; r_ = n_(0.06); v[corte - r_:corte] *= np.linspace(1, 0, r_)
    VOZ = np.stack([v, v], 1)
    # graves sob controle: tudo que não é voz perde o subgrave; efeitos e ambiências sem lixo abaixo de 35 Hz
    for k in STEMS: STEMS[k] = hpz(STEMS[k], 35, 2)
    # níveis relativos (medidos): ambiência ~19 dB abaixo da voz, efeitos ~7 dB abaixo, música ~17 dB abaixo
    Lv = lufs(VOZ); alvo = {'ambiencias': Lv + amb_rel, 'efeitos': Lv + efeitos_rel, 'musica': Lv - 16}   # antes do ducking
    for k, a_ in alvo.items(): STEMS[k] *= db(a_ - lufs(STEMS[k]))
    # ducking dinâmico multibanda: durante a fala a banda da voz (200 Hz–4 kHz) de efeitos/ambiências fica ≥ 12 dB abaixo
    w = n_(0.03); ativa = np.clip(lpz((np.sqrt(media_movel(v ** 2, w)) > db(-42)).astype(float), 3.0), 0, 1)
    vm = np.sqrt(media_movel(bp(v, 200, 4000) ** 2, w)) + 1e-6
    # ducking dinâmico sobre a SOMA de efeitos + ambiências + música: na banda da voz (200 Hz–5 kHz) o conjunto fica
    # ≥ 13 dB abaixo da fala; fora da fala (pausas) os efeitos voltam inteiros. Graves −6 dB fixos e agudos meio-caminho.
    bandas = {}
    for k in ('efeitos', 'ambiencias', 'musica'):
        x = STEMS[k]; baixo = lpz(x, 200, 4); alto = hpz(x, 5000, 4); bandas[k] = (baixo, x - baixo - alto, alto)
    meio_tot = sum(b[1] for b in bandas.values())
    sm = np.sqrt(media_movel((meio_tot ** 2).mean(1), w)) + 1e-9
    g = np.minimum(1.0, vm * db(-13) / sm); g = np.maximum(g, db(-24)); g = 1 - (1 - g) * ativa
    a_at16, a_lb16 = math.exp(-16 / (0.010 * SR)), math.exp(-16 / (0.45 * SR)); gd = g[::16]; out = np.empty_like(gd); cur = 1.0
    for i, val in enumerate(gd):          # ataque 10 ms, liberação 450 ms (pausas curtas entre palavras não "bombeiam")
        cur = cur * a_at16 + val * (1 - a_at16) if val < cur else cur * a_lb16 + val * (1 - a_lb16); out[i] = cur
    gs = np.repeat(out, 16)[:N]
    fixo_baixo = 1 - (1 - db(-6)) * ativa
    for k, (baixo, meio, alto) in bandas.items():
        STEMS[k] = baixo * fixo_baixo[:, None] + meio * gs[:, None] + alto * np.sqrt(gs)[:, None]
    rel = dict(ducking_max_db=round(float(20 * np.log10(gs.min())), 1), ducking_medio_na_fala_db=round(float(20 * np.log10(gs[ativa > 0.5].mean())), 1))
    # final natural: tudo que não é voz desce junto entre 166,4 e 168,0 s (a voz já terminou em 166,12 s)
    fim = np.clip((DUR - 0.03 - tt(N)) / 1.6, 0, 1) ** 1.5
    for k in STEMS: STEMS[k] *= fim[:, None]
    STEMS['narracao'] = VOZ
    mix = sum(STEMS.values())
    g0 = -14.0 - lufs(mix); mix *= db(g0)
    mix, red = limitador(mix, -1.8)
    for _ in range(2):
        d = -14.0 - lufs(mix)
        if abs(d) < 0.1: break
        mix *= db(d); g0 += d; mix, red = limitador(mix, -1.8)
    os.makedirs(os.path.join(EP, stems_dir), exist_ok=True)
    for k, x in STEMS.items(): sf.write(os.path.join(EP, stems_dir, f'ep01_{k}{sufixo}.wav'), x * db(g0), SR, subtype='PCM_24')
    sf.write(os.path.join(EP, saida), mix, SR, subtype='PCM_24')
    # verificações: estéreo × mono, alto-falante de celular, inteligibilidade (voz × resto na banda da fala)
    mono = np.stack([mix.mean(1)] * 2, 1)
    def celular(x): return hpz(lpz(x.mean(1), 7000, 4), 350, 4)
    resto = sum(STEMS[k] for k in ('efeitos', 'ambiencias', 'musica')) * db(g0); vv = VOZ * db(g0)
    jan = int(0.1 * SR); snr = []; nivel = []
    vc, rc = celular(vv), celular(resto)
    for i in range(0, N - jan, jan):
        pv = np.mean(vc[i:i + jan] ** 2)
        if pv > np.mean(vc ** 2) * 0.05: snr.append(10 * np.log10(pv / (np.mean(rc[i:i + jan] ** 2) + 1e-12))); nivel.append(10 * np.log10(pv))
    snr = np.array(snr); nivel = np.array(nivel); plena = nivel > np.median(nivel) - 10          # fala plena (sem finais de palavra e respirações)
    corr = float(np.corrcoef(mix[:, 0], mix[:, 1])[0, 1])
    res = dict(duracao_s=DUR, lufs_integrado=round(lufs(mix), 2), pico_verdadeiro_dbtp=round(pico_verdadeiro(mix), 2), reducao_max_limitador_db=round(red, 2),
               lufs_mono=round(lufs(mono), 2), correlacao_LR=round(corr, 3),
               inteligibilidade_celular=dict(janelas_de_fala=int(len(snr)), snr_voz_mediana_db=round(float(np.median(snr)), 1),
                                             snr_p5_db=round(float(np.percentile(snr, 5)), 1), pct_janelas_acima_10db=round(float((snr >= 10).mean() * 100), 1),
                                             fala_plena_p5_db=round(float(np.percentile(snr[plena], 5)), 1), fala_plena_pct_acima_10db=round(float((snr[plena] >= 10).mean() * 100), 1)),
               ducking_max_db=rel, stems={k: round(lufs(x * db(g0)), 1) if np.abs(x).max() > 0 else None for k, x in STEMS.items()},
               loudness_curto_max={k: round(float(lufs(x * db(g0), curto=True).max()), 1) for k, x in STEMS.items()},
               limitador_acima_1_5db=LIM.get('reducoes', []), efeitos=sorted(LISTA))
    json.dump(res, open(os.path.join(A, relatorio), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'efeitos'}, ensure_ascii=False, indent=1)); print(len(LISTA), 'efeitos registrados')
    return res


if __name__ == '__main__':
    gerar_sintetico(); mixar()
