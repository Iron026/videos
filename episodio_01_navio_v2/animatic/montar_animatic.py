"""Monta o animatic: planos 1–4 na linha do tempo global (30 fps), fusões, legendas da narração PROVISÓRIA
(só texto, nos planos 1–3), etiqueta de status, áudio (amostra real só na assinatura) → animatic_ep01.mp4
Uso: python3 animatic/montar_animatic.py
"""
import os, json, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

A = os.path.dirname(os.path.abspath(__file__)); FPS = 30; DUR = 19.5; W, H = 1080, 1920
FONTE = os.path.join(A, '..', 'fontes')
F_LEG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-800.ttf'), 60)
F_TAG = ImageFont.truetype(os.path.join(FONTE, 'Montserrat-700.ttf'), 30)
AZUL, BRANCO, AMARELO = (32, 43, 87), (246, 244, 236), (243, 181, 68)
PLANOS = [('p1', 0.00, 5.60), ('p23', 5.25, 15.15), ('p4', 14.80, 19.533)]
FUSOES = [(5.25, 5.60), (14.80, 15.15)]
# narração provisória (texto do roteiro aprovado; tempos estimados no ritmo medido da amostra, ~140 pal/min)
LEGENDAS = [(0.30, 2.45, 'Se eu jogar este bloco'), (2.45, 4.17, 'de aço na água,'), (4.17, 5.05, 'ele afunda.'),
            (5.50, 8.08, 'Mas e se eu usar toneladas'), (8.08, 10.23, 'do mesmo aço para construir'), (10.23, 11.10, 'um navio?'),
            (11.60, 12.50, 'Parece impossível.'), (12.90, 14.50, 'Então vamos montar um.')]


def quadro_plano(nome, t0, t):
    d = os.path.join(A, f'quadros_{nome}'); fs = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))
    i = min(max(int(round((t - t0) * FPS)), 0), len(fs) - 1)
    return Image.open(os.path.join(d, fs[i])).convert('RGB').resize((W, H))


def texto_contorno(dr, xy, txt, fonte, cor, contorno=7):
    dr.text(xy, txt, font=fonte, fill=cor, stroke_width=contorno, stroke_fill=(16, 22, 46), anchor='mm')


def etiqueta(img, txt):
    dr = ImageDraw.Draw(img); x0, y0 = 40, 120
    w = dr.textlength(txt, font=F_TAG) + 44
    dr.rounded_rectangle((x0, y0, x0 + w, y0 + 56), radius=28, fill=(*AZUL,)); dr.rounded_rectangle((x0, y0 + 50, x0 + w, y0 + 56), radius=3, fill=AMARELO)
    dr.text((x0 + 22, y0 + 27), txt, font=F_TAG, fill=BRANCO, anchor='lm')


def compor(t):
    ativos = [(n, t0, t1) for n, t0, t1 in PLANOS if t0 - 1e-6 <= t <= t1 + 1e-6]
    if len(ativos) == 1: img = quadro_plano(*ativos[0][:2], t)
    else:
        (na, ta, _), (nb, tb, _) = ativos[0], ativos[1]
        f0, f1 = next((a, b) for a, b in FUSOES if a - 1e-6 <= t <= b + 1e-6)
        k = (t - f0) / (f1 - f0); img = Image.blend(quadro_plano(na, ta, t), quadro_plano(nb, tb, t), max(0.0, min(1.0, k)))
    dr = ImageDraw.Draw(img)
    for a, b, txt in LEGENDAS:
        if a <= t < b: texto_contorno(dr, (W // 2, 1330), txt, F_LEG, BRANCO)
    if t < 14.95: etiqueta(img, 'ANIMATIC · narração definitiva pendente (texto)')
    else: etiqueta(img, 'Amostra real · Will - Deep (avaliação)')
    return img


if __name__ == '__main__':
    out = os.path.join(A, 'montagem'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    n = int(round(DUR * FPS))
    for i in range(n):
        compor(i / FPS).save(os.path.join(out, f'f{i:04d}.jpg'), quality=94)
    # áudio: loudness alvo −14 LUFS / −1,5 dBTP (duas passagens)
    au = os.path.join(A, 'audio_animatic.wav')
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', au, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rfind('{'):m.rfind('}') + 1])
    filtro = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    saida = os.path.join(A, 'animatic_ep01.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(out, 'f%04d.jpg'), '-i', au,
                    '-af', filtro, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                    '-metadata', 'title=De Olho no Invisível · Ep. 01 · animatic (avaliação)', saida], check=True)
    print('ok', saida, n, 'quadros')
