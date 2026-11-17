"""Gera a narração (Kokoro-82M, voz pt-BR) ancorada nos tempos do storyboard.

Saídas: narracao/narracao.wav (24 kHz mono) e narracao/frases.json (início/fim de cada frase).
Uso: python3 narracao/gerar_narracao.py --modelo <kokoro.onnx> --vozes <voices.npz> [--voz pm_alex]
"""
import argparse, json, re, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

AQUI = os.path.dirname(os.path.abspath(__file__))
DURACAO_TOTAL = 75.0
SR = 24000
# Para cada parágrafo: lista de alvos (s) para o início de cada frase. None = logo após a anterior.
ALVOS = [
    [0.30, None],   # Cena 01
    [8.20, None],   # Cena 02
    [13.30, 20.60], # Cena 03
    [28.30, 31.90], # Cena 04
    [36.30, 41.60], # Cena 05
    [47.30],        # Cena 06
    [56.40],        # Cena 07
    [63.40, None],  # Cena 08
    [70.60, None],  # Cena 09 (assinatura)
]
PAUSA = 0.42  # pausa mínima entre frases

def aparar(a, lim=0.004):
    idx = np.where(np.abs(a) > lim)[0]
    if len(idx) == 0: return a
    i0 = max(0, idx[0] - int(0.03*SR)); i1 = min(len(a), idx[-1] + int(0.06*SR))
    return a[i0:i1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modelo', required=True); ap.add_argument('--vozes', required=True)
    ap.add_argument('--voz', default='pm_alex'); ap.add_argument('--velocidade', type=float, default=0.9)
    a = ap.parse_args()
    k = Kokoro(a.modelo, a.vozes)
    texto = open(os.path.join(AQUI, 'roteiro.txt'), encoding='utf-8').read()
    paras = [p.strip() for p in texto.split('\n\n') if p.strip()]
    assert len(paras) == len(ALVOS)
    faixa = np.zeros(int(DURACAO_TOTAL*SR), dtype=np.float32)
    frases, fim_ant = [], 0.0
    for pi, (p, alvos) in enumerate(zip(paras, ALVOS)):
        sents = re.split(r'(?<=[.?!])\s+', p)
        assert len(sents) == len(alvos), (p, alvos)
        for si, (s, alvo) in enumerate(zip(sents, alvos)):
            audio, sr = k.create(s, voice=a.voz, speed=a.velocidade, lang='pt-br')
            assert sr == SR
            audio = aparar(audio.astype(np.float32))
            ini = max(alvo if alvo is not None else 0.0, fim_ant + PAUSA if fim_ant else 0.0)
            ini = round(ini, 3); dur = len(audio)/SR
            i0 = int(ini*SR)
            if i0 + len(audio) > len(faixa):
                raise SystemExit(f'Frase ultrapassa a duração total: {s!r} termina em {ini+dur:.2f}s')
            faixa[i0:i0+len(audio)] += audio
            fim_ant = ini + dur
            frases.append({'paragrafo': pi+1, 'frase': si+1, 'texto': s, 'inicio': ini, 'fim': round(fim_ant, 3)})
            print(f'P{pi+1}.{si+1} {ini:6.2f}-{fim_ant:6.2f}  {s}')
    # checa sobreposição com o próximo alvo
    for f1, f2 in zip(frases, frases[1:]):
        assert f1['fim'] <= f2['inicio'], (f1, f2)
    sf.write(os.path.join(AQUI, 'narracao.wav'), faixa, SR)
    json.dump(frases, open(os.path.join(AQUI, 'frases.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
