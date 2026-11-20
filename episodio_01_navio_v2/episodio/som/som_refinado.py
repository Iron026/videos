"""Direção sonora REFINADA do Ep. 01 (só som e mixagem; imagem, narração e tempos inalterados).

Princípios desta versão (em relação a som_hibrido.py):
- MENOS ÁGUA: cada cena tem UMA gravação de água principal e só as camadas necessárias; mar, correnteza e ambiente
  submerso ficam discretos (−3 a −8 dB conforme a cena); os impactos continuam fortes onde a imagem pede.
- INTERATIVO: motores e guinchos seguem velocidade E aceleração reais da animação (volume + leve variação de rotação),
  silenciam quando o equipamento para; arrasto segue o deslocamento do bloco; solda só nos cordões, com pausas;
  contêiner = contato no encaixe + vibração curta; bolhas seguem o afundamento; ondas do casco seguem o movimento.
- PERSPECTIVA: a distância real câmera→fonte (cenas/*.json) controla volume e agudos (perto: definido; longe: suave).
- MODERAÇÃO: sem whoosh de corte, graves sintéticos só nos 4 impactos que pedem escala, reverberação metálica contida,
  sem repetir a mesma gravação de impacto em cenas diferentes, ambiências sempre com fusões (nada surge ou some seco).
- MIXAGEM: mesma cadeia e mesmo ducking moderado; os stems usam os MESMOS ganhos absolutos da versão anterior, para que
  tirar camadas reduza de fato o som (sem renormalizar), e o master leva o todo a −14 LUFS.
Saídas: audio_ep01_refinado.wav, stems/ep01_*_refinado.wav (+ grupos/ e categorias/), som/mix_refinado.json, som/usos_refinado.json"""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import som_ep01 as SE
import amostras as AM
import som_hibrido as H                       # grupos de substituição, reservas do Commons, auditoria da água
from som_hibrido import G, C, estavel
from som_real import por, hp_, lp_
from amostras import trecho, laco, ataque, SR
from sintese import lpz, hpz, tt, ruido, lp
import sintese as S
import movimento as MV

def _cat():   # auditoria por categoria: água (como antes) e buzina
    i = AM.ULTIMO[0]; AM.ULTIMO[0] = None
    if i == 'CruiseshipAlbatroshorn': return 'buzina'
    return 'agua' if (i in H.AGUA or getattr(i, 'reserva_de', '') in H.AGUA) else None
SE.CAT_FN = _cat

EV = SE.EV; DUR = SE.DUR
BUZINA = os.environ.get('BUZINA', '0') == '1'; BUZ_DB = [float(v) for v in os.environ.get('BUZINA_DB', '-12,-22').split(',')]


# ------------------------------------------------------------------------------------------------ utilitários
def amb(t0, t1, i, dB, ini=None, sub=False, eq=None, envio=0.12, ambiente='ext', uso='', pre=0.45, pos=0.45, fade=1.0, curva=None):
    """Ambiência com FUSÕES: começa um pouco antes do corte e termina um pouco depois, entrando e saindo em ~1 s."""
    i = H._r(i); a = max(0.0, t0 - pre) if t0 > 0.05 else 0.0; b = min(DUR, t1 + pos); n = int((b - a) * SR)
    x = laco(i, b - a + 0.3, estavel(i, min(8.0, b - a)) if ini is None else ini, None, xf=0.8, ref=-20, t=t0, uso=uso)[:n]
    k = min(n // 2, int(fade * SR)); ki = k if a > 0 else int(0.25 * SR)
    x[:ki] *= np.linspace(0, 1, ki)[:, None] ** 1.5; x[-k:] *= np.linspace(1, 0, k)[:, None] ** 1.5
    if curva is not None: x *= curva(a, n)[:, None]
    por(a, x, dB, 0.0, ambiente, envio, 'ambiencias', sub, eq)


def automacao(a, n, pontos):
    """Ganho por amostra para recuos pontuais [(t1, t2, dB, rampa)] em tempo absoluto: rampas cossenoidais, sem cortes."""
    tl = a + tt(n); g = np.ones(n)
    for (t1, t2, gdb, rp) in pontos:
        up = np.clip((tl - (t1 - rp)) / rp, 0, 1); dn = np.clip(((t2 + rp) - tl) / rp, 0, 1)
        g *= 1 - (1 - 10 ** (gdb / 20)) * (0.5 - 0.5 * np.cos(np.pi * up)) * (0.5 - 0.5 * np.cos(np.pi * dn))
    return g


def controle(t, y, a, b, fs=1000):
    """Curva de movimento (t, y) na taxa de controle (1 kHz) entre a e b."""
    tc = np.arange(a, b, 1 / fs); return tc, np.interp(tc, t, y)


def seguir(y, ataque_s=0.08, solta_s=0.35, fs=1000):
    """Seguidor de envelope (ataque/liberação) na taxa de controle: o som entra e sai com o movimento, sem cliques."""
    aa, ar = np.exp(-1 / (ataque_s * fs)), np.exp(-1 / (solta_s * fs)); out = np.empty_like(y); c = 0.0
    for k, v in enumerate(y): c = (c * aa + v * (1 - aa)) if v > c else (c * ar + v * (1 - ar)); out[k] = c
    return out


def p_amostra(tc, y, a, n): return np.interp(a + tt(n), tc, y)


def motor(i, a, b, t, v, dB, pan=0.0, ambiente='ind', envio=0.2, r0=0.95, r1=1.05, carga=0.6, persp=None, eq=None, uso='', ini=None, automacao=None):
    """Motor/guincho que RESPONDE à animação: volume = velocidade^0,7 × (1 + carga na aceleração), rotação levemente
    maior com a velocidade (r0→r1) e silêncio quando o equipamento está parado. v: velocidade normalizada (0–1) em t."""
    i = H._r(i); tc, vc = controle(t, np.clip(v, 0, 1), a, b); vs = seguir(vc)
    ac = np.gradient(seguir(vc, 0.15, 0.15)) * 1000; ac = np.clip(ac / (np.percentile(np.abs(ac), 98) + 1e-6), 0, 1)
    n = int((b - a) * SR); r = p_amostra(tc, r0 + (r1 - r0) * vs, a, n)
    src = laco(i, (b - a) * r1 + 1.0, estavel(i, 8.0) if ini is None else ini, None, xf=0.5, ref=-20, t=a, uso=uso)
    idx = np.cumsum(r); idx -= idx[0]; idx = np.minimum(idx, len(src) - 2)
    y = np.stack([np.interp(idx, np.arange(len(src)), src[:, c]) for c in range(2)], 1)
    g = p_amostra(tc, vs ** 0.7 * (1 + carga * ac), a, n)
    y *= g[:, None]
    if persp: y = MV.perspectiva(y, a, *persp)
    if automacao: y = y * globals()['automacao'](a, n, automacao)[:, None]   # recuo pontual: o mecanismo continua soando, só mais baixo
    por(a, y, dB, pan, ambiente, envio, eq=eq)


def sint_grave(t, dur, f0, f1, dB, pan=0.0, ambiente='ext', sub=False, nome=''):
    """Reforço grave sintético (só nos impactos que pedem ESCALA)."""
    n = int(dur * SR); x = tt(n); fr = np.linspace(f0, f1, n)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-x / (dur * 0.35)) * np.clip(x / 0.012, 0, 1) + 0.35 * lp(ruido(n), 90) * np.exp(-x / (dur * 0.25))
    AM.ULTIMO[0] = None; por(t, y, dB, pan, ambiente, 0.12, sub=sub)
    AM.USOS.append(dict(t=round(t, 2), id='sintese', titulo='reforço grave (síntese discreta)', ini=0, dur=dur, tom=1.0, uso=nome, grupo=SE.GRUPO[0]))


def sint_sopro(t, dur, dB, f=(300, 1600), sub=False, ambiente='ext', nome=''):
    n = int(dur * SR); y = S.bp(ruido(n), *f) * np.sin(np.linspace(0, np.pi, n)) ** 2
    AM.ULTIMO[0] = None; por(t, y, dB, 0.0, ambiente, 0.2, sub=sub)
    AM.USOS.append(dict(t=round(t, 2), id='sintese', titulo='textura gráfica sutil (síntese)', ini=0, dur=dur, tom=1.0, uso=nome, grupo=SE.GRUPO[0]))


def janela_env(n, env):
    """Envelope (lista de (fração, nível)) aplicado a n amostras."""
    fr, lv = zip(*env); return np.interp(np.linspace(0, 1, n), fr, lv)


# ------------------------------------------------------------------------------------------------ buzina do navio
BUZ = 'CruiseshipAlbatroshorn'      # Wikimedia Commons, CC0: buzina real de navio (três toques ao deixar Bremerhaven)


def buzina(t0, sust, dB, persp=None, envio=0.25, extra_lp=None, uso='', rel=2.04, compensa_fim=False, sob_fala_db=None):
    """UM toque de buzina montado só com a gravação real: ATAQUE real do 1º toque (fim da subida de pressão) → sustentação breve
    (trecho estável) → DISSIPAÇÃO real do último toque (fim do sopro + eco do porto). Fusões de 0,25 s entre as partes.
    Levemente mais grave (tom 0,9 ≈ −1,8 semitom: ~104 Hz) para a escala de um cargueiro; filtro passa-alta em 80 Hz tira o
    vento do microfone. Perspectiva pela distância real da câmera ao navio."""
    tom = 0.9; xf = int(0.25 * SR)
    A_ = trecho(BUZ, 3.15, 0.6, fi=0.08, fo=0.0, norm=None, tom=tom, t=t0, uso=uso)        # fim da subida de pressão: ~0,5 s
    S_ = trecho(BUZ, 7.0, sust + 0.5, fi=0.0, fo=0.0, norm=None, tom=tom)
    R_ = trecho(BUZ, 26.95, rel, fi=0.0, fo=0.25 if rel >= 2.0 else 0.5, norm=None, tom=tom)   # rel < 2: corte real + eco curto
    def junta(a, b):
        r = np.linspace(0, 1, xf)[:, None]; return np.concatenate([a[:-xf], a[-xf:] * (1 - r) + b[:xf] * r, b[xf:]])
    x = hpz(junta(junta(A_, S_), R_), 80, 4)
    if extra_lp: x = lpz(x, extra_lp, 2)
    x = x * 10 ** (-20 / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12)          # nível de referência −20 dB RMS (como as camas)
    if persp: x = MV.perspectiva(x, t0, *persp)
    if sob_fala_db is not None:   # soa pleno na pausa da narração e já está baixo quando a fala volta (rampa cossenoidal de 0,15 s
        # que TERMINA 30 ms antes da 1ª sílaba após a pausa); depois fica baixo até se dissipar — sem bombear, timbre intacto
        pal = json.load(open(os.path.join(SE.EP, '..', 'voz', 'narracao_ep01', 'trabalho', 'palavras.json')))
        tf = min(p['inicio'] for p in pal if p['inicio'] > t0 + 0.3) - 0.03 - t0; rp = 0.15
        r = 0.5 - 0.5 * np.cos(np.pi * np.clip((tt(len(x)) - (tf - rp)) / rp, 0, 1)); x = x * (1 - (1 - 10 ** (sob_fala_db / 20)) * r)[:, None]
        for u in AM.USOS[::-1]:
            if u.get('uso') == uso: u['recuo_sob_fala'] = dict(inicio_s=round(t0 + tf - rp, 2), completo_s=round(t0 + tf, 2), db=sob_fala_db); break
    if compensa_fim:   # o fade geral do encerramento (166,37→168 s) já atua sobre tudo; a buzina final termina pelo próprio
        fim = np.clip((SE.DUR - 0.03 - (t0 + tt(len(x)))) / 1.6, 0, 1) ** 1.5      # decaimento real, então desfaz-se o fade
        x = x * np.minimum(1 / np.maximum(fim, 1e-3), 10.0)[:, None]                # (limite +20 dB) só no trecho dela
    por(t0, x, dB, 0.05, 'ext', envio)
    return len(x) / SR


# ================================================================================================ 0–15 · abertura e navegação
def abertura():
    e = EV['abertura']
    amb(0.0, 2.85, 1208, -25, ini=3.0, uso='marulho no cais (pedras do porto)')
    amb(0.0, 2.85, 1191, -30, uso='mar distante')
    # ARRASTO que segue o deslocamento: começa com o empurrão, cresce enquanto o bloco ganha velocidade e acaba quando ele
    # perde o apoio na borda (o plano 1 vem do animatic: perfil de velocidade do próprio plano, sem curva exportada)
    t0, t1 = e['empurrao'], e['borda'] + 0.06; d = t1 - t0
    env = lambda n: janela_env(n, [(0, 0.0), (0.12, 0.55), (0.35, 0.85), (0.9, 1.0), (0.96, 0.6), (1.0, 0.0)])
    x = trecho(1523, max(0, ataque(1523, -20) - 0.02), d, fo=0.02, ref=-3, t=t0, uso='aço pesado arrastando no concreto: corpo (segue o deslocamento)')
    por(t0, x * env(len(x))[:, None], -6, 0.15, 'ext', 0.15)
    x = trecho(809, ataque(809), d, fo=0.02, ref=-3, tom=0.85, t=t0, uso='aço raspando no concreto: grão (segue o deslocamento)')
    por(t0 + 0.05, x * env(len(x))[:, None], -18, 0.15, 'ext', 0.1, eq=hp_(400))
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, t=e['borda'], uso='bloco tomba na borda'), -5, 0.15, 'ext', 0.2, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 1.0, ref=-6, t=e['borda'], uso='ar deslocado na queda'), -20, 0.1)
    # IMPACTO forte (câmera lenta) — mantido; camadas de corpo um pouco menores
    por(e['agua'] - 0.02, trecho(1304, ataque(1304), 1.9, tom=0.8, ref=-1, t=e['agua'], uso='impacto do bloco na água (principal)'), -4, 0.1, 'ext', 0.3)
    por(e['agua'] + 0.01, trecho(1180, ataque(1180), 1.8, tom=0.72, fo=0.6, ref=-1, t=e['agua'], uso='lençol de água (corpo)'), -9, -0.15, 'ext', 0.25)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.75, t=e['agua'], uso='peso do aço no impacto'), -9, 0.1, eq=lp_(900))
    sint_grave(e['agua'], 1.1, 55, 34, -20, 0.1, nome='peso do bloco ao entrar na água (câmera lenta)')
    # BOLHAS que seguem a descida: fortes logo após a entrada e somem até o leito
    d = e['leito'] - e['agua']; x = trecho(1178, 0.0, d, fo=0.3, ref=-3, t=e['agua'], uso='bolhas da descida (diminuem até o leito)')
    por(e['agua'] + 0.1, x * janela_env(len(x), [(0, 0.3), (0.1, 1.0), (0.6, 0.5), (1.0, 0.1)])[:, None], -13, 0.0, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, t=e['leito'], uso='bloco toca o leito de areia'), -7, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, 1.2, ref=-3, t=e['leito'], uso='sedimento levantado (abafado)'), -17, 0.0, sub=True)
    # NAVEGAÇÃO (4,4–15,1): mar e vento discretos com espaço; o navio soa conforme a distância REAL da câmera
    amb(4.4, 15.1, 1189, -19, ini=10, uso='mar aberto (ondas, discreto)')
    amb(4.4, 15.1, 1200, -25, uso='vento sobre o mar (espaço)')
    a, b = 4.4, 15.1; n = int((b - a) * SR)
    tp, dp = MV.distancia('s02', 'navio_outro', (104, 0, 0)); tm, dm = MV.distancia('s02', 'navio_outro', (0, 0, 0)); ts, ds = MV.distancia('s02', 'navio_outro', (-100, 0, 0))
    x = laco(H._r(C('IcebreakerKunashipsengine')), b - a + 0.2, estavel(C('IcebreakerKunashipsengine'), 10), xf=0.8, ref=-20, t=a, uso='máquinas do navio (perspectiva: distância da câmera)')[:n]
    por(a, MV.perspectiva(lpz(x, 500, 2), a, tm, dm, 60, k=0.7, piso=-16), -23, 0.0, 'ext', 0.05)
    x = laco(2461, b - a + 0.2, 6.0, 60.0, xf=0.8, ref=-20, t=a, uso='onda de proa (segue a distância da câmera à proa)')[:n]
    por(a, MV.perspectiva(x, a, tp, dp, 45, k=0.8, piso=-18), -11, 0.25, 'ext', 0.08)
    x = laco(1195, b - a + 0.2, 5.0, 40.0, xf=0.8, ref=-20, t=a, uso='espuma e borrifo da proa (segue a distância)')[:n]
    por(a, MV.perspectiva(hpz(x, 300, 2), a, tp, dp, 35, k=0.9, piso=-20), -15, 0.3, 'ext', 0.08)
    x = laco(1195, b - a + 0.2, 60.0, 120.0, xf=0.8, ref=-20, t=a, uso='esteira (segue a distância da câmera à popa)')[:n]
    por(a, MV.perspectiva(x, a, ts, ds, 60, k=0.8, piso=-20), -19, -0.4, 'ext', 0.08)
    x = trecho(3078, 0, 5.0, ref=-3, t=7.9, uso='casco passando perto da câmera (travelling)')
    por(7.9, MV.perspectiva(x, 7.9, tm, dm, 60, k=0.6, piso=-12), -18, -0.3, eq=lp_(1500))
    if BUZINA: buzina(5.85, 0.8, BUZ_DB[0], (tm, dm, 150, 0.35, -8, 1.0, 1800), 0.3, sob_fala_db=-12, uso='buzina do navio ao aparecer (ataque na pausa após "gigante:")')


# ================================================================================================ 15–30 · estaleiro
def estaleiro():
    # a gravação do galpão tem uma batida metálica própria em ~17,0 s, sob "navio," (16,74–17,14 s): recuo suave de 8 dB só ali (o galpão continua)
    amb(15.1, 30.3, 3074, -17, ambiente='ind', envio=0.15, uso='ambiente de estaleiro (galpão de construção naval)', curva=lambda a, n: automacao(a, n, [(16.86, 17.16, -8.0, 0.12)]))
    with G('guindastes'): amb(15.1, 30.3, C('Shipyardcrane'), -30, ambiente='ind', ini=estavel(C('Shipyardcrane'), 15, ini=20), eq=hp_(80), uso='guindastes distantes (fundo)')
    persp = (*MV.distancia('s03', 'carro'), 40, 0.6, -14)
    tv, vc = MV.velocidade('s03', 'carro'); tg, vg = MV.velocidade('s03', 'grupo_carga')
    with G('guindastes'):
        motor(C('Shipyardcrane'), 15.1, 30.3, tv, vc / 2.8, -11, -0.2, 'ind', 0.2, 0.95, 1.05, 0.6, persp, eq=hp_(60),
              uso='motor de translação do pórtico: segue velocidade e aceleração do carro; para quando o carro para')
        motor(1534, 15.1, 30.3, tv, vc / 2.8, -21, -0.2, 'ind', 0.15, 0.97, 1.03, 0.2, persp, uso='rodas do carro rolando no trilho (só em movimento)')
        motor(2139, 15.1, 30.3, tg, vg / 3.9, -17, 0.1, 'ind', 0.15, 0.97, 1.08, 0.8, persp, eq=hp_(80), uso='guincho de içamento: segue a carga subindo/descendo')
        # cabos tensionados: rangidos discretos só nas arrancadas e frenagens da carga (aceleração forte), no máx. 4
        ac = np.abs(np.gradient(np.convolve(vg, np.ones(5) / 5, 'same'))); pk = [tg[i] for i in range(1, len(ac) - 1) if ac[i] > 0.12 and ac[i] >= ac[i - 1] and ac[i] >= ac[i + 1]]
        ult = -9; k = 0
        for t0 in pk:
            if t0 - ult > 1.5 and k < 4:
                por(t0, trecho(3076, 1.0 + 1.6 * (k % 4), 1.2, fo=0.4, ref=-3, t=t0, uso='cabos rangendo na arrancada/frenagem da carga'), -20, 0.1, 'ind', 0.25, eq=hp_(90)); ult = t0; k += 1
    # ENCAIXE da chapa: contato metálico pesado no instante do toque (única vez que 783 é usado no episódio)
    por(23.58, trecho(783, ataque(783, -12) - 0.01, 1.6, fo=0.6, ref=-1, t=23.6, uso='encaixe da chapa: corpo grave de aço'), -6, 0.0, 'ind', 0.25)
    por(23.59, trecho(2983, ataque(2983), 1.2, fo=0.4, ref=-1, t=23.6, uso='encaixe: batida metálica (eco real do galpão)'), -11, 0.05, 'ind', 0.1)
    por(23.60, trecho(2980, ataque(2980), ref=-1, t=23.6, uso='encaixe: contato agudo'), -14, 0.1, 'ind', 0.2)
    sint_grave(23.6, 0.6, 62, 40, -25, ambiente='ind', nome='peso da chapa no encaixe')
    # SOLDA: só nos cordões (com as pausas entre eles); crepitar = brilho do shader (±4 dB) + falhas curtas do arco
    def tremor(g, sem, tr=0.5):
        q = np.floor(g * 30 + 0.5).astype(np.float32)
        def h(x): return np.mod(np.sin(x * np.float32(12.9898) + np.float32(sem * 78.233)).astype(np.float32) * np.float32(43758.5453), 1.0)
        return 1 - tr + tr * (0.6 * h(q) + 0.4 * h(q * np.float32(0.5) + np.float32(3.1)))
    rr = np.random.default_rng(23)
    for (ta, tb), sem, g_, p_, ini, i, lpf in (((23.75, 24.55), 0.25, -11, 0.1, 0.6, 2603, None), ((24.68, 25.25), 1.25, -11, 0.1, 3.2, 2603, None),
                                             ((24.0, 24.7), 3.25, -19, 0.3, 5.0, 2603, 6000), ((24.85, 25.4), 4.25, -19, 0.3, 1.8, 2603, 6000),
                                             ((24.9, 26.4), 5.25, -23, -0.35, 0.5, 812, 3500), ((25.1, 26.4), 6.25, -24, -0.45, 0.3, 814, 3500)):
        x = trecho(i, ini, tb - ta + 0.06, fi=0.015, fo=0.05, norm='rms', ref=-20, t=ta, uso='arco de solda e faíscas (só no cordão, com o brilho)')
        env = 10 ** ((tremor(ta + tt(len(x)), sem).astype(float) - 1) * 4 / 20 / 0.5)
        for _ in range(int((tb - ta) * 3)):                       # falhas curtas do arco (o eletrodo "engasga"), sem padrão fixo
            c0 = int(rr.uniform(0.1, 0.9) * len(x)); w = int(rr.uniform(0.02, 0.05) * SR); env[c0:c0 + w] *= rr.uniform(0.15, 0.4)
        x = x * np.convolve(env, np.ones(96) / 96, 'same')[:, None]
        por(ta, lpz(x, lpf, 2) if lpf else x, g_, p_, 'ind', 0.15)
    # chapas chegando: 5 contatos selecionados, gravações variadas (sem 783), reverberação contida
    ch = EV['chapas']; sel = [ch[0], ch[len(ch) // 4], ch[len(ch) // 2], ch[3 * len(ch) // 4], ch[-1]]
    for k, (t0, i, ini) in enumerate(zip(sel, (2754, 3158, 2983, 2754, 3158), (0.79, None, None, 0.79, None))):
        x = trecho(i, ini if ini is not None else ataque(i), 0.9, fo=0.3, ref=-1, t=t0, uso='chapa encostando no casco (contato)')
        por(t0, x, -14 - 2 * (k % 2), (-0.4, 0.3, -0.2, 0.4, 0.0)[k], 'ind', 0.2)
    por(29.75, trecho(1167, 0.4, 1.2, fi=0.4, fo=0.5, ref=-6, t=29.75, uso='passagem de tempo "Meses depois" (sopro suave, único)'), -26, 0.0, eq=lp_(2500))


# ================================================================================================ 30–41 · navio pronto, corte do casco
def navio_corte():
    amb(30.3, 35.0, 3074, -23, ambiente='ind', ini=30, uso='estaleiro (navio pronto)')
    with G('guindastes'): amb(30.3, 35.0, C('Shipyardcrane'), -33, ambiente='ind', ini=estavel(C('Shipyardcrane'), 5, ini=40), eq=hp_(80), uso='guindastes distantes')
    por(33.15, trecho(1523, ataque(1523, -20), 1.3, fi=0.15, fo=0.5, ref=-3, tom=0.8, t=33.15, uso='proa se separando: aço pesado deslizando'), -15, 0.2, 'ind', 0.2)
    por(33.25, trecho(3076, 2.0, 1.4, fi=0.2, fo=0.6, ref=-3, t=33.25, uso='estrutura rangendo no corte'), -22, 0.15, 'ind', 0.2, eq=hp_(80))
    amb(35.0, 41.55, 2504, -30, ambiente='int', envio=0.2, eq=lp_(1800), uso='interior do casco vazio (zumbido distante)')
    sint_sopro(37.0, 1.0, -39, (2500, 7000), nome='células acendendo (brilho sutil)')
    sint_sopro(39.2, 1.0, -40, (2500, 7000), nome='células acendendo (brilho sutil)')
    por(39.6, trecho(3076, 5.2, 1.0, fi=0.05, fo=0.4, ref=-3, t=39.6, uso='estalo térmico no porão vazio'), -30, -0.2, 'int', 0.25, eq=hp_(120))


# ================================================================================================ 41–49 · dique
def dique():
    e = EV['dique']
    amb(41.55, 48.0, C('Adjustingadrydock'), -19, ambiente='dique', ini=estavel(C('Adjustingadrydock'), 7), uso='bombas do dique (fundo)')
    por(e['comporta'] - 0.012, trecho(2982, 1.055, 1.4, fi=0.003, fo=0.5, ref=-1, t=e['comporta'], uso='comporta/válvula abrindo (batida metálica)'), -7, -0.3, 'dique', 0.4)
    por(e['comporta'] - 0.25, trecho(2757, ataque(2757), 0.9, fo=0.3, ref=-1, t=e['comporta'] - 0.25, uso='mecanismo da válvula (destrava)'), -22, -0.3, 'dique', 0.15, eq=lp_(4000))
    sint_grave(e['comporta'], 0.9, 52, 36, -22, -0.3, 'dique', nome='peso da comporta (grande estrutura)')
    # ÁGUA PRINCIPAL: os jatos (uma gravação), que nascem na abertura e perdem força; depois o enchimento, cada vez mais
    # grave e calmo conforme o nível sobe (uma camada), até o casco flutuar
    k = e['jatos_fim'] - e['comporta'] + 0.8; n = int(k * SR); u = tt(n)
    x = laco(3029, k, 4.0, 11.0, xf=0.5, ref=-20, t=e['comporta'], uso='jatos de água entrando no dique (principal)')[:n]
    por(e['comporta'] + 0.12, x * (np.clip(u / 0.2, 0, 1) * np.clip(1 - 0.45 * u / k, 0, 1) * np.clip((k - u) / 0.8, 0, 1))[:, None], -10, -0.25, 'dique', 0.35)
    c0, c1 = 43.2, 48.4; n = int((c1 - c0) * SR); u = tt(n) / (c1 - c0)
    x = laco(2461, c1 - c0, 10.0, 40.0, xf=0.8, ref=-20, t=c0, uso='enchimento do dique: mais grave e calmo conforme o nível sobe')[:n]
    x = (1 - u)[:, None] * lpz(x, 2200, 2) + u[:, None] * lpz(x, 900, 2)
    por(c0, x * (np.clip(u / 0.15, 0, 1) * (1 - 0.6 * u) * np.clip((1 - u) / 0.12, 0, 1))[:, None], -18, -0.2, 'dique', 0.25)
    por(e['picadeiros'] - 0.05, trecho(3076, 6.0, 1.2, fi=0.1, fo=0.5, ref=-3, t=e['picadeiros'], uso='casco deixa os picadeiros (rangido leve)'), -23, 0.0, 'dique', 0.2, eq=hp_(60))
    por(46.5, trecho(1208, 30.0, 1.8, fi=0.4, fo=0.8, norm='rms', ref=-20, t=46.5, uso='casco livre: água em volta (leve)'), -25, 0.2, 'dique', 0.2)


# ================================================================================================ 48–75 · empuxo (explicação subaquática)
def empuxo():
    amb(48.0, 49.3, 1189, -20, ini=40, uso='mar antes do mergulho')
    por(48.95, trecho(2923, ataque(2923), 1.0, fo=0.4, ref=-1, t=49.0, uso='câmera entra na água'), -14, 0.0, 'ext', 0.1)
    por(49.1, trecho(1321, 0, 1.6, fo=0.6, ref=-3, t=49.1, uso='bolhas do mergulho'), -18, 0.0, sub=True)
    for (a, b) in ((49.3, 63.1), (65.8, 74.85)):     # ambiente submerso DISCRETO (uma camada), sem ruído constante forte
        amb(a, b, 1312, -15, ini=20, sub=True, uso='mundo subaquático (discreto)')
    amb(63.1, 65.8, 1189, -22, ini=70, uso='mar (vista do navio inteiro)')
    por(51.0, trecho(3076, 3.0, 2.2, fi=0.4, fo=0.8, ref=-3, t=51.0, uso='casco sob pressão (rangido grave, discreto)'), -22, 0.0, sub=True)
    por(63.25, trecho(1877, 4.0, 2.2, fi=0.4, fo=0.8, norm='rms', ref=-20, t=63.25, uso='água deslocada preenchendo o volume'), -18, 0.0, sub=True)
    # formações gráficas: síntese discreta só nas três que explicam (sem som em cada seta)
    n = int(0.9 * SR)
    for p in (-0.7, 0.7):
        x = S.bp(ruido(n), 250, 1400) * np.sin(np.linspace(0, np.pi, n)) ** 2
        AM.ULTIMO[0] = None; por(58.35, np.stack([x * (1 - 0.5 * (1 + p) * np.linspace(1, 0, n)), x * (1 - 0.5 * (1 - p) * np.linspace(1, 0, n))], 1), -34, 0.0, 'sub', 0.2)
    AM.ULTIMO[0] = None; por(59.8, S.passagem_ar(1.8, 180, 850), -33, 0.0, 'sub', 0.2)
    n = int(1.1 * SR); t_ = tt(n); bloom = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.minimum(t_ / 0.8, 1)) / SR) * np.sin(np.pi * t_ / 1.1) ** 1.5
    AM.ULTIMO[0] = None; por(61.3, bloom + 0.4 * lp(ruido(n), 200) * np.sin(np.pi * t_ / 1.1), -27, 0.0, 'sub', 0.2)
    AM.USOS.append(dict(t=58.35, id='sintese', titulo='formações gráficas do empuxo (3 momentos)', ini=0, dur=4.0, tom=1.0, uso='abstrato, discreto', grupo=None))


# ================================================================================================ 75–95 · retomada e experimento
def retomada():
    e = EV['retomada']
    amb(74.85, 76.2, 1208, -25, ini=20, uso='marulho no cais (retomada)')
    # arrasto segue a velocidade REAL do bloco (cenas/s08a, objeto bloco_anim) até deixar a borda
    tb, vb = MV.velocidade('s08a', 'bloco_anim', 3); a, b = 74.85, e['borda'] + 0.04; n = int((b - a) * SR)
    gv = np.clip(np.interp(a + tt(n), tb, vb) / 1.6, 0, 1) ** 0.6 * np.clip((b - a - tt(n)) / 0.05, 0, 1)
    x = trecho(1523, max(0, ataque(1523, -20) + 0.1), b - a, fi=0.01, fo=0.01, ref=-3, t=a, uso='o mesmo arrasto no cais: segue a velocidade do bloco')
    por(a, x[:n] * gv[:len(x)][:, None], -7, 0.15, 'ext', 0.15)
    x = trecho(809, ataque(809) + 0.2, b - a, fi=0.01, fo=0.01, ref=-3, tom=0.85, t=a, uso='aço raspando (grão), segue a velocidade')
    por(a, x[:n] * gv[:len(x)][:, None], -19, 0.15, 'ext', 0.1, eq=hp_(400))
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, tom=0.95, t=e['borda'], uso='bloco deixa a borda'), -5, 0.15, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 0.9, ref=-6, t=e['borda'], uso='queda'), -21, 0.1)
    por(e['agua'] - 0.02, trecho(2923, ataque(2923), tom=0.85, ref=-1, t=e['agua'], uso='impacto na água (principal)'), -3, 0.1, 'ext', 0.3)
    por(e['agua'], trecho(1304, ataque(1304) + 0.05, 1.4, tom=0.78, fo=0.5, ref=-1, t=e['agua'], uso='corpo do respingo'), -10, -0.1, 'ext', 0.25)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.7, t=e['agua'], uso='peso do aço'), -10, 0.1, eq=lp_(900))
    sint_grave(e['agua'], 1.0, 55, 34, -21, 0.1, nome='peso do bloco (retomada)')
    por(75.9, trecho(1167, 0.5, 1.4, fi=0.5, fo=0.4, ref=-6, tom=0.85, t=75.9, uso='entrada na câmera lenta (sopro, discreto)'), -25, 0.0, eq=lp_(1200))
    amb(76.2, 83.85, 1312, -16, ini=40, sub=True, uso='mundo subaquático em câmera lenta (discreto)')
    # bolhas seguem a descida do bloco (velocidade real em s08a): fortes no início, somem ao pousar
    a, b = 76.3, e['leito']; n = int((b - a) * SR); x = trecho(1178, 2.0, (b - a) * 0.8, fo=0.6, ref=-3, tom=0.8, t=a, uso='bolhas lentas: seguem a descida do bloco')
    gv = np.clip(np.interp(a + tt(len(x)), tb, vb) / 3.0, 0.15, 1); por(a, x * gv[:, None], -13, 0.05, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, tom=0.9, t=e['leito'], uso='bloco toca o leito (tempo volta ao normal)'), -5, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, 1.2, ref=-3, t=e['leito'], uso='sedimento se espalhando (abafado)'), -15, 0.0, sub=True)


def experimento():
    e = EV['experimento']; m = EV['experimento_mov']
    amb(83.85, 88.6, 1201, -23, uso='brisa sobre o mar'); amb(83.85, 88.6, 1189, -21, ini=60, uso='mar (calmo)')
    for p in (-0.4, 0.3): por(e['solto'], trecho(1461, ataque(1461), 0.7, ref=-6, t=e['solto'], uso='queda dos dois objetos'), -24, p)
    # BLOCO: compacto e pesado — respingo curto e denso + peso; depois bolhas que somem conforme ele desce
    por(e['agua'] - 0.01, trecho(1304, ataque(1304), 1.4, fo=0.5, ref=-1, t=e['agua'], uso='bloco entra na água (compacto)'), -6, -0.4, 'ext', 0.2)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.8, t=e['agua'], uso='peso do bloco'), -10, -0.4, eq=lp_(900))
    x = trecho(1178, 6.0, 2.6, fo=1.0, ref=-3, t=e['agua'] + 0.25, uso='bolhas do bloco afundando (somem)')
    por(e['agua'] + 0.25, x * np.linspace(1, 0.2, len(x))[:, None], -16, -0.4, sub=True)
    # CASCO: largo — entrada + água ao longo do costado; o deslocamento segue o MOVIMENTO VERTICAL do casco (arfagem)
    por(e['agua'] + 0.01, trecho(1180, ataque(1180), 1.8, tom=0.85, fo=0.6, ref=-1, t=e['agua'], uso='casco entra na água (largo)'), -7, 0.35, 'ext', 0.2)
    por(e['agua'] + 0.05, trecho(1198, ataque(1198), ref=-1, t=e['agua'], uso='água espirrando ao longo do casco'), -14, 0.45, 'ext', 0.15)
    sint_grave(e['agua'] + 0.02, 1.2, 46, 32, -25, 0.35, nome='casco largo: massa de água deslocada')
    tg = np.array(m['t']); vz = np.abs(np.gradient(np.array(m['navio']['z'])) * 30)
    a, b = e['agua'] + 0.1, 94.55; n = int((b - a) * SR); gv = np.clip(np.interp(a + tt(n), tg, np.convolve(vz, np.ones(9) / 9, 'same')) / 1.2, 0, 1) ** 0.8
    x = laco(1195, b - a, 2.0, 30.0, xf=0.6, ref=-20, t=a, uso='água deslocada pelo casco: segue a arfagem e diminui até parar')[:n]
    por(a, x * gv[:, None], -12, 0.3, 'ext', 0.15)
    z = np.array(m['navio']['z']); vzz = np.gradient(z)
    ext = [tg[i] for i in range(1, len(vzz) - 1) if tg[i] > e['agua'] + 0.4 and np.sign(vzz[i]) != np.sign(vzz[i - 1])]
    for k, t0 in enumerate(ext[:3]):           # batidas a cada inversão do balanço, cada vez mais fracas
        por(t0, trecho(1208, 10.0 + 3 * k, 1.2, fi=0.05, fo=0.5, norm='rms', ref=-20, t=t0, uso='água batendo no casco a cada balanço'), -15 - 5 * k, 0.3)
    amb(88.6, 94.55, 1205, -27, sub=True, uso='vista submersa do experimento (discreta)')
    amb(88.6, 94.55, 1189, -27, ini=90, uso='mar (vista aérea, longe)')


# ================================================================================================ 94–134 · porto, carregamento, calado, marcas
def porto():
    m = EV['porto_mov']; tg = np.array(m['t'])
    def vel(nome, vmax): v = np.array(m[nome]['v']); v[v > 12] = 0; return np.clip(v / vmax, 0, 1)
    a, b = 94.55, 117.2
    amb(94.55, 134.0, C('ContainerTerminalatthePortofDortmund'), -20, ambiente='porto', envio=0.1, ini=estavel(C('ContainerTerminalatthePortofDortmund'), 40), uso='ambiente de porto (fundo)')
    amb(94.55, 117.2, C('Containerreachstackers'), -30, ambiente='porto', ini=estavel(C('Containerreachstackers'), 20), eq=lp_(2500), uso='veículos do pátio ao fundo')
    amb(94.55, 134.0, 1208, -29, ini=40, uso='água junto ao cais (leve)')
    # PORTÊINER principal: carro (translação) + spreader (içamento) → um motor que segue velocidade e aceleração reais;
    # silencioso quando parado; perspectiva pela distância da câmera ao carro
    vc = vel('carro_anc5', 4.0); zs = np.array(m['spreader_anc5']['z']); vz = np.abs(np.gradient(zs) * 30); vz[vz > 12] = 0
    mov = np.clip(np.maximum(vc, np.clip(vz / 5.0, 0, 1)), 0, 1)
    persp5 = (*MV.distancia('s09', 'carro_anc5'), 45, 0.6, -15)
    with G('guindastes'):
        motor(C('Containershipgantrycrane'), a, b, tg, mov, -12, 0.0, 'porto', 0.15, 0.95, 1.06, 0.6, persp5, eq=hp_(60),
              uso='portêiner: motores do carro e do guincho seguem o movimento (param quando ele para)')
        vv = np.maximum(vel('carro_anc3', 4.0), vel('carro_anc7', 4.0))
        motor(C('Mobileharbourcrane'), a, b, tg, vv, -25, 0.4, 'porto', 0.1, 0.97, 1.04, 0.3, (*MV.distancia('s09', 'carro_anc3'), 60, 0.6, -15), eq=lp_(3000),
              uso='portêineres vizinhos (mais distantes, só em movimento)')
        # cabos tensionados: rangido discreto quando o spreader arranca/freia com carga (aceleração vertical forte), no máx. 3
        acz = np.abs(np.gradient(np.convolve(vz, np.ones(7) / 7, 'same'))); pk = [tg[i] for i in range(1, len(acz) - 1) if a < tg[i] < 105 and acz[i] > 0.25 and acz[i] >= acz[i - 1] and acz[i] >= acz[i + 1]]
        ult = -9; k = 0
        for t0 in pk:
            if t0 - ult > 2.0 and k < 3 and all(abs(t0 - p) > 0.6 for p in EV['pousos']):
                por(t0, trecho(3076, 0.5 + 1.3 * k, 0.8, fi=0.08, fo=0.4, ref=-3, t=t0, uso='cabos tensionando (arrancada/frenagem do spreader)'), -25, 0.0, 'porto', 0.15, eq=hp_(150)); ult = t0; k += 1
    # POUSOS dos 3 contêineres do plano próximo: contato no encaixe + vibração curta da caixa (sem pancada grave longa)
    for i, t0 in enumerate(EV['pousos']):
        pan = (-0.1, -0.3, 0.3)[i]
        por(t0 - 0.01, trecho(2754, 0.79, 0.6, fi=0.003, fo=0.3, ref=-1, t=t0, uso='contêiner encaixa (contato metálico)'), -8, pan, 'porto', 0.15)
        por(t0 + 0.03, trecho(3158, 0.2, 0.45, fi=0.01, fo=0.3, ref=-1, t=t0 + 0.03, uso='vibração curta da caixa após o encaixe'), -24, pan, 'porto', 0.1, eq=lp_(3500))
    # tempo acelerado: sem som por contêiner — o ambiente do porto um pouco mais ativo + 3 contatos distantes
    amb(105.45, 117.2, C('ContainerTerminalatthePortofDortmund'), -24, ambiente='porto', ini=estavel(C('ContainerTerminalatthePortofDortmund'), 12, ini=100), uso='porto em atividade (tempo acelerado)')
    for k, t0 in enumerate((107.3, 110.1, 113.4)):
        por(t0, trecho(2983, ataque(2983), 0.9, fo=0.4, ref=-1, t=t0, uso='contato distante de contêiner'), -27, (-0.5, 0.4, -0.2)[k], 'porto', 0.2, eq=lp_(2000))
    # água junto ao casco: segue a velocidade com que o navio afunda com a carga (nada quando ele está parado)
    zn = np.array(m['navio']['z']); vzn = np.convolve(np.abs(np.gradient(zn) * 30), np.ones(15) / 15, 'same')
    tc, gc = controle(tg, np.clip(vzn / 0.25, 0, 1), a, b); g2 = seguir(gc, 0.4, 0.8); n = int((b - a) * SR)
    x = laco(H._r(C('Smallwaves')), b - a, 20.0, 80.0, xf=0.8, ref=-20, t=a, uso='água no casco enquanto o navio afunda com a carga')[:n]
    por(a, x * (0.15 + 0.85 * p_amostra(tc, g2, a, n))[:, None], -21, 0.2, 'porto', 0.1)
    amb(117.2, 134.0, C('Smallwaves'), -26, ambiente='porto', ini=30, uso='água no casco (calado e marcas, leve)')
    por(118.9, trecho(1208, 50.0, 2.0, fi=0.3, fo=0.8, norm='rms', ref=-20, t=118.9, uso='cota do calado sobe (marulho junto à quilha)'), -26, 0.1)
    sint_sopro(130.4, 2.6, -39, (1800, 6000), nome='marcas acendendo (um único brilho sutil)')


# ================================================================================================ 134–155 · avaria e inundação
def avaria():
    e = EV['avaria']
    amb(134.0, 137.0, 1189, -20, ini=90, uso='mar (exterior do casco)')
    por(e['rasgo'] + 0.055, trecho(2980, ataque(2980), ref=-1, t=e['rasgo'], uso='ruptura: impacto metálico localizado'), -4, 0.2, 'ext', 0.15)
    por(e['rasgo'] + 0.075, trecho(200, 0.0, 1.0, fo=0.4, ref=-1, t=e['rasgo'], uso='ruptura: aço rasgando'), -10, 0.2, 'ext', 0.15)
    sint_grave(e['rasgo'] + 0.05, 0.6, 70, 45, -24, 0.2, nome='ruptura (peso)')
    por(e['bolhas'][0], trecho(1877, 1.0, 1.8, fi=0.15, fo=0.5, norm='rms', ref=-20, t=e['bolhas'][0], uso='bolhas sugadas pelo rombo'), -13, 0.2, sub=True)
    # ÁGUA PRINCIPAL da inundação: o JATO sob pressão (uma gravação) — nasce na entrada da água, mantém-se enquanto o rombo
    # está livre e perde força quando ele é coberto; dentro do porão, reverberação de aço contida
    a, b = e['jato']; n = int((b - a) * SR); k = tt(n)
    intens = np.clip(k / 0.35, 0, 1) * np.where(a + k < 143.5, 1.0, np.clip(1 - (a + k - 143.5) / 3.0, 0.1, 1))
    x = laco(3029, b - a, 4.0, 11.0, xf=0.8, ref=-20, t=a, uso='jato de água sob pressão entrando pelo rombo (principal)')[:n]
    por(a, x * intens[:, None], -9, 0.15, 'int', 0.3)
    # SEGUNDA camada só onde a imagem pede: o porão enchendo (cresce com o nível e se acalma quando o jato perde força)
    c0, c1 = e['enche']; n = int((c1 - c0 + 1.5) * SR); u = tt(n) / (c1 - c0)
    nivel = np.clip(u, 0, 1) ** 1.5 * np.clip((c1 - c0 + 1.5 - tt(n)) / 1.5, 0, 1)
    x = laco(2461, c1 - c0 + 1.5, 5.0, 60.0, xf=1.0, ref=-20, t=c0, uso='porão enchendo (cresce com o nível)')[:n]
    por(c0, lpz(x, 2500, 2) * nivel[:, None], -18, 0.0, 'int', 0.3)
    for t0, i, p in ((137.6, 1198, -0.4), (139.6, 1311, 0.3), (142.2, 3216, -0.3)):   # 3 golpes (eram 5)
        por(t0, trecho(i, ataque(i), 1.0, fo=0.4, ref=-1, t=t0, uso='água golpeando anteparas'), -15, p, 'int', 0.3)
    for k_, (t0, ini, g) in enumerate(((139.5, 0.6, -16), (142.3, 2.4, -15), (146.8, 5.6, -14), (149.7, 3.3, -15))):   # 4 rangidos (eram 6)
        por(t0, trecho(3076, ini, 1.4, fo=0.5, ref=-3, t=t0, uso='casco rangendo sob a carga'), g, (-0.4, 0.3, -0.2, 0.2)[k_], 'int', 0.3, eq=hp_(45))
    # tensão que cresce com a inundação e ALIVIA com a explicação das divisórias (cai a partir de 150,6 s, some em 154,6)
    t0, t1 = 137.0, 155.0; n = int((t1 - t0) * SR); g = t0 + tt(n)
    nivel = np.interp(g, [137, 146, 147.9, 150.6, 151.05, 152.5, 154.6], [0.12, 0.55, 0.9, 0.9, 0.6, 0.25, 0.0])
    x = laco(2509, t1 - t0, 0.0, 20.0, xf=1.0, ref=-20, t=t0, uso='tensão grave da inundação (alivia nas divisórias)')[:n]
    por(t0, x * nivel[:, None], -14, 0.0, 'int', 0.15)
    por(e['divisorias'] - 0.012, trecho(2982, 1.055, 1.4, fi=0.003, fo=0.5, ref=-1, t=e['divisorias'], uso='divisórias estanques: batida firme e calma'), -10, 0.0, 'int', 0.2)


# ================================================================================================ 154–168 · conclusão
def conclusao():
    e = EV['conclusao']
    amb(154.6, 156.4, 1189, -20, ini=120, uso='mar (bloco de 17 m sobre a água)')
    amb(154.6, 156.4, 1201, -26, ini=10, uso='brisa')
    por(e['solto'], trecho(1471, ataque(1471) - 0.1, ref=-4, t=e['solto'], uso='queda do bloco de 17 m (ar deslocado)'), -22, 0.25)
    # IMPACTO com escala (mantido forte), sem camadas de água a mais
    por(e['agua'] - 0.02, trecho(1180, ataque(1180), 2.4, tom=0.7, fo=0.8, ref=-1, t=e['agua'], uso='bloco de 17 m entra na água (massa)'), -4, 0.2, 'ext', 0.2)
    por(e['agua'], trecho(1304, ataque(1304), 1.8, tom=0.75, fo=0.6, ref=-1, t=e['agua'], uso='respingo largo'), -10, 0.3, 'ext', 0.2)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.65, t=e['agua'], uso='peso do aço'), -10, 0.25, eq=lp_(800))
    sint_grave(e['agua'], 1.6, 50, 30, -18, 0.25, nome='escala do bloco de 17 m')
    amb(156.4, 164.35, 1312, -18, ini=10, sub=True, uso='debaixo d\'água (discreto)')
    # bolhas seguem a descida real do bloco (cenas/s13, cubo_fim)
    tb, vb = MV.velocidade('s13', 'cubo_fim'); a = e['agua'] + 0.4; b = 160.5; n = int((b - a) * SR)
    x = trecho(1178, 0.5, b - a, fo=1.0, ref=-3, tom=0.85, t=a, uso='bolhas da descida do bloco (seguem a velocidade)')
    por(a, x * np.clip(np.interp(a + tt(len(x)), tb, vb) / (vb.max() + 1e-6), 0.1, 1)[:, None] ** 0.7, -12, 0.25, sub=True)
    sint_sopro(159.6, 1.4, -34, (150, 900), sub=True, nome='volume deslocado sob o casco (textura sutil)')
    n = int(1.0 * SR); y = np.sin(2 * np.pi * np.cumsum(np.linspace(60, 82, n)) / SR) * np.sin(np.linspace(0, np.pi, n)) ** 2
    AM.ULTIMO[0] = None; por(161.4, y, -32, 0.0, 'sub', 0.2); AM.USOS.append(dict(t=161.4, id='sintese', titulo='peso = empuxo (pulso grave sutil)', ini=0, dur=1.0, tom=1.0, uso='gráfico', grupo=None))
    # plano final: o navio no mar, com espaço (vento e ondas discretos); sem whoosh de saída
    amb(164.35, 168.0, 1189, -18, ini=30, uso='mar aberto (plano final)', pos=0.0)
    amb(164.35, 168.0, C('Smallwaves'), -25, ini=10, uso='água no casco (leve)', pos=0.0)
    amb(164.35, 168.0, 1201, -25, ini=30, uso='vento (espaço)', pos=0.0)
    # mesma buzina, mais distante e discreta: entra DEPOIS da última palavra ("navio." termina em 166,12 s), toque curto
    # que se dissipa sozinho (corte real + eco) antes de 168 s, junto com a resolução da trilha
    if BUZINA: buzina(166.25, 0.25, BUZ_DB[1], (*MV.distancia('s13', 'navio'), 150, 0.35, -10, 0.0, 1200), 0.45, extra_lp=2500, rel=1.15, compensa_fim=True,
                      uso='buzina distante no plano final (despedida, após "navio.")')


if __name__ == '__main__':
    for f, g in ((abertura, None), (estaleiro, 'estaleiro'), (navio_corte, 'estaleiro'), (dique, 'dique'), (empuxo, None), (retomada, None),
                 (experimento, None), (porto, 'porto'), (avaria, 'inundacao'), (conclusao, None)):
        with G(g): f()
    SE.musica()
    ref = json.load(open(os.path.join(SE.A, 'mix_hibrido.json')))
    P = dict(efeitos_rel=-3.5, amb_rel=-12.5, duck_alvo=-13.0, duck_piso=-18.0, duck_grave=-3.0, musica_rel=-16.0, duck_amb_max=-9.0,   # mesmo ducking moderado
             ganhos_fixos_db=ref['ganhos_stem_db'])                                                                                 # mesmos ganhos absolutos
    suf = os.environ.get('SUFIXO_REFINADO', '')
    if os.environ.get('MASTER_DE'):   # A/B: herda o ganho de master da versão sem buzina (sem renormalizar por versão)
        P['master_fixo_db'] = json.load(open(os.path.join(SE.A, os.environ['MASTER_DE'])))['master_db']
    res = SE.mixar(saida=f'audio_ep01_refinado{suf}.wav', stems_dir='stems', sufixo=f'_refinado{suf}', relatorio=f'mix_refinado{suf}.json', **P)
    res['parametros_mix'] = P; json.dump(res, open(os.path.join(SE.A, f'mix_refinado{suf}.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(AM.USOS, open(os.path.join(SE.A, f'usos_refinado{suf}.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(AM.USOS), 'usos registrados; reservas:', H.TROCAS)
