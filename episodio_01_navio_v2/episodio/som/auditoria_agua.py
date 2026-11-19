"""Auditoria da ÁGUA por seção: loudness da água (stems/categorias), do resto dos efeitos/ambiências e da narração,
na mesma escala do mix final. Uso: python3 som/auditoria_agua.py <sufixo> (ex.: hibrido, refinado)"""
import sys, os, json, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_ep01 import lufs
A = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(A, '..', 'stems'); suf = sys.argv[1]; SR = 48000
SEC = [(0, 15.1, 'abertura e navegação'), (15.1, 41.55, 'estaleiro e corte'), (41.55, 49.0, 'dique'), (49.0, 75.0, 'empuxo subaquático'),
       (75.0, 95.0, 'retomada e experimento'), (95.0, 134.0, 'carregamento e calado'), (134.0, 155.0, 'avaria e inundação'), (155.0, 168.0, 'conclusão')]
ld = lambda f: sf.read(os.path.join(E, f))[0]
agua = ld(f'categorias/ep01_efeitos_agua_{suf}.wav') + ld(f'categorias/ep01_ambiencias_agua_{suf}.wav')
fundo = ld(f'ep01_efeitos_{suf}.wav') + ld(f'ep01_ambiencias_{suf}.wav'); voz = ld(f'ep01_narracao_{suf}.wav')
def st(x):   # loudness de curto prazo (3 s, passo 0,5 s)
    w, h = 3 * SR, SR // 2; return np.array([lufs(x[i:i + w]) if np.abs(x[i:i + w]).max() > 1e-5 else -70 for i in range(0, len(x) - w, h)])
res = []
for a, b, nome in SEC:
    s = slice(int(a * SR), int(b * SR)); la, lf, lv = lufs(agua[s]), lufs(fundo[s]), lufs(voz[s])
    ea = (agua[s] ** 2).sum(); ef = (fundo[s] ** 2).sum()
    sa = st(agua[s]); sa = sa[np.isfinite(sa)] if np.isfinite(sa).any() else np.array([-70.0]); res.append(dict(secao=nome, ini=a, fim=b, agua_lufs=round(la, 1), agua_max_curto=round(float(sa.max()), 1), fundo_lufs=round(lf, 1),
                                      narracao_lufs=round(lv, 1), agua_menos_narracao_db=round(la - lv, 1), agua_pct_energia_do_fundo=round(100 * ea / max(ef, 1e-12))))
json.dump(res, open(os.path.join(A, f'auditoria_agua_{suf}.json'), 'w'), ensure_ascii=False, indent=1)
print(f"{'seção':26s} {'água':>6s} {'máx3s':>6s} {'fundo':>6s} {'voz':>6s} {'água−voz':>8s} {'%fundo':>6s}")
for r in res: print(f"{r['secao']:26s} {r['agua_lufs']:6.1f} {r['agua_max_curto']:6.1f} {r['fundo_lufs']:6.1f} {r['narracao_lufs']:6.1f} {r['agua_menos_narracao_db']:8.1f} {r['agua_pct_energia_do_fundo']:6.0f}")
