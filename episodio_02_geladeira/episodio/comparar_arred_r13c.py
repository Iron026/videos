"""Rodada 13C — comparativo do "início travado": quadros repetidos (15 qps efetivos) em planos com g0 a meio quadro.
A = montagem aprovada (round() com empate para o par); B = ARRED_QUADROS=1 (empate sempre para o quadro seguinte).
Quadros COMPOSTOS pela montagem real (compor_janela_r13c.py), 1080, lado a lado. Saídas (episodio/previas_r13c):
 09_quadros_repetidos_lado_a_lado.mp4  A1 · B7 · H1 · I1 em velocidade normal (com o áudio final do trecho)
 10_quadros_repetidos_camera_lenta.mp4 os mesmos a 1/4 da velocidade (sem áudio)
Uso: python3 comparar_arred_r13c.py <pasta_png_raiz>  (subpastas <plano>_A e <plano>_B)"""
import os, sys, subprocess, glob, tempfile
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(A, 'previas_r13c'); raiz = sys.argv[1]; FPS = 30
F = lambda s: ImageFont.truetype(os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf'), s)
AUD = os.path.join(A, '..', 'som', 'audio_ep02_r13_r13c_final_r13_teste.wav')
TMP = tempfile.mkdtemp(prefix='arred_r13c_')
def lado(q, pid):
    a = Image.open(os.path.join(raiz, f'{pid}_A', f'c{q:05d}.png')).convert('RGB'); b = Image.open(os.path.join(raiz, f'{pid}_B', f'c{q:05d}.png')).convert('RGB')
    im = Image.new('RGB', (a.width * 2 + 16, a.height + 90), (14, 18, 26)); im.paste(a, (0, 90)); im.paste(b, (a.width + 16, 90)); d = ImageDraw.Draw(im)
    d.text((a.width // 2, 45), 'A · aprovado (quadros repetidos)', font=F(36), fill=(255, 214, 90), anchor='mm')
    d.text((a.width + 16 + b.width // 2, 45), 'B · corrigido (30 qps)', font=F(36), fill=(120, 230, 150), anchor='mm')
    g = q / FPS; d.text((im.width // 2, 45), f'{pid} {int(g // 60)}:{g % 60:05.2f}', font=F(28), fill=(235, 235, 240), anchor='mm'); return im
def video(nome, rep, com_audio):
    partes = []
    for pid in ('A1', 'B7', 'H1', 'I1'):
        qs = sorted(int(os.path.basename(f)[1:6]) for f in glob.glob(os.path.join(raiz, f'{pid}_A', 'c*.png')))
        im0 = lado(qs[0], pid); w, h = im0.size; seg = os.path.join(TMP, f'{nome}_{pid}.mp4')
        args = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-']
        if com_audio: args += ['-ss', f'{qs[0] / FPS:.4f}', '-t', f'{len(qs) / FPS:.4f}', '-i', AUD, '-map', '0:v', '-map', '1:a']
        else: args += ['-f', 'lavfi', '-t', f'{len(qs) * rep / FPS:.4f}', '-i', 'anullsrc=r=48000:cl=stereo', '-map', '0:v', '-map', '1:a']
        args += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', seg]
        p = subprocess.Popen(args, stdin=subprocess.PIPE)
        for q in qs:
            b = lado(q, pid).tobytes()
            for _ in range(rep): p.stdin.write(b)
        p.stdin.close(); p.wait(); partes.append(seg)
    lst = os.path.join(TMP, nome + '.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in partes))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', os.path.join(OUT, nome)], check=True)
    print(os.path.join(OUT, nome), flush=True)
video('09_quadros_repetidos_lado_a_lado.mp4', 1, True)
video('10_quadros_repetidos_camera_lenta.mp4', 4, False)
