"""Medidas objetivas de cada gravação candidata (eu não escuto — a escolha é por medição; a aprovação auditiva é do
usuário): duração, loudness integrada, piso de ruído, estabilidade (desvio da envoltória — zumbido/ambiência estáveis),
eventos transitórios (porta, passos), centróide espectral, energia < 120 Hz (zumbido real tem fundamental baixa),
fração de quadros com cara de FALA (energia na banda 300–3400 Hz modulada a 3–8 Hz, como sílabas) — fala desclassifica.
Saída: som/analise_fontes.json"""
import os, json, subprocess
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); SR = 48000


def carregar(f):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                                     capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    return x


def env_db(x, w=0.02):
    n = int(w * SR); m = len(x) // n
    return 20 * np.log10(np.sqrt(np.mean(x[:m * n].reshape(m, n) ** 2, axis=1)) + 1e-9)


def banda(x, f0, f1):
    X = np.fft.rfft(x * np.hanning(len(x))); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < f0) | (f > f1)] = 0
    return np.fft.irfft(X, len(x))


def medir(f):
    x = carregar(f)
    if len(x) < SR * 0.2: return None
    e = env_db(x); pico = float(e.max()); piso = float(np.percentile(e, 10))
    ativos = e > pico - 30
    est = float(np.std(e[ativos])) if ativos.sum() > 5 else 99.0
    d = np.diff(e); trans = [round(i * 0.02, 2) for i in np.where(d > 12)[0] if e[i + 1] > pico - 18]
    seg = x[:min(len(x), SR * 20)]
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2; fr = np.fft.rfftfreq(len(seg), 1 / SR)
    cent = float((S * fr).sum() / (S.sum() + 1e-12)); grave = float(S[fr < 120].sum() / (S.sum() + 1e-12))
    # fala: envoltória da banda de voz modulada a 3–8 Hz (ritmo silábico)
    v = banda(seg, 300, 3400); ev = 10 ** (env_db(v, 0.01) / 20); ev = ev - ev.mean()
    M = np.abs(np.fft.rfft(ev * np.hanning(len(ev)))); fm = np.fft.rfftfreq(len(ev), 0.01)
    fala = float(M[(fm > 3) & (fm < 8)].sum() / (M[(fm > 0.5) & (fm < 20)].sum() + 1e-9))
    return dict(dur=round(len(x) / SR, 2), pico_db=round(pico, 1), piso_db=round(piso, 1), estabilidade_db=round(est, 2),
                transientes_s=trans[:12], centroide_hz=round(cent), fracao_grave=round(grave, 3), indice_fala=round(fala, 3))


reg = json.load(open(os.path.join(A, 'fontes_freesound.json'))); out = {}
for r in reg:
    f = os.path.join(A, 'bib', 'freesound', f"{r['id']}.mp3")
    if os.path.exists(f):
        m = medir(f)
        if m: out[r['id']] = dict(m, titulo=r['titulo'], papeis=r['papeis'])
json.dump(out, open(os.path.join(A, 'analise_fontes.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in sorted(out.items(), key=lambda kv: kv[1]['papeis'][0]):
    print(f"{v['papeis'][0]:9s} {k:>7s} {v['dur']:6.1f}s est {v['estabilidade_db']:5.1f} cent {v['centroide_hz']:5d} grave {v['fracao_grave']:.2f} fala {v['indice_fala']:.2f} tr {v['transientes_s'][:4]} | {v['titulo'][:40]}")
