"""Rodada 13: baixa candidatos de efeitos do Mixkit (prévias públicas MP3) e registra procedência e licença.
Licença conferida em https://mixkit.co/license/modal/sfxFree/ (26/11/2026): "Mixkit Sound Effects Free License" — uso em
vídeos do YouTube, redes sociais, projetos comerciais e educacionais, SEM atribuição; PROIBIDO redistribuir o item isolado
(por isso os arquivos ficam em som/bib/mixkit_sfx/, fora do git; este script os baixa de novo).
Uso: python3 baixar_mixkit_sfx.py  → som/bib/mixkit_sfx/<id>.mp3 + som/fontes_mixkit_sfx.json"""
import os, json, time, subprocess, hashlib
A = os.path.dirname(os.path.abspath(__file__)); BIB = os.path.join(A, 'bib', 'mixkit_sfx'); os.makedirs(BIB, exist_ok=True)
REG = os.path.join(A, 'fontes_mixkit_sfx.json')
LIC = dict(nome='Mixkit Sound Effects Free License', url='https://mixkit.co/license/#sfxFree', conferida_em='2026-11-26',
           resumo='uso comercial e não comercial grátis (YouTube, redes sociais, educacional, filmes); sem atribuição; '
                  'proibido redistribuir o item isolado, como banco de sons, em ferramenta/template ou com arquivos-fonte; '
                  'proibido registrar em serviço de gestão de direitos (Content ID)')
CANDIDATOS = {   # id → (título no Mixkit, papel pretendido)
    '1489': ('Air woosh', 'whoosh'), '166': ('Fast small sweep transition', 'whoosh'), '175': ('Short transition sweep', 'whoosh'),
    '1474': ('Transition windy swoosh', 'whoosh'), '1168': ('Woosh wind', 'whoosh'), '1465': ('Vacuum swoosh transition', 'whoosh'),
    '2608': ('Air zoom vacuum', 'whoosh'), '1486': ('Cinematic tunnel reverb woosh', 'whoosh'), '1493': ('Swirling whoosh', 'whoosh'),
    '3005': ('Explainer video pops whoosh light pop', 'apresentacao'), '3120': ('Technology transition slide', 'whoosh'),
    '2615': ('Mighty mysterious swoosh', 'whoosh'), '1492': ('Cinematic whoosh fast transition', 'whoosh'), '1490': ('Fast whoosh transition', 'whoosh'),
    '1143': ('Cinematic whoosh deep impact', 'impacto'), '2902': ('Movie impact intro presentation', 'impacto'),
    '2917': ('Suspence cinematic impact', 'impacto'), '781': ('Cinematic impact waves', 'impacto'), '498': ('Deep heartbeat impact', 'impacto'),
    '772': ('Quick zoom impact', 'impacto'), '784': ('Reverse cinematic impact trailer', 'riser'), '2589': ('Shot light energy flowing', 'pulso'),
    '1317': ('Water bubble', 'bolhas'), '3000': ('Liquid bubble', 'bolhas'), '1321': ('Deep water bubbles', 'bolhas'),
    '2833': ('Pouring soda in a glass', 'bolhas'), '3126': ('Water flowing ambience loop', 'fluxo'), '1879': ('Bathroom sink water drip', 'gotas'),
    '2858': ('Gear metallic lock sound', 'valvula'), '2857': ('Gear fast lock tap', 'valvula'), '1131': ('Mechanical tool click', 'valvula'),
    '2585': ('On or off light switch tap', 'valvula'), '2364': ('Hard pop click', 'apresentacao'), '2358': ('Long pop', 'apresentacao'),
}
reg = {x['id']: x for x in json.load(open(REG))} if os.path.exists(REG) else {}
for i, (tit, papel) in CANDIDATOS.items():
    url = f'https://assets.mixkit.co/active_storage/sfx/{i}/{i}-preview.mp3'; dst = os.path.join(BIB, f'{i}.mp3')
    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
        subprocess.run(['curl', '-s', '-A', 'Mozilla/5.0', '-o', dst, url]); time.sleep(1.5)
    ok = os.path.exists(dst) and os.path.getsize(dst) > 1000
    reg[i] = dict(id=i, titulo=tit, papel=papel, fonte='Mixkit', url_pagina='https://mixkit.co/free-sound-effects/', url_arquivo=url,
                  arquivo_local=f'som/bib/mixkit_sfx/{i}.mp3', baixado=ok, sha256=hashlib.sha256(open(dst, 'rb').read()).hexdigest() if ok else None,
                  licenca=LIC['nome'], licenca_url=LIC['url'], atribuicao_exigida=False, obs='prévia pública MP3 do Mixkit; fora do git (licença proíbe redistribuir o item isolado)')
    print(i, tit, 'ok' if ok else 'FALHOU', flush=True)
json.dump(list(reg.values()), open(REG, 'w'), ensure_ascii=False, indent=1)
json.dump(LIC, open(os.path.join(A, 'licenca_mixkit_sfx.json'), 'w'), ensure_ascii=False, indent=1)
print('fim', len(reg))
