"""Sound design HÍBRIDO do Ep. 01 (linha do tempo inteira, 0–168 s).
Base: gravações reais — Mixkit (Sound Effects Free License) e Wikimedia Commons / Work With Sounds (CC BY 4.0, com
créditos em som/fontes_efeitos_hibrido.md). Síntese só como complemento discreto: reforço grave de impactos,
transições sutis, formações gráficas do empuxo e pequenas texturas de peso/escala — nunca no lugar do timbre real.
Mixagem: a mesma cadeia de som_ep01.mixar (reverberação por ambiente, master −14 LUFS / pico ≤ −1,8 dBTP), com
ducking MODERADO (ambiência e efeitos continuam presentes sob a voz).
Saídas: audio_ep01_hibrido.wav, stems/ep01_*_hibrido.wav, som/mix_hibrido.json, som/usos_hibrido.json."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import som_ep01 as SE
import amostras as AM
from amostras import trecho, laco, ataque, SR
from sintese import lpz, hpz, tt, ruido, lp
import sintese as S
import som_real as R
from som_real import por, cama, hp_, lp_

EV = SE.EV

# Gravações do Wikimedia Commons (Work With Sounds). Se o arquivo não pôde ser baixado (o servidor de arquivos limita
# este IP de nuvem compartilhado), usa a reserva do Mixkit indicada e registra a troca — nada é inventado.
RESERVA = {'Shipyardcrane': 2504, 'Crane': 1534, 'Weldingonshipinfloatingdrydock': 812, 'IcebreakerKunashipsengine': 3077,
           'Adjustingadrydock': 2509, 'Waterintakepumpingstation': 1303, 'ContainerTerminalatthePortofDortmund': 819,
           'Containerreachstackers': 1621, 'Containershipgantrycrane': 2504, 'Mobileharbourcrane': 802, 'Smallwaves': 1195}
TROCAS = {}


class _Reserva(int):
    reserva_de = ''


def C(nome):
    if os.path.exists(os.path.join(AM.A, 'bib', 'commons', f'{nome}.ogg')): return nome
    TROCAS[nome] = RESERVA[nome]; r = _Reserva(RESERVA[nome]); r.reserva_de = nome; return r


# ------------------------------------------------------------------------------------------------ utilitários
def _r(i): return C(i) if isinstance(i, str) and i in RESERVA else i


def _rms_db(i, jan=0.05):
    a = AM.carregar(_r(i)).mean(1); w = int(jan * SR); n = len(a) // w
    return 20 * np.log10(np.sqrt((a[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)


def estavel(i, dur, ini=0.0, fim=None, jan=0.05):
    """Início (s) do trecho de 'dur' s mais estável (menor variação de nível), entre os 50% mais fortes da gravação."""
    r = _rms_db(i, jan); L = int(dur / jan); k0 = int(ini / jan); k1 = len(r) - L if fim is None else min(len(r) - L, int(fim / jan))
    cand = [(np.std(r[k:k + L]), k) for k in range(k0, max(k0 + 1, k1), max(1, L // 6)) if r[k:k + L].mean() > np.median(r)]
    return (min(cand)[1] if cand else k0) * jan


def golpes(i, n=6, sep=0.8, jan=0.02, faixa=18):
    """Instantes (s) dos n transientes mais fortes (separados por 'sep' s), em ordem de força."""
    r = _rms_db(i, jan); on = np.maximum(0, np.diff(r, prepend=r[0])); sel = []
    for k in np.argsort(-on):
        if r[k] < r.max() - faixa: continue
        if all(abs(k - j) * jan > sep for j in sel): sel.append(k)
        if len(sel) >= n: break
    return [k * jan for k in sel]


def golpe(i, k=0, **kw):
    g = golpes(i, max(6, k + 1), **kw); t = g[min(k, len(g) - 1)]
    return max(0.0, ataque(i, -12, max(0.0, t - 0.15)) - 0.01)


def grave(t, dur=0.9, f0=58, f1=36, dB=-20, pan=0.0, amb='ext', sub=False, nome=''):
    """Reforço grave SINTÉTICO discreto sob um impacto real (peso/escala): seno com glissando + ruído grave, sem ataque próprio."""
    n = int(dur * SR); x = tt(n); fr = np.linspace(f0, f1, n)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-x / (dur * 0.35)) * np.clip(x / 0.012, 0, 1)
    y = y + 0.35 * lp(ruido(n), 90) * np.exp(-x / (dur * 0.25))
    por(t, y, dB, pan, amb, 0.15, sub=sub)
    AM.USOS.append(dict(t=round(t, 2), id='sintese', titulo='reforço grave (síntese discreta)', ini=0, dur=dur, tom=1.0, uso=nome or 'peso do impacto'))


def sopro(t, dur, dB=-30, f=(300, 1600), pan=0.0, amb='ext', sub=False, nome=''):
    """Transição/textura sutil sintética (ar filtrado com envelope em seno)."""
    n = int(dur * SR); y = S.bp(ruido(n), *f) * np.sin(np.linspace(0, np.pi, n)) ** 2
    por(t, y, dB, pan, amb, 0.3, sub=sub)
    AM.USOS.append(dict(t=round(t, 2), id='sintese', titulo='transição sutil (síntese)', ini=0, dur=dur, tom=1.0, uso=nome))


def segue(i, a, b, curva, dB, pan=0.0, amb='ext', envio=0.35, ini=None, fim=None, eq=None, xf=0.6, uso='', expo=0.7):
    """Cama real cujo VOLUME acompanha uma curva de movimento (0–1); a altura nunca muda."""
    i = _r(i); n = int((b - a) * SR); x = laco(i, b - a, ini if ini is not None else estavel(i, min(8.0, b - a)), fim, xf=xf, ref=-20, t=a, uso=uso)[:n]
    por(a, x * (np.clip(curva, 0, 1) ** expo)[:, None], dB, pan, amb, envio, eq=eq)


# ================================================================================================ 0–15 · abertura
def abertura():
    e = EV['abertura']
    cama(0.0, 2.85, 1208, -22, ini=3.0, uso='marulho no cais (pedras do porto)')
    cama(0.0, 2.85, 1191, -27, uso='mar distante')
    d = e['borda'] - e['empurrao'] + 0.25
    # ARRASTO do bloco de aço no concreto (substitui a tampa de bueiro 2927): porta pesada deslizando (corpo grave) + raspagem metálica (grão)
    por(e['empurrao'], trecho(1523, max(0, ataque(1523, -20) - 0.02), d, fo=0.15, ref=-3, t=e['empurrao'], uso='aço pesado arrastando: corpo grave (porta de correr pesada)'), -6, 0.15, 'ext', 0.25)
    por(e['empurrao'] + 0.08, trecho(809, ataque(809), min(d, 1.0), fo=0.2, ref=-3, tom=0.85, t=e['empurrao'], uso='aço raspando no concreto: grão metálico'), -16, 0.15, 'ext', 0.25, eq=hp_(400))
    n = int(d * SR); por(e['empurrao'], lp(ruido(n), 110) * np.sin(np.linspace(0, np.pi, n)) ** 0.7, -24, 0.1)
    AM.USOS.append(dict(t=e['empurrao'], id='sintese', titulo='reforço grave do arrasto (síntese discreta)', ini=0, dur=d, tom=1.0, uso='massa do bloco'))
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, t=e['borda'], uso='baque grave quando o bloco tomba na borda'), -4, 0.15, 'ext', 0.3, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 1.2, ref=-6, t=e['borda'], uso='ar deslocado na queda'), -16, 0.1)
    por(e['agua'] - 0.02, trecho(1304, ataque(1304), 1.9, tom=0.8, ref=-1, t=e['agua'], uso='impacto do bloco na água (camada principal, câmera lenta)'), -5, 0.1, 'ext', 0.3)
    por(e['agua'] + 0.01, trecho(1180, ataque(1180), 2.2, tom=0.72, ref=-1, t=e['agua'], uso='lençol e retorno da água (camada de corpo)'), -8, -0.15, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.75, t=e['agua'], uso='peso do aço no impacto (baque grave)'), -9, 0.1, eq=lp_(900))
    grave(e['agua'], 1.1, 55, 34, -19, 0.1, nome='peso do bloco ao entrar na água (câmera lenta)')
    por(e['agua'] + 0.1, trecho(1178, 0.0, 1.7, ref=-3, t=e['agua'], uso='bolhas e afundamento (ouvido debaixo d\'água)'), -10, 0.0, sub=True)
    por(e['agua'] + 0.25, trecho(1321, 0, ref=-3, t=e['agua'] + 0.25, uso='bolhas profundas'), -14, 0.05, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, t=e['leito'], uso='bloco toca o leito de areia'), -6, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, ref=-3, t=e['leito'], uso='sedimento levantado (abafado)'), -14, 0.0, sub=True)
    grave(e['leito'], 0.7, 48, 32, -22, sub=True, nome='peso no leito')
    # o gigante no mar
    por(4.30, trecho(1471, ataque(1471) - 0.1, ref=-4, t=4.3, uso='rajada no corte para o mar aberto'), -17)
    cama(4.4, 15.1, 1189, -14, ini=10, uso='mar aberto (ondas)')
    cama(4.4, 15.1, 1200, -21, uso='vento sobre o mar')
    cama(4.4, 15.1, C('IcebreakerKunashipsengine'), -25, ini=estavel('IcebreakerKunashipsengine', 12), eq=lp_(500), uso='máquinas do navio, ouvidas de fora (praça de máquinas real, filtrada)')
    por(7.9, trecho(3078, 0, 5.0, ref=-3, t=7.9, uso='casco/máquinas passando (travelling)'), -15, -0.3, eq=lp_(1500))
    x = trecho(2461, 3.0, 4.6, fi=0.8, fo=1.2, norm='rms', ref=-20, t=9.0, uso='água empurrada pela proa (onda de proa)')
    por(9.0, x * np.sin(np.linspace(0, np.pi, len(x)))[:, None] ** 0.8, -6, 0.25)
    por(10.9, trecho(1195, 6.0, 2.6, fi=0.3, fo=0.8, norm='rms', ref=-20, t=10.9, uso='espuma e borrifo da proa'), -9, 0.3)
    por(11.2, trecho(1198, ataque(1198), ref=-3, t=11.2, uso='borrifo da crista na roda de proa'), -18, 0.35)
    por(13.3, trecho(1195, 12.0, 1.8, fi=0.2, fo=1.2, norm='rms', ref=-20, t=13.3, uso='esteira se afastando'), -14, -0.4)


# ================================================================================================ 15–30 · estaleiro
def estaleiro():
    cama(15.1, 30.75, 3074, -16, amb='ind', envio=0.2, uso='ambiente de estaleiro (galpão de construção naval)')
    cama(15.1, 30.75, C('Shipyardcrane'), -24, amb='ind', ini=estavel('Shipyardcrane', 15), eq=hp_(50), uso='guindaste de estaleiro ao fundo (Gotenius, Gotemburgo)')
    cama(15.1, 30.75, C('Weldingonshipinfloatingdrydock'), -31, amb='ind', ini=estavel('Weldingonshipinfloatingdrydock', 15), uso='solda distante em outro ponto do casco (estaleiro real)')
    m = EV['estaleiro_mov']; tg = np.array(m['t'])
    v = np.clip(np.array(m['carro']['v']) / 3.05, 0, 1); v = np.convolve(v, np.ones(9) / 9, 'same')
    a, b = 15.1, 30.3; n = int((b - a) * SR); vs = np.interp(a + tt(n), tg, v)
    # MOTOR do carro do pórtico (substitui o motor de escada de bombeiro 1619): guindaste de estaleiro real; volume = velocidade real
    segue('Shipyardcrane', a, b, vs, -11, -0.2, 'ind', 0.4, uso='motor/translação do pórtico (guindaste de estaleiro real) seguindo a velocidade do carro')
    # rodas/carro rolando no trilho: ponte rolante real (substitui a porta de correr 1534)
    segue('Crane', a, b, vs, -18, -0.2, 'ind', 0.4, uso='carro rolando no trilho (ponte rolante real)', expo=1.0)
    vg = np.clip(np.array(m['grupo_carga']['v']) / 3.97, 0, 1); acel = np.abs(np.gradient(np.convolve(vg, np.ones(5) / 5, 'same')))
    picos = [tg[i] for i in range(1, len(acel) - 1) if acel[i] > 0.02 and acel[i] >= acel[i - 1] and acel[i] >= acel[i + 1]]
    ult = -9; k = 0
    for t0 in picos:
        if t0 - ult > 1.2:
            por(t0, trecho(3076, 1.0 + 1.6 * (k % 4), 1.4, fo=0.4, ref=-3, t=t0, uso='cabos e estrutura rangendo na arrancada/freada'), -16, 0.1, 'ind', 0.5, eq=hp_(60)); ult = t0; k += 1
    # ENCAIXE da chapa (23,60 s) (substitui a porta de prisão 201): impacto metálico pesado e grave + batida de fábrica com eco + contato agudo
    por(23.58, trecho(783, ataque(783, -12) - 0.01, 2.2, fo=0.8, ref=-1, t=23.6, uso='encaixe da chapa: corpo grave de aço pesado'), -5, 0.0, 'ind', 0.5)
    por(23.59, trecho(2983, ataque(2983), ref=-1, t=23.6, uso='encaixe da chapa: batida metálica no galpão (com eco real)'), -8, 0.05, 'ind', 0.35)
    por(23.60, trecho(2980, ataque(2980), ref=-1, t=23.6, uso='contato metálico duro (camada aguda)'), -12, 0.1, 'ind', 0.5)
    grave(23.6, 0.6, 62, 40, -24, amb='ind', nome='peso da chapa no encaixe')
    # solda: arco real só nos cordões, envelope do brilho do shader (±4 dB)
    def tremor(g, sem, tr=0.5):
        q = np.floor(g * 30 + 0.5).astype(np.float32)
        def h(x): return np.mod(np.sin(x * np.float32(12.9898) + np.float32(sem * 78.233)).astype(np.float32) * np.float32(43758.5453), 1.0)
        return 1 - tr + tr * (0.6 * h(q) + 0.4 * h(q * np.float32(0.5) + np.float32(3.1)))
    for (ta, tb), sem, g_, p_, ini in (((23.75, 24.55), 0.25, -10, 0.1, 0.6), ((24.68, 25.25), 1.25, -10, 0.1, 3.2), ((24.0, 24.7), 3.25, -17, 0.3, 5.0), ((24.85, 25.4), 4.25, -17, 0.3, 1.8)):
        x = trecho(2603, ini, tb - ta + 0.1, fi=0.02, fo=0.08, norm='rms', ref=-20, t=ta, uso='arco elétrico de solda e faíscas (gravação real)')
        env = tremor(ta + tt(len(x)), sem).astype(float); env = 10 ** ((env - 1) * 4 / 20 / 0.5)
        por(ta, x * env[:, None], g_, p_, 'ind', 0.3)
    for t0, i in ((24.9, 812), (25.1, 814)):
        por(t0, trecho(i, ataque(i), ref=-3, t=t0, uso='solda ao fundo (bojo)'), -17, -0.35, 'ind', 0.4)
    # chapas chegando: poucos contatos selecionados
    ch = EV['chapas']; sel = [ch[0], ch[len(ch) // 4], ch[len(ch) // 2], ch[3 * len(ch) // 4], ch[-1]]
    for k, (t0, i) in enumerate(zip(sel, (2754, 3158, 2983, 2754, 783))):
        x = trecho(i, ataque(i, -12) - 0.01 if i == 783 else 0.79 if i == 2754 else ataque(i), 1.6 if i == 783 else None, fo=0.5 if i == 783 else 0.08, ref=-1, t=t0, uso='chapas chegando ao costado e à proa (contatos selecionados)')   # 2754: batida real em 0,79 s
        por(t0, x, -11 - 2 * (k % 2), (-0.4, 0.3, -0.2, 0.4, 0.0)[k], 'ind', 0.55)
    # PASSAGEM DE TEMPO (30,3 s; "Meses depois"): ar suave real + fusão das ambiências
    por(29.75, trecho(1167, 0.4, 1.2, fi=0.4, fo=0.5, ref=-6, t=29.75, uso='passagem de tempo do estaleiro (sopro suave)'), -24, 0.0, eq=lp_(2500))


# ================================================================================================ 30–41 · navio pronto, corte do casco
def navio_corte():
    cama(30.0, 35.4, 3074, -22, amb='ind', ini=30, uso='estaleiro (navio já pronto)')
    cama(30.0, 35.4, C('Shipyardcrane'), -30, amb='ind', ini=estavel('Shipyardcrane', 5, ini=60), uso='guindaste ao fundo')
    # proa se separando no corte (33,15 s): aço pesado deslizando + rangido; reforço grave discreto
    por(33.15, trecho(1523, ataque(1523, -20), 1.3, fi=0.15, fo=0.5, ref=-3, tom=0.8, t=33.15, uso='proa se separando: aço pesado deslizando'), -13, 0.2, 'ind', 0.5)
    por(33.25, trecho(3076, 2.0, 1.6, fi=0.2, fo=0.6, ref=-3, t=33.25, uso='estrutura rangendo no corte'), -19, 0.15, 'ind', 0.5, eq=hp_(60))
    grave(33.15, 1.6, 50, 38, -24, 0.2, 'ind', nome='massa da proa deslizando')
    # interior do casco vazio: ar parado de compartimento de aço (zumbido industrial real, distante)
    cama(35.0, 41.9, 2504, -27, amb='int', envio=0.3, eq=lp_(1800), uso='interior do casco vazio (zumbido industrial distante)')
    sopro(37.0, 1.0, -36, (2500, 7000), nome='células acendendo (brilho sutil, sem bipe)')
    sopro(39.2, 1.0, -37, (2500, 7000), nome='células acendendo (brilho sutil, sem bipe)')
    por(39.6, trecho(3076, 5.2, 1.2, fi=0.05, fo=0.5, ref=-3, t=39.6, uso='estalo térmico no porão vazio'), -27, -0.2, 'int', 0.6, eq=hp_(80))


# ================================================================================================ 41–48 · dique
def dique():
    e = EV['dique']
    # dique flutuante real (Gotenius): bombas e água, a base do trecho inteiro
    cama(41.3, 48.25, C('Adjustingadrydock'), -17, amb='dique', ini=estavel('Adjustingadrydock', 7), uso='dique flutuante sendo ajustado (bombas e água, gravação real)')
    por(e['comporta'] - 0.03, trecho(783, ataque(783, -12) - 0.01, 2.5, fo=0.8, ref=-1, t=e['comporta'], uso='comporta/válvulas abrindo (impacto metálico grave)'), -13, -0.3, 'dique', 0.5)
    grave(e['comporta'], 1.0, 52, 36, -23, -0.3, 'dique', nome='peso da comporta')
    k = e['jatos_fim'] - e['comporta']; n = int((k + 0.6) * SR); g = np.clip(tt(n) / 0.25, 0, 1) * (1 - 0.35 * tt(n) / (k + 0.6))
    x = laco(3029, k + 0.6, 4.0, 11.0, xf=0.5, ref=-20, t=e['comporta'], uso='jatos de água entrando no dique (cascata forte)')[:n]
    por(e['comporta'] + 0.15, x * g[:, None] * np.clip((k + 0.6 - tt(n)) / 0.6, 0, 1)[:, None], -9, -0.25, 'dique', 0.45)
    cama(42.0, 48.0, C('Waterintakepumpingstation'), -16, amb='dique', ini=estavel('Waterintakepumpingstation', 6), uso='água correndo pelas tubulações de enchimento (estação de bombeamento real)')
    n = int(4.6 * SR); kk = np.linspace(0, 1, n)
    x = laco(2461, 4.6, 10.0, 40.0, xf=0.8, ref=-20, t=43.4, uso='enchimento contínuo, cada vez mais grave')[:n]
    por(43.4, x * ((0.6 + 0.4 * np.sin(np.pi * kk)) * (1 - 0.5 * kk))[:, None], -15, -0.2, 'dique', 0.5, eq=lp_(1800))
    por(42.3, trecho(1208, 20.0, 3.8, fi=0.5, fo=1.0, norm='rms', ref=-20, t=42.3, uso='água alcançando o casco e os picadeiros'), -17, 0.1, 'dique', 0.4)
    por(e['picadeiros'] - 0.05, trecho(3076, 6.0, 1.4, fi=0.1, fo=0.5, ref=-3, t=e['picadeiros'], uso='estrutura alivia quando o peso deixa os picadeiros'), -20, 0.0, 'dique', 0.4, eq=hp_(50))
    grave(e['picadeiros'], 1.4, 44, 34, -25, 0.0, 'dique', nome='casco se desprende dos picadeiros (leve)')
    por(46.4, trecho(1208, 30.0, 1.8, fi=0.3, fo=0.8, norm='rms', ref=-20, t=46.4, uso='casco livre: água ao redor'), -20, 0.2, 'dique', 0.4)


# ================================================================================================ 48–95 (empuxo e experimento: como na demo aprovada para teste; retomada com o novo arrasto)
def retomada():
    e = EV['retomada']
    cama(74.85, 76.25, 1208, -22, ini=20, uso='marulho no cais (retomada)')
    d = e['borda'] - 74.85 + 0.25
    por(74.85, trecho(1523, max(0, ataque(1523, -20) + 0.1), d, fo=0.12, ref=-3, t=74.85, uso='o mesmo arrasto no cais (outro trecho da gravação)'), -6, 0.15, 'ext', 0.25)
    por(74.9, trecho(809, ataque(809) + 0.2, d, fo=0.12, ref=-3, tom=0.85, t=74.85, uso='aço raspando (grão)'), -17, 0.15, 'ext', 0.25, eq=hp_(400))
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, tom=0.95, t=e['borda'], uso='bloco deixa a borda'), -5, 0.15, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 1.0, ref=-6, t=e['borda'], uso='queda'), -17, 0.1)
    por(e['agua'] - 0.02, trecho(2923, ataque(2923), tom=0.85, ref=-1, t=e['agua'], uso='impacto na água (variação da abertura)'), -3, 0.1, 'ext', 0.3)
    por(e['agua'], trecho(1304, ataque(1304) + 0.05, 1.6, tom=0.78, ref=-1, t=e['agua'], uso='corpo do respingo'), -9, -0.1, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.7, t=e['agua'], uso='peso do aço'), -10, 0.1, eq=lp_(900))
    grave(e['agua'], 1.0, 55, 34, -20, 0.1, nome='peso do bloco (retomada)')
    por(75.9, trecho(1167, 0.5, 1.4, fi=0.5, fo=0.4, ref=-6, tom=0.85, t=75.9, uso='transição para a câmera lenta'), -22, 0.0, eq=lp_(1200))
    cama(76.2, 83.85, 1312, -9, ini=40, sub=True, uso='mundo subaquático em câmera lenta')
    por(76.3, trecho(1178, 2.0, 5.6, fo=0.8, ref=-3, tom=0.8, t=76.3, uso='bolhas lentas do bloco (câmera lenta)'), -10, 0.05, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, tom=0.9, t=e['leito'], uso='bloco toca o leito (tempo volta ao normal)'), -4, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, ref=-3, t=e['leito'], uso='sedimento se espalhando (abafado)'), -11, 0.0, sub=True)
    grave(e['leito'], 0.7, 48, 32, -21, sub=True, nome='peso no leito')


def experimento():
    R.experimento()
    e = EV['experimento']
    grave(e['agua'], 0.8, 60, 40, -23, -0.4, nome='bloco compacto (peso)')
    grave(e['agua'] + 0.02, 1.4, 46, 32, -23, 0.35, nome='casco largo (massa de água deslocada)')
    cama(88.6, 94.55, 1205, -22, sub=True, uso='vista submersa do experimento')


# ================================================================================================ 94–134 · porto, carregamento, calado, marcas
def porto():
    m = EV['porto_mov']; tg = np.array(m['t'])
    def vel(nome, vmax):
        v = np.array(m[nome]['v']); v[v > 12] = 0; v = np.clip(v / vmax, 0, 1); return np.convolve(v, np.ones(7) / 7, 'same')
    a, b = 94.55, 117.2; n = int((b - a) * SR)
    # ambiente portuário real: terminal de contêineres (Dortmund) + empilhadeiras de contêiner ao fundo
    cama(94.55, 134.3, C('ContainerTerminalatthePortofDortmund'), -17, amb='porto', envio=0.15, ini=estavel('ContainerTerminalatthePortofDortmund', 40), uso='ambiente de terminal de contêineres (gravação real)')
    cama(94.55, 117.2, C('Containerreachstackers'), -27, amb='porto', ini=estavel('Containerreachstackers', 20), eq=lp_(2500), uso='empilhadeiras de contêiner ao fundo')
    cama(94.55, 134.3, 1208, -24, ini=40, uso='água junto ao cais')
    # portêineres: guindaste de navio porta-contêineres real; volume segue carro + spreader do guindaste principal
    vc = np.interp(a + tt(n), tg, vel('carro_anc5', 4.0))
    z = np.array(m['spreader_anc5']['z']); vz = np.abs(np.gradient(z) * 30); vz[vz > 12] = 0
    vs = np.interp(a + tt(n), tg, np.convolve(np.clip(vz / 5.0, 0, 1), np.ones(7) / 7, 'same'))
    mov = np.clip(0.75 * vc + 0.9 * vs, 0, 1)
    segue('Containershipgantrycrane', a, b, 0.25 + 0.75 * mov, -12, 0.0, 'porto', 0.4, uso='portêiner carregando o navio (guindaste real): carro, guincho e cabos seguem o movimento')
    vc2 = np.maximum(np.interp(a + tt(n), tg, vel('carro_anc3', 4.0)), np.interp(a + tt(n), tg, vel('carro_anc7', 4.0)))
    segue('Mobileharbourcrane', a, b, 0.2 + 0.8 * vc2, -22, 0.4, 'porto', 0.4, uso='guindastes vizinhos (guindaste portuário real, mais distante)')
    # pousos dos 3 contêineres do plano próximo, no instante do contato: batida metálica real + grave discreto
    for i, t0 in enumerate(EV['pousos']):
        por(t0 - 0.01, trecho(2754, 0.79, fi=0.003, ref=-1, t=t0, uso='contêiner pousando (batida de caixa metálica)'), -9, (-0.1, -0.3, 0.3)[i], 'porto', 0.45)
        por(t0, trecho(783, ataque(783, -12) - 0.01, 1.4, fo=0.6, ref=-1, t=t0, uso='peso do contêiner no pouso'), -16, (-0.1, -0.3, 0.3)[i], 'porto', 0.4, eq=lp_(1500))
        por(t0 - 0.9, trecho(3076, 0.5 + 1.3 * i, 0.9, fi=0.1, fo=0.4, ref=-3, t=t0 - 0.9, uso='cabos tensionando antes do pouso'), -24, 0.0, 'porto', 0.4, eq=hp_(120))
    # time-lapse (105,45–117,2): NÃO um som por contêiner — o terminal real mais presente + poucos contatos distantes
    cama(105.45, 117.2, C('ContainerTerminalatthePortofDortmund'), -21, amb='porto', ini=estavel('ContainerTerminalatthePortofDortmund', 12, ini=100), uso='terminal em atividade (tempo acelerado)')
    for k, t0 in enumerate((107.3, 110.1, 113.4)):
        por(t0, trecho(2983, ataque(2983), ref=-1, t=t0, uso='contato distante de contêiner (só alguns, no tempo acelerado)'), -24, (-0.5, 0.4, -0.2)[k], 'porto', 0.6, eq=lp_(2000))
    # água contra o casco conforme o calado aumenta (ondas pequenas batendo no casco, gravação real)
    zn = np.array(m['navio']['z']); vzn = np.abs(np.gradient(zn) * 30)
    intens = np.interp(a + tt(n), tg, np.convolve(np.clip(vzn / 0.25, 0, 1), np.ones(15) / 15, 'same'))
    segue('Smallwaves', a, b, 0.3 + 0.7 * intens, -15, 0.2, 'porto', 0.3, uso='água batendo no casco enquanto o navio afunda com a carga')
    # calado e marcas (117,2–134): água junto à quilha, sem sons para cada linha
    cama(117.2, 134.3, C('Smallwaves'), -19, amb='porto', ini=30, uso='água no casco (calado / marcas)')
    por(118.9, trecho(1208, 50.0, 2.0, fi=0.3, fo=0.8, norm='rms', ref=-20, t=118.9, uso='cota do calado sobe (marulho junto à quilha)'), -21, 0.1)
    sopro(130.4, 2.6, -36, (1800, 6000), nome='marcas de calado acendendo (um único brilho sutil para as 5 linhas)')


# ================================================================================================ 134–155 · avaria
def avaria():
    # mesma direção da demo, com as divisórias estanques no impacto metálico grave (substitui a porta de prisão 201)
    import amostras
    orig = R.trecho
    def trecho_sem_201(i, *a, **k):
        if i == 201: return orig(783, ataque(783, -12) - 0.01, 2.4, fo=0.8, ref=-1, t=k.get('t'), uso='divisórias estanques: batida firme e calma (aço pesado)')
        return orig(i, *a, **k)
    R.trecho = trecho_sem_201
    try: R.avaria()
    finally: R.trecho = orig
    e = EV['avaria']
    grave(e['rasgo'] + 0.05, 0.6, 70, 45, -22, 0.2, nome='ruptura (peso)')
    grave(e['divisorias'], 1.2, 50, 36, -24, 0.0, 'int', nome='divisórias (peso)')


# ================================================================================================ 154–168 · conclusão
def conclusao():
    e = EV['conclusao']
    cama(154.6, 156.5, 1189, -15, ini=120, uso='mar (bloco de 17 m sobre a água)')
    cama(154.6, 156.5, 1201, -23, ini=10, uso='brisa')
    por(e['solto'], trecho(1471, ataque(1471) - 0.1, ref=-4, t=e['solto'], uso='queda do bloco de 17 m (ar deslocado)'), -18, 0.25)
    # impacto ENORME: camadas reais mais graves (escala) + respingo largo + reforço grave
    por(e['agua'] - 0.02, trecho(1180, ataque(1180), 2.6, tom=0.7, ref=-1, t=e['agua'], uso='bloco de 17 m entra na água (massa)'), -4, 0.2, 'ext', 0.35)
    por(e['agua'], trecho(1304, ataque(1304), 2.0, tom=0.75, ref=-1, t=e['agua'], uso='respingo largo'), -7, 0.3, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.65, t=e['agua'], uso='peso do aço'), -10, 0.25, eq=lp_(800))
    por(e['agua'] + 0.15, trecho(1198, ataque(1198), ref=-1, t=e['agua'], uso='água espirrando e caindo de volta'), -12, 0.35, 'ext', 0.3)
    grave(e['agua'], 1.6, 50, 30, -17, 0.25, nome='escala do bloco de 17 m')
    # afundamento debaixo d'água
    cama(156.4, 164.35, 1312, -11, ini=10, sub=True, uso='debaixo d\'água: bloco afundando, casco ao lado')
    por(e['agua'] + 0.4, trecho(1178, 0.5, 3.0, fo=1.0, ref=-3, tom=0.85, t=e['agua'] + 0.4, uso='bolhas da descida do bloco'), -9, 0.25, sub=True)
    por(156.6, trecho(1321, 0, ref=-3, t=156.6, uso='bolhas profundas'), -14, 0.2, sub=True)
    sopro(159.6, 1.4, -31, (150, 900), sub=True, nome='volume deslocado sob o casco (textura sutil)')
    n = int(1.0 * SR); y = np.sin(2 * np.pi * np.cumsum(np.linspace(60, 82, n)) / SR) * np.sin(np.linspace(0, np.pi, n)) ** 2
    por(161.4, y, -30, 0.0, 'sub', 0.3); AM.USOS.append(dict(t=161.4, id='sintese', titulo='peso = empuxo (pulso grave sutil)', ini=0, dur=1.0, tom=1.0, uso='gráfico'))
    # plano final: o navio no mar, natural
    por(164.2, trecho(1167, 0.3, 1.0, fi=0.3, fo=0.5, ref=-6, t=164.2, uso='saída da água para o plano aéreo final'), -25, 0.0, eq=lp_(2000))
    cama(164.35, 168.0, 1189, -13, ini=30, uso='mar aberto (plano final)')
    cama(164.35, 168.0, C('Smallwaves'), -20, ini=10, uso='água no casco')
    cama(164.35, 168.0, 1201, -22, ini=30, uso='vento')


def mar_s05():
    """s05 (41,55–48) usa o dique; s0607b (63,1–65,8) e transições já cobertas. Nada extra aqui."""


if __name__ == '__main__':
    for f in (abertura, estaleiro, navio_corte, dique, R.empuxo, retomada, experimento, porto, avaria, conclusao): f()
    SE.musica()
    P = dict(efeitos_rel=-3.5, amb_rel=-12.5, duck_alvo=-13.0, duck_piso=-18.0, duck_grave=-3.0, musica_rel=-16.0, duck_amb_max=-9.0)   # ducking moderado (calibração C)
    P.update(json.loads(os.environ.get('MIX_HIBRIDO', '{}'))); suf = os.environ.get('SUFIXO_HIBRIDO', '')
    res = SE.mixar(saida=f'audio_ep01_hibrido{suf}.wav', stems_dir='stems', sufixo=f'_hibrido{suf}', relatorio=f'mix_hibrido{suf}.json', **P)
    res['parametros_mix'] = P; json.dump(res, open(os.path.join(SE.A, f'mix_hibrido{suf}.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(AM.USOS, open(os.path.join(SE.A, 'usos_hibrido.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(TROCAS, open(os.path.join(SE.A, 'reservas_hibrido.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(AM.USOS), 'usos registrados; reservas Mixkit usadas no lugar do Commons:', TROCAS)
