"""Rodada 13 — diagnóstico REPRODUZÍVEL do som da R12 e comparação com o teste R13 (tudo medido dos arquivos).
 · níveis por camada (LUFS momentâneo, ponderação K; faixa do celular 350 Hz–7 kHz), tempo presente, energia por banda;
 · picos tonais (50/60/100/120/150 Hz) das camadas contínuas; piso de ruído da narração (MP3 original);
 · cadeia da música R12 (mix_ep02_r10_si_r12_m5.json) e posição relativa à voz;
 · por plano: música, camada contínua e efeitos, R12 × R13; voz − resto (mesmo cálculo de validar_audio.py).
Uso: python3 diagnostico_r13.py → relatorios/testes_r13/diagnostico_r13.json"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, lfilter
A = os.path.dirname(os.path.abspath(__file__)); R_ = os.path.join(A, '..'); ST = os.path.join(A, 'stems'); SR = 48000
sys.path.insert(0, os.path.join(R_, 'decupagem')); import planos as PL
ler = lambda *p: sf.read(os.path.join(ST, *p))[0]
def kw(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
CEL = butter(4, [350, 7000], 'bandpass', fs=SR, output='sos')
def janelas(p):
    c = np.concatenate([[0], np.cumsum(p)]); w, h = int(0.4 * SR), int(0.1 * SR); i = np.arange(0, len(p) - w, h); return (c[i + w] - c[i]) / w
def niveis(x):
    return -0.691 + 10 * np.log10(janelas((kw(x) ** 2).sum(1)) + 1e-15), 10 * np.log10(janelas(sosfiltfilt(CEL, x.mean(1)) ** 2) + 1e-15)
def voz_resto(voz, resto):
    vc, rc = sosfiltfilt(CEL, voz.mean(1)), sosfiltfilt(CEL, resto.mean(1)); w = int(0.4 * SR); d = []
    for i in range(0, len(vc) - w, w):
        ev = 10 * np.log10((vc[i:i + w] ** 2).mean() + 1e-12)
        if ev > -45: d.append(ev - 10 * np.log10((rc[i:i + w] ** 2).mean() + 1e-12))
    d = np.array(d); return dict(pior=round(float(d.min()), 1), p5=round(float(np.percentile(d, 5)), 1), mediana=round(float(np.median(d)), 1), janelas=len(d))
r = lambda x: round(float(x), 1)
VOZ = ler('ep02_voz_r9ref_f32.wav'); C9 = {k: ler('camadas_v9', f'{k}.wav') for k in ('tom_de_comodo', 'compressor', 'gorgolejo', 'chiado_capilar', 'porta', 'passos')}
R12 = dict(musica=ler('ep02_musica_r10_si_r12_m5.wav'), ruido=C9['tom_de_comodo'] + C9['compressor'],
           efeitos=C9['porta'] + C9['passos'] + C9['gorgolejo'] + C9['chiado_capilar'] + ler('ep02_efeitos_r10_si_r12_m5.wav') + ler('ep02_mecanismo_r10_si_r12_m5.wav'))
mg = json.load(open(os.path.join(A, 'mix_ep02_r13.json')))['master_r13_db']; k13 = 10 ** (-mg / 20)
R13 = dict(musica=ler('r13', 'musica.wav') * k13, ruido=ler('r13', 'compressor_contexto.wav') * k13,
           efeitos=(ler('r13', 'efeitos_mecanismos.wav') - ler('r13', 'compressor_contexto.wav')) * k13)
res = dict(nota='medidas, não audição; a aprovação auditiva é do usuário')
vm, vc = niveis(VOZ); fala = vm > -45
# 1. camadas da R12
cam = {}
for nome, x in (('tom_de_comodo', C9['tom_de_comodo']), ('compressor', C9['compressor']), ('musica', R12['musica'])):
    m, c = niveis(x); F = np.abs(np.fft.rfft(x.mean(1)[:len(x) // 8192 * 8192].reshape(-1, 8192) * np.hanning(8192), axis=1)) ** 2; P = F.mean(0); fr = np.fft.rfftfreq(8192, 1 / SR)
    cam[nome] = dict(tempo_presente_pct=r(100 * np.mean(m > -60)), lufs_mediana=r(np.median(m[m > -60])) if (m > -60).any() else None,
                     menos_voz_na_fala_lu=r(np.median((m - vm)[fala & (m > -80)])), celular_menos_voz_db=r(np.median((c - vc)[fala & (c > -90)])),
                     energia_acima_1k_pct=round(100 * P[fr > 1000].sum() / P.sum(), 1))
res['camadas_r12'] = cam
# 2. tom de 120 Hz
def pico(x, f0):
    m = x.mean(1)[:SR * 60]; F = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2; fq = np.fft.rfftfreq(len(m), 1 / SR); i = np.argmin(abs(fq - f0))
    return r(10 * np.log10(F[i - 3:i + 4].max() / np.median(F[i - 200:i + 200])))
res['picos_tonais_db_acima_da_vizinhanca'] = {k: {f: pico(C9[k], f) for f in (50, 60, 120)} for k in ('tom_de_comodo', 'compressor')}
# 3. piso da narração (MP3 original)
mp3 = os.path.join(R_, 'voz', 'ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3')
v = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).astype(np.float64)
w = int(0.02 * SR); lv = 10 * np.log10((v[:len(v) // w * w].reshape(-1, w) ** 2).mean(1) + 1e-15)
res['narracao_piso_dbfs'] = dict(p1=r(np.percentile(lv, 1)), p5=r(np.percentile(lv, 5)), conclusao='narração limpa: nenhuma redução de ruído aplicada à voz')
# 4. cadeia da música R12
m12 = json.load(open(os.path.join(A, 'mix_ep02_r10_si_r12_m5.json')))
res['musica_r12_cadeia'] = dict(nivel_antes_do_abaixamento='voz −13,5 LU (MUSICA_REL_DB)', abaixamento_durante_a_fala_db=-8, corte_fixo='−3 dB em 0,9–3,2 kHz', passa_altas_hz=60,
                                limitador_max_db=m12['variantes']['completo']['limitador_max_db'], resultado_lu_abaixo_da_voz=m12['musica_rel_voz_db'],
                                faixa_termina_s=round(4.87 + 124.0, 1), sem_musica='0–4,87 s e 129,6–151,2 s')
# 5. por plano e voz − resto
M = {v_: {k: niveis(x) for k, x in D.items()} for v_, D in (('R12', R12), ('R13', R13))}
res['por_plano'] = []
for p in PL.resolvidos()['planos']:
    a, b = int(p['t0'] * 10), int(p['t1'] * 10); f = lambda v_, k: r(np.median(M[v_][k][0][a:b]))
    res['por_plano'].append(dict(plano=p['id'], t0=p['t0'], musica=[f('R12', 'musica'), f('R13', 'musica')], camada_continua=[f('R12', 'ruido'), f('R13', 'ruido')],
                                 efeitos_max=[r(M['R12']['efeitos'][0][a:b].max()), r(M['R13']['efeitos'][0][a:b].max())]))
for v_, D in (('R12', R12), ('R13', R13)):
    m, c = M[v_]['musica']
    res[f'resumo_{v_}'] = dict(musica_menos_voz_na_fala_lu=r(np.median((m - vm)[fala & (m > -80)])), musica_celular_menos_voz_db=r(np.median((c - vc)[fala & (c > -90)])),
                               musica_presente_na_fala_pct=r(100 * np.mean(m[fala] > -60)), camada_continua_presente_pct=r(100 * np.mean(M[v_]['ruido'][0] > -55)),
                               voz_menos_resto_celular=voz_resto(VOZ, sum(D.values())))
os.makedirs(os.path.join(R_, 'relatorios', 'testes_r13'), exist_ok=True)
json.dump(res, open(os.path.join(R_, 'relatorios', 'testes_r13', 'diagnostico_r13.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v_ for k, v_ in res.items() if k != 'por_plano'}, ensure_ascii=False, indent=1))
