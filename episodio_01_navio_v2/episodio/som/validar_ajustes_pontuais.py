"""Valida os dois ajustes pontuais (recuo antecipado da buzina em ~6,46 s; guincho mais baixo sob "navio," em ~17 s),
comparando a mixagem aprovada (antes) com a nova (depois). Uso: python3 som/validar_ajustes_pontuais.py <antes.wav> <amb_antes.wav> <buz_antes.wav>
Saída: som/validacao_ajustes_pontuais.json"""
import os, sys, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from sintese import hpz, lpz
from som_ep01 import lufs
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); E = os.path.join(EP, 'stems'); SR = 48000; SUF = 'refinado_buzina'
antes, amb_antes, buz_antes = (sf.read(f)[0] for f in sys.argv[1:4])
depois = sf.read(f'{EP}/audio_ep01_{SUF}.wav')[0]; voz = sf.read(f'{E}/ep01_narracao_{SUF}.wav')[0]
amb = sf.read(f'{E}/ep01_ambiencias_{SUF}.wav')[0]; buz = sf.read(f'{E}/categorias/ep01_efeitos_buzina_{SUF}.wav')[0]
est = sf.read(f'{E}/grupos/ep01_ambiencias_guindastes_{SUF}.wav')[0]
def cel(x): return hpz(lpz(x.mean(1), 7000, 4), 350, 4)
cv = cel(voz); j = int(0.1 * SR); thr = np.mean(cv ** 2) * 0.05
def blocos(mix, a, b):   # margem voz × resto no celular simulado, blocos de 100 ms com fala
    cr = cel(mix) - cv; out = []
    for i in range(int(a * SR), int(b * SR), j):
        pv = np.mean(cv[i:i + j] ** 2)
        if pv > thr: out.append((round(i / SR, 1), round(10 * np.log10(pv / (np.mean(cr[i:i + j] ** 2) + 1e-12)), 1)))
    return out
def env(x, a, b, w=0.05): x = x.mean(1); return [(round(t, 2), round(20 * np.log10(np.sqrt(np.mean(x[int(t * SR):int((t + w) * SR)] ** 2)) + 1e-12), 1)) for t in np.arange(a, b, w)]
def tot(mix):
    cr = cel(mix) - cv; s = []
    for i in range(0, len(cv) - j, j):
        pv = np.mean(cv[i:i + j] ** 2)
        if pv > thr: s.append(10 * np.log10(pv / (np.mean(cr[i:i + j] ** 2) + 1e-12)))
    return round(100 * float(np.mean(np.array(s) >= 10)), 1), round(float(np.min(s)), 1)
R = dict(
    ponto_1_buzina=dict(palavra='"um" começa em 6,46 s (pausa 6,04–6,46 s)', margem_voz_db_antes=blocos(antes, 6.4, 7.0), margem_voz_db_depois=blocos(depois, 6.4, 7.0),
                        buzina_dbfs_antes=env(buz_antes, 6.0, 6.7), buzina_dbfs_depois=env(buz, 6.0, 6.7),
                        buzina_na_pausa_6_05_6_25_dif_db=round(20 * np.log10(np.sqrt(np.mean(buz[int(6.05 * SR):int(6.25 * SR)] ** 2)) / np.sqrt(np.mean(buz_antes[int(6.05 * SR):int(6.25 * SR)] ** 2))), 2),
                        buzina_apos_recuo_7_0_9_5_dif_db=round(20 * np.log10(np.sqrt(np.mean(buz[int(7 * SR):int(9.5 * SR)] ** 2)) / np.sqrt(np.mean(buz_antes[int(7 * SR):int(9.5 * SR)] ** 2))), 2)),
    ponto_2_guincho=dict(palavra='"navio," 16,74–17,14 s', margem_voz_db_antes=blocos(antes, 16.6, 17.4), margem_voz_db_depois=blocos(depois, 16.6, 17.4),
                         ambiencias_dbfs_antes=env(amb_antes, 16.4, 17.6, 0.1), ambiencias_dbfs_depois=env(amb, 16.4, 17.6, 0.1),
                         guindastes_dbfs_depois=env(est, 16.4, 17.6, 0.1)),
    episodio=dict(voz_10db_pct_antes=tot(antes)[0], voz_10db_pct_depois=tot(depois)[0], pior_bloco_antes=tot(antes)[1], pior_bloco_depois=tot(depois)[1],
                  lufs_antes=round(lufs(antes), 2), lufs_depois=round(lufs(depois), 2)))
d = np.abs(depois - antes).max(1); w = int(0.1 * SR); ev = np.array([d[i:i + w].max() for i in range(0, len(d) - w, w)])
ch = np.where(ev > 10 ** (-100 / 20))[0] / 10
R['diferenca_antes_depois'] = dict(trechos_alterados_s=[[round(float(g[0]), 1), round(float(g[-1]) + 0.1, 1)] for g in np.split(ch, np.where(np.diff(ch) > 0.15)[0] + 1) if len(g)])
json.dump(R, open(os.path.join(A, 'validacao_ajustes_pontuais.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False))
