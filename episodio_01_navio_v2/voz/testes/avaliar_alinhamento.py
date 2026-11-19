"""Avalia a precisão de comparar_narracao.py numa narração simulada (simular_narracao.py). Uso: python3 voz/testes/avaliar_alinhamento.py <sim.wav> <pasta_saida_da_ferramenta>"""
import os
import json, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); import comparar_narracao as CN
sim, saida = sys.argv[1], sys.argv[2]; v = json.load(open(sim + '.verdade.json')); r = json.load(open(saida + '/comparacao_tempos.json'))
pal = json.load(open(CN.TRAB + '/palavras.json'))
a = CN.carregar(CN.TRAB + '/narracao_48k.wav'); b = CN.carregar(sim); f = CN.alinhar(a, b)
ep = np.array([float(f(pal[int(i)]['inicio'])) - t for i, t in v['palavras'].items()]) * 1000
ef = np.array([r['frases'][int(k)]['inicio_novo'] - t for k, t in v['frases'].items()]) * 1000
print('palavras (%d): erro mediana %.0f ms · p95 %.0f ms · máx %.0f ms' % (len(ep), np.median(np.abs(ep)), np.percentile(np.abs(ep), 95), np.abs(ep).max()))
print('inícios de frase (%d): mediana %.0f ms · p95 %.0f ms · máx %.0f ms' % (len(ef), np.median(np.abs(ef)), np.percentile(np.abs(ef), 95), np.abs(ef).max()))
print(json.dumps(r['sem_encaixe'], ensure_ascii=False)); print(json.dumps({k: v for k, v in r['com_encaixe'].items() if k != 'blocos_acima_do_limite'}, ensure_ascii=False))
print('blocos acima do limite:', [(b['bloco'], b['fator']) for b in r['com_encaixe']['blocos_acima_do_limite']])
