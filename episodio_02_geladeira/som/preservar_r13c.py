"""Rodada 13C — preserva as mixagens candidatas (moderada, discreta e FINAL = discreta + batida da porta mais baixa, escolhida pelo usuário) SEM tocar na R13B:
 · no git (FLAC 24 bits): as duas mixagens completas (contêm efeitos Mixkit e música só MISTURADOS — permitido);
 · fora do git (licença): stems da música e dos efeitos Mixkit — só o SHA-256, para provar que a reconstrução é idêntica;
 · prova de que a R13B e a R12 continuam intactas (SHA-256 registrados em preservado_r13/preservado_r13.json).
Uso: python3 preservar_r13c.py → som/preservado_r13c/*.flac + preservado_r13c.json"""
import os, json, hashlib, math
import numpy as np, soundfile as sf
A = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(A, 'preservado_r13c'); os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
res = dict(rodada='13C — correções pontuais depois da escuta da R13B; candidatas, NÃO são o definitivo (aguardam aprovação auditiva)', variantes={})
for v in ('moderada', 'discreta', 'final'):
    src = os.path.join(A, f'audio_ep02_r13_r13c_{v}_r13_teste.wav'); x, sr = sf.read(src); dst = os.path.join(OUT, f'audio_ep02_r13C_{v}.flac')
    sf.write(dst, x, sr, subtype='PCM_24'); y = sf.read(dst)[0]; err = 20 * math.log10(np.abs(y - x).max() + 1e-15)
    st = os.path.join(A, 'stems', f'r13_r13c_{v}')
    res['variantes'][v] = dict(origem=os.path.relpath(src, A), sha256_origem=sha(src), flac=os.path.relpath(dst, A), sha256_flac=sha(dst), erro_max_dbfs=round(err, 1),
                               stems_sha256={f: sha(os.path.join(st, f)) for f in sorted(os.listdir(st))},
                               comando=(f'R13C=1 C2_REVELA={v} SUF_R13=_r13c_{v} MASTER_R13_DB=-0.03170566623698933 SO_VARIANTES=r13_teste python3 som/som_r13.py' if v != 'final' else
                                       'R13C=1 PORTA_R13C=1 C2_REVELA=discreta SUF_R13=_r13c_final MASTER_R13_DB=-0.03170566623698933 SO_VARIANTES=r13_teste python3 som/som_r13.py'),
                               registro=f'som/mix_ep02_r13_r13c_{v}.json')
P = json.load(open(os.path.join(A, 'preservado_r13', 'preservado_r13.json'))); ok = {}
for nome, d in P['arquivos'].items():
    ok[d['origem']] = sha(os.path.join(A, d['origem'])) == d['sha256_origem']; ok['preservado_r13/' + nome] = sha(os.path.join(A, 'preservado_r13', nome)) == d['sha256_flac']
for nome, d in P['fora_do_git'].items(): ok['stems/r13/' + nome] = sha(os.path.join(A, 'stems', 'r13', nome)) == d['sha256']
ok['preservado_r12/audio_ep02_r12_musica_m5.flac (5c3b593e…)'] = sha(os.path.join(A, 'preservado_r12', 'audio_ep02_r12_musica_m5.flac')).startswith('5c3b593e')
res['r13b_e_r12_intactos'] = ok; res['tudo_intacto'] = all(ok.values())
res['master'] = 'o MESMO da R13B (−0,031706 dB, obtido por mínimos quadrados do stem de voz da R13B): voz e música idênticas (≤ −150 dBFS)'
json.dump(res, open(os.path.join(OUT, 'preservado_r13c.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])
