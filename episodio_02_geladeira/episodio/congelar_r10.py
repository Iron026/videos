"""Rodada 10: MANIFESTO DE CONGELAMENTO técnico (o que o render definitivo vai usar, com hashes para provar que nada mudou).
Registra versões (three.js, Playwright/Chromium, Node, FFmpeg), hashes do motor e dos scripts, a configuração única
(config/producao.json: perfis, obturadores, verificação), o hash de CADA cena dos 42 planos (+ cenas de sub-quadros),
as correções localizadas, os arquivos de áudio (narração, stems, mixagens) e as fontes/licenças.
Uso: python3 congelar_r10.py → relatorios/manifesto_congelamento_r10.json"""
import os, sys, json, hashlib, subprocess
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
def hcena(d):
    h = hashlib.sha256()
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
ver = lambda cmd: subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()[0]   # comandos fixos, sem shell
cfg = json.load(open(os.path.join(R, 'config', 'producao.json')))
sys.path.insert(0, os.path.join(R, 'decupagem')); import planos as PL
ids = [x for p in PL.resolvidos()['planos'] for x in ([p['id']] + ([p['id'] + 'b'] if p['id'] in ('A4', 'J1') else ['G3z'] if p['id'] == 'G3' else []))]
cen = {pid: hcena(os.path.join(A, 'cenas', pid)) for pid in ids}
cen.update({pid + '_obt': hcena(os.path.join(A, 'cenas', pid + '_obt')) for pid in cfg.get('obturador', {})})
arq = lambda *ps: {os.path.relpath(os.path.join(R, *p.split('/')), R): sha(os.path.join(R, *p.split('/'))) for p in ps}
m = dict(
    rodada=10, observacao='Gerado depois das correções da rodada 10; o render definitivo só começa com a aprovação do usuário e deve conferir este manifesto antes de cada plano (hash do motor, consulta e cena).',
    versoes=dict(three=json.load(open(os.path.join(R, 'motor', 'node_modules', 'three', 'package.json')))['version'],
                 playwright=json.load(open(os.path.join(R, 'motor', 'node_modules', 'playwright', 'package.json')))['version'] if os.path.exists(os.path.join(R, 'motor', 'node_modules', 'playwright', 'package.json')) else 'global',
                 node=ver(['node', '--version']), ffmpeg=ver(['ffmpeg', '-version']), navegador='Chromium (Playwright) + SwiftShader (ANGLE), sem GPU'),
    motor=arq('motor/render3.js', 'motor/render_anim.mjs', 'motor/index.html'),
    configuracao=dict(arquivo='config/producao.json', sha256=sha(os.path.join(R, 'config', 'producao.json')), perfil_final=cfg['perfis']['final'],
                      consulta_final=cfg['perfis']['final']['consulta'], antisserrilhado='MSAA 4× (render target com 4 amostras; MAX_SAMPLES do SwiftShader)',
                      ao='GTAO 16 amostras, raio/espessura por cena (meta ao_raio/ao_espessura), AO com corte + máscara das tampas onde aprovado',
                      bloom=0.18, correcao_de_cor='grade.py (curva em S leve, saturação +5 %, sombras frias/altas luzes quentes, vinheta −10 %) — aplicada na montagem',
                      obturadores=cfg.get('obturador', {}), fps=cfg['fps'], verificacao=cfg['verificacao'], quadro_jpeg='q95 (screenshot do Chromium)',
                      x264='CRF 17 (final), preset medium, yuv420p; áudio AAC 192 kb/s 48 kHz'),
    scripts=arq('episodio/render_definitivo.py', 'episodio/montar_ep02.py', 'episodio/montar_v9.sh', 'episodio/grade.py', 'episodio/legendas_r9.py', 'episodio/rotulos_r9.py',
                'blender/episodio02.py', 'blender/encenacao02.py', 'blender/geladeira.py', 'blender/ep_base.py', 'som/som_ep02.py', 'som/som_r10.py'),
    cenas=cen,
    correcoes_localizadas=[
        dict(onde='C4 q126–178', o_que='obturador 180°, 5 sub-quadros (aprovado na rodada 10)', prova='relatorios/testes_r10/c4_1080_obturador.json'),
        dict(onde='A4 q34', o_que='troca de câmera mais curta que 1 quadro: o quadro caía entre as chaves (parede vazia); câmera do fim da janela e visão térmica no mesmo instante', prova='relatorios/testes_r10/prova_reuso_A4.json (só q34 muda)'),
        dict(onde='C2 inteiro', o_que='obturador 180° (aprovado na rodada 8)'),
        dict(onde='A2', o_que='porta segue a curva física do A1 (rodada 9)'),
    ],
    audio=dict(narracao=arq('voz/ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3') if os.path.exists(os.path.join(R, 'voz', 'ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3')) else {},
               palavras=arq('roteiro/palavras.json'), mixagem_v9=arq('som/audio_ep02_v9.flac'),
               mixagens_r10={f: sha(os.path.join(R, 'som', f)) for f in ('audio_ep02_r10_efeitos.wav', 'audio_ep02_r10_musica.wav', 'audio_ep02_r10_completo.wav') if os.path.exists(os.path.join(R, 'som', f))},
               parametros=json.load(open(os.path.join(R, 'som', 'mix_ep02_r10.json'))) if os.path.exists(os.path.join(R, 'som', 'mix_ep02_r10.json')) else {}),
    licencas='relatorios/licencas_r10.md',
    criterios_validacao=dict(quadro='decodifica, luma média ≥ 3, ≥ 4000 bytes, semelhança com o anterior (corr ≥ 0,93 OU dif ≤ 6) ou salto justificado com prova',
                             composicao='testar_composicao_r9.py em todos os quadros: 0 sobreposições/cortes/zonas', audio='AAC: −14 ± 0,5 LUFS, pico verdadeiro ≤ −1,5 dBTP, voz − resto no celular p5 ≥ 10 dB, mono sem perda',
                             cintilacao='detector absoluto por plano comparado à versão aprovada; picos classificados por mapa'),
)
json.dump(m, open(os.path.join(R, 'relatorios', 'manifesto_congelamento_r10.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', len(cen), 'cenas')
