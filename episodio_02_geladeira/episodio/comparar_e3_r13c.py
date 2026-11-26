"""Rodada 13C — comparativo VISUAL em 1080 do E3 (1:17–1:24): definitivo × correção da bobina (e, opcional, corte seco
E2 → E3). Usa quadros COMPOSTOS pela montagem real (compor_janela_r13c.py → PNG), sem recodificar nada no meio.
Saídas (episodio/previas_r13c):
 05_e3_1080_lado_a_lado.mp4   2160×1920, velocidade normal, áudio R13C (moderada) do trecho
 06_e3_1080_camera_lenta.mp4  2160×1920, 1/4 da velocidade (cada quadro 4×), sem áudio
 07_e3_detalhe_motor.mp4      recorte do motor ampliado 2× (onde estava o defeito), lado a lado, 1/4 da velocidade
 08_e2_e3_transicao_opcao.mp4 fusão atual × corte seco (opção desligada), 1/4 da velocidade
Uso: python3 comparar_e3_r13c.py <png_A> <png_B> <png_C>"""
import os, sys, subprocess, glob
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(A, 'previas_r13c'); os.makedirs(OUT, exist_ok=True)
pa, pb, pc = sys.argv[1:4]; FPS = 30; SUF = os.environ.get('SUF_CMP', '')   # 2ª parte: _v2 (bobina + bloco)
F = lambda s: ImageFont.truetype(os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf'), s)
qs = sorted(int(os.path.basename(f)[1:6]) for f in glob.glob(os.path.join(pa, 'c*.png')))
AUD = os.path.join(A, '..', 'som', 'audio_ep02_r13_r13c_moderada_r13_teste.wav')
def enc(nome, frames, repetir=1, audio=None, t0=None):
    w, h = frames[0][1]
    args = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-']
    if audio: args += ['-ss', f'{t0:.4f}', '-t', f'{len(frames) * repetir / FPS:.4f}', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k']
    args += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, nome)]
    p = subprocess.Popen(args, stdin=subprocess.PIPE)
    for f, _ in frames:
        b = f().tobytes()
        for _ in range(repetir): p.stdin.write(b)
    p.stdin.close(); p.wait(); print(os.path.join(OUT, nome), flush=True)
enc0 = enc
def enc(nome, *a, **k): return enc0(nome.replace('.mp4', SUF + '.mp4'), *a, **k)
def par(q, da, db, ta, tb, caixa=None, esc=1):
    def f():
        a = Image.open(os.path.join(da, f'c{q:05d}.png')).convert('RGB'); b = Image.open(os.path.join(db, f'c{q:05d}.png')).convert('RGB')
        if caixa: a, b = a.crop(caixa), b.crop(caixa)
        if esc != 1: a, b = a.resize((a.width * esc, a.height * esc), Image.LANCZOS), b.resize((b.width * esc, b.height * esc), Image.LANCZOS)
        im = Image.new('RGB', (a.width * 2 + 16, a.height + 90), (14, 18, 26)); im.paste(a, (0, 90)); im.paste(b, (a.width + 16, 90)); d = ImageDraw.Draw(im)
        d.text((a.width // 2, 45), ta, font=F(40), fill=(255, 214, 90), anchor='mm'); d.text((a.width + 16 + b.width // 2, 45), tb, font=F(40), fill=(120, 230, 150), anchor='mm')
        g = q / FPS; d.text((im.width // 2, 45), f'{int(g // 60)}:{g % 60:05.2f}', font=F(30), fill=(235, 235, 240), anchor='mm')
        return im
    a0 = Image.open(os.path.join(da, f'c{qs[0]:05d}.png')); w, h = (caixa[2] - caixa[0], caixa[3] - caixa[1]) if caixa else a0.size
    return (f, ((w * esc) * 2 + 16, h * esc + 90))
enc('05_e3_1080_lado_a_lado.mp4', [par(q, pa, pb, 'A · definitivo R12', 'B · corrigido R13C') for q in qs], 1, AUD, qs[0] / FPS)
enc('06_e3_1080_camera_lenta.mp4', [par(q, pa, pb, 'A · definitivo (1/4 vel.)', 'B · corrigido (1/4 vel.)') for q in qs if 2335 <= q <= 2500], 4)
CX = (180, 1240, 760, 1900)   # motor: bobina de baixo, estator e cunha da junção de cima
enc('07_e3_detalhe_motor.mp4', [par(q, pa, pb, 'A · definitivo (2×)', 'B · corrigido (2×)', CX, 2) for q in qs if 2340 <= q <= 2500], 4)
CP = (640, 540, 1040, 1140)   # 2ª parte: placa de válvulas (onde o pistão chega ao fim do curso)
enc('07b_e3_detalhe_placa.mp4', [par(q, pa, pb, 'A · definitivo (2×)', 'B · corrigido (2×)', CP, 2) for q in qs if 2340 <= q <= 2500], 4)
enc('08_e2_e3_transicao_opcao.mp4', [par(q, pb, pc, 'B · fusão 0,2 s (atual)', 'C · corte seco (opção)') for q in qs if 2328 <= q <= 2362 and os.path.exists(os.path.join(pc, f'c{q:05d}.png'))], 4)
