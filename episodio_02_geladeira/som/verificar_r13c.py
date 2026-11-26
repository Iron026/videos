"""Rodada 13C — verificação medida (não escutada) das correções sonoras, no AAC do arquivo de escuta e nos stems:
 · eventos que FICARAM (critério da R13): sobre a fala, voz − resto ≥ 6 dB na janela t−0,02…t+0,20 s (faixa do celular);
   sincronia no som isolado e processado (stem da camada: início e pico em relação ao instante da ação); AAC × WAV ≥ 0,98;
 · trechos retirados (0:14, 1:12, 1:48): nível dos efeitos antes × depois na janela do efeito (loudness K de 0,4 s);
 · 0:33: pico da combinação de efeitos (K 0,4 s) e relação com a voz, R13B × variante;
 · 1:55: passos — instante de cada contato (correlação R13B × R13C: atraso 0) e nível relativo à voz antes × depois.
Uso: python3 verificar_r13c.py <variante: moderada|discreta> → relatorios/testes_r13c/verificacao_r13c_<v>.json"""
import os, sys, json, subprocess, math
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, lfilter
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..'); SR = 48000; v = sys.argv[1]
OUT = os.path.join(R, 'relatorios', 'testes_r13c'); os.makedirs(OUT, exist_ok=True)
STB, STC = os.path.join(A, 'stems', 'r13'), os.path.join(A, 'stems', f'r13_r13c_{v}')
ler = lambda p: sf.read(p)[0]
CEL = butter(4, [350, 7000], 'bandpass', fs=SR, output='sos')
def kw(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
def kpico(x, t0, t1):
    y = kw(x[int(t0 * SR):int(t1 * SR)]); p = (y ** 2).sum(1); w = int(0.4 * SR)
    if len(p) < w: return -99.0
    c = np.cumsum(np.concatenate([[0], p])); m = (c[w:] - c[:-w]) / w; return round(float(10 * np.log10(m.max() + 1e-15) - 0.691), 1)
def dec(f):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).astype(np.float64).reshape(-1, 2)
MIX = os.path.join(A, f'audio_ep02_r13_r13c_{v}_r13_teste.wav'); MIXB = os.path.join(A, 'audio_ep02_r13_r13_teste.wav')
VID = os.path.join(R, 'episodio', 'previas_r13c', f'ep02_r13C_{v}_escuta_1080x1920.mp4')
wav = ler(MIX); aac = dec(VID); n = min(len(wav), len(aac))
# atraso global AAC × WAV (0 esperado)
seg = slice(int(30 * SR), int(40 * SR)); xc = np.correlate(aac[seg, 0], wav[seg, 0][2048:-2048], 'valid'); atraso = int(np.argmax(xc) - 2048)
voz = ler(os.path.join(STC, 'voz.wav')); resto = ler(os.path.join(STC, 'musica.wav')) + ler(os.path.join(STC, 'efeitos_mecanismos.wav'))
vc, rc = sosfiltfilt(CEL, voz.mean(1)), sosfiltfilt(CEL, resto.mean(1))
REG = json.load(open(os.path.join(A, f'mix_ep02_r13_r13c_{v}.json')))
camadas = {c: ler(os.path.join(STC, f'camada_{c}.wav')) for c in {e['camada'] for e in REG['eventos']}}
ev_out = []
for e in REG['eventos']:
    t = e['t']; a_, b_ = int((t - 0.02) * SR), int((t + 0.20) * SR)
    ev_db = 10 * np.log10((vc[a_:b_] ** 2).mean() + 1e-15); na_pausa = bool(ev_db < -45)
    vr = round(float(ev_db - 10 * np.log10((rc[a_:b_] ** 2).mean() + 1e-15)), 1)
    x = np.abs(camadas[e['camada']][int((t - 0.3) * SR):int((t + 0.3) * SR)]).max(1)
    env = np.convolve(x, np.ones(48) / 48, 'same'); pk = int(np.argmax(env)); lim = env[pk] * 10 ** (-20 / 20)
    ini = int(np.argmax(env > lim)); i0, i1 = int((t - 0.2) * SR), int((t + 0.5) * SR)
    cor = float(np.corrcoef(aac[i0:i1].ravel(), wav[i0:i1].ravel())[0, 1])
    ev_out.append(dict(t=t, uso=REG['fontes_usadas'].get(e['fonte'], ''), fonte=e['fonte'], na_pausa=na_pausa, voz_menos_resto_evento_db=vr,
                       inicio_ms=round((ini / SR - 0.3) * 1000), pico_ms=round((pk / SR - 0.3) * 1000), aac_x_wav_corr=round(cor, 4),
                       representacao_didatica=e.get('representacao_didatica', False)))
ok_ev = all((e['na_pausa'] or e['voz_menos_resto_evento_db'] >= 6) and e['aac_x_wav_corr'] >= 0.98 for e in ev_out)
# retirados: efeitos (stem efeitos_mecanismos) antes × depois na janela de cada efeito
efB, efC = ler(os.path.join(STB, 'efeitos_mecanismos.wav')), ler(os.path.join(STC, 'efeitos_mecanismos.wav'))
vzB = ler(os.path.join(STB, 'voz.wav'))
retirados = {}
for nome, (t0, t1) in {'0:14 impacto (fs:754424)': (14.3, 16.1), '1:12 whoosh E1 (mk:1474)': (71.8, 74.5), '1:48 sopro H1 (mk:1489)': (109.2, 111.3)}.items():
    retirados[nome] = dict(efeitos_k_pico_r13b_lufs=kpico(efB, t0, t1), efeitos_k_pico_r13c_lufs=kpico(efC, t0, t1), voz_k_pico_lufs=kpico(vzB, t0, t1),
                           mixagem_k_pico_r13b=kpico(ler(MIXB), t0, t1), mixagem_k_pico_r13c=kpico(wav, t0, t1))
# 0:33: combinação da revelação
rev = dict(janela_s=[33.0, 38.6], efeitos_k_pico_r13b_lufs=kpico(efB, 33.0, 38.6), efeitos_k_pico_r13c_lufs=kpico(efC, 33.0, 38.6),
           voz_k_pico_lufs=kpico(vzB, 33.0, 38.6), camadas_r13b=['mk:2615 aproximação', 'fs:754422 impacto', 'mk:1474 pulso'],
           camadas_r13c=['mk:2615 aproximação', 'mk:1474 pulso'], ajustes_db=REG['r13c'])
# 1:55: passos — mesmo instante (correlação) e nível
pB, pC = ler(os.path.join(STB, 'objetos_mantidos.wav')), ler(os.path.join(STC, 'objetos_mantidos.wav'))
passos = []
for p in REG['r13c'].get('passos', []):
    t = p['t']; a_, b_ = int((t - 0.05) * SR), int((t + 0.30) * SR); xb, xc_ = pB[a_:b_, 0], pC[a_:b_, 0]
    cc = np.correlate(xc_, xb[200:-200], 'valid'); lag = int(np.argmax(np.abs(cc)) - 200)
    eb = np.abs(xb).max(); ec = np.abs(xc_).max()
    passos.append(dict(t=t, distancia_m=p['distancia_m'], atraso_amostras=lag, ganho_medido_db=round(20 * math.log10(ec / eb), 1), ganho_aplicado_db=p['ganho_db'],
                       k_pico_r13b_lufs=kpico(pB, t - 0.05, t + 0.45), k_pico_r13c_lufs=kpico(pC, t - 0.05, t + 0.45), voz_k_pico_lufs=kpico(vzB, t - 0.8, t + 0.8)))
fora = float(20 * np.log10(np.abs(np.concatenate([pB[:int(115.9 * SR)] - pC[:int(115.9 * SR)], pB[int(120.05 * SR):] - pC[int(120.05 * SR):]])).max() + 1e-30))
res = dict(variante=v, arquivo=os.path.relpath(VID, R), atraso_aac_amostras=atraso, eventos_mantidos=ev_out, eventos_aprovados=ok_ev,
           criterio='sobre a fala: voz − resto ≥ 6 dB na janela t−0,02…t+0,20 (celular); efeitos NA PAUSA fora do critério; AAC × WAV ≥ 0,98; sincronia no som isolado (stem da camada)',
           retirados=retirados, revelacao_033=rev, passos_155=passos, objetos_fora_de_115_9_120_05_dif_max_dbfs=round(fora, 1))
json.dump(res, open(os.path.join(OUT, f'verificacao_r13c_{v}.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: x for k, x in res.items() if k != 'eventos_mantidos'}, ensure_ascii=False, indent=1))
print('eventos:', len(ev_out), 'aprovados' if ok_ev else 'FALHA', ' voz−resto min (sobre a fala):', min(e['voz_menos_resto_evento_db'] for e in ev_out if not e['na_pausa']),
      ' pico ms:', min(e['pico_ms'] for e in ev_out), max(e['pico_ms'] for e in ev_out), ' corr min:', min(e['aac_x_wav_corr'] for e in ev_out))
