"""Validação dos ajustes de áudio da rodada "seis ajustes" (buzina inicial +2 dB, fim do estaleiro em 0:30, cinco brilhos das
linhas de carga, buzina final logo após "navio."), comparando a mixagem aprovada (antes) com a nova (depois).
Uso: python3 som/validar_seis_ajustes.py <mix_antes.wav> <pasta_stems_antes>   → som/validacao_seis_ajustes_audio.json"""
import os, sys, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sintese import hpz, lpz
import sintese as S_
from som_ep01 import lufs
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); E = os.path.join(EP, 'stems'); SR = 48000; SUF = 'refinado_buzina'
mix_a = sf.read(sys.argv[1])[0]; EA = sys.argv[2]; mix_d = sf.read(f'{EP}/audio_ep01_{SUF}.wav')[0]
ld = lambda d, f: sf.read(os.path.join(d, f))[0]
voz = ld(E, f'ep01_narracao_{SUF}.wav').mean(1)
pal = json.load(open(os.path.join(EP, '..', 'voz', 'narracao_ep01', 'trabalho', 'palavras.json')))
def db(x): return float(20 * np.log10(np.sqrt(np.mean(np.asarray(x) ** 2)) + 1e-12))
def env(x, a, b, w=0.05): x = x.mean(1) if x.ndim > 1 else x; return [round(db(x[int(t * SR):int((t + w) * SR)]), 1) for t in np.arange(a, b, w)]
def cel(x): return hpz(lpz(x.mean(1) if x.ndim > 1 else x, 7000, 4), 350, 4)
cv = cel(voz); thr = np.mean(cv ** 2) * 0.05; j = int(0.1 * SR)
def margem(mix, a, b):
    cr = cel(mix) - cv; o = []
    for i in range(int(a * SR), int(b * SR), j):
        pv = np.mean(cv[i:i + j] ** 2)
        if pv > thr: o.append((round(i / SR, 1), round(10 * np.log10(pv / (np.mean(cr[i:i + j] ** 2) + 1e-12)), 1)))
    return o
def inicio(x, a, b, rel=-30, w=0.005):   # primeiro instante em que a envoltória (5 ms) chega a 'rel' dB do pico do trecho
    x = x.mean(1) if x.ndim > 1 else x; s = x[int(a * SR):int(b * SR)]; e = np.sqrt(np.convolve(s ** 2, np.ones(int(w * SR)) / int(w * SR), 'same'))
    e = 20 * np.log10(e + 1e-12); return round(a + int(np.argmax(e > e.max() + rel)) / SR, 3), round(float(e.max()), 1)
R = {}
# 1 · buzina inicial
bz_a = ld(EA, f'categorias/ep01_efeitos_buzina_{SUF}.wav'); bz_d = ld(E, f'categorias/ep01_efeitos_buzina_{SUF}.wav')
R['1_buzina_inicial'] = dict(
    pausa_6_05_6_28_db=dict(antes=round(db(bz_a[int(6.05 * SR):int(6.28 * SR)]), 2), depois=round(db(bz_d[int(6.05 * SR):int(6.28 * SR)]), 2)),
    sob_fala_7_0_9_5_db=dict(antes=round(db(bz_a[int(7 * SR):int(9.5 * SR)]), 2), depois=round(db(bz_d[int(7 * SR):int(9.5 * SR)]), 2)),
    momentaneo_max_lufs=dict(antes=round(float(lufs(bz_a[int(5.6 * SR):int(10 * SR)], curto=True).max()), 1), depois=round(float(lufs(bz_d[int(5.6 * SR):int(10 * SR)], curto=True).max()), 1)),
    margem_voz_um_navio=dict(antes=margem(mix_a, 6.4, 7.2), depois=margem(mix_d, 6.4, 7.2)),
    envoltoria_dbfs_6_0_6_7=dict(antes=env(bz_a, 6.0, 6.7), depois=env(bz_d, 6.0, 6.7)))
# 2 · transição de 0:30: sons do estaleiro (grupos estaleiro + guindastes, ambiências) depois da fusão de imagem (29,85–30,75 s)
def grupo(d, g):
    tot = 0
    for k in ('ambiencias', 'efeitos'):
        f = os.path.join(d, 'grupos', f'ep01_{k}_{g}_{SUF}.wav')
        if os.path.exists(f): tot = tot + sf.read(f)[0]
    return tot
amb_a = ld(EA, f'ep01_ambiencias_{SUF}.wav'); amb_d = ld(E, f'ep01_ambiencias_{SUF}.wav')
usos = json.load(open(os.path.join(A, f'usos_{SUF}.json')))
R['2_transicao_0_30'] = dict(
    ambiencias_rms_dbfs_29_33=dict(antes=env(amb_a, 29.0, 33.0, 0.25), depois=env(amb_d, 29.0, 33.0, 0.25)),
    ambiencias_media_31_35_db=dict(antes=round(db(amb_a[int(31 * SR):int(35 * SR)]), 1), depois=round(db(amb_d[int(31 * SR):int(35 * SR)]), 1)),
    ambiencias_media_35_41_db=dict(antes=round(db(amb_a[int(35.5 * SR):int(41.5 * SR)]), 1), depois=round(db(amb_d[int(35.5 * SR):int(41.5 * SR)]), 1)),
    maior_salto_100ms_29_42_db=dict(antes=float(np.max(np.abs(np.diff(env(amb_a, 29.0, 42.0, 0.1))))), depois=float(np.max(np.abs(np.diff(env(amb_d, 29.0, 42.0, 0.1)))))),
    sons_ativos_apos_30_75=[dict(t=u['t'], uso=u['uso']) for u in usos if 30.0 <= u.get('t', 0) < 41.55],
    margem_voz_30_41_pct_10db=dict(antes=round(100 * np.mean([m >= 10 for _, m in margem(mix_a, 30.3, 41.5)]), 1), depois=round(100 * np.mean([m >= 10 for _, m in margem(mix_d, 30.3, 41.5)]), 1)))
# 4 · cinco brilhos: início medido no stem de efeitos × primeiro quadro com brilho visível; nível × narração; ausência de graves
fx_d = ld(E, f'ep01_efeitos_{SUF}.wav'); fx_a = ld(EA, f'ep01_efeitos_{SUF}.wav'); dif = (fx_d - fx_a).mean(1)
QUADROS = [130.517, 131.050, 131.617, 132.150, 132.717]
br = []
for t in QUADROS:
    # início: na banda do "tilintar" (2–3 kHz) do stem de efeitos NOVO (o sopro antigo foi removido, não entra na conta)
    s = dif[int((t - 0.1) * SR):int((t + 0.45) * SR)]; bb = S_.bp(fx_d.mean(1)[int((t - 0.1) * SR):int((t + 0.45) * SR)], 2000, 3000)
    e = 20 * np.log10(np.sqrt(np.convolve(bb ** 2, np.ones(240) / 240, 'same')) + 1e-12)
    t_on = t - 0.1 + int(np.argmax(e > e.max() - 20)) / SR; seg = s[int(0.1 * SR):]
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2; fr = np.fft.rfftfreq(len(seg), 1 / SR)
    br.append(dict(quadro_s=t, inicio_audio_s=round(t_on, 3), desvio_ms=round((t_on - t) * 1000, 1), pico_dbfs=round(float(e.max()), 1),
                   energia_abaixo_500hz_pct=round(100 * float(sp[fr < 500].sum() / sp.sum()), 2),
                   narracao_no_instante_lufs_mom=round(float(lufs(np.stack([voz, voz], 1)[int((t - 0.3) * SR):int((t + 0.5) * SR)], curto=True).max()), 1),
                   brilho_lufs_mom=round(float(lufs(np.stack([dif, dif], 1)[int((t - 0.3) * SR):int((t + 0.5) * SR)], curto=True).max()), 1)))
R['4_linhas'] = dict(brilhos=br, margem_voz_130_134=dict(antes=margem(mix_a, 130.4, 133.8), depois=margem(mix_d, 130.4, 133.8)))
# 6 · buzina final
fim_navio = [p for p in pal if p['palavra'].startswith('navio.')][-1]['fim']
on_a = inicio(bz_a, 165.9, 168.0); on_d = inicio(bz_d, 165.9, 168.0)
def chega(x, a, b, rel):
    x = x.mean(1); s = x[int(a * SR):int(b * SR)]; w = int(0.02 * SR); e = np.array([db(s[i:i + w]) for i in range(0, len(s) - w, w // 4)])
    return round(a + int(np.argmax(e > e.max() + rel)) * (w // 4) / SR, 3)
R['6_buzina_final'] = dict(fim_de_navio_s=fim_navio,
    inicio_audivel_s=dict(antes=chega(bz_a, 165.9, 168, -30), depois=chega(bz_d, 165.9, 168, -30)),
    chega_a_6db_do_pico_s=dict(antes=chega(bz_a, 165.9, 168, -6), depois=chega(bz_d, 165.9, 168, -6)),
    separacao_ms=dict(antes=round((chega(bz_a, 165.9, 168, -30) - fim_navio) * 1000), depois=round((chega(bz_d, 165.9, 168, -30) - fim_navio) * 1000)),
    pico_momentaneo_lufs=dict(antes=round(float(lufs(bz_a[int(166 * SR):], curto=True).max()), 1), depois=round(float(lufs(bz_d[int(166 * SR):], curto=True).max()), 1),
                              abertura_depois=R['1_buzina_inicial']['momentaneo_max_lufs']['depois']),
    voz_ate_fim_de_navio_igual=bool(np.allclose(ld(EA, f'ep01_narracao_{SUF}.wav'), ld(E, f'ep01_narracao_{SUF}.wav'), atol=1e-6)),
    sobreposicao_com_voz_db=round(db(bz_d[int((fim_navio - 0.15) * SR):int(fim_navio * SR)]), 1),
    envoltoria_dbfs_166_168=env(bz_d, 166.0, 168.0, 0.1), mix_ultimos_20ms_dbfs=round(db(mix_d[-int(0.02 * SR):]), 1))
# geral
d = np.abs(mix_d - mix_a).max(1); w = SR // 10; ev = np.array([d[i:i + w].max() for i in range(0, len(d) - w, w)]); ch = np.where(ev > 1e-5)[0] / 10
R['trechos_alterados_s'] = [[round(float(g[0]), 1), round(float(g[-1]) + 0.1, 1)] for g in np.split(ch, np.where(np.diff(ch) > 0.15)[0] + 1) if len(g)]
R['lufs'] = dict(antes=round(lufs(mix_a), 2), depois=round(lufs(mix_d), 2))
json.dump(R, open(os.path.join(A, 'validacao_seis_ajustes_audio.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
