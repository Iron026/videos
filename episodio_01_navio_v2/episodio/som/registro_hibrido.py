"""Registro de fontes e licenças do som HÍBRIDO (a partir de usos_hibrido.json): uma linha por gravação, com biblioteca,
autor, URLs, licença, crédito exigido, arquivo local e onde foi usada. Gera fontes_efeitos_hibrido.json / .md e
creditos_descricao.txt (texto pronto para a descrição do vídeo, exigido pela CC BY 4.0)."""
import os, json
from collections import defaultdict
A = os.path.dirname(os.path.abspath(__file__))
MIX = {x['id']: x for x in json.load(open(os.path.join(A, 'candidatos_mixkit.json')))}
COM = {x['id']: x for x in json.load(open(os.path.join(A, 'fontes_commons.json')))}
usos = json.load(open(os.path.join(A, 'usos_hibrido.json')))
por_id = defaultdict(list)
for u in usos: por_id[u['id']].append(u)
lin, sint = [], []
for i, us in sorted(por_id.items(), key=lambda kv: (isinstance(kv[0], str), str(kv[0]))):
    onde = sorted({(round(u['t'], 1), u['uso']) for u in us})
    if i == 'sintese': sint = onde; continue
    if isinstance(i, int):
        x = MIX[i]; lin.append(dict(id=i, nome=x['titulo'], biblioteca='Mixkit', autor='Mixkit (Envato); a página não identifica o artista', url_original=x['url_pagina'],
                                    url_arquivo=x['url_arquivo'], licenca='Mixkit Sound Effects Free License', url_licenca='https://mixkit.co/license/#sfxFree',
                                    atribuicao_exigida=False, credito='', arquivo_local=x['arquivo_local'], voz_detectada=bool(x.get('voz_detectada')), usos=onde))
    else:
        x = COM[i]; lin.append(dict(id=i, nome=x['titulo'], biblioteca='Wikimedia Commons (Work With Sounds)', autor=x['autor'], url_original=x['pagina'],
                                    url_arquivo=x['url_arquivo'].split('?')[0], licenca=x['licenca'], url_licenca=x['licenca_url'], atribuicao_exigida=True,
                                    credito=x['credito'], arquivo_local=x['arquivo_local'], voz_detectada=x.get('voz_detectada'), usos=onde))
json.dump(dict(gravacoes=lin, sintese=sint), open(os.path.join(A, 'fontes_efeitos_hibrido.json'), 'w'), ensure_ascii=False, indent=1)
nm = sum(1 for x in lin if x['biblioteca'] == 'Mixkit'); nc = len(lin) - nm
md = ['# Som híbrido do Ep. 01 · fontes, licenças e usos', '',
      f'{len(lin)} gravações reais ({nm} Mixkit · {nc} Wikimedia Commons) · {sum(len(x["usos"]) for x in lin)} usos · {len(sint)} complementos sintéticos', '',
      '## Licenças', '',
      '- **Mixkit — Mixkit Sound Effects Free License** (https://mixkit.co/license/#sfxFree): uso em vídeos do YouTube e projetos comerciais e monetizados permitido; atribuição não exigida; proibido redistribuir o arquivo isolado e registrá-lo em Content ID. Os arquivos ficam fora do git (`som/baixar_efeitos.py`).',
      '- **Wikimedia Commons / Work With Sounds — CC BY 4.0** (https://creativecommons.org/licenses/by/4.0): uso comercial e monetizado permitido, inclusive com edição; **atribuição obrigatória** (texto pronto em `som/creditos_descricao.txt`, para a descrição do vídeo). Nenhum arquivo CC BY-NC, CC BY-SA, de procedência duvidosa ou extraído de vídeo foi usado.', '',
      '## Gravações', '', '| ID | Nome | Biblioteca | Autor | URL | Licença | Crédito exigido | Arquivo local | Onde foi usado |', '|---|---|---|---|---|---|---|---|---|']
for x in lin:
    onde = '; '.join(f'{u} ({t} s)' for t, u in x['usos'][:6]) + (f' … (+{len(x["usos"]) - 6})' if len(x['usos']) > 6 else '')
    md.append(f"| {x['id']} | {x['nome']} | {x['biblioteca']} | {x['autor']} | {x['url_original']} | {x['licenca']} | {x['credito'] or 'não'} | `{x['arquivo_local']}` | {onde} |")
md += ['', '## Complementos sintéticos (originais, sem licença de terceiros)', '', *[f'- {t} s · {u}' for t, u in sint]]
open(os.path.join(A, 'fontes_efeitos_hibrido.md'), 'w').write('\n'.join(md) + '\n')
cred = ['Efeitos sonoros:', '- Mixkit (Mixkit Sound Effects Free License).']
cred += [f'- {x["credito"]}' for x in lin if x['atribuicao_exigida']]
open(os.path.join(A, 'creditos_descricao.txt'), 'w').write('\n'.join(cred) + '\n')
print(len(lin), 'gravações;', nc, 'Commons;', len(sint), 'sínteses')
