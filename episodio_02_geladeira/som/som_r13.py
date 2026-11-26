"""Rodada 13 — revisão do sound design (TESTE para aprovação; o definitivo R12 continua congelado).

Diagnóstico medido (relatorios/testes_r13/diagnostico_r13.json):
 · RUÍDO CONTÍNUO = duas camadas da V9 presentes o episódio inteiro: "tom de cômodo" (Freesound 329568, −37 LUFS constante,
   tom de 120 Hz) e "zumbido do compressor" (455776, ligado 100 % do tempo, −30 LUFS integrado; chega a −21 LUFS no E3).
   A narração é limpa (piso −85 dBFS): nada de redução de ruído na voz.
 · MÚSICA ~21 LU abaixo da voz na fala (−24,6 dB na faixa do celular): nível calibrado ANTES do abaixamento, abaixamento de
   −8 dB ligado em quase toda a narração, corte fixo de −3 dB em 0,9–3,2 kHz, faixa escura (2,4 % > 1 kHz), mascarada pelas
   duas camadas contínuas; e a faixa acaba aos 124 s (os últimos 21 s do episódio ficavam sem música).

O que esta mixagem faz (camadas separadas, cada uma com papel e fonte registrados):
 · voz: o MESMO stem da V9 (stems/ep02_voz_r9ref_f32.wav; MP3 intocado, mesmos tempos);
 · tom de cômodo: REMOVIDO; compressor: a MESMA camada da V9 (distância real da câmera, abafado atrás do gabinete, câmera
   lenta no E3) multiplicada por uma automação de CONTEXTO — só onde o compressor é mostrado ou a narração fala dele
   (A3/A4 traseira, E2 a partir do instante em que o trabalho elétrico liga, E3, E4 saindo, I2 trabalhando mais, J4 parando);
 · música: Spice Intrigue estendida 9 compassos (emendas no tempo forte, provadas por similaridade espectral) para o acorde
   final cair depois de "calor."; sem corte fixo; abaixamento só na banda da voz durante a fala; automação de contexto;
 · efeitos: os já adequados (porta, passos, mão, leite, garrafa, gorgolejo) mantidos; pops trocados por um "pop" de vídeo
   explicativo; novas transições SÓ em 5 movimentos/revelações; impactos discretos em 2 revelações; pistão e válvulas no E3
   (representação didática da câmera lenta); fluxo do refrigerante no pulso do C2 e no C3; expansão no capilar (G3).
Uso: python3 som_r13.py  → som/audio_ep02_r13_*.wav (variantes para os A/B), stems/r13/*.wav (float), mix_ep02_r13.json"""
import os, sys, json, math, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, resample_poly, lfilter
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A); R_ = os.path.join(A, '..')
import som_ep02 as B
from sintese import SR, n_, lpz, hpz, db
N, DUR, PAL, PLAN = B.N, B.DUR, B.PAL, B.PLAN
ST = os.path.join(A, 'stems'); CAM = os.path.join(ST, 'camadas_v9'); SUF = os.environ.get('SUF_R13', ''); OUT = os.path.join(ST, 'r13' + SUF); os.makedirs(OUT, exist_ok=True)
ler = lambda p: sf.read(p)[0][:N]
VOZ = ler(os.path.join(ST, 'ep02_voz_r9ref_f32.wav'))
L9 = {k: ler(os.path.join(CAM, f'{k}.wav')) for k in ('tom_de_comodo', 'compressor', 'gorgolejo', 'chiado_capilar', 'porta', 'passos')}
R12 = dict(efeitos_r10=ler(os.path.join(ST, 'ep02_efeitos_r10_si_r12_m5.wav')), valvulas=ler(os.path.join(ST, 'ep02_mecanismo_r10_si_r12_m5.wav')),
           musica=ler(os.path.join(ST, 'ep02_musica_r10_si_r12_m5.wav')))
SEMPOP = ler(os.path.join(ST, 'ep02_efeitos_r10_r13_sempop.wav'))       # mão, leite, prateleira, garrafa (sem os 5 pops); provado
TA = np.arange(N) / SR
REG = dict(eventos=[], automacoes={}, fontes_usadas={})

# ------------------------------------------------------------------ utilidades
def pal(p, apos=0.0):
    return next(w for w in PAL if w['palavra'].strip('.,:;?!').lower() == p and w['inicio'] >= apos)
CEL = butter(4, [350, 7000], 'bandpass', fs=SR, output='sos')
VCEL = sosfiltfilt(CEL, VOZ.mean(1))
def kw(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
VKW = kw(VOZ)
_e = np.sqrt(np.convolve(VOZ.mean(1) ** 2, np.ones(1440) / 1440, 'same')); VATIVA = _e > db(-42 + 5.45)   # fala ativa (mesmo limiar do abaixamento)
VREF_GLOBAL = float(np.sqrt(np.mean(VCEL[VATIVA] ** 2)))
rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-12)
def curva(chaves, suave=0.25):
    """Automação: [(t, valor)] interpolada linearmente e suavizada (s) → vetor por amostra."""
    t = [a for a, _ in chaves]; v = [b for _, b in chaves]; g = np.interp(TA, t, v)
    k = max(1, n_(suave)); return np.convolve(np.pad(g, (k, k), mode='edge'), np.ones(k) / k, 'same')[k:-k]
_cache = {}
def carregar(fonte):
    """('fs', id) Freesound | ('mk', id) Mixkit → estéreo 48 kHz."""
    if fonte not in _cache:
        pasta = {'fs': 'freesound', 'mk': 'mixkit_sfx'}[fonte[0]]
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(A, 'bib', pasta, f'{fonte[1]}.mp3'), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True)
        _cache[fonte] = np.frombuffer(r.stdout, np.float32).astype(np.float64).reshape(-1, 2)
    return _cache[fonte]
def colocar(camada, t, fonte, ini, dur, ataque, rel_db, pan=0.0, pan_fim=None, tom=1.0, filtro=None, fi=0.004, fo=0.08,
            teto_lu=-6.0, uso='', representacao=False, ref_janela=None):
    """Coloca um trecho da gravação com o ataque PERCEBIDO (posição `ataque` na gravação, medida) no instante t.
    Nível: `rel_db` em relação à voz NAQUELE instante na faixa do celular (350 Hz–7 kHz); teto: a janela mais forte do
    efeito (0,4 s, ponderação K) não passa de voz + teto_lu (impede grave exagerado quando o efeito tem pouca energia no celular)."""
    a = carregar(fonte); i0 = int(ini * SR); x = a[i0:i0 + int(dur * SR)].copy()
    if tom != 1.0:
        from fractions import Fraction
        fr = Fraction(1 / tom).limit_denominator(40); x = resample_poly(x, fr.numerator, fr.denominator, axis=0)
    if filtro: x = filtro(x)
    k1, k2 = min(len(x), n_(fi)), min(len(x), n_(fo))
    if k1: x[:k1] *= np.linspace(0, 1, k1)[:, None]
    if k2: x[-k2:] *= np.linspace(1, 0, k2)[:, None]
    x /= np.abs(x).max() + 1e-9
    p = np.linspace(pan, pan if pan_fim is None else pan_fim, len(x)); x = x * np.stack([np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)], 1) * math.sqrt(2)
    s = int(round((t - (ataque - ini) / tom) * SR)); x = x[max(0, -s): N - s]; s = max(0, s)
    y = np.zeros((N, 2)); y[s:s + len(x)] = x
    a_, b_ = int((t - 0.02) * SR), int((t + 0.25) * SR)
    ra, rb = (int(ref_janela[0] * SR), int(ref_janela[1] * SR)) if ref_janela else (max(0, int((t - 0.8) * SR)), int((t + 0.8) * SR))
    sel = VATIVA[ra:rb]; rv = rms(VCEL[ra:rb][sel]) if sel.sum() > SR // 20 else VREF_GLOBAL   # referência = FALA ATIVA em volta (estável; pausa-segura)
    g = rv * db(rel_db) / rms(sosfiltfilt(CEL, y[a_:b_].mean(1)))
    yk = kw(y[s:s + len(x)] * g); w = n_(0.4); pe = np.convolve((yk ** 2).sum(1), np.ones(w) / w, 'same').max() if len(yk) > w else (yk ** 2).sum(1).mean()
    vk = (VKW[max(0, a_ - SR // 2):b_ + SR // 2] ** 2).sum(1).mean(); lim = db(teto_lu) * math.sqrt(vk / (pe + 1e-15))
    gf = min(g, g * lim) if lim < 1 else g
    CAMADAS.setdefault(camada, np.zeros((N, 2))); CAMADAS[camada] += y * gf
    lic = 'mixkit' if fonte[0] == 'mk' else 'cc0'; POR_LICENCA.setdefault(lic, np.zeros((N, 2))); POR_LICENCA[lic] += y * gf   # preservação por licença
    REG['eventos'].append(dict(t=round(t, 3), camada=camada, fonte=f'{fonte[0]}:{fonte[1]}', trecho=[round(ini, 3), round(ini + dur, 3)], ataque=ataque, tom=tom,
                               rel_voz_celular_db=rel_db, referencia=('fala ativa em %.2f–%.2f s' % ref_janela) if ref_janela else 'fala ativa em ±0,8 s', limitado_pelo_teto=bool(lim < 1), ganho_db=round(20 * math.log10(gf + 1e-12), 1), pan=[pan, pan_fim], uso=uso,
                               representacao_didatica=representacao))
    REG['fontes_usadas'][f'{fonte[0]}:{fonte[1]}'] = uso
CAMADAS = {}
POR_LICENCA = {}
passa_baixa = lambda fc, o=2: (lambda x: lpz(x, fc, o))
passa_alta = lambda fc, o=2: (lambda x: hpz(x, fc, o))

# ------------------------------------------------------------------ 1. camadas contínuas: tom de cômodo removido; compressor por contexto
E2_LIGA = 75.37   # cena E2: curva uTrab 0→1 em 75,37–75,96 s (pulsos violeta: o trabalho elétrico chega ao compressor)
COMP_CTX = [(0.0, 0.0), (2.55, 0.0), (3.10, 0.75), (4.87, 0.75), (5.70, 0.45), (9.10, 0.45), (10.10, 0.0),       # A3/A4: traseira à vista
            (71.42, 0.0), (73.40, 0.80), (78.14, 0.80), (78.30, 0.62), (82.94, 0.62),                          # E1→E2: a câmera CHEGA a um compressor que já funcionava · E3 (câmera lenta)
            # (verificação R13: o clique de relé + subida em 75,37 s dizia 'o compressor liga agora'; uTrab 0→1 é só a visualização
            #  didática do trabalho elétrico, e o compressor está ligado desde a abertura — relé removido)
            (83.40, 0.50), (86.40, 0.0),                                                                          # E4: a câmera segue a descarga
            (119.18, 0.0), (119.80, 0.45), (121.25, 0.45), (122.81, 0.85), (124.36, 0.85), (125.30, 0.0),         # I2: trabalha mais (uTrabVel 1→2,2)
            (145.30, 0.0), (145.80, 0.40), (149.90, 0.0), (DUR, 0.0)]                                                             # J4: o trabalho cai a zero (uTrab 1→0)
g_comp = curva(COMP_CTX, 0.20); REG['automacoes']['compressor_contexto'] = COMP_CTX
TDC_E3 = [78.69, 79.957, 81.19, 82.457]                                                # pistão no fim da compressão (cena E3)
pulso = np.ones(N)
for t in TDC_E3: pulso += 0.45 * np.exp(-0.5 * ((TA - t) / 0.12) ** 2)                 # carga: o zumbido "pesa" a cada compressão
COMPRESSOR = L9['compressor'] * (g_comp * pulso)[:, None]
GORG_CTX = [(0.0, 0.0), (48.54, 0.0), (49.6, 0.55), (53.06, 0.9), (64.07, 0.9), (64.8, 1.35), (67.82, 1.2), (69.2, 0.0), (DUR, 0.0)]
GORGOLEJO = L9['gorgolejo'] * curva(GORG_CTX, 0.3)[:, None]; REG['automacoes']['gorgolejo_contexto'] = GORG_CTX

# ------------------------------------------------------------------ 2. efeitos novos (fontes medidas; ver relatorio_r13 e fontes_*.json)
# transição C (empurrão lateral de 0,3 s centrado em 5,737 s): corpo grave + ar, da direita para a esquerda
colocar('transicoes', 5.737, ('mk', '166'), 0.0, 0.78, 0.296, -12.0, 0.5, -0.5, uso='transição C: empurrão rosto → interior (corpo)')
colocar('transicoes', 5.737, ('mk', '175'), 0.15, 0.46, 0.462, -19.0, 0.6, -0.6, uso='transição C: empurrão rosto → interior (ar)')
# B2 → B3: "A geladeira não fabrica frio." impacto discreto NA PAUSA depois de "frio." (14,42 s); depois o calor viaja
t_frio = pal('frio', 13.0)['fim'] + 0.02
R13C = os.environ.get('R13C', '0') == '1'   # rodada 13C (correções pontuais depois da escuta da R13B); desligada = R13B idêntica
C2_REVELA = os.environ.get('C2_REVELA', 'atual')   # 0:33 — 'atual' (R13B) | 'moderada' | 'discreta'
if not R13C:   # R13C: retirado (0:14) — o impacto na pausa depois de 'não fabrica frio.' sobrava
    colocar('impactos', t_frio, ('fs', '754424'), 0.0, 1.6, 0.009, -9.0, 0.0, fo=0.9, teto_lu=-8.0, uso='revelação "não fabrica frio" — impacto na pausa')
# (retirado na verificação R13 — 1,1 s depois do impacto do 'não fabrica frio.': efeito sobre efeito) colocar('transicoes', 15.55, ('mk', '1474'), 0.2, 2.6, 1.168, -18.0, -0.35, 0.35, fo=0.6, uso='B3: o calor é transportado (feixe contorna a parede)')
# C2: "Escondido…" — revelação do circuito (uRevela 34,33→35,36) e pulso que dá a volta (uPulso 34,74→37,86)
# R13C (0:33): sem o impacto cinematográfico; ficam só a aproximação (o circuito aparece) e o sopro que acompanha o pulso
# (o caminho do circuito). Mesmas fontes, trechos e instantes; só níveis: moderada = aproximação −4 dB; discreta = −8 dB e pulso −2 dB.
REV_DB = dict(atual=(0.0, 0.0), moderada=(-4.0, 0.0), discreta=(-8.0, -2.0))[C2_REVELA]
REG['r13c'] = dict(ativa=R13C, c2_revela=C2_REVELA, c2_aproximacao_db=REV_DB[0], c2_pulso_db=REV_DB[1])
colocar('transicoes', 34.33, ('mk', '2615'), 0.4, 2.6, 1.607, -14.0 + REV_DB[0], 0.0, fo=0.7, uso='C2: revelação do circuito (aproximação misteriosa)')
if C2_REVELA == 'atual':
    colocar('impactos', 34.33, ('fs', '754422'), 0.0, 2.2, 0.034, -10.0, 0.0, fo=1.2, teto_lu=-7.0, uso='C2: o circuito surge (impacto principal do episódio)')
colocar('fluxo', 35.90, ('mk', '1474'), 0.0, 3.2, 1.168, -18.0 + REV_DB[1], -0.5, 0.5, fi=0.3, fo=0.8, uso='C2: pulso percorre o circuito', representacao=True)
# apresentações dos componentes: pop de vídeo explicativo no 1º quadro visível do rótulo, pan pela posição do rótulo
for ev in json.load(open(os.path.join(A, 'apresentacoes_r11.json')))['eventos']:
    colocar('apresentacoes', ev['t'], ('mk', '3005'), 0.0, 0.18, 0.021, -10.5, round((ev['u'] - 0.5) * 0.5, 2), fo=0.05, teto_lu=-6.0,
            uso=f"apresentação: {ev['nome']} ({ev['plano']})")
# movimentos de câmera que levam a outro ponto do circuito (só 3; cortes comuns NÃO ganham som)
# (retirado na verificação R13 — 2 s antes do pop do rótulo 'Evaporador': dois acentos para a mesma chegada) colocar('transicoes', 47.73, ('mk', '2608'), 0.2, 0.9, 0.454, -13.0, 0.3, -0.2, uso='C4 → D1: câmera vai à caixa do congelador')
if not R13C:   # R13C: retirados — 1:12 (E1, whoosh da descida; o zumbido do compressor que entra junto é outra camada e fica)
    colocar('transicoes', 72.77, ('mk', '1474'), 0.2, 2.6, 1.168, -14.0, 0.0, 0.0, fo=0.6, uso='E1: câmera desce com o vapor pela linha de sucção')
if not R13C:   # R13C: retirado — 1:48 (H1, sopro do recuo de câmera; não é apresentação de mecanismo; a imagem fica igual)
    colocar('transicoes', 109.88, ('mk', '1489'), 0.1, 1.9, 0.713, -13.0, -0.2, 0.3, fo=0.5, uso='H1: câmera se afasta até o circuito inteiro')
# compressor: relé fecha quando o trabalho elétrico chega (E2), pistão e válvulas na câmera lenta (E3)
# (removido na verificação R13) relé de partida em E2_LIGA: comunicava incorretamente que o compressor só começa a funcionar ali
for t in TDC_E3:
    colocar('mecanismo', t, ('fs', '669468'), 0.0, 0.22, 0.014, -19.0, 0.1, tom=0.8, filtro=passa_baixa(2500), fo=0.10,   # 'Low Click 1' (CC0): toque grave e curto; 414055 descartado (som contínuo, sem golpes isolados)
            ref_janela=(78.14, 82.94),
            uso='E3: pistão no fim da compressão (câmera lenta)', representacao=True)
for t in (78.59, 79.823, 81.09, 82.323):
    colocar('mecanismo', t, ('mk', '2857'), 0.085, 0.16, 0.097, -22.0, 0.15, filtro=passa_baixa(5000), fo=0.08, ref_janela=(78.14, 82.94), uso='E3: válvula de descarga abre', representacao=True)
for t in (79.323, 80.59, 81.823):
    colocar('mecanismo', t, ('mk', '2857'), 0.085, 0.16, 0.097, -26.0, -0.1, filtro=passa_baixa(3500), fo=0.08, ref_janela=(78.14, 82.94), uso='E3: válvula de sucção abre', representacao=True)
# circulação do refrigerante no close do tubo (C3) — representação discreta, abafada (sem "água" em primeiro plano)
FONTE_FLUXO = json.loads(os.environ.get('FONTE_FLUXO', '["fs", "553257", 5.0, 4.6]'))
colocar('fluxo', 38.30 + 2.0, tuple(FONTE_FLUXO[:2]), FONTE_FLUXO[2], FONTE_FLUXO[3], FONTE_FLUXO[2] + 2.0, -20.0, 0.0, filtro=passa_baixa(1800), fi=0.8, fo=1.2,
        uso='C3: fluido refrigerante circulando no tubo', representacao=True)
# capilar (G3): expansão — fonte escolhida por medição (FONTE_CHIADO); sem gravação adequada, fica o chiado sintetizado da V9
FONTE_CHIADO = json.loads(os.environ.get('FONTE_CHIADO', '["fs", "453443", 4.0, 3.2]'))   # 'hiss small pipe ext like propane gas' (CC0): chiado de gás em tubo fino
tp = pal('parte', PLAN['G3']['t0'] - 0.5)['inicio']
if FONTE_CHIADO:
    colocar('mecanismo', tp + 0.05, tuple(FONTE_CHIADO[:2]), FONTE_CHIADO[2], FONTE_CHIADO[3] - 0.4, FONTE_CHIADO[2] + 0.25, -20.0, 0.1, filtro=passa_alta(1500), fi=0.25, fo=1.0,   # começa em 'parte' (a lupa chega à evaporação), não na pausa antes do 'e'
            uso='G3: líquido expande ao sair do capilar (chiado real)')
    CHIADO = np.zeros((N, 2))
else:
    CHIADO = L9['chiado_capilar'] * curva([(0, 0), (tp - 0.9, 0.0), (tp - 0.3, 1.0), (106.4, 1.0), (107.2, 0.0), (DUR, 0)], 0.2)[:, None]

# ------------------------------------------------------------------ 3. música: Spice Intrigue estendida + automação de contexto
GRADE = dict(batida=0.6385, fase=0.330, forte=2)          # 93,97 BPM; tempo forte na 3ª batida da grade (medido)
BAR = 4 * GRADE['batida']
# Rodada 13 (verificação): a 1ª versão repetia IMEDIATAMENTE os 8 compassos recém-ouvidos (1:43,6) e repetia 1 compasso no
# meio de uma frase de 4 (2:04,0). Agora: 8 compassos (17–24 da faixa, 45,04–65,46 s) entram no início do compasso 29
# (75,67 s): mesma posição na frase de 4 compassos, emendas com maior semelhança de croma e espectro (entrada 1,82 / saída
# 1,94 de 2,0), Δ nível 0,7 dB; o trecho repetido foi ouvido ~30 s antes, com outra passagem no meio (reprise de seção, não eco).
# Nenhum compasso isolado do final emenda bem (0,39–0,74), então não há "+1 compasso": o acorde final cai em "não cria frio.".
EMENDA = dict(insere_no_compasso=29, t_insercao=75.67, trecho_compassos=(17, 24), trecho_ini=45.04, trecho_fim=65.46)
def musica_estendida():
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(A, 'bib', 'pixabay', '334566.mp3'), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True)
    m = np.frombuffer(r.stdout, np.float32).astype(np.float64).reshape(-1, 2)
    def ataque(t):   # refina o tempo forte pelo ataque real mais próximo (±40 ms)
        a = m[int((t - 0.04) * SR):int((t + 0.04) * SR)].mean(1); e = np.convolve(a ** 2, np.ones(96) / 96, 'same'); d = np.diff(e)
        return t - 0.04 + int(np.argmax(d)) / SR
    P = ataque(EMENDA['t_insercao']); Q0 = ataque(EMENDA['trecho_ini']); Q1 = ataque(EMENDA['trecho_fim'])
    segs = [(0.0, P), (Q0, Q1), (P, len(m) / SR)]; xf = n_(0.040); out = None
    for (a, b) in segs:
        s = m[int(a * SR) - (xf if a > 0 else 0):int(b * SR)]
        if out is None: out = s; continue
        w = np.linspace(0, np.pi / 2, xf)[:, None]; out = np.concatenate([out[:-xf], out[-xf:] * np.cos(w) + s[:xf] * np.sin(w), s[xf:]])   # emenda 40 ms antes do tempo forte
    REG['musica_emendas'] = dict(insercao_na_faixa=round(P, 4), trecho_inserido=[round(Q0, 4), round(Q1, 4)], compassos_inseridos='17–24 (8)', compasso_s=round(BAR, 4),
                                 inseridos_s=round(Q1 - Q0, 3), duracao_nova_s=round(len(out) / SR, 2),
                                 emendas_no_episodio_s=[round(4.87 + P, 3), round(4.87 + P + (Q1 - Q0), 3)])
    return out
ENTRA = 4.87                                           # entra com o rosto do rapaz ("Parece estranho…"), como na R12
ms = musica_estendida(); mus = np.zeros((N, 2)); i0 = int(ENTRA * SR); n = min(N - i0, len(ms)); mus[i0:i0 + n] = ms[:n]
mus *= curva([(0, 0), (ENTRA, 0.0), (ENTRA + 0.40, 1.0), (DUR - 0.90, 1.0), (DUR - 0.20, 0.0), (DUR, 0.0)], 0.05)[:, None]   # cauda do acorde final some ~0,2 s antes do último quadro (silêncio no fim)
FINAL_MUS = ENTRA + 121.90 + REG['musica_emendas']['inseridos_s']; REG['musica_acorde_final_s'] = round(FINAL_MUS, 3)
mus = hpz(mus, 45, 2)
# fala ativa (voz real) com antecipação de 0,12 s
w = n_(0.03); vmono = VOZ.mean(1); env = np.sqrt(np.convolve(vmono ** 2, np.ones(w) / w, 'same'))
ativa = np.clip(lpz((env > db(-42 + 5.45)).astype(float), 3.0), 0, 1); ativa = np.maximum(ativa, np.r_[ativa[n_(0.12):], np.zeros(n_(0.12))])
def suaviza(g, at, lb):
    a_at, a_lb = math.exp(-1 / (at * SR / 16)), math.exp(-1 / (lb * SR / 16)); gd = g[::16]; o = np.empty_like(gd); cur = 1.0
    for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); o[i] = cur
    return np.repeat(o, 16)[:N]
SEP, MAXD, DUCK_TOTAL = float(os.environ.get('SEP_DB', '16')), float(os.environ.get('MAXD_DB', '-12')), float(os.environ.get('DUCK_TOTAL_DB', '-1.0'))
BANDA_VOZ = butter(4, [250, 4000], 'bandpass', fs=SR, output='sos')
# automação de contexto (dB): sobe em transições/revelações e no fim; desce um pouco nas demonstrações densas de mecanismo
gaps = [(a['fim'], b['inicio']) for a, b in zip(PAL, PAL[1:]) if b['inicio'] - a['fim'] >= 0.60]   # pausas reais (≥ 0,6 s)
AUTO = [(0.0, 0.0), (5.40, 0.0), (5.65, 3.0), (6.40, 3.0), (6.90, 0.0),                        # transição C
        (33.40, 0.0), (33.85, 2.5), (36.20, 2.5), (37.20, 0.0),                                 # revelação do circuito
        (47.40, 0.0), (47.70, 2.0), (48.70, 2.0), (49.20, 0.0),                                  # → evaporador
        (53.06, 0.0), (53.60, -1.5), (63.60, -1.5), (64.07, 0.0),                                # convecção (explicação densa)
        (78.14, 0.0), (78.40, -2.5), (82.94, -2.5), (83.40, 0.0),                                # E3: pistão e válvulas em primeiro plano
        (102.07, 0.0), (102.40, -1.5), (107.0, -1.5), (107.30, 0.0),                             # G3: capilar
        (109.50, 0.0), (109.90, 2.5), (112.30, 2.5), (113.00, 0.0),                              # "E tudo recomeça"
        (147.56, 0.0), (147.62, 2.0), (147.86, 2.0), (147.92, 0.0), (DUR, 0.0)]                   # acorde final em "frio." abre na pausa antes de "Ela dá…"
PAUSA_DB = float(os.environ.get('PAUSA_DB', '1.5')); PAUSAS = [(0.0, 0.0)]                                                                             # pausas ≥ 0,45 s: a música aparece +2 dB
for a, b in gaps: PAUSAS += [(a + 0.30, 0.0), (a + 0.45, PAUSA_DB), (b - 0.22, PAUSA_DB), (b - 0.10, 0.0)]   # começa 0,3 s depois da palavra (não cobre a cauda)
PAUSAS.append((DUR, 0.0))
base = np.maximum(curva(AUTO, 0.12), curva(PAUSAS, 0.08))      # curvas separadas (sem zigue-zague quando uma pausa cai numa revelação)
REG['automacoes']['musica_contexto_db'] = [(round(a, 3), b) for a, b in AUTO]; REG['automacoes']['musica_pausas_s'] = [(round(a, 2), round(b, 2)) for a, b in gaps]
mus = mus * db(base)[:, None]
# nível: na fala, a música fica ALVO_MUS_LU abaixo da voz (mediana do momentâneo, ponderação K) — R12: −21,4 LU
ALVO = float(os.environ.get('ALVO_MUS_LU', '-16.0'))
def momentaneo(x):
    y = kw(x); p = (y ** 2).sum(1); c = np.concatenate([[0], np.cumsum(p)]); w4, h = n_(0.4), n_(0.1); i = np.arange(0, len(p) - w4, h)
    return -0.691 + 10 * np.log10((c[i + w4] - c[i]) / w4 + 1e-15)
# abaixamento DINÂMICO só na banda da voz (250 Hz–4 kHz): a cada instante de fala a música fica ≥ SEP dB abaixo da voz
# nessa banda (no máximo MAXD dB de redução); graves e agudos da música seguem (presença sem disputar as palavras).
REL_S = float(os.environ.get('REL_S', '0.5'))
FATIAS = os.environ.get('FATIAS', '0') == '1'; PRESENCA = float(os.environ.get('PRESENCA_DB', '0'))
if PRESENCA: mus = mus + (db(PRESENCA) - 1) * sosfiltfilt(butter(2, 2000, 'highpass', fs=SR, output='sos'), mus, axis=0)   # realce suave > 2 kHz (faixa forte do celular)
wv = n_(0.03); mmv = lambda x: np.sqrt(np.convolve(x ** 2, np.ones(wv) / wv, 'same')) + 1e-9
g_tot = suaviza(1 - (1 - db(DUCK_TOTAL)) * ativa, 0.06, REL_S); vm_ = momentaneo(VOZ); GM = ALVO + 6.0
if not FATIAS:   # abaixamento dinâmico numa banda só (250 Hz–4 kHz)
    lo = sosfiltfilt(butter(4, 250, 'lowpass', fs=SR, output='sos'), mus, axis=0); hi = sosfiltfilt(butter(4, 4000, 'highpass', fs=SR, output='sos'), mus, axis=0); meio = mus - lo - hi
    env_v = mmv(sosfiltfilt(BANDA_VOZ, VOZ.mean(1))); env_m = mmv(meio.mean(1))
    for it in range(5):
        g = np.clip(env_v * db(-SEP) / (env_m * db(GM)), db(MAXD), 1.0); g = 1 - (1 - g) * ativa; g_meio = suaviza(g, 0.02, REL_S)
        cand = (lo + meio * g_meio[:, None] + hi) * g_tot[:, None] * db(GM); mm_ = momentaneo(cand); ok = (vm_ > -45) & (mm_ > -70)
        err = ALVO - float(np.median(mm_[ok] - vm_[ok])); GM += err
        if abs(err) < 0.1: break
else:            # EQ dinâmica por banda ("fatias"): a música só recua nas bandas em que a VOZ tem energia naquele instante
    CORTES = [250, 500, 1000, 2000, 4000, 8000]
    def dividir(x):   # bandas complementares por subtração (soma exata)
        partes = []; resto = x
        for fc in CORTES:
            lp = sosfiltfilt(butter(4, fc, 'lowpass', fs=SR, output='sos'), resto, axis=0); partes.append(lp); resto = resto - lp
        partes.append(resto); return partes   # [<250, 250–500, …, 4k–8k, >8k]
    PM = dividir(mus); PV = dividir(VOZ.mean(1))
    EV = [mmv(PV[b]) for b in range(1, 6)]; EM = [mmv(PM[b].mean(1)) for b in range(1, 6)]
    EVdb = np.array([20 * np.log10(e) for e in EV]); vmax = EVdb.max(0)
    FAIXA = float(os.environ.get('FAT_FAIXA', '18')); SIG = [np.clip((EVdb[b] - (vmax - FAIXA)) / 8.0, 0, 1) for b in range(5)]   # banda "importante" se a voz está a < 10–18 dB do seu pico naquele instante
    for it in range(5):
        cand = PM[0] + PM[6]
        for b in range(5):
            g = np.clip(EV[b] * db(-SEP) / (EM[b] * db(GM)), db(MAXD), 1.0); g = 1 - (1 - g) * SIG[b] * ativa
            cand = cand + PM[b + 1] * suaviza(g, 0.02, REL_S)[:, None]
        cand = cand * g_tot[:, None] * db(GM); mm_ = momentaneo(cand); ok = (vm_ > -45) & (mm_ > -70)
        err = ALVO - float(np.median(mm_[ok] - vm_[ok])); GM += err
        if abs(err) < 0.1: break
    g_meio = np.ones(N)
REG['musica_eq_dinamica'] = dict(fatias=FATIAS, presenca_db=PRESENCA, faixa_protegida_db=float(os.environ.get('FAT_FAIXA', '18')), sep_db=SEP)
MUSICA = cand; REG['musica_abaixamento_medio_na_fala_db'] = round(float(20 * np.log10(np.mean(g_meio[ativa > 0.5]) + 1e-9)), 1)
REG['musica'] = dict(ganho_db=round(GM, 2), alvo_lu_abaixo_da_voz_na_fala=ALVO, abaixamento='dinâmico na banda 250 Hz–4 kHz: música ≥ %g dB abaixo da voz, no máximo %g dB' % (SEP, MAXD), abaixamento_total_db=DUCK_TOTAL,
                     passa_altas_hz=45, corte_fixo_removido='−3 dB em 0,9–3,2 kHz (R12)', entra_s=ENTRA)

# ------------------------------------------------------------------ 4. somas, variantes e master
# R13C (1:55): passos do I1 discretos e coerentes com a perspectiva — ganho PRÓPRIO de cada passo (instantes intactos), medido:
# alvo = voz − 18 dB na faixa do celular (fala ativa em ±0,8 s) e voz − 18 LU em loudness K (janela 0,4 s), menos a
# atenuação de distância 20·log10(d / 2,4 m) (distância câmera → pé, cena I1). Só reduz; fora de 115,9–120,0 s nada muda.
PASSOS = L9['passos']
if R13C:
    PASSOS_I1 = [(116.017, 2.39), (116.483, 2.37), (116.950, 2.66), (118.220, 2.68), (119.085, 2.47), (119.550, 2.26)]
    ALVO_P = float(os.environ.get('PASSOS_ALVO_DB', '-18'))
    def _med(x, w): c = np.cumsum(np.concatenate([[0.0], x])); y = (c[w:] - c[:-w]) / w; return np.pad(y, (w // 2, len(x) - len(y) - w // 2), mode='edge')
    i0, i1 = int(114 * SR), int(121 * SR); pc = sosfiltfilt(CEL, PASSOS[i0:i1].mean(1)); pkw = kw(PASSOS[i0:i1])
    ep = np.sqrt(_med(pc ** 2, n_(0.05))); kp = 10 * np.log10(_med((pkw ** 2).sum(1), n_(0.4)) + 1e-15)
    vk = 10 * np.log10(_med((VKW[i0:i1] ** 2).sum(1), n_(0.4)) + 1e-15)
    gp = np.ones(N); REG['r13c']['passos'] = []
    for j, (t, d) in enumerate(PASSOS_I1):
        i = int((t - 114) * SR); a_, b_ = i - n_(0.02), i + n_(0.25); ra, rb = int((t - 0.8) * SR), int((t + 0.8) * SR)
        sel = VATIVA[ra:rb]; rv = rms(VCEL[ra:rb][sel]) if sel.sum() > SR // 20 else VREF_GLOBAL
        dist = -20 * math.log10(d / 2.4)
        rel_cel = 20 * math.log10(ep[a_:b_].max() / rv); rel_k = kp[a_:b_].max() - vk[i - n_(0.8):i + n_(0.8)].max()
        g_db = min(0.0, ALVO_P + dist - rel_cel, ALVO_P + dist - rel_k)
        ini = t - 0.06; fim = (PASSOS_I1[j + 1][0] - 0.06) if j + 1 < len(PASSOS_I1) else 120.0
        r = n_(0.03); s0, s1 = int(ini * SR), int(fim * SR); gp[s0:s1] = db(g_db)
        REG['r13c']['passos'].append(dict(t=t, distancia_m=d, antes_rel_voz_celular_db=round(rel_cel, 1), antes_rel_voz_k_lu=round(rel_k, 1), ganho_db=round(g_db, 1)))
    gp = _med(gp, n_(0.03))   # rampas de 30 ms (média móvel por soma acumulada)
    PASSOS = L9['passos'] * gp[:, None]
# R13C (pedido depois da escuta): a BATIDA da porta fechando no C1 (Freesound 489749, ângulo chega a zero em 29,577 s; som em
# 29,569 s) — mesma regra dos passos: voz − 18 dB (celular) e − 18 LU (K 0,4 s), menos 20·log10(d / 2,4 m), d = 2,9 m (câmera →
# borda da porta no quadro do fechamento). Só o trecho 29,2–30,6 s da camada da porta; abertura no A1 e no I1 intactas.
PORTA = L9['porta']
if R13C and os.environ.get('PORTA_R13C', '0') == '1':
    def _med2(x, w): c = np.cumsum(np.concatenate([[0.0], x])); y = (c[w:] - c[:-w]) / w; return np.pad(y, (w // 2, len(x) - len(y) - w // 2), mode='edge')
    t, d = 29.569, 2.9; i0, i1 = int(28.4 * SR), int(31.0 * SR); i = int(t * SR) - i0
    pc = sosfiltfilt(CEL, PORTA[i0:i1].mean(1)); ep = np.sqrt(_med2(pc ** 2, n_(0.05))); kp = 10 * np.log10(_med2((kw(PORTA[i0:i1]) ** 2).sum(1), n_(0.4)) + 1e-15)
    vk = 10 * np.log10(_med2((VKW[i0:i1] ** 2).sum(1), n_(0.4)) + 1e-15)
    a_, b_ = i - n_(0.05), i + n_(0.40); ra, rb = int((t - 0.8) * SR), int((t + 0.8) * SR); sel = VATIVA[ra:rb]; rv = rms(VCEL[ra:rb][sel]) if sel.sum() > SR // 20 else VREF_GLOBAL
    dist = -20 * math.log10(d / 2.4); rel_cel = 20 * math.log10(ep[a_:b_].max() / rv); rel_k = kp[a_:b_].max() - vk[i - n_(0.8):i + n_(0.8)].max()
    g_db = min(0.0, -18.0 + dist - rel_cel, -18.0 + dist - rel_k)
    gpt = np.ones(N); gpt[int(29.2 * SR):int(30.6 * SR)] = db(g_db); gpt = _med2(gpt, n_(0.03))
    PORTA = L9['porta'] * gpt[:, None]
    REG['r13c']['porta_c1'] = dict(t=t, distancia_m=d, antes_rel_voz_celular_db=round(rel_cel, 1), antes_rel_voz_k_lu=round(rel_k, 1), ganho_db=round(g_db, 1), trecho_s=[29.2, 30.6])
OBJ = PORTA + PASSOS + SEMPOP                                                   # efeitos já adequados, mantidos
EF13 = OBJ + GORGOLEJO + CHIADO + COMPRESSOR + sum(CAMADAS.values())                         # efeitos + mecanismos R13
EF12 = L9['porta'] + L9['passos'] + L9['gorgolejo'] + L9['chiado_capilar'] + R12['efeitos_r10'] + R12['valvulas']   # efeitos R12 (sem as camadas contínuas)
RUIDO12 = L9['tom_de_comodo'] + L9['compressor']
def limitar(x, teto):
    return B.limitador(x, teto)
TETO = float(os.environ.get('TETO_R13', '-2.2'))   # verificação R13: −2,0 deixava o AAC em −1,53 dBTP (margem de 0,03 dB)
VARIANTES = {   # (nome: soma) — A/B usam o master FIXO da V9 (voz idêntica); o teste completo é normalizado a −14 LUFS
    'ruido_isolado_r12': (RUIDO12, None),
    'tom_de_comodo_isolado_r12': (L9['tom_de_comodo'], None),
    'compressor_isolado_r12': (L9['compressor'], None),
    'r12_sem_ruido': (VOZ + EF12 + COMPRESSOR + R12['musica'], 'fixo'),          # também é o lado A do A/B da música
    'base_musica_r13': (VOZ + EF12 + COMPRESSOR + MUSICA, 'fixo'),
    'efeitos_r12': (VOZ + MUSICA + EF12, 'fixo'),
    'efeitos_r13': (VOZ + MUSICA + EF13, 'fixo'),
    'r13_teste': (VOZ + MUSICA + EF13, 'norm'),
}
REG['variantes'] = {}
SO_VAR = [v for v in os.environ.get('SO_VARIANTES', '').split(',') if v]   # R13C: gerar só estas variantes (as demais já existem na R13B)
MASTER_FIXO = os.environ.get('MASTER_R13_DB')   # R13C: o MESMO master da R13B → voz e música idênticas amostra a amostra
for nome, (soma, modo) in VARIANTES.items():
    if SO_VAR and nome not in SO_VAR: continue
    if modo is None: mix = soma; red = 0.0
    else:
        mg = 0.0 if modo == 'fixo' else (float(MASTER_FIXO) if MASTER_FIXO else (-14.0 - B.lufs(soma)))
        mix, red = limitar(soma * db(mg), TETO)
    sf.write(os.path.join(A, f'audio_ep02_r13{SUF}_{nome}.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
    REG['variantes'][nome] = dict(lufs=round(B.lufs(mix), 2) if np.abs(mix).max() > 0 else None, tp=round(B.pico_verdadeiro(mix), 2), limitador_max_db=round(red, 2), modo=modo)
    print(nome, REG['variantes'][nome], flush=True)
mg13 = float(MASTER_FIXO) if MASTER_FIXO else -14.0 - B.lufs(VOZ + MUSICA + EF13); REG['master_r13_db'] = round(mg13, 2); REG['master_fixo'] = bool(MASTER_FIXO)
for k, x in (('voz', VOZ), ('musica', MUSICA), ('efeitos_mecanismos', EF13), ('objetos_mantidos', OBJ), ('compressor_contexto', COMPRESSOR),
             ('gorgolejo', GORGOLEJO), ('chiado', CHIADO), *[(f'camada_{c}', v) for c, v in CAMADAS.items()]):
    sf.write(os.path.join(OUT, f'{k}.wav'), (x * db(mg13)).astype(np.float32), SR, subtype='FLOAT')   # stems no MESMO ganho do teste completo
# preservação por licença: CC0 + camadas próprias (podem ir ao git em FLAC) × Mixkit (não podem: item isolado)
CC0 = OBJ + GORGOLEJO + CHIADO + COMPRESSOR + POR_LICENCA.get('cc0', 0); MK = POR_LICENCA.get('mixkit', np.zeros((N, 2)))
for k, x in (('efeitos_cc0_e_proprios', CC0), ('efeitos_mixkit', MK)): sf.write(os.path.join(OUT, f'{k}.wav'), (x * db(mg13)).astype(np.float32), SR, subtype='FLOAT')
REG['prova_divisao_por_licenca_dbfs'] = round(20 * math.log10(np.abs(CC0 + MK - EF13).max() + 1e-15), 1)
REG['stems'] = sorted(os.listdir(OUT)); REG['teto_limitador_dbfs'] = TETO
json.dump(REG, open(os.path.join(A, f'mix_ep02_r13{SUF}.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in REG.items() if k in ('musica', 'musica_emendas', 'musica_acorde_final_s', 'master_r13_db')}, ensure_ascii=False, indent=1))
