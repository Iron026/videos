"""Rodada 9: legendas por UNIDADES DE SENTIDO (texto idêntico à narração, tempos pelas palavras de palavras.json).
Divisão por programação dinâmica sobre os pontos de quebra possíveis:
 · fim de frase (. ? !) quebra SEMPRE;
 · nenhum bloco (nem linha) termina em palavra fraca (artigo, preposição, conjunção, pronome átono…);
 · até 2 linhas de largura limitada (medida com a fonte real), preferência por 1 linha;
 · preferência por quebrar em vírgula/dois-pontos e em pausas reais da fala;
 · blocos muito rápidos são PENALIZADOS, não forçados (não atrasa nem adianta nenhuma palavra).
Exibição: o bloco entra no ataque da 1ª palavra e sai 0,25 s depois da última (ou na entrada do próximo). Se houver pausa
interna > 0,45 s, as palavras depois da pausa APARECEM no seu ataque (o layout do bloco é fixo; nada pula).
Uso direto: python3 legendas_r9.py  → imprime os blocos e as métricas."""
import os, re, sys
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(A, '..', 'decupagem'))
import planos as PL

FRACAS = set('a o as os um uma uns umas de do da dos das que e em no na nos nas por pelo pela pelos pelas para pra com se ao aos à às '
             'é mais muito ela ele sem até como quando esse essa esses essas isso seu sua seus suas não num numa dum duma '
             'sobre entre mas ou nem já também sua lhe me te nos vos vamos pode está estão'.split())
FORTE = re.compile(r'[.?!]$'); MEDIA = re.compile(r'[,:;]$')
limpa = lambda s: re.sub(r'[.,:;?!]+$', '', s).lower()


def _quebra_linhas(palavras, largura, LMAX):
    """Melhor divisão em 1 ou 2 linhas: menor largura máxima, sem linha terminando em palavra fraca. None se não couber."""
    txt = ' '.join(palavras); exib = lambda t: re.sub(r'[.,:;]+$', '', t)   # mede como é exibido (sem a pontuação final)
    if largura(exib(txt)) <= LMAX: return [txt]
    melhor = None
    for k in range(1, len(palavras)):
        l1, l2 = ' '.join(palavras[:k]), ' '.join(palavras[k:])
        if limpa(palavras[k - 1]) in FRACAS: continue
        m = (min(k, len(palavras) - k) == 1, max(largura(l1), largura(exib(l2))))   # evita palavra órfã; depois, a menor largura
        if m[1] <= LMAX and (melhor is None or m < melhor[0]): melhor = (m, [l1, l2])
    return melhor[1] if melhor else None


def blocos(largura, LMAX, DUR, min_dur=0.8, max_dur=3.4):
    p = PL.carregar_palavras()[0]; n = len(p)
    # custo[i] = melhor custo cobrindo as palavras [0, i); quebras só onde permitido
    INF = float('inf'); custo = [INF] * (n + 1); ant = [None] * (n + 1); custo[0] = 0.0
    forcada = [bool(FORTE.search(w['palavra'])) for w in p]
    for i in range(n):
        if custo[i] == INF: continue
        for j in range(i + 1, min(n, i + 14) + 1):
            if any(forcada[k] for k in range(i, j - 1)): break                  # não atravessa fim de frase
            ws = [w['palavra'] for w in p[i:j]]
            linhas = _quebra_linhas(ws, largura, LMAX)
            if linhas is None: break
            dur = p[j - 1]['fim'] - p[i]['inicio']
            c = 10.0                                                            # cada bloco custa (prefere menos trocas)
            if limpa(ws[-1]) in FRACAS and not re.search(r'[.,:;?!]$', ws[-1]) and j < n: c += 1000.0                   # nunca termina em palavra fraca
            if j < n and not forcada[j - 1]:
                pausa = p[j]['inicio'] - p[j - 1]['fim']
                c += 7.0 - (6.0 if MEDIA.search(ws[-1]) else 0.0) - min(4.0, 10.0 * max(0.0, pausa - 0.10))
            if j - i == 1: c += 12.0                                              # bloco de uma palavra só
            if dur < min_dur: c += 25.0 * (min_dur - dur) / min_dur                 # rápido demais: penaliza, não força
            if dur > max_dur: c += 8.0 * (dur - max_dur)
            if len(linhas) == 2: c += 2.0 + (12.0 if min(len(l.split()) for l in linhas) == 1 else 0.0)   # evita palavra órfã numa linha
            if custo[i] + c < custo[j]: custo[j] = custo[i] + c; ant[j] = (i, linhas)
    out, j = [], n
    while j > 0:
        i, linhas = ant[j]; out.append((i, j, linhas)); j = i
    out.reverse()
    res = []
    for k, (i, j, linhas) in enumerate(out):
        t0 = p[i]['inicio']; nxt = p[out[k + 1][0]]['inicio'] if k + 1 < len(out) else DUR
        t1 = min(p[j - 1]['fim'] + 0.25, nxt)
        # revelação progressiva só depois de pausas internas longas (> 0,45 s)
        revela = []; acum = 0
        for m in range(i, j):
            if m > i and p[m]['inicio'] - p[m - 1]['fim'] > 0.45: revela.append((p[m]['inicio'], m - i))
        linhas = [re.sub(r'[.,:;]+$', '', l) if q == len(linhas) - 1 else l for q, l in enumerate(linhas)]
        res.append(dict(t0=t0, t1=t1, linhas=linhas, palavras=[w['palavra'] for w in p[i:j]], revela=revela,
                        inicios=[w['inicio'] for w in p[i:j]]))
    return res


def metricas(bl):
    fracos = [b for b in bl[:-1] if limpa(b['palavras'][-1]) in FRACAS and not re.search(r'[.,:;?!]$', b['palavras'][-1])]
    rapidos = [b for b in bl if b['t1'] - b['t0'] < 0.6]
    return dict(blocos=len(bl), terminam_em_palavra_fraca=len(fracos), menos_de_0_6s=len(rapidos),
                duas_linhas=sum(len(b['linhas']) == 2 for b in bl), com_revelacao=sum(bool(b['revela']) for b in bl))


if __name__ == '__main__':
    from PIL import ImageFont
    F = ImageFont.truetype(os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf'), 58)
    bl = blocos(lambda s: F.getlength(s) + 14, 840, PL.resolvidos()['duracao'])
    for b in bl: print(f"{b['t0']:7.2f}–{b['t1']:7.2f}  " + ' / '.join(b['linhas']) + ('  [revela]' if b['revela'] else ''))
    print(metricas(bl))
    p = PL.carregar_palavras()[0]
    print('texto idêntico à narração:', ' '.join(w for b in bl for w in b['palavras']) == ' '.join(w['palavra'] for w in p))
