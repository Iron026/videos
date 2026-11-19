"""Sound design com GRAVAÇÕES REAIS (Mixkit, Sound Effects Free License) para os trechos de validação:
0–15 s (abertura), 15–30 s (estaleiro e solda), 48–95 s (empuxo, retomada, experimento) e 134–155 s (avaria).
Mesma narração, mesma trilha e MESMA mixagem (som_ep01.mixar: reverberação por ambiente, ducking, master) da versão
sintética — só os efeitos físicos e as ambiências mudam. Síntese só nas formações gráficas do empuxo (abstratas).
Saídas: audio_ep01_real.wav, stems/ep01_*_real.wav, som/mix_real.json, som/usos_real.json."""
import os, sys, json, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import som_ep01 as SE
import amostras as AM
from amostras import trecho, laco, ataque
from sintese import SR, lpz, hpz, n_, tt, ruido, lp
import sintese as S

EV = SE.EV; N = SE.N
TRECHOS = [(0.0, 15.1), (15.1, 30.3), (48.0, 95.0), (134.0, 155.0)]


def por(t, x, dB, pan=0.0, amb='ext', envio=0.25, stem='efeitos', sub=False, eq=None):
    if eq: x = eq(x)
    SE.por(t, x, dB, pan, amb, envio, stem, sub)


def cama(t0, t1, i, dB, ini=0.0, fim=None, amb='ext', envio=0.15, sub=False, fade=0.6, eq=None, uso=''):
    """Ambiência contínua real entre t0 e t1 (emendas por fusão), com entrada e saída suaves."""
    x = laco(i, t1 - t0 + 0.2, ini, fim, xf=0.8, ref=-20, t=t0, uso=uso); n = len(x); k = int(fade * SR)
    x[:k] *= np.linspace(0, 1, k)[:, None]; x[-k:] *= np.linspace(1, 0, k)[:, None]
    por(t0, x, dB, 0.0, amb, envio, 'ambiencias', sub, eq)


def hp_(f): return lambda x: hpz(x, f, 2)
def lp_(f): return lambda x: lpz(x, f, 2)


# ================================================================================================ 0–15 · abertura
def abertura():
    e = EV['abertura']
    cama(0.0, 2.85, 1208, -22, ini=3.0, uso='marulho no cais (pedras do porto)')
    cama(0.0, 2.85, 1191, -27, uso='mar distante')
    a = ataque(2927)
    por(e['empurrao'], trecho(2927, a, e['borda'] - e['empurrao'] + 0.25, fo=0.15, ref=-3, t=e['empurrao'], uso='aço arrastado no concreto (tampa de bueiro de ferro)'), -6, 0.15, 'ext', 0.25)
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, t=e['borda'], uso='baque grave quando o bloco tomba na borda'), -4, 0.15, 'ext', 0.3, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 1.2, ref=-6, t=e['borda'], uso='ar deslocado na queda'), -16, 0.1)
    # impacto (em câmera lenta 0,35×: gravações levemente mais graves/lentas, sem exagero)
    por(e['agua'] - 0.02, trecho(1304, ataque(1304), 1.9, tom=0.8, ref=-1, t=e['agua'], uso='impacto do bloco na água (camada principal, câmera lenta)'), -5, 0.1, 'ext', 0.3)
    por(e['agua'] + 0.01, trecho(1180, ataque(1180), 2.2, tom=0.72, ref=-1, t=e['agua'], uso='lençol e retorno da água (camada de corpo)'), -8, -0.15, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.75, t=e['agua'], uso='peso do aço no impacto (baque grave)'), -9, 0.1, eq=lp_(900))
    por(e['agua'] + 0.1, trecho(1178, 0.0, 1.7, ref=-3, t=e['agua'], uso='bolhas e afundamento (ouvido debaixo d\'água)'), -10, 0.0, sub=True)
    por(e['agua'] + 0.25, trecho(1321, 0, ref=-3, t=e['agua'] + 0.25, uso='bolhas profundas'), -14, 0.05, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, t=e['leito'], uso='bloco toca o leito de areia'), -6, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, ref=-3, t=e['leito'], uso='sedimento levantado (abafado)'), -14, 0.0, sub=True)
    # o gigante no mar
    por(4.30, trecho(1471, ataque(1471) - 0.1, ref=-4, t=4.3, uso='rajada no corte para o mar aberto'), -17)
    cama(4.4, 15.1, 1189, -14, ini=10, uso='mar aberto (ondas)')
    cama(4.4, 15.1, 1200, -21, uso='vento sobre o mar')
    cama(4.4, 15.1, 3077, -23, amb='ext', eq=lp_(600), uso='máquinas do navio (distante)')
    por(7.9, trecho(3078, 0, 5.0, ref=-3, t=7.9, uso='casco/máquinas passando (travelling)'), -15, -0.3, eq=lp_(1500))
    n = int(4.6 * SR); x = trecho(2461, 3.0, 4.6, fi=0.8, fo=1.2, norm='rms', ref=-20, t=9.0, uso='água empurrada pela proa (onda de proa)')
    por(9.0, x * np.sin(np.linspace(0, np.pi, len(x)))[:, None] ** 0.8, -6, 0.25)
    por(10.9, trecho(1195, 6.0, 2.6, fi=0.3, fo=0.8, norm='rms', ref=-20, t=10.9, uso='espuma e borrifo da proa'), -10, 0.3)
    por(13.3, trecho(1195, 12.0, 1.8, fi=0.2, fo=1.2, norm='rms', ref=-20, t=13.3, uso='esteira se afastando'), -14, -0.4)


# ================================================================================================ 15–30 · estaleiro
def estaleiro():
    cama(15.1, 30.3, 3074, -15, amb='ind', envio=0.2, uso='ambiente de estaleiro (galpão de construção naval)')
    cama(15.1, 30.3, 803, -24, amb='ind', uso='máquinas de obra ao fundo')
    m = EV['estaleiro_mov']; tg = np.array(m['t'])
    v = np.clip(np.array(m['carro']['v']) / 3.05, 0, 1); v = np.convolve(v, np.ones(9) / 9, 'same')
    a, b = 15.1, 30.3; n = int((b - a) * SR); vs = np.interp(a + tt(n), tg, v)
    mot = laco(1619, b - a, 0.3, 3.8, xf=0.4, ref=-20, t=15.17, uso='motor do carro do pórtico (segue a velocidade real)')[:n]
    por(a, mot * (vs ** 0.7)[:, None], -12, -0.2, 'ind', 0.4)
    rod = laco(1534, b - a, 0.1, 2.3, xf=0.3, ref=-20, t=15.17, uso='rodas do carro rolando no trilho')[:n]
    por(a, rod * vs[:, None], -17, -0.2, 'ind', 0.4)
    vg = np.clip(np.array(m['grupo_carga']['v']) / 3.97, 0, 1); acel = np.abs(np.gradient(np.convolve(vg, np.ones(5) / 5, 'same')))
    picos = [tg[i] for i in range(1, len(acel) - 1) if acel[i] > 0.02 and acel[i] >= acel[i - 1] and acel[i] >= acel[i + 1]]
    ult = -9; k = 0
    for t0 in picos:
        if t0 - ult > 1.2:
            por(t0, trecho(3076, 1.0 + 1.6 * (k % 4), 1.4, fo=0.4, ref=-3, t=t0, uso='cabos e estrutura rangendo na arrancada/freada'), -15, 0.1, 'ind', 0.5, eq=hp_(60)); ult = t0; k += 1
    # ENCAIXE da chapa (23,60 s): batida pesada de aço + eco do galpão
    por(23.58, trecho(201, ataque(201, -6) - 0.03, ref=-1, t=23.6, uso='encaixe da chapa no casco (porta de aço pesada fechando)'), -2, 0.0, 'ind', 0.55)
    por(23.60, trecho(2980, ataque(2980), ref=-1, t=23.6, uso='contato metálico duro (camada aguda)'), -9, 0.1, 'ind', 0.5)
    # solda: gravação real de arco + faíscas, só nos cordões, com o brilho do shader como envelope suave (±4 dB)
    def tremor(g, sem, tr=0.5):
        q = np.floor(g * 30 + 0.5).astype(np.float32)
        def h(x): return np.mod(np.sin(x * np.float32(12.9898) + np.float32(sem * 78.233)).astype(np.float32) * np.float32(43758.5453), 1.0)
        return 1 - tr + tr * (0.6 * h(q) + 0.4 * h(q * np.float32(0.5) + np.float32(3.1)))
    for (ta, tb), sem, g_, p_, ini in (((23.75, 24.55), 0.25, -8, 0.1, 0.6), ((24.68, 25.25), 1.25, -8, 0.1, 3.2), ((24.0, 24.7), 3.25, -15, 0.3, 5.0), ((24.85, 25.4), 4.25, -15, 0.3, 1.8)):
        x = trecho(2603, ini, tb - ta + 0.1, fi=0.02, fo=0.08, norm='rms', ref=-20, t=ta, uso='arco elétrico de solda e faíscas (gravação real)')
        env = tremor(ta + tt(len(x)), sem).astype(float); env = 10 ** ((env - 1) * 4 / 20 / 0.5)   # ±4 dB em torno do nível
        por(ta, x * env[:, None], g_, p_, 'ind', 0.3)
    for t0, i in ((24.9, 812), (25.1, 814)):
        por(t0, trecho(i, ataque(i), ref=-3, t=t0, uso='solda ao fundo (bojo)'), -16, -0.35, 'ind', 0.4)
    # chapas chegando: poucos contatos selecionados, sem um som para cada uma
    ch = EV['chapas']; sel = [ch[0], ch[len(ch) // 4], ch[len(ch) // 2], ch[3 * len(ch) // 4], ch[-1]]
    for k, (t0, i) in enumerate(zip(sel, (2754, 3158, 2980, 2754, 201))):
        por(t0, trecho(i, ataque(i, -6) - 0.03 if i == 201 else ataque(i), ref=-1, t=t0, uso='chapas chegando ao costado e à proa (contatos selecionados)'), -10 - 2 * (k % 2), (-0.4, 0.3, -0.2, 0.4, 0.0)[k], 'ind', 0.55)


# ================================================================================================ 48–95 · empuxo, retomada, experimento
def empuxo():
    cama(48.0, 49.3, 1189, -14, uso='mar (antes do mergulho)')
    por(48.95, trecho(2923, ataque(2923), ref=-1, t=49.0, uso='câmera entra na água'), -10, 0.0)
    por(49.1, trecho(1321, 0, ref=-3, t=49.1, uso='bolhas do mergulho'), -12, 0.0, sub=True)
    for (a, b) in ((49.3, 63.1), (65.8, 74.85)):
        cama(a, b, 1312, -10, ini=20, sub=True, uso='mundo subaquático (pressão grave)')
        cama(a, b, 1205, -20, sub=True, uso='ambiente submarino')
    cama(63.1, 65.8, 1189, -18, uso='mar (vista do navio inteiro)')
    por(51.0, trecho(3076, 3.0, 2.5, fi=0.4, fo=0.8, ref=-3, t=51.0, uso='casco sob pressão (rangido grave, discreto)'), -18, 0.0, sub=True)
    por(63.2, trecho(1877, 4.0, 2.4, fi=0.4, fo=0.8, norm='rms', ref=-20, t=63.2, uso='água deslocada enchendo o volume'), -12, 0.0, sub=True)
    # formações GRÁFICAS (abstratas): síntese discreta, só onde ajuda a leitura
    n = int(0.9 * SR)
    for p in (-0.7, 0.7):
        x = S.bp(ruido(n), 250, 1400) * np.sin(np.linspace(0, np.pi, n)) ** 2
        por(58.35, np.stack([x * (1 - 0.5 * (1 + p) * np.linspace(1, 0, n)), x * (1 - 0.5 * (1 - p) * np.linspace(1, 0, n))], 1), -31, 0.0, 'sub', 0.3)
    por(59.8, S.passagem_ar(1.8, 180, 850), -29, 0.0, 'sub', 0.4)
    n = int(1.1 * SR); t_ = tt(n); bloom = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.minimum(t_ / 0.8, 1)) / SR) * np.sin(np.pi * t_ / 1.1) ** 1.5
    por(61.3, bloom + 0.4 * lp(ruido(n), 200) * np.sin(np.pi * t_ / 1.1), -23, 0.0, 'sub', 0.4)
    AM.USOS.append(dict(t=58.35, id='sintese', titulo='formação gráfica do empuxo (laterais se anulam, convergência, empuxo)', ini=0, dur=4.0, tom=1.0, uso='abstrato'))


def retomada():
    e = EV['retomada']
    cama(74.85, 76.25, 1208, -22, ini=20, uso='marulho no cais (retomada)')
    a = ataque(2927, ini=0.25)
    por(74.85, trecho(2927, a, e['borda'] - 74.85 + 0.25, fo=0.15, ref=-3, t=74.85, uso='o mesmo arrasto no cais (outro trecho da gravação)'), -6, 0.15, 'ext', 0.25)
    por(e['borda'] - 0.03, trecho(752, 0, ref=-1, tom=0.95, t=e['borda'], uso='bloco deixa a borda'), -5, 0.15, eq=lp_(2500))
    por(e['borda'], trecho(1461, ataque(1461), 1.0, ref=-6, t=e['borda'], uso='queda'), -17, 0.1)
    por(e['agua'] - 0.02, trecho(2923, ataque(2923), tom=0.85, ref=-1, t=e['agua'], uso='impacto na água (variação da abertura)'), -3, 0.1, 'ext', 0.3)
    por(e['agua'], trecho(1304, ataque(1304) + 0.05, 1.6, tom=0.78, ref=-1, t=e['agua'], uso='corpo do respingo'), -9, -0.1, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.7, t=e['agua'], uso='peso do aço'), -10, 0.1, eq=lp_(900))
    por(75.9, trecho(1167, 0.5, 1.4, fi=0.5, fo=0.4, ref=-6, tom=0.85, t=75.9, uso='transição para a câmera lenta'), -22, 0.0, eq=lp_(1200))
    cama(76.2, 83.85, 1312, -9, ini=40, sub=True, uso='mundo subaquático em câmera lenta')
    por(76.3, trecho(1178, 2.0, 5.6, fo=0.8, ref=-3, tom=0.8, t=76.3, uso='bolhas lentas do bloco (câmera lenta)'), -10, 0.05, sub=True)
    por(e['leito'], trecho(2498, ataque(2498), ref=-1, tom=0.9, t=e['leito'], uso='bloco toca o leito (tempo volta ao normal)'), -4, 0.0, sub=True)
    por(e['leito'] + 0.03, trecho(753, 0, ref=-3, t=e['leito'], uso='sedimento se espalhando (abafado)'), -11, 0.0, sub=True)


def experimento():
    e = EV['experimento']; m = EV['experimento_mov']
    cama(83.85, 95.0, 1201, -19, uso='brisa sobre o mar')
    cama(83.85, 95.0, 1189, -17, ini=60, uso='mar')
    for p in (-0.4, 0.3): por(e['solto'], trecho(1461, ataque(1461), 0.8, ref=-6, t=e['solto'], uso='queda dos dois objetos'), -20, p)
    # BLOCO: compacto e pesado — respingo curto e denso + baque, depois afunda borbulhando
    por(e['agua'] - 0.01, trecho(1304, ataque(1304), 1.6, ref=-1, t=e['agua'], uso='bloco entra na água (compacto, pesado)'), -6, -0.4, 'ext', 0.3)
    por(e['agua'], trecho(752, 0, ref=-1, tom=0.8, t=e['agua'], uso='peso do bloco'), -9, -0.4, eq=lp_(900))
    por(e['agua'] + 0.25, trecho(1178, 6.0, 3.5, fo=1.0, ref=-3, t=e['agua'] + 0.25, uso='bloco afundando (bolhas, abafado)'), -12, -0.4, sub=True)
    # CASCO: largo e oco — grande massa de água deslocada, onda que se espalha, e balanço até parar
    por(e['agua'] + 0.01, trecho(1180, ataque(1180), tom=0.85, ref=-1, t=e['agua'], uso='casco entra na água (largo)'), -6, 0.35, 'ext', 0.35)
    por(e['agua'] + 0.05, trecho(1198, ataque(1198), ref=-1, t=e['agua'], uso='água espirrando ao longo do casco'), -9, 0.45, 'ext', 0.3)
    por(e['agua'] + 0.1, trecho(1195, 2.0, 2.4, fi=0.2, fo=1.0, norm='rms', ref=-20, t=e['agua'] + 0.1, uso='onda de deslocamento do casco'), -4, 0.3)
    tg = np.array(m['t']); z = np.array(m['navio']['z']); vz = np.gradient(z)
    ext = [tg[i] for i in range(1, len(vz) - 1) if tg[i] > e['agua'] + 0.4 and np.sign(vz[i]) != np.sign(vz[i - 1])]
    for k, t0 in enumerate(ext[:4]):
        por(t0, trecho(1208, 10.0 + 3 * k, 1.4, fi=0.05, fo=0.6, norm='rms', ref=-20, t=t0, uso='água batendo no casco a cada balanço'), -9 - 4 * k, 0.3)


# ================================================================================================ 134–155 · avaria
def avaria():
    e = EV['avaria']
    cama(134.0, 137.0, 1189, -15, ini=90, uso='mar (exterior do casco)')
    por(e['rasgo'] + 0.055, trecho(2980, ataque(2980), ref=-1, t=e['rasgo'], uso='ruptura: impacto metálico localizado'), -3, 0.2, 'ext', 0.25)
    por(e['rasgo'] + 0.075, trecho(200, 0.0, 1.2, fo=0.4, ref=-1, t=e['rasgo'], uso='ruptura: aço rasgando/raspando'), -8, 0.2, 'ext', 0.25)
    por(e['bolhas'][0], trecho(1877, 1.0, 2.0, fi=0.2, fo=0.5, norm='rms', ref=-20, t=e['bolhas'][0], uso='bolhas sugadas pelo rombo'), -8, 0.2, sub=True)
    por(e['bolhas'][0] + 0.3, trecho(1321, 0, ref=-3, t=e['bolhas'][0] + 0.3, uso='bolhas'), -13, 0.2, sub=True)
    # dentro do porão: compartimento de aço (reverberação 'int')
    a, b = e['jato']; n = int((b - a) * SR); k = tt(n)
    intens = np.clip(k / 0.5, 0, 1) * np.where(a + k < 143.5, 1.0, np.clip(1 - (a + k - 143.5) / 3.0, 0.12, 1))
    jato = laco(3029, b - a, 4.0, 11.0, xf=0.8, ref=-20, t=a, uso='água sob pressão entrando pelo rombo (cascata forte)')[:n]
    por(a, jato * intens[:, None], -6, 0.15, 'int', 0.5)
    jato2 = laco(3140, b - a, 2.0, 27.0, xf=0.8, ref=-20, t=a, uso='jorro despejando no porão')[:n]
    por(a, jato2 * intens[:, None], -12, -0.1, 'int', 0.55)
    c0, c1 = 137.2, 147.8; n = int((c1 - c0) * SR); k = tt(n) / (c1 - c0)
    ench = laco(2461, c1 - c0, 5.0, 60.0, xf=1.0, ref=-20, t=c0, uso='turbulência do porão enchendo')[:n]
    por(c0, ench * (np.clip(k, 0, 1) ** 0.7 * np.clip((1 - k) / 0.15, 0, 1))[:, None], -11, 0.0, 'int', 0.6, eq=lp_(3000))
    gurg = laco(1877, c1 - c0, 6.0, 27.0, xf=0.8, ref=-20, t=c0, uso='borbulhar e gorgolejo da água subindo')[:n]
    por(c0, gurg * (np.clip(k * 1.5, 0, 1) * np.clip((1 - k) / 0.2, 0, 1))[:, None], -15, 0.0, 'int', 0.5)
    for t0, i, p in ((137.6, 1198, -0.4), (138.5, 3216, 0.5), (139.6, 1311, -0.2), (140.9, 1198, 0.4), (142.2, 3216, -0.5)):
        por(t0, trecho(i, ataque(i), ref=-1, t=t0, uso='água golpeando anteparas e piso'), -11, p, 'int', 0.6)
    for k_, (t0, ini, g) in enumerate(((139.5, 0.6, -13), (142.3, 2.4, -12), (144.9, 4.2, -11), (146.8, 5.6, -10), (148.4, 1.5, -10), (149.7, 3.3, -11))):
        por(t0, trecho(3076, ini, 1.6, fo=0.5, ref=-3, t=t0, uso='casco rangendo sob a carga crescente'), g, (-0.4, 0.3, -0.2, 0.4, -0.3, 0.2)[k_], 'int', 0.6, eq=hp_(45))
    # tensão que cresce com a inundação e alivia depois das divisórias estanques (cama industrial grave, real)
    t0, t1 = 137.0, 155.0; n = int((t1 - t0) * SR); g = t0 + tt(n)
    nivel = np.interp(g, [137, 146, 147.9, 150.6, 151.05, 154.6], [0.15, 0.6, 1.0, 1.0, 0.8, 0.0])
    ten = laco(2509, t1 - t0, 0.0, 20.0, xf=1.0, ref=-20, t=t0, uso='tensão grave crescente (alivia após as divisórias)')[:n]
    por(t0, ten * nivel[:, None], -11, 0.0, 'int', 0.3)
    por(e['divisorias'] - 0.01, trecho(201, ataque(201, -6) - 0.03, ref=-1, t=e['divisorias'], uso='divisórias estanques: batida firme e calma'), -9, 0.0, 'int', 0.5)


if __name__ == '__main__':
    for f in (abertura, estaleiro, empuxo, retomada, experimento, avaria): f()
    SE.musica()
    res = SE.mixar(saida='audio_ep01_real.wav', stems_dir='stems', sufixo='_real', relatorio='mix_real.json', efeitos_rel=-2.0, amb_rel=-12.0)
    json.dump(AM.USOS, open(os.path.join(SE.A, 'usos_real.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(AM.USOS), 'usos de gravações registrados')
