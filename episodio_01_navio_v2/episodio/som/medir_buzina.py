"""Mede a buzina isolada (stems/categorias) contra a narração e a trilha, nos dois momentos, na escala do mix final."""
import sys, os, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from som_ep01 import lufs, pico_verdadeiro
A = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(A, '..', 'stems'); SR = 48000; suf = sys.argv[1] if len(sys.argv) > 1 else 'refinado_buzina'
bz = sf.read(f'{E}/categorias/ep01_efeitos_buzina_{suf}.wav')[0]; vz = sf.read(f'{E}/ep01_narracao_{suf}.wav')[0]; mu = sf.read(f'{E}/ep01_musica_{suf}.wav')[0]
fx = sf.read(f'{E}/ep01_efeitos_{suf}.wav')[0] + sf.read(f'{E}/ep01_ambiencias_{suf}.wav')[0]
mix = sf.read(f'{A}/../audio_ep01_{suf}.wav')[0]
res = {}
for nome, a, b in (('abertura', 5.6, 10.0), ('conclusao', 165.8, 168.0)):
    s = slice(int(a * SR), int(b * SR)); m = lambda x: lufs(x[s], curto=True)
    mb, mv, mm, mf = m(bz), m(vz), m(mu), m(fx - bz)
    k = int(np.argmax(mb)); ativo = mb > mb.max() - 20
    nz = np.where(np.abs(bz[s]).max(1) > 10 ** (-60 / 20))[0]
    res[nome] = dict(buzina_pico_momentaneo=round(float(mb.max()), 1), narracao_no_pico=round(float(mv[k]), 1), musica_no_pico=round(float(mm[k]), 1),
                     resto_do_som_no_pico=round(float(mf[k]), 1), instante_do_pico_s=round(a + 0.4 + k * 0.1, 2),
                     buzina_menos_narracao_max_db=round(float(np.max((mb - mv)[ativo & (mv > -40)])) if (ativo & (mv > -40)).any() else None, 1) if (ativo & (mv > -40)).any() else None,
                     duracao_audivel_s=round((nz[-1] - nz[0]) / SR, 2) if len(nz) else 0, mix_pico_dbtp=round(pico_verdadeiro(mix[s]), 1))
print(json.dumps(res, ensure_ascii=False, indent=1)); json.dump(res, open(f'{A}/medidas_buzina.json', 'w'), ensure_ascii=False, indent=1)
