"""Decupagem do Ep. 02 como DADOS: cada plano começa numa PALAVRA do roteiro (âncora), nunca num segundo fixo.
Âncora 'F10' = início da frase 10; 'F10.3' = início da 3ª palavra (1-based) da frase 10; 'F10>' = fim da frase 10.
Os tempos absolutos vêm de palavras.json (narração aprovada, quando existir) ou de palavras_provisorio.json.
Trocar a narração recalcula automaticamente todos os cortes, movimentos, rótulos e legendas.
Uso: python3 planos.py  → imprime e grava planos_resolvidos.json (com a origem dos tempos)."""
import json, os
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'roteiro')
CAUDA = 1.6   # respiro depois da última palavra (s)

# (id, âncora de início, sequência, cena 3D, resumo do acontecimento)
PLANOS = [
    ('A1', 'F01',     'A', 'cozinha',   'Cozinha ao entardecer; a porta da geladeira se abre; luz interna; garrafa na prateleira'),
    ('A2', 'F01.8',   'A', 'cozinha',   '"fria por dentro": visão térmica varre o interior, que fica azul (mais frio que o ambiente)'),
    ('A3', 'F01.12',  'A', 'cozinha',   '"quente por fora": a câmera contorna até a traseira; serpentina e compressor laranja/vermelho'),
    ('A4', 'F02',     'A', 'cozinha',   'Plano 3/4 traseiro em visão térmica: interior azul e traseira quente no MESMO quadro'),
    ('B1', 'F03',     'B', 'cozinha',   'Volta à imagem normal; aproximação lenta da geladeira'),
    ('B2', 'F04',     'B', 'cozinha',   '"não fabrica frio": interior e caixa do congelador sem nenhuma "névoa de frio" saindo'),
    ('B3', 'F05',     'B', 'cozinha',   '"transporta calor": um feixe de calor sai do interior, contorna a parede e sai pela traseira'),
    ('B4', 'F06',     'B', 'cozinha',   'Garrafa sobre a bancada, cinza-claro na visão térmica (igual ao ambiente)'),
    ('B5', 'F07',     'B', 'interior',  'Garrafa na prateleira; feixes de calor saem dela para o ar frio; ela esfria (Tempo acelerado)'),
    ('B6', 'F08',     'B', 'interior',  '"não desaparece": os feixes sobem com o ar morno, sem sumir'),
    ('B7', 'F09',     'B', 'interior',  '"algum lugar": os feixes chegam ao evaporador; a câmera sobe junto'),
    ('C1', 'F10',     'C', 'corte',     'Afastamento; porta fecha; a carcaça e o isolamento entram em corte ilustrativo'),
    ('C2', 'F11',     'C', 'corte',     'Circuito de tubos revelado; um pulso percorre o circuito inteiro e volta ao início (fechado)'),
    ('C3', 'F12',     'C', 'corte',     'Close de um tubo em corte com o fluido circulando; rótulo "fluido refrigerante"'),
    ('C4', 'F13',     'C', 'corte',     'Circuito inteiro com as cores de temperatura; manômetros de baixa e alta; fases visíveis'),
    ('D1', 'F14',     'D', 'evaporador','Câmera vai à caixa do congelador; rótulo "Evaporador"'),
    ('D2', 'F15',     'D', 'evaporador','Entrada do evaporador em corte: mistura azul com bolhas; manômetro "baixa pressão"'),
    ('D3', 'F16',     'D', 'interior',  'Convecção do ar: alimentos → ar → paredes dos canais; feixes de calor entrando no fluido'),
    ('D4', 'F17',     'D', 'evaporador','Macro do canal: bolhas crescem, o líquido diminui até restar só vapor'),
    ('D5', 'F18',     'D', 'evaporador','Afastamento: calor dos alimentos dentro do fluido; o vapor segue para a linha de sucção'),
    ('E1', 'F19',     'E', 'corte',     'A câmera acompanha o vapor pela linha de sucção descendo por dentro da parede traseira'),
    ('E2', 'F20',     'E', 'compressor','Compressor por fora; cabo com pulsos violeta (trabalho); rótulo "Compressor"'),
    ('E3', 'F21',     'E', 'compressor','Corte do compressor: motor, virabrequim, pistão e válvulas (Câmera lenta); fluido azul → vermelho; manômetro sobe'),
    ('E4', 'F22',     'E', 'compressor','Linha de descarga vermelha ao lado do ar da cozinha (cinza): comparação "mais quente que a cozinha"'),
    ('F1', 'F23',     'F', 'traseira',  'Serpentina traseira: feixes de calor saem para o ar, que sobe atrás da geladeira; rótulo "Condensador"'),
    ('F2', 'F24',     'F', 'traseira',  'Macro do tubo do condensador: vapor → gotas nas paredes → líquido; cor esfria de vermelho para laranja-claro'),
    ('G1', 'F25',     'G', 'traseira',  'Filtro secador e início do capilar'),
    ('G2', 'F26',     'G', 'capilar',   'Capilar ao lado da linha de sucção: comparação de diâmetro; rótulo "Capilar"'),
    ('G3', 'F27',     'G', 'capilar',   'Macro ao longo do capilar: manômetro cai, bolhas surgem a partir da metade, a cor vai para azul'),
    ('H1', 'F28',     'H', 'corte',     'A mistura entra de novo no evaporador; a câmera se afasta até o circuito inteiro'),
    ('H2', 'F29',     'H', 'corte',     'Sistema completo: calor entra no evaporador, trabalho no compressor, calor sai no condensador, fluxo contínuo'),
    ('I1', 'F30',     'I', 'cozinha',   'Volta à cozinha; a porta se abre e fica aberta'),
    ('I2', 'F31',     'I', 'cozinha',   'Ar frio escapa por baixo, ar da cozinha entra por cima: feixes de calor entrando; pulsos violeta mais rápidos'),
    ('I3', 'F32',     'I', 'cozinha',   'Cozinha fechada vista de cima: o calor entra pela frente e volta pela traseira para o MESMO cômodo'),
    ('I4', 'F33',     'I', 'cozinha',   'Balanço: faixa de entrada (Q̇_abs) + violeta (Ẇ) = faixa de saída mais larga; termômetro do cômodo sobe um pouco'),
    ('J1', 'F34',     'J', 'cozinha',   'Retoma o plano da abertura em visão térmica: frio dentro, quente fora'),
    ('J2', 'F35',     'J', 'cozinha',   'Imagem normal: nada de "frio" saindo do evaporador'),
    ('J3', 'F36',     'J', 'corte',     'Corte: um feixe de calor percorre o caminho do interior até a traseira pelo circuito'),
    ('J4', 'F37',     'J', 'cozinha',   'Geladeira fechada na cozinha; calor saindo discretamente pela traseira; fim na última palavra'),
]


def carregar_palavras():
    real = os.path.join(R, 'palavras.json')
    if os.path.exists(real): return json.load(open(real)), 'narração aprovada (palavras.json · alinhamento por pausas)'
    pz = os.path.join(R, 'palavras_pausas.json')
    if os.path.exists(pz): return json.load(open(pz))['palavras'], 'NARRAÇÃO RECEBIDA, alinhada por pausas (palavras não verificadas; não aprovada)'
    d = json.load(open(os.path.join(R, 'palavras_provisorio.json'))); return d['palavras'], 'PROVISÓRIO (palavras_provisorio.json)'


def frases(p):
    fr, cur = [], []
    for i, w in enumerate(p):
        cur.append(i)
        if w['palavra'][-1] in '.?!': fr.append(cur); cur = []
    return fr


def resolver(anc, p, fr):
    fim = anc.endswith('>'); a = anc.rstrip('>')
    n, _, k = a[1:].partition('.')
    idx = fr[int(n) - 1]
    if fim: return p[idx[-1]]['fim']
    return p[idx[int(k) - 1 if k else 0]]['inicio']


def resolvidos():
    p, origem = carregar_palavras(); fr = frases(p)
    assert len(fr) == 38, f'o roteiro deveria ter 38 frases, tem {len(fr)}'
    ts = [resolver(a, p, fr) for (_, a, _, _, _) in PLANOS]
    ts[0] = 0.0
    dur = round(p[-1]['fim'] + CAUDA, 2)
    out = []
    for i, (pid, anc, seq, cena, txt) in enumerate(PLANOS):
        t1 = ts[i + 1] if i + 1 < len(PLANOS) else dur
        # o corte acontece um pouco ANTES da palavra (antecipação de 0,25 s), como na montagem do Ep. 01
        t0 = max(0.0, ts[i] - 0.25) if i else 0.0
        t1 = (max(0.0, t1 - 0.25) if i + 1 < len(PLANOS) else t1)
        palavras = ' '.join(w['palavra'] for w in p if t0 <= w['inicio'] < t1)
        out.append(dict(id=pid, seq=seq, cena=cena, ancora=anc, t0=round(t0, 3), t1=round(t1, 3), dur=round(t1 - t0, 3), narrado=palavras, acontecimento=txt))
    return dict(origem=origem, duracao=dur, planos=out)


if __name__ == '__main__':
    r = resolvidos()
    json.dump(r, open(os.path.join(A, 'planos_resolvidos.json'), 'w'), ensure_ascii=False, indent=1)
    print('tempos:', r['origem'], '· duração', r['duracao'], 's')
    for q in r['planos']: print(f"{q['id']:3s} {q['t0']:7.2f}–{q['t1']:7.2f} ({q['dur']:4.1f} s) [{q['cena']:10s}] {q['narrado'][:70]}")
    longos = [q['id'] for q in r['planos'] if q['dur'] > 6.5]; curtos = [q['id'] for q in r['planos'] if q['dur'] < 1.4]
    print('planos > 6,5 s (precisam de acontecimento interno a cada 2–4 s):', longos); print('planos < 1,4 s:', curtos)
