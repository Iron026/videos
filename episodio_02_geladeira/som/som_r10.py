"""Rodada 10: enriquecimento sonoro + trilha musical EXPERIMENTAL, sobre a mixagem V9 APROVADA (que não muda).

Arquitetura: os 4 stems da V9 (stems/ep02_*_r9ref_f32.wav: a V9 regenerada em ponto flutuante, provada idêntica à aprovada;
os *_r9.wav antigos estão cortados em 0 dBFS pelo PCM 24 e não somam a V9), já com o master de 5,45 dB, são
somados SEM alteração; as camadas novas entram em stems próprios, com o MESMO master fixo, e o conjunto passa pelo MESMO
limitador (teto −1,8 dBFS) da V9. Prova: sem camadas novas, a saída é igual à V9 amostra a amostra (`nulo_v9`).

Camadas novas (gravações reais Freesound CC0, eventos tirados das cenas exportadas — nada para movimento inexistente):
 · mão no puxador: A1 0,20 s e I1 117,51 s (distância mão × puxador ≤ 1 mm na animação);
 · caixa de leite: pega 118,44 s (mão fecha na caixa) e saída da prateleira de vidro 118,62 s (ergue 3,2 cm);
 · válvulas do compressor (E2, E3 — únicos planos em que as válvulas aparecem de perto): um estalo abafado a cada abertura
   da válvula de descarga (e mais fraco na de sucção), nos instantes em que a válvula abre na cena; nível pela distância
   real da câmera. Representação sonora discreta (clique de relé filtrado), declarada como tal.
Trilha (stem `musica`, ganho independente): "Rest Now" (Eugenio Mininni, Mixkit Stock Music Free License), deslocada
0,4 s, com automação por função narrativa, abaixamento pela fala real (palavras.json/voz) e saída antes da última frase.
Uso: python3 som_r10.py  → som/audio_ep02_r10_{efeitos,musica,completo}.wav, stems/ep02_*_r10.wav, mix_ep02_r10.json"""
import os, sys, json, math, subprocess
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, sosfiltfilt, butter
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
import som_ep02 as B                                          # funções da mixagem aprovada (só importadas)
from sintese import SR, n_, lpz, hpz, bp, db
N, DUR, PAL = B.N, B.DUR, B.PAL
MG = 5.45                                                     # master fixo da V9 (mix_ep02_r9.json)
GK = {'efeitos': 0.15, 'mecanismo': -10.85}                   # ganhos fixos de stem da V9: mesma escala de 'db' por som
V9 = {k: sf.read(os.path.join(A, 'stems', f'ep02_{k}_r9ref_f32.wav'))[0] for k in ('voz', 'efeitos', 'mecanismo', 'ambiencias')}   # stems V9 em ponto flutuante (regenerados idênticos: CENAS_SOM=cenas_v8)

# ------------------------------------------------------------------ camadas novas (stems próprios, gerador isolado)
B.STEMS = {k: np.zeros((N, 2)) for k in ('efeitos', 'mecanismo')}; B.ENVIO = {k: np.zeros(N) for k in B.STEMS}; B.USOS = []
EV = []
def evento(t, fonte, ini, dur, ataque, gdb, stem, uso, pan=0.0, envio=0.25, filtro=None):
    x = B.trecho(fonte, ini, dur, fi=0.003, fo=min(0.08, dur / 3), uso=uso)
    if filtro: x = filtro(x); x /= np.abs(x).max() + 1e-9
    B.por(t - (ataque - ini), x, gdb, stem, pan, envio); EV.append(dict(t=round(t, 3), fonte=fonte, trecho=[ini, round(ini + dur, 3)], ataque_na_gravacao=ataque, db=gdb, stem=stem, uso=uso))
abafa = lambda fc: (lambda x: lpz(x, fc, 2))
# mão no puxador (pega plástica): 706115 "ObjectCatchHold", 1º evento (ataque 0,19 s), suavizado acima de 5 kHz
evento(0.20, '706115', 0.17, 0.24, 0.19, -20.0, 'efeitos', 'mão fecha no puxador (A1)', 0.15, filtro=abafa(5000))
evento(117.51, '706115', 0.17, 0.24, 0.19, -20.0, 'efeitos', 'mão fecha no puxador (I1)', 0.15, filtro=abafa(5000))
# caixa de leite: 616056 (manuseio de caixa de leite), evento em 1,795 s (papelão com líquido, centroide 700 Hz)
evento(118.44, '616056', 1.77, 0.30, 1.795, -19.0, 'efeitos', 'mão fecha na caixa de leite (I1)', -0.1)
# saída da prateleira: 624481 ("Freezer - fridge floor - glass - take"), evento "take" em 0,80 s, mais fraco
evento(118.62, '624481', 0.78, 0.30, 0.80, -26.0, 'efeitos', 'caixa sai da prateleira de vidro (I1)', -0.1, filtro=abafa(6000))
# válvulas do compressor (E2, E3): instantes de abertura nas cenas; nível pela distância câmera × compressor
DES = [74.897, 76.13, 77.397, 78.59, 79.823, 81.09, 82.323]; SUC = [75.197, 76.463, 77.697, 79.323, 80.59, 81.823]
gdist = B.curva_distancia(B.COMP, ref=0.6, minimo_db=-24)
for lista, base, nome in ((DES, -24.0, 'descarga'), (SUC, -30.0, 'sucção')):
    for t in lista:
        if not (B.PLAN['E2']['t0'] <= t < B.PLAN['E3']['t1']): continue
        gd = 20 * math.log10(gdist[int(t * SR)] + 1e-9)
        evento(t, '876593', 0.005, 0.06, 0.015, base + gd, 'mecanismo', f'válvula de {nome} abre (E2/E3) — clique de relé filtrado (representação)', 0.1, 0.12, filtro=abafa(2200))
ir = B.S.resposta_impulso('cozinha')
NOVO = {}
for k in B.STEMS:
    x = B.STEMS[k].copy()
    for c in range(2): x[:, c] += fftconvolve(B.ENVIO[k], ir[:, c])[:N]
    NOVO[k] = hpz(x, 30, 2) * db(GK[k]) * db(MG)

# ------------------------------------------------------------------ voz (atividade real) e abaixamento das camadas novas
v = V9['voz'].mean(1); w = n_(0.03); mm = lambda x: np.convolve(x, np.ones(w) / w, 'same')
ativa = np.clip(lpz((np.sqrt(mm(v ** 2)) > db(-42 + MG)).astype(float), 3.0), 0, 1)
vm = np.sqrt(mm(bp(v, 200, 4000) ** 2)) + 1e-6
def suaviza(g, at, lb):
    a_at, a_lb = math.exp(-1 / (at * SR / 16)), math.exp(-1 / (lb * SR / 16)); gd = g[::16]; out = np.empty_like(gd); cur = 1.0
    for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); out[i] = cur
    return np.repeat(out, 16)[:N]
resto = V9['efeitos'] + V9['mecanismo'] + V9['ambiencias']
meio = lambda x: x - lpz(x, 200, 4) - hpz(x, 5000, 4)
nm = sum(meio(NOVO[k]) for k in NOVO); tot = np.sqrt(mm(((meio(resto) + nm) ** 2).mean(1))) + 1e-9
gfx = suaviza(1 - (1 - np.maximum(np.minimum(1.0, vm * db(-13.0) / tot), db(-18.0))) * ativa, 0.010, 0.45)
for k in NOVO: NOVO[k] = NOVO[k] - meio(NOVO[k]) + meio(NOVO[k]) * gfx[:, None]

# ------------------------------------------------------------------ trilha
MUS = dict(id='584', titulo='Rest Now', autor='Eugenio Mininni', fonte='Mixkit', url_pagina='https://mixkit.co/free-stock-music/ambient/',
           url_arquivo='https://assets.mixkit.co/music/584/584.mp3', licenca='Mixkit Stock Music Free License (https://mixkit.co/license/#musicFree)',
           arquivo_local='som/bib/mixkit/584.mp3', deslocamento_s=0.4)
m = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(A, 'bib', 'mixkit', '584.mp3'), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                 capture_output=True, check=True).stdout, np.float32).astype(np.float64).reshape(-1, 2)
i0 = int(MUS['deslocamento_s'] * SR); mus = m[i0:i0 + N]; mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
mus = hpz(mus, 60, 2)                                                                  # sem graves contínuos
s1 = butter(2, [900, 3200], 'bandpass', fs=SR, output='sos'); mus = mus - 0.30 * sosfiltfilt(s1, mus, axis=0)   # ≈ −3 dB na faixa da voz
AUTO = [(0.0, -40), (2.5, -4), (10.3, -4), (10.6, -3), (16.0, -3), (16.6, -6), (28.6, -6), (33.6, -4), (33.92, -3), (37.5, -3), (40.0, -7),
        (71.4, -7), (72.0, -5), (74.2, -5), (75.0, -12), (91.5, -12), (92.5, -8), (111.6, -8), (112.2, -5), (115.3, -5), (115.9, -6),
        (135.2, -6), (135.6, -7), (145.0, -7), (147.6, -60), (DUR, -60)]                    # (s, dB): função narrativa
ta = np.arange(N) / SR; auto = db(np.interp(ta, [a for a, _ in AUTO], [b for _, b in AUTO]))
ativa_m = np.maximum(ativa, np.r_[ativa[n_(0.15):], np.zeros(n_(0.15))])   # antecipa 0,15 s: a música já está baixa no início da palavra
gvoz = suaviza(1 - (1 - db(float(os.environ.get('MUSICA_DUCK_DB', '-8')))) * ativa_m, 0.06, 0.6)   # abaixa enquanto há fala real (−8 dB: p5 voz−resto no celular ≥ 13 dB)
Lv = B.lufs(V9['voz']); mus = mus * auto[:, None]; GM = (Lv + float(os.environ.get('MUSICA_REL_DB', '-18.5'))) - B.lufs(mus); mus = mus * db(GM) * gvoz[:, None]
k_ = n_(1.0); mus[-k_:] *= 0.0

# ------------------------------------------------------------------ variantes e medidas
def final(extra):
    soma = sum(V9.values()) + extra
    return B.limitador(soma, -1.8)
nulo, _ = final(0.0); ref = sf.read(os.path.join(A, 'audio_ep02_r9.wav'))[0]
nulo_db = 20 * math.log10(np.abs(nulo - ref).max() + 1e-12)
VAR = {'efeitos': NOVO['efeitos'] + NOVO['mecanismo'], 'musica': mus, 'completo': NOVO['efeitos'] + NOVO['mecanismo'] + mus}
rel = dict(nulo_v9_dbfs=round(nulo_db, 1), master_fixo_db=MG, ganho_musica_db=round(GM, 2), lufs_voz=round(Lv, 2), trilha=MUS, automacao_musica=AUTO, eventos=EV, variantes={})
for nome, x in VAR.items():
    mix, red = final(x); sf.write(os.path.join(A, f'audio_ep02_r10_{nome}.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
    d = mix - ref; fora = np.ones(N, bool)
    rel['variantes'][nome] = dict(lufs_wav=round(B.lufs(mix), 2), tp_wav=round(B.pico_verdadeiro(mix), 2), limitador_max_db=round(red, 2),
                                  diferenca_max_v9_dbfs=round(20 * math.log10(np.abs(d).max() + 1e-12), 1))
for k, x in (('efeitos_r10', NOVO['efeitos']), ('mecanismo_r10', NOVO['mecanismo']), ('musica_r10', mus)):
    sf.write(os.path.join(A, 'stems', f'ep02_{k}.wav'), x.astype(np.float32), SR, subtype='PCM_24')
rel['musica_lufs'] = round(B.lufs(mus), 2); rel['musica_rel_voz_db'] = round(B.lufs(mus) - Lv, 2)
json.dump(rel, open(os.path.join(A, 'mix_ep02_r10.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(B.USOS, open(os.path.join(A, 'usos_ep02_r10.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in rel.items() if k not in ('eventos', 'automacao_musica')}, ensure_ascii=False, indent=1))
