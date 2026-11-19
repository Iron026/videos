"""Mapa de substituição dos efeitos (para trocas depois da escuta): por grupo, cada som com instante, duração, gravação,
se é reserva, uso e o stem de grupo onde ele pode ser ouvido isolado. Gera som/mapa_substituicao.md."""
import os, json
from collections import defaultdict
A = os.path.dirname(os.path.abspath(__file__))
SUF = os.environ.get('SUFIXO_REG', 'hibrido'); NOME_SUF = {'hibrido': 'híbrido', 'refinado': 'refinado'}
usos = json.load(open(os.path.join(A, f'usos_{SUF}.json'))); mix = json.load(open(os.path.join(A, f'mix_{SUF}.json')))['stems_por_grupo']
NOMES = {'estaleiro': 'Estaleiro (ambiente, encaixe, solda, chapas, corte do casco)', 'guindastes': 'Guindastes (pórtico do estaleiro e portêineres)',
         'porto': 'Porto (ambiente, empilhadeiras, pousos de contêiner, água no casco)', 'dique': 'Dique (comporta, jatos, enchimento)',
         'inundacao': 'Inundação da avaria (ruptura, jato, porão enchendo, rangidos, divisórias)'}
g = defaultdict(list)
for u in usos: g[u.get('grupo')].append(u)
md = [f'# Mapa de substituição dos efeitos · Ep. 01 (som {NOME_SUF.get(SUF, SUF)})', '',
      'Cada grupo tem stems próprios em `episodio/stems/grupos/` (efeitos e ambiências), com a **mesma cadeia de mixagem** do episódio',
      '(reverberação, nível, ducking, fade e master). Somados ao `resto`, reconstroem exatamente os stems de efeitos e ambiências',
      '(erro máx. −132 dBFS). Dá para ouvir um grupo isolado, ou o episódio sem ele, e trocar só aquele grupo.', '',
      '**Como trocar uma gravação depois da escuta (sem editar código e sem refazer animação):**',
      '1. Coloque o arquivo novo em `episodio/som/bib/manual/`.',
      '2. Em `episodio/som/substituicoes.json`, adicione o **ID original** (coluna "Gravação") apontando para o arquivo, com título, autor, URL e licença.',
      f'3. Rode `python3 som/som_{SUF}.py && SUFIXO_REG={SUF} python3 som/registro_hibrido.py && SUFIXO_REG={SUF} python3 som/mapa_substituicao.py`.',
      '4. A troca entra nos mesmos instantes, camadas e níveis. Só a montagem 2D é refeita para o vídeo de revisão.', '',
      'Atenção: um mesmo ID pode ser usado em vários grupos (ex.: 3076, rangido do casco). A troca por ID vale para todos os usos dele.', '']
for k in ('estaleiro', 'guindastes', 'porto', 'dique', 'inundacao'):
    us = sorted(g.get(k, []), key=lambda u: u['t'])
    md += [f'## {NOMES[k]}', '']
    for st in ('efeitos', 'ambiencias'):
        x = mix.get(f'{k}/{st}')
        if x: md.append(f'- Stem: `{x["arquivo"]}` · ativo de {x["ativo_s"][0]} a {x["ativo_s"][1]} s')
    md += ['', '| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |', '|---|---|---|---|---|']
    for u in us:
        res = 'sim — no lugar de WWS ' + u['uso'].split('WWS ')[1].split(' ')[0] if 'RESERVA' in u['uso'] else ('síntese' if u['id'] == 'sintese' else 'não')
        uso = u['uso'].split(' [RESERVA')[0]
        md.append(f"| {u['t']:.2f} | {u['dur']:.2f} | {u['id']} · {u['titulo']} | {res} | {uso} |")
    md.append('')
outros = [u for u in usos if not u.get('grupo')]
md += ['## Demais efeitos (abertura, empuxo, retomada, experimento, conclusão)', '',
       f'{len(outros)} usos, no stem `resto`. A lista completa por gravação está em `som/fontes_efeitos_{SUF}.md`.', '']
open(os.path.join(A, 'mapa_substituicao.md' if SUF == 'hibrido' else f'mapa_substituicao_{SUF}.md'), 'w').write('\n'.join(md) + '\n')
print({k: len(v) for k, v in g.items()})
