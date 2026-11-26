"""Rodada 13 — decompõe os stems da V9 aprovada (stems/ep02_*_r9ref_f32.wav, base de R10, R11 e R12) em CAMADAS:
uma por fonte sonora (tom de cômodo, zumbido do compressor, gorgolejo, chiado do capilar, porta, passos).

A cadeia de som_ep02.mixar é LINEAR em cada stem depois que o abaixamento sob a voz (gs) está calculado:
  (sinal + reverberação do envio) → passa-altas 30 Hz → ganho do stem → abaixamento só na banda 200 Hz–5 kHz (gs) → master.
Então cada camada é gerada SOZINHA pelas mesmas funções e passa pela mesma cadeia, com o MESMO gs (calculado da soma de
todas, como na V9). Prova: soma das camadas de cada stem = stem aprovado (nulo em dBFS, gravado no JSON).
Mesmas condições da regeneração da V9 (rodada 10): CENAS_SOM=cenas_v8, ganhos fixos e master 5,45 dB.
Uso: CENAS_SOM=cenas_v8 python3 decompor_v9.py → stems/camadas_v9/<camada>.wav (float) + camadas_v9.json"""
import os, sys, json, math
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
import som_ep02 as B
from sintese import SR, n_, lpz, hpz, bp, db
N = B.N; MG = 5.45; GK = {'efeitos': 0.15, 'mecanismo': -10.85, 'ambiencias': -21.13}
CAMADAS = [('tom_de_comodo', B.ambiencia), ('compressor', B.compressor), ('gorgolejo', B.evaporador), ('chiado_capilar', B.capilar),
           ('porta', B.porta), ('passos', B.passos)]
brutos = {}
for nome, f in CAMADAS:   # cada camada sozinha, mesmas funções e geradores isolados da V9
    B.STEMS = {k: np.zeros((N, 2)) for k in ('efeitos', 'mecanismo', 'ambiencias')}; B.ENVIO = {k: np.zeros(N) for k in B.STEMS}
    f(); st = [k for k in B.STEMS if np.abs(B.STEMS[k]).max() > 0]; assert len(st) == 1, (nome, st)
    brutos[nome] = (st[0], B.STEMS[st[0]].copy(), B.ENVIO[st[0]].copy()); print(nome, '→', st[0], flush=True)
ir = B.S.resposta_impulso('cozinha')
def cadeia_pre(x, env, k):   # reverberação do envio + passa-altas + ganho do stem
    y = x.copy()
    for c in range(2): y[:, c] += fftconvolve(env, ir[:, c])[:N]
    return hpz(y, 30, 2) * db(GK[k])
pre = {nome: (k, cadeia_pre(x, e, k)) for nome, (k, x, e) in brutos.items()}
# voz e abaixamento: o MESMO código de som_ep02.mixar (gs depende da soma de todas as camadas na banda média)
import subprocess
voz = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', B.MP3, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout, np.int16).astype(np.float64) / 32768
v = np.zeros(N); v[:min(N, len(voz))] = voz[:N]
w5 = n_(0.005); nv = np.sqrt(np.convolve(v ** 2, np.ones(w5) / w5, 'same')) + 1e-9; ndb = 20 * np.log10(nv)
LIM_V = float(np.percentile(ndb[ndb > -45], 90)); RAZ = 2.0
gr = np.minimum(0.0, -(ndb - LIM_V) * (1 - 1 / RAZ)); gr = np.where(ndb > LIM_V, gr, 0.0)
a_at, a_lb = math.exp(-1 / (0.005 * SR / 16)), math.exp(-1 / (0.12 * SR / 16)); gd = gr[::16]; sm_ = np.empty_like(gd); cur = 0.0
for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); sm_[i] = cur
v = v * db(np.repeat(sm_, 16)[:N])
meio = lambda x: x - lpz(x, 200, 4) - hpz(x, 5000, 4)
STK = {k: sum(y for (kk, y) in pre.values() if kk == k) for k in ('efeitos', 'mecanismo', 'ambiencias')}
w = n_(0.03); mm = lambda x: np.convolve(x, np.ones(w) / w, 'same')
ativa = np.clip(lpz((np.sqrt(mm(v ** 2)) > db(-42)).astype(float), 3.0), 0, 1); vm = np.sqrt(mm(bp(v, 200, 4000) ** 2)) + 1e-6
tot = sum(meio(STK[k]) for k in STK)
sm = np.sqrt(mm((tot ** 2).mean(1))) + 1e-9; g = np.minimum(1.0, vm * db(-13.0) / sm); g = np.maximum(g, db(-18.0)); g = 1 - (1 - g) * ativa
a_at, a_lb = math.exp(-1 / (0.010 * SR / 16)), math.exp(-1 / (0.45 * SR / 16)); gd = g[::16]; out = np.empty_like(gd); cur = 1.0
for i, val in enumerate(gd): cur = cur * a_at + val * (1 - a_at) if val < cur else cur * a_lb + val * (1 - a_lb); out[i] = cur
gs = np.repeat(out, 16)[:N]
OUT = os.path.join(A, 'stems', 'camadas_v9'); os.makedirs(OUT, exist_ok=True); res = dict(camadas={}, nulo_por_stem_dbfs={})
fim = {}
for nome, (k, y) in pre.items():
    m_ = meio(y); z = (y - m_ + m_ * gs[:, None]) * db(MG); fim[nome] = (k, z)
    sf.write(os.path.join(OUT, f'{nome}.wav'), z.astype(np.float32), SR, subtype='FLOAT')
    res['camadas'][nome] = dict(stem=k, pico_dbfs=round(20 * math.log10(np.abs(z).max() + 1e-12), 1), lufs=round(B.lufs(z), 2))
for k in ('efeitos', 'mecanismo', 'ambiencias'):
    soma = sum(z for (kk, z) in fim.values() if kk == k); ref = sf.read(os.path.join(A, 'stems', f'ep02_{k}_r9ref_f32.wav'))[0]
    res['nulo_por_stem_dbfs'][k] = round(20 * math.log10(np.abs(soma - ref).max() + 1e-15), 1)
res['condicoes'] = dict(CENAS_SOM=os.environ.get('CENAS_SOM'), CENA_R9=os.environ.get('CENA_R9'), master_db=MG, ganhos_stems_db=GK)
json.dump(res, open(os.path.join(OUT, 'camadas_v9.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
