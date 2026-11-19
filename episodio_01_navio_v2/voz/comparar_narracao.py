"""Compara os TEMPOS de uma narração nova (ex.: a mesma voz regenerada num plano pago) com a narração atual da montagem,
e prepara uma versão ENCAIXADA na linha do tempo aprovada — sem refazer animação.

Uso:  python3 voz/comparar_narracao.py <narracao_nova.mp3|wav> [pasta_saida]

Não gera nem altera nenhuma voz; o arquivo novo e o MP3 atual não são modificados.
1. Alinhamento acústico (DTW em faixa sobre espectrogramas mel) da narração atual com a nova: não depende de reconhecimento
   de fala, só de as duas dizerem o mesmo texto.
2. Leva cada frase e cada palavra da narração atual (frases.json / palavras.json) para o tempo da nova.
3. Relatório de impacto: deriva de cada frase se a nova fosse usada como está; frases que não cabem no espaço aprovado.
4. Versão encaixada por BLOCO de fala (frases ligadas sem pausa formam um bloco): cada bloco novo começa no MESMO instante
   do bloco atual (cenas, cortes e rótulos seguem a voz); só se um bloco não couber no espaço até o próximo ele é
   levemente acelerado (rubberband, sem mudar a altura). Acima de 6% o bloco é apontado para revisão. Gera narracao_48k.wav + palavras.json + frases.json encaixados, prontos para som_hibrido e montagem.
"""
import os, sys, json, ctypes, subprocess, tempfile
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, stft

V = os.path.dirname(os.path.abspath(__file__)); TRAB = os.path.join(V, 'narracao_ep01', 'trabalho')
SR, HOP = 16000, 160                     # 10 ms por quadro
LIM_ACEL = 1.06                          # aceleração máxima aceitável sem revisão (6%)
FOLGA = 0.10                             # silêncio mínimo antes da próxima frase (s)


def _lib():
    so = os.path.join(tempfile.gettempdir(), 'dtw_faixa.so')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(os.path.join(V, 'dtw_faixa.c')):
        subprocess.run(['gcc', '-O3', '-shared', '-fPIC', '-o', so, os.path.join(V, 'dtw_faixa.c')], check=True)
    lib = ctypes.CDLL(so); P = ctypes.POINTER
    lib.dtw_faixa.argtypes = [P(ctypes.c_float), ctypes.c_int, P(ctypes.c_float), ctypes.c_int, ctypes.c_int, ctypes.c_int, P(ctypes.c_int), P(ctypes.c_int)]
    return lib


def carregar(f, sr=SR):
    if not f.lower().endswith('.wav'):
        tmp = tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ac', '1', '-ar', str(sr), tmp], check=True)
        x, _ = sf.read(tmp); os.remove(tmp); return x
    x, s = sf.read(f); x = x.mean(1) if x.ndim == 2 else x
    return resample_poly(x, sr, s) if s != sr else x


def mel(x, bandas=40):
    _, _, Z = stft(x, SR, nperseg=512, noverlap=512 - HOP, boundary=None, padded=False); P = np.abs(Z) ** 2
    f = np.linspace(0, SR / 2, P.shape[0]); hz = lambda m: 700 * (10 ** (m / 2595) - 1); mm = lambda h: 2595 * np.log10(1 + h / 700)
    c = hz(np.linspace(mm(60), mm(7600), bandas + 2)); Fb = np.zeros((bandas, len(f)))
    for k in range(bandas):
        Fb[k] = np.clip(np.minimum((f - c[k]) / (c[k + 1] - c[k]), (c[k + 2] - f) / (c[k + 2] - c[k + 1])), 0, None)
    M = np.log(Fb @ P + 1e-8).T
    M = (M - M.mean(0)) / (M.std(0) + 1e-6)
    return np.ascontiguousarray((M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)).astype(np.float32))   # ordem C: a rotina em C lê por linha


def alinhar(a, b):
    """Devolve função: tempo na narração a (s) -> tempo na narração b (s)."""
    A, B = mel(a), mel(b); n, m, d = len(A), len(B), A.shape[1]
    w = int(abs(n - m) + 12.0 * SR / HOP)          # faixa: diferença de duração + 12 s
    pi = (ctypes.c_int * (n + m)); pj = (ctypes.c_int * (n + m)); PI, PJ = pi(), pj()
    t = _lib().dtw_faixa(A.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), n, B.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), m, d, w, PI, PJ)
    if t <= 0: raise RuntimeError('DTW sem memória')
    ii = np.array(PI[:t])[::-1]; jj = np.array(PJ[:t])[::-1]
    mapa = np.array([jj[ii == i].mean() for i in range(n)]) * HOP / SR
    return lambda s: np.interp(np.asarray(s) * SR / HOP, np.arange(n), mapa)


def envelope(x):
    """Envelope em dB, quadros de 10 ms."""
    n = len(x) // HOP; return 20 * np.log10(np.sqrt((x[:n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-9)


def borda(e, t, sobe, raio=0.35, limiar=-32.0):
    """Borda de fala (subida se sobe, descida se não) mais próxima de t (s), a menos de 'raio' s: cruzamento do limiar
    (relativo ao pico local) com ≥ 80 ms abaixo dele do lado do silêncio. None se não houver."""
    e = np.concatenate([np.full(10, -120.0), e, np.full(10, -120.0)]); t = t + 10 * HOP / SR     # antes do início e depois do fim: silêncio
    q = HOP / SR; i0, i1 = max(8, int((t - raio) / q)), min(len(e) - 9, int((t + raio) / q))
    if i1 <= i0: return None
    lim = e[max(0, i0 - 100):i1 + 100].max() + limiar; c = []
    for i in range(i0, i1):
        if sobe and e[i] >= lim and (e[i - 8:i] < lim).all(): c.append(i)
        if not sobe and e[i] >= lim and (e[i + 1:i + 9] < lim).all(): c.append(i + 1)
    return min(c, key=lambda i: abs(i * q - t)) * q - 10 * HOP / SR if c else None


def esticar(x, sr, fator):
    """Acelera (fator > 1) sem mudar a altura (rubberband)."""
    if abs(fator - 1) < 1e-3: return x
    d = tempfile.mkdtemp(); i, o = os.path.join(d, 'i.wav'), os.path.join(d, 'o.wav'); sf.write(i, x, sr, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', i, '-af', f'rubberband=tempo={fator:.5f}:pitchq=quality', o], check=True)
    y, _ = sf.read(o); return y


def main(novo, saida):
    os.makedirs(saida, exist_ok=True)
    atual = carregar(os.path.join(TRAB, 'narracao_48k.wav')); nova = carregar(novo)
    frases = json.load(open(os.path.join(TRAB, 'frases.json'))); palavras = json.load(open(os.path.join(TRAB, 'palavras.json')))
    f = alinhar(atual, nova)
    # frases e palavras levadas para a narração nova
    for p in palavras: p['inicio_novo'], p['fim_novo'] = float(f(p['inicio'])), float(f(p['fim']))
    for fr in frases: fr['inicio_novo'], fr['fim_novo'] = float(f(fr['inicio'])), float(f(fr['fim']))
    # BLOCOS de fala: frases seguidas sem pausa real (< 0,12 s) na narração atual formam um bloco único (encaixe natural)
    blocos = [[0]]
    for k in range(1, len(frases)):
        (blocos[-1].append(k) if frases[k]['inicio'] - frases[k - 1]['fim'] < 0.12 else blocos.append([k]))
    # refinamento nas bordas dos blocos: no silêncio o DTW pode "escorregar"; a borda da fala é localizada pela energia perto
    # da estimativa, com o mesmo critério aplicado à narração atual (a diferença entre os dois critérios é preservada)
    ea, en = envelope(atual), envelope(nova)
    for bl in blocos:
        for k, chave, sobe in ((bl[0], 'inicio', True), (bl[-1], 'fim', False)):
            ra = 1.2 if k == 0 and sobe else 0.35          # 1ª fala: o DTW é preso em (0, 0) e não vê silêncio inicial diferente
            fr = frases[k]; ref = borda(ea, fr[chave], sobe, raio=ra); nb = borda(en, fr[chave + '_novo'], sobe, raio=ra)
            if ref is not None and nb is not None and abs(nb - (ref - fr[chave]) - fr[chave + '_novo']) < ra: fr[chave + '_novo'] = nb - (ref - fr[chave])
    # encaixe por bloco: o bloco novo começa no instante do bloco atual; acelera (sem mudar a altura) só se não couber
    x48, sr48 = sf.read(novo) if novo.lower().endswith('.wav') else (None, None)
    if x48 is None or sr48 != 48000:
        tmp = tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', novo, '-ac', '1', '-ar', '48000', tmp], check=True); x48, _ = sf.read(tmp)
    x48 = x48.mean(1) if x48.ndim == 2 else x48
    dur_atual = len(atual) / SR; out = np.zeros(int((dur_atual + 3) * 48000)); res_bl = []
    for q, bl in enumerate(blocos):
        bo0, bo1 = frases[bl[0]]['inicio'], frases[bl[-1]]['fim']; bn0, bn1 = frases[bl[0]]['inicio_novo'], frases[bl[-1]]['fim_novo']
        c0 = max(0.0, bn0 - 0.25, (frases[blocos[q - 1][-1]]['fim_novo'] + bn0) / 2 if q else 0.0)
        c1 = min(len(x48) / 48000, bn1 + 0.35, (bn1 + frases[blocos[q + 1][0]]['inicio_novo']) / 2 if q + 1 < len(blocos) else 1e9)
        vaga = (frases[blocos[q + 1][0]]['inicio'] - FOLGA if q + 1 < len(blocos) else dur_atual) - bo0
        fator = max(1.0, (bn1 - bn0) / vaga) if vaga > 0 else 1.0
        seg = x48[int(c0 * 48000):int(c1 * 48000)].copy()
        if fator > 1.0: seg = esticar(seg, 48000, fator)
        r = min(len(seg) // 4, int(0.02 * 48000)); seg[:r] *= np.linspace(0, 1, r); seg[-r:] *= np.linspace(1, 0, r)
        i0 = int(round((bo0 - (bn0 - c0) / fator) * 48000))
        if i0 < 0: seg, i0 = seg[-i0:], 0
        n_ = min(len(seg), len(out) - i0); out[i0:i0 + n_] += seg[:n_]
        enc = lambda t: bo0 + (t - bn0) / fator
        for k in bl:
            fr = frases[k]; fr['fator_aceleracao'] = round(fator, 4); fr['bloco'] = q + 1
            fr['inicio_encaixado'], fr['fim_encaixado'] = enc(fr['inicio_novo']), enc(fr['fim_novo'])
            fr['deriva_sem_encaixe_s'] = round(fr['inicio_novo'] - fr['inicio'], 3); fr['deriva_com_encaixe_s'] = round(fr['inicio_encaixado'] - fr['inicio'], 3)
            fr['duracao_atual_s'] = round(fr['fim'] - fr['inicio'], 3); fr['duracao_nova_s'] = round(fr['fim_novo'] - fr['inicio_novo'], 3)
        for p in palavras:
            if bo0 - 1e-3 <= p['inicio'] <= bo1 + 1e-3: p['inicio_encaixado'], p['fim_encaixado'] = enc(p['inicio_novo']), enc(p['fim_novo'])
        res_bl.append(dict(bloco=q + 1, frases=[k + 1 for k in bl], atual_s=[round(bo0, 2), round(bo1, 2)], novo_s=[round(bn0, 2), round(bn1, 2)],
                           vaga_s=round(vaga, 2), fator=round(fator, 4)))
    # saídas encaixadas (prontas para o pipeline; nada do projeto é sobrescrito)
    pico = np.abs(out).max(); sf.write(os.path.join(saida, 'narracao_48k.wav'), out / max(pico, 1e-9) * 10 ** (-1.5 / 20) if pico > 10 ** (-1.5 / 20) else out, 48000, subtype='PCM_24')
    json.dump([dict(palavra=p['palavra'], inicio=round(p.get('inicio_encaixado', p['inicio']), 3), fim=round(p.get('fim_encaixado', p['fim']), 3), confianca=p.get('confianca'))
               for p in palavras], open(os.path.join(saida, 'palavras.json'), 'w'), ensure_ascii=False, indent=0)
    json.dump([dict(inicio=round(fr['inicio_encaixado'], 3), fim=round(fr['fim_encaixado'], 3), texto=fr['texto']) for fr in frases],
              open(os.path.join(saida, 'frases.json'), 'w'), ensure_ascii=False, indent=0)
    # relatório
    dc = np.array([fr['deriva_com_encaixe_s'] for fr in frases]); der = np.array([fr['deriva_sem_encaixe_s'] for fr in frases]); fat = np.array([fr['fator_aceleracao'] for fr in frases])
    dp = np.array([(p.get('inicio_encaixado', p['inicio']) - p['inicio']) for p in palavras])
    res = dict(arquivo_novo=os.path.abspath(novo), duracao_atual_s=round(len(atual) / SR, 2), duracao_nova_s=round(len(nova) / SR, 2),
               fala_atual_s=[frases[0]['inicio'], frases[-1]['fim']], fala_nova_s=[round(frases[0]['inicio_novo'], 2), round(frases[-1]['fim_novo'], 2)],
               sem_encaixe=dict(deriva_max_s=round(float(np.abs(der).max()), 2), deriva_final_s=round(float(der[-1]), 2),
                                frases_com_deriva_acima_1_quadro=int((np.abs(der) > 1 / 30).sum())),
               com_encaixe=dict(blocos=len(blocos), deriva_inicio_de_frase_s=dict(mediana=round(float(np.median(np.abs(dc))), 3), max=round(float(np.abs(dc).max()), 3),
                                acima_de_1_quadro=int((np.abs(dc) > 1 / 30).sum())), frases_aceleradas=int((fat > 1.0005).sum()), aceleracao_max=round(float(fat.max()), 4),
                                blocos_acima_do_limite=[b for b in res_bl if b['fator'] > LIM_ACEL],
                                deriva_de_palavra_dentro_da_frase_s=dict(mediana=round(float(np.median(np.abs(dp))), 3), p95=round(float(np.percentile(np.abs(dp), 95)), 3), max=round(float(np.abs(dp).max()), 3)),
                                ultima_fala_termina_s=round(frases[-1]['fim_encaixado'], 2)), blocos=res_bl,
               frases=[{k: (round(fr[k], 3) if isinstance(fr[k], float) else fr[k]) for k in ('texto', 'bloco', 'inicio', 'fim', 'inicio_novo', 'fim_novo', 'inicio_encaixado', 'deriva_sem_encaixe_s',
                                                                                   'deriva_com_encaixe_s', 'duracao_atual_s', 'duracao_nova_s', 'fator_aceleracao')} for fr in frases])
    json.dump(res, open(os.path.join(saida, 'comparacao_tempos.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k != 'frases'}, ensure_ascii=False, indent=1))
    return res, palavras


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(V, 'narracao_nova_encaixada'))
