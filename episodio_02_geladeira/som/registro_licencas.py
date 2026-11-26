"""Registro de arquivos e licenças da mixagem (gerado dos dados, não à mão): usos_ep02.json (o que a mixagem usou, trecho e
função) × fontes_freesound.json (autor, página, licença conferida na página) + narração + síntese.
Saída: relatorios/licencas_ep02.md"""
import os, json, hashlib, glob
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..')
usos = json.load(open(os.path.join(A, 'usos_ep02.json'))); fontes = {f['id']: f for f in json.load(open(os.path.join(A, 'fontes_freesound.json')))}
mp3 = glob.glob(os.path.join(R, 'voz', '*.mp3'))[0]; h = hashlib.sha256(open(mp3, 'rb').read()).hexdigest()
L = ['# Ep. 02 · Registro de arquivos e licenças (mixagem da rodada 5)', '',
     '**Nada publicado.** Gerado de `som/usos_ep02.json` e `som/fontes_freesound.json`.', '',
     '## Narração', '',
     f'- `voz/{os.path.basename(mp3)}`: SHA-256 `{h}`. Arquivo **intocado**: a mixagem lê uma cópia decodificada.',
     '- **Licença PENDENTE.** O plano da ElevenLabs não foi confirmado. Até lá vale o tratamento do plano gratuito: **sem uso comercial**,',
     '  atribuição obrigatória. Nada foi gerado nem gasto nesta rodada.', '',
     '## Gravações (Freesound, todas CC0 1.0)', '',
     'CC0 = domínio público: uso comercial permitido e atribuição dispensada. Mesmo assim, os créditos ficam registrados aqui por',
     'procedência. A licença de cada som foi **conferida na página do som** no momento do download. O arquivo usado é a prévia HQ',
     '(MP3 128 kb/s) que o próprio Freesound serve. A pasta `som/bib/` fica fora do git: os arquivos são de terceiros e podem ser',
     'baixados de novo pelo id.', '',
     '| id | Título | Autor | Licença | Uso na mixagem | Página |', '|---|---|---|---|---|---|']
vistos = {}
for u in usos:
    if u.get('id', 'sintese') == 'sintese': continue
    vistos.setdefault(u['id'], []).append(u['uso'])
for i, us in vistos.items():
    f = fontes.get(i, {})
    L.append(f"| {i} | {f.get('titulo', '?')} | {f.get('autor', '?')} | {f.get('licenca', '?')} | {'; '.join(dict.fromkeys(us))} | {f.get('url_pagina', '')} |")
sint = [u for u in usos if u.get('id', 'sintese') == 'sintese']
L += ['', '## Síntese (gerada aqui, sem terceiros)', '']
L += [f"- {u.get('uso', '?')}: {u.get('titulo', 'síntese')} ({u['dur']:.2f} s, ruído filtrado 2,5–7 kHz, semente fixa 2026)" for u in sint] or ['- (nenhuma)']
L += ['', '## Não usados', '',
      '- **Mixkit:** nenhum arquivo (a busca deu erro 429, limite de acesso). **Wikimedia Commons:** nenhum arquivo (429).',
      '- **Música:** nenhuma. Nenhum som do YouTube, nenhuma licença CC BY-NC ou CC BY-SA.',
      '- **Reverb da cozinha:** resposta ao impulso **sintetizada** pelo módulo de síntese do Ep. 01 (`sintese.py`, lido sem',
      '  alteração; o ambiente "cozinha" é acrescentado em tempo de execução).', '',
      '## Honestidade sobre os sons', '',
      '- O zumbido é de **um** compressor de geladeira real (gravação CC0), não do modelo mostrado. O som não é apresentado como',
      '  gravação do equipamento do episódio.',
      '- O chiado do capilar é **síntese** (não havia gravação real adequada entre os candidatos) e fica discreto (−24 dB no evento).']
open(os.path.join(R, 'relatorios', 'licencas_ep02.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
