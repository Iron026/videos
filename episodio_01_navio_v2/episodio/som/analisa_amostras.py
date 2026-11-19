"""Análise objetiva das gravações candidatas (não substitui a escuta): formato, pico, clipping, piso de ruído,
faixa útil de frequências, centroide e posição do ataque."""
import json, numpy as np, soundfile as sf, sys
m = json.load(open('candidatos_mixkit.json')); out = []
for x in m:
    info = sf.info(x['arquivo_local'].replace('som/', '')); a, sr = sf.read(x['arquivo_local'].replace('som/', ''), always_2d=True)
    mono = a.mean(1); pk = np.abs(a).max(); clip = int((np.abs(a) > 0.998).sum())
    w = int(0.05 * sr); r = np.sqrt(np.convolve(mono ** 2, np.ones(w) / w, 'valid')[::w // 2] + 1e-12); rdb = 20 * np.log10(r)
    piso = np.percentile(rdb, 10); topo = np.percentile(rdb, 95)
    S = np.abs(np.fft.rfft(mono[:sr * 20] * np.hanning(min(len(mono), sr * 20)))); f = np.fft.rfftfreq(min(len(mono), sr * 20), 1 / sr)
    c = np.cumsum(S ** 2); c /= c[-1]; roll = f[np.searchsorted(c, 0.95)]; cent = float((f * S ** 2).sum() / (S ** 2).sum())
    hf = 20 * np.log10(S[f > 12000].mean() / (S[(f > 500) & (f < 4000)].mean() + 1e-12) + 1e-12) if sr > 30000 else -99
    on = np.argmax(rdb > rdb.max() - 20) * (w // 2) / sr
    corr = float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]) if a.shape[1] == 2 and np.std(a[:, 1]) > 0 else 1.0
    x.update(sr=sr, canais=a.shape[1], bits=info.subtype, dur=round(len(a) / sr, 2), pico_db=round(20 * np.log10(pk + 1e-12), 1), clip=clip,
             piso_db=round(float(piso), 1), dinamica_db=round(float(topo - piso), 1), rolloff95_hz=int(roll), centroide_hz=int(cent), ataque_s=round(float(on), 2), corr_LR=round(corr, 2), hf_rel_db=round(float(hf), 1))
    out.append(x)
json.dump(out, open('candidatos_mixkit.json', 'w'), ensure_ascii=False, indent=1)
for x in out:
    print(f"{x['id']:5d} {x['titulo'][:38]:38s} {x['sr']//1000}k/{x['canais']}/{x['bits'][:6]:6s} {x['dur']:6.1f}s pk{x['pico_db']:6.1f} clip{x['clip']:5d} piso{x['piso_db']:6.1f} din{x['dinamica_db']:5.1f} roll{x['rolloff95_hz']:6d} cent{x['centroide_hz']:5d} at{x['ataque_s']:5.2f} c{x['corr_LR']:5.2f}")
