"""Rodada 13C — comparativos de som para aprovação (imagem IDÊNTICA: quadros do definitivo R12; só o áudio muda).
Cada trecho é precedido por uma cartela (1,4 s) que diz qual versão vem a seguir. A = R13B (como você ouviu).
Saída: episodio/previas_r13c/0{1,2,3}_*.mp4 (720 × 1280, H.264 CRF 20, AAC 192 kb/s) + previas_r13c/trechos_r13c.json
Uso: python3 ab_r13c.py"""
import os, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..', 'episodio'); OUT = os.path.join(EP, 'previas_r13c'); os.makedirs(OUT, exist_ok=True)
VID = os.path.join(EP, 'ep02_definitivo_r12_1080x1920.mp4'); W, H = 720, 1280
F = lambda t, s: ImageFont.truetype(os.path.join(A, '..', 'fontes', f'Montserrat-{t}.ttf'), s)
WAV = {'R13B': os.path.join(A, 'audio_ep02_r13_r13_teste.wav'),
       'moderada': os.path.join(A, 'audio_ep02_r13_r13c_moderada_r13_teste.wav'),
       'discreta': os.path.join(A, 'audio_ep02_r13_r13c_discreta_r13_teste.wav')}
TMP = tempfile.mkdtemp(prefix='ab_r13c_')
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


def trecho(t0, t1, wav):
    n[0] += 1; mp4 = os.path.join(TMP, f'p{n[0]:03d}.mp4'); d = t1 - t0
    af = f'afade=t=in:st=0:d=0.03,afade=t=out:st={d - 0.05:.3f}:d=0.05'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', VID, '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', wav,
                    '-map', '0:v', '-map', '1:a', '-vf', f'scale={W}:{H}:flags=lanczos', '-af', af, *ENC, mp4], check=True)
    return mp4


def juntar(nome, partes):
    lst = os.path.join(TMP, nome + '.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in partes))
    dst = os.path.join(OUT, nome); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', dst], check=True)
    print(dst, flush=True); return dst


tc = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'.replace('.', ',')
REG = {}


def ab(nome, titulo, trechos, versoes):
    partes = []
    for (t0, t1, rotulo) in trechos:
        for (letra, desc, wav) in versoes:
            partes += [cartela(f'{letra} · {desc}', [titulo, f'{rotulo} · {tc(t0)}–{tc(t1)}']), trecho(t0, t1, WAV[wav])]
    REG[nome] = dict(trechos=[(t0, t1, r) for t0, t1, r in trechos], versoes=[(l, d, os.path.basename(WAV[w])) for l, d, w in versoes])
    return juntar(nome, partes)


ab('01_efeitos_retirados_014_112_148.mp4', 'Efeitos retirados (nada no lugar)',
   [(11.8, 17.2, '0:14 impacto depois de "não fabrica frio."'), (70.4, 75.4, '1:12 whoosh da descida (E1)'), (106.8, 112.0, '1:48 sopro do recuo (H1)')],
   [('A', 'R13B (como você ouviu)', 'R13B'), ('B', 'R13C: efeito retirado', 'moderada')])
ab('02_revelacao_033.mp4', 'Revelação do circuito ("Escondido…")', [(29.0, 39.5, '0:33')],
   [('A', 'R13B (como você ouviu)', 'R13B'), ('B', 'Redução moderada', 'moderada'), ('C', 'Mais discreta', 'discreta')])
ab('03_passos_155.mp4', 'Passos na cozinha (perspectiva da câmera)', [(114.6, 121.0, '1:55')],
   [('A', 'R13B (como você ouviu)', 'R13B'), ('B', 'R13C: passos discretos', 'moderada')])
json.dump(REG, open(os.path.join(OUT, 'trechos_r13c.json'), 'w'), ensure_ascii=False, indent=1)
