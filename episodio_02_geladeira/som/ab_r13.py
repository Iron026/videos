"""Rodada 13 — comparativos para aprovação (imagem IDÊNTICA: quadros do definitivo R12; só o áudio muda).
Cada trecho é precedido por uma cartela (1,4 s) que diz qual versão vem a seguir; a imagem dos trechos não recebe nada.
Saída: episodio/previas_r13/0{1..5}_*.mp4 (720 × 1280, H.264 CRF 20, AAC 192 kb/s) + previas_r13/trechos_r13.json
Uso: python3 ab_r13.py"""
import os, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..', 'episodio'); OUT = os.path.join(EP, 'previas_r13'); os.makedirs(OUT, exist_ok=True)
VID = os.path.join(EP, 'ep02_definitivo_r12_1080x1920.mp4'); W, H = 720, 1280
F = lambda t, s: ImageFont.truetype(os.path.join(A, '..', 'fontes', f'Montserrat-{t}.ttf'), s)
WAV = {'R12': os.path.join(A, 'audio_ep02_r12_musica_m5.wav')}
for k in ('ruido_isolado_r12', 'tom_de_comodo_isolado_r12', 'compressor_isolado_r12', 'r12_sem_ruido', 'base_musica_r13', 'efeitos_r12', 'efeitos_r13', 'r13_teste'):
    WAV[k] = os.path.join(A, f'audio_ep02_r13_{k}.wav')
WAV['base_musica_r13_mais'] = os.path.join(A, 'audio_ep02_r13_mais_base_musica_r13.wav')
TMP = tempfile.mkdtemp(prefix='ab_r13_')
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2']
n = [0]


def cartela(titulo, linhas, cor=(255, 214, 90)):
    im = Image.new('RGB', (W, H), (18, 22, 30)); d = ImageDraw.Draw(im); y = 470
    d.text((W // 2, y), titulo, font=F(800, 46), fill=cor, anchor='mm'); y += 80
    for l in linhas: d.text((W // 2, y), l, font=F(700, 27), fill=(235, 235, 240), anchor='mm'); y += 44
    n[0] += 1; png = os.path.join(TMP, f'c{n[0]:03d}.png'); im.save(png); mp4 = os.path.join(TMP, f'p{n[0]:03d}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', '1.4', '-i', png, '-f', 'lavfi', '-t', '1.4', '-i', 'anullsrc=r=48000:cl=stereo',
                    '-vf', 'fps=30', *ENC, '-shortest', mp4], check=True)
    return mp4


def trecho(t0, t1, wav, ganho_db=0.0):
    n[0] += 1; mp4 = os.path.join(TMP, f'p{n[0]:03d}.mp4'); d = t1 - t0
    af = f'volume={ganho_db}dB,afade=t=in:st=0:d=0.03,afade=t=out:st={d - 0.05:.3f}:d=0.05'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', VID, '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', wav,
                    '-map', '0:v', '-map', '1:a', '-vf', f'scale={W}:{H}:flags=lanczos', '-af', af, *ENC, mp4], check=True)
    return mp4


def juntar(nome, partes):
    lst = os.path.join(TMP, nome + '.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in partes))
    dst = os.path.join(OUT, nome); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', dst], check=True)
    print(dst, flush=True); return dst


tc = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'.replace('.', ',')
REG = {}
# 1 · ruído contínuo isolado (nível exato da R12; sem voz, música e efeitos)
P = [cartela('1 · Ruído contínuo isolado', ['Camadas que tocam o episódio INTEIRO na R12,', 'no nível exato da mixagem (sem voz, música', 'e efeitos). Abertura 0:00–0:10.']),
     trecho(0.0, 10.0, WAV['ruido_isolado_r12']),
     cartela('Tom de cômodo sozinho', ['Freesound 329568 "Room Tone Apartment"', 'presente 100 % do tempo, −37 LUFS constante', 'Encerramento 2:16–2:26']),
     trecho(136.0, 146.0, WAV['tom_de_comodo_isolado_r12']),
     cartela('Zumbido do compressor sozinho', ['Freesound 455776, ligado o episódio todo', 'forte nos planos internos (−21 LUFS no E3)', 'Compressor 1:14–1:24']),
     trecho(74.0, 84.0, WAV['compressor_isolado_r12']),
     cartela('Os dois juntos, +12 dB', ['amplificado só para ouvir o caráter:', 'zumbido de 120 Hz + ar/chiado de fundo', 'Abertura 0:00–0:08']),
     trecho(0.0, 8.0, WAV['ruido_isolado_r12'], 12.0)]
REG['01_ruido_isolado.mp4'] = 'abertura 0–10 (os dois) · 136–146 (tom de cômodo) · 74–84 (compressor) · 0–8 (+12 dB)'
juntar('01_ruido_isolado.mp4', P)


def ab(nome, titulo, trechos, versoes):
    partes = []
    for (t0, t1, rotulo) in trechos:
        for (letra, desc, wav) in versoes:
            partes += [cartela(f'{letra} · {desc}', [titulo, f'{rotulo} · {tc(t0)}–{tc(t1)}']), trecho(t0, t1, WAV[wav])]
    REG[nome] = dict(trechos=[(t0, t1, r) for t0, t1, r in trechos], versoes=[(l, d, os.path.basename(WAV[w])) for l, d, w in versoes])
    return juntar(nome, partes)


ab('02_ab_ruido.mp4', 'Ruído contínuo', [(0.0, 10.0, 'Abertura'), (38.0, 48.0, 'Fluido / circuito'), (72.0, 86.0, 'Compressor'), (136.0, 151.2, 'Encerramento')],
   [('A', 'R12 (como entregue)', 'R12'), ('B', 'R12 sem o ruído contínuo', 'r12_sem_ruido')])
ab('03_ab_musica.mp4', 'Presença da música (mesma base, sem ruído)', [(4.0, 14.5, 'Entrada da música'), (28.5, 40.0, 'Revelação do circuito'),
   (53.0, 64.0, 'Explicação contínua'), (107.3, 116.0, '"E tudo recomeça"'), (129.6, 151.2, 'Encerramento')],
   [('A', 'Música R12', 'r12_sem_ruido'), ('B', 'Nova presença musical', 'base_musica_r13'), ('C', 'Opção: música +3 dB', 'base_musica_r13_mais')])
ab('04_ab_efeitos.mp4', 'Efeitos (mesma música nova, sem ruído)', [(3.5, 9.0, 'Transição do rosto'), (11.5, 17.0, '"Não fabrica frio"'), (29.0, 39.0, 'Revelação do circuito'),
   (39.5, 51.5, 'Apresentações'), (71.4, 86.7, 'Compressor'), (86.5, 91.0, 'Condensador'), (99.0, 107.5, 'Capilar'), (115.5, 120.0, 'Leite')],
   [('A', 'Efeitos R12', 'efeitos_r12'), ('B', 'Efeitos revisados', 'efeitos_r13')])
ab('05_previa_combinada.mp4', 'Tudo junto: R12 × teste R13', [(0.0, 10.1, 'Abertura'), (28.5, 40.0, 'Revelação do circuito'), (53.0, 68.0, 'Demonstração: evaporador'),
   (71.4, 86.7, 'Compressor'), (86.7, 96.3, 'Condensador'), (96.3, 107.3, 'Capilar'), (115.6, 124.4, 'Retirada do leite'), (135.3, 151.2, 'Encerramento')],
   [('A', 'R12 (como entregue)', 'R12'), ('B', 'Teste R13', 'r13_teste')])
json.dump(REG, open(os.path.join(OUT, 'trechos_r13.json'), 'w'), ensure_ascii=False, indent=1)
