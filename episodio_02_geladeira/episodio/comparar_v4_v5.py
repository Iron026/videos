"""Comparativo V4 × V5 (rodada 5: polimento + primeira mixagem).
1. Estrutura: planos_resolvidos da V4 × atual (cortes, durações, ids) — devem ser IDÊNTICOS (polimento não muda tempo).
2. Folhas antes × depois: 1 quadro por plano no meio (V4 em cima, V5 embaixo), tirados dos dois mp4 nos mesmos instantes.
3. Vídeo lado a lado V4 | V5 com o áudio da V5.
4. Diferença média por plano (V4 × V5 montados, 4 quadros por plano, 0–255) para mostrar ONDE mudou.
Uso: python3 comparar_v4_v5.py <planos_resolvidos_v4.json> <ep02_animatic_v4.mp4> <ep02_animatic_v5.mp4>"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); REL = os.path.join(RAIZ, 'relatorios')
V4P = json.load(open(sys.argv[1]))['planos']; V5P = json.load(open(os.path.join(RAIZ, 'decupagem', 'planos_resolvidos.json')))['planos']
v4, v5 = sys.argv[2], sys.argv[3]
fonte = ImageFont.truetype(os.path.join(RAIZ, 'fontes', 'Montserrat-800.ttf'), 15)
chaves = ('id', 't0', 't1', 'dur')
estr = dict(planos_v4=len(V4P), planos_v5=len(V5P),
            identicos=[{k: p.get(k) for k in chaves} for p in V4P] == [{k: p.get(k) for k in chaves} for p in V5P],
            duracao_v4=round(V4P[-1]['t1'], 3), duracao_v5=round(V5P[-1]['t1'], 3))
dif_pl = [{k: (a.get(k), b.get(k)) for k in chaves if a.get(k) != b.get(k)} | {'id': a['id']} for a, b in zip(V4P, V5P) if any(a.get(k) != b.get(k) for k in chaves)]
estr['diferencas'] = dif_pl


def quadro(video, t, w=270):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', f'scale={w}:-2', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       capture_output=True, check=True).stdout
    return Image.frombytes('RGB', (w, len(r) // (w * 3)), r)


por_plano = []
for p in V5P:
    ts = [p['t0'] + (p['t1'] - p['t0']) * f for f in (0.15, 0.4, 0.65, 0.9)]
    d = [float(np.abs(np.asarray(quadro(v4, t), np.float32) - np.asarray(quadro(v5, t), np.float32)).mean()) for t in ts]
    por_plano.append(dict(id=p['id'], ini=p['t0'], fim=p['t1'], dif_media=round(float(np.mean(d)), 2), dif_max_quadro=round(max(d), 2)))
    print(por_plano[-1]['id'], por_plano[-1]['dif_media'], flush=True)
json.dump(dict(estrutura=estr, por_plano=por_plano), open(os.path.join(REL, 'v4_x_v5_montado.json'), 'w'), ensure_ascii=False, indent=1)

# folhas: 7 planos por folha, V4 em cima / V5 embaixo
lote = 7; folhas = []
for f0 in range(0, len(V5P), lote):
    grupo = V5P[f0:f0 + lote]; W, H = 270, 480
    fol = Image.new('RGB', (len(grupo) * (W + 4), 2 * (H + 4) + 22), (30, 30, 30)); d = ImageDraw.Draw(fol)
    for k, p in enumerate(grupo):
        t = (p['t0'] + p['t1']) / 2
        for lin, vid, rot in ((0, v4, 'V4'), (1, v5, 'V5')):
            im = quadro(vid, t); x, y = k * (W + 4), 22 + lin * (H + 4); fol.paste(im, (x, y))
            dd = ImageDraw.Draw(fol); dd.rectangle([x, y, x + 110, y + 20], fill=(0, 0, 0)); dd.text((x + 4, y + 2), f"{rot} {p['id']} {t:.1f}s", font=fonte, fill=(255, 230, 0))
    d.text((6, 3), 'em cima: V4 (aprovada)  ·  embaixo: V5 (polimento)  ·  mesmo instante', font=fonte, fill=(230, 230, 230))
    nome = os.path.join(REL, f'antes_depois_v5_{f0 // lote + 1}.jpg'); fol.save(nome, quality=86); folhas.append(nome)
print('folhas', folhas)

# vídeo lado a lado
lado = os.path.join(A, 'ep02_v4_x_v5_lado_a_lado.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v4, '-i', v5, '-filter_complex',
                '[0:v]scale=360:640[a];[1:v]scale=360:640[b];[a][b]hstack=inputs=2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text=V4:x=8:y=8:fontsize=20:fontcolor=yellow,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text=V5:x=368:y=8:fontsize=20:fontcolor=yellow[v]',
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '22', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '192k', lado], check=True)
print(json.dumps(estr, ensure_ascii=False))
