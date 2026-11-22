"""Busca gravações REAIS no Freesound restritas à licença CC0 (domínio público: uso comercial livre, sem atribuição),
confere a licença na página de cada som e baixa a prévia em alta qualidade (MP3 128 kb/s, pública, sem login).
Consultas espaçadas (3 s) para não esbarrar em limite de requisições. Os arquivos ficam em som/bib/freesound/ (fora do
git; este script os baixa de novo); o REGISTRO (título, autor, URL, licença, etiquetas) fica em som/fontes_freesound.json.
Uso: python3 buscar_freesound.py"""
import os, re, json, time, html, subprocess, urllib.parse
A = os.path.dirname(os.path.abspath(__file__)); BIB = os.path.join(A, 'bib', 'freesound'); os.makedirs(BIB, exist_ok=True)
REG = os.path.join(A, 'fontes_freesound.json')
UA = 'Mozilla/5.0'
CONSULTAS = {   # papel no episódio → termos (só CC0)
    'porta': ['refrigerator door', 'fridge door open', 'fridge door close'],
    'zumbido': ['refrigerator hum', 'fridge hum', 'fridge compressor'],
    'gorgolejo': ['refrigerator gurgle', 'fridge gurgling', 'refrigerator bubbling'],
    'chiado': ['refrigerator hiss', 'fridge hiss'],
    'partida': ['refrigerator compressor start', 'fridge click relay'],
    'cozinha': ['kitchen room tone', 'kitchen ambience quiet', 'apartment room tone'],
    'passos': ['footsteps tile floor', 'footsteps kitchen', 'footsteps indoor'],
}
POR_CONSULTA = 5


def get(url, tent=4):
    for k in range(tent):
        r = subprocess.run(['curl', '-s', '-A', UA, '-w', '\n%{http_code}', url], capture_output=True, text=True)
        corpo, _, cod = r.stdout.rpartition('\n')
        if cod == '200': return corpo
        time.sleep(10 * (k + 1))
    return None


reg = {x['id']: x for x in json.load(open(REG))} if os.path.exists(REG) else {}
for papel, termos in CONSULTAS.items():
    for q in termos:
        url = 'https://freesound.org/search/?' + urllib.parse.urlencode({'q': q, 'f': 'license:"Creative Commons 0"'})
        h = get(url); time.sleep(3)
        if not h: print('falhou', q); continue
        achados = []
        for m in re.finditer(r'href="/people/([^"/]+)/sounds/(\d+)/"', h):
            if m.group(2) not in [a[1] for a in achados]: achados.append((m.group(1), m.group(2)))
        for (user, sid) in achados[:POR_CONSULTA]:
            if sid in reg: reg[sid]['papeis'] = sorted(set(reg[sid]['papeis'] + [papel])); continue
            pg = f'https://freesound.org/people/{user}/sounds/{sid}/'; p = get(pg); time.sleep(3)
            if not p: continue
            lic = 'CC0 1.0' if 'creativecommons.org/publicdomain/zero/1.0' in p else None
            hq = re.search(r'previews/\d+/[0-9_]+-hq\.mp3', p)
            tit = re.search(r'<meta property="og:audio:title" content="([^"]*)"', p)
            desc = re.search(r'<meta property="og:description" content="([^"]*)"', p) or re.search(r'<meta name="description" content="([^"]*)"', p)
            tags = re.findall(r'"/browse/tags/([^"/]+)/"', p)
            if not (lic and hq): print('pulado (licença/arquivo)', sid); continue
            dst = os.path.join(BIB, f'{sid}.mp3')
            if not os.path.exists(dst):
                subprocess.run(['curl', '-s', '-A', UA, '-o', dst, 'https://cdn.freesound.org/' + hq.group(0)]); time.sleep(2)
            reg[sid] = dict(id=sid, titulo=html.unescape(tit.group(1)) if tit else '', autor=user, url_pagina=pg,
                            url_arquivo='https://cdn.freesound.org/' + hq.group(0), licenca=lic, atribuicao_exigida=False,
                            arquivo_local=f'som/bib/freesound/{sid}.mp3', papeis=[papel], consulta=q,
                            descricao=html.unescape(desc.group(1))[:300] if desc else '', etiquetas=sorted(set(tags))[:20],
                            obs='prévia pública em MP3 128 kb/s do Freesound (o original exige login)')
            print(papel, sid, reg[sid]['titulo'], flush=True)
            json.dump(list(reg.values()), open(REG, 'w'), ensure_ascii=False, indent=1)
json.dump(list(reg.values()), open(REG, 'w'), ensure_ascii=False, indent=1)
print('fim', len(reg))
