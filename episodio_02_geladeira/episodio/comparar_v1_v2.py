"""Comparativo v1 × v2 do animatic do Ep. 02.
1. Planos com os MESMOS tempos nas duas versões: compara quadro a quadro (mesmos índices) os JPEG renderizados
   (quadros_animatic_v1/ × quadros_animatic/): bytes idênticos, diferença média e máxima (0–255) e % de pixels com |Δ| > 8.
2. Folhas antes × depois dos planos alterados: 4 quadros por plano (10/37/63/90 % do plano em cada versão), tirados dos mp4.
3. Vídeo lado a lado (v1 | v2) com o áudio da v2.
Uso: python3 comparar_v1_v2.py <planos_resolvidos_v1.json> [ruido.json]"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); REL = os.path.join(RAIZ, 'relatorios')
V1 = {p['id']: p for p in json.load(open(sys.argv[1]))['planos']}
V2 = {p['id']: p for p in json.load(open(os.path.join(RAIZ, 'decupagem', 'planos_resolvidos.json')))['planos']}
ALTERADOS = json.load(open(os.path.join(REL, 'alteracoes_v2.json')))['planos_alterados']
ids = [p for p in V1] + ['A4b', 'J1b']
fonte = ImageFont.truetype(os.path.join(RAIZ, 'fontes', 'Montserrat-800.ttf'), 16)

def cmp_plano(pid):
    d1, d2 = os.path.join(A, 'quadros_animatic_v1', pid), os.path.join(A, 'quadros_animatic', pid)
    f1 = sorted(f for f in os.listdir(d1) if f.endswith('.jpg')); f2 = sorted(f for f in os.listdir(d2) if f.endswith('.jpg'))
    if f1 != f2: return dict(plano=pid, comparavel=False, motivo=f'quadros diferentes ({len(f1)} × {len(f2)})')
    iguais = 0; medias = []; maxs = []; frac = []
    for f in f1:
        b1, b2 = open(os.path.join(d1, f), 'rb').read(), open(os.path.join(d2, f), 'rb').read()
        if b1 == b2: iguais += 1; medias.append(0.0); maxs.append(0); frac.append(0.0); continue
        a = np.asarray(Image.open(os.path.join(d1, f)).convert('RGB'), np.int16); b = np.asarray(Image.open(os.path.join(d2, f)).convert('RGB'), np.int16)
        dd = np.abs(a - b).max(axis=2); medias.append(float(dd.mean())); maxs.append(int(dd.max())); frac.append(float((dd > 8).mean() * 100))
    return dict(plano=pid, comparavel=True, quadros=len(f1), bytes_identicos=iguais, dif_media=round(float(np.mean(medias)), 4),
                dif_media_pior_quadro=round(float(np.max(medias)), 3), dif_max=int(np.max(maxs)), pct_pixels_acima_8_pior=round(float(np.max(frac)), 3))

res = dict(mesmos_tempos=[], tempos_mudaram=[])
for pid in ids:
    base = pid[:2]
    mesmo = (V1[base]['t0'], V1[base]['t1']) == (V2[base]['t0'], V2[base]['t1'])
    if mesmo: res['mesmos_tempos'].append(dict(cmp_plano(pid), alterado_de_proposito=pid in ALTERADOS))
    else: res['tempos_mudaram'].append(dict(plano=pid, v1=[V1[base]['t0'], V1[base]['t1']], v2=[V2[base]['t0'], V2[base]['t1']], alterado_de_proposito=pid in ALTERADOS))
if len(sys.argv) > 2: res['variacao_natural'] = json.load(open(sys.argv[2]))
json.dump(res, open(os.path.join(REL, 'comparativo_v1_v2.json'), 'w'), ensure_ascii=False, indent=1)

# folhas antes × depois (dos mp4 montados: o que o espectador vê, com rótulos e legendas)
def quadro(mp4, t):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', mp4, '-frames:v', '1', '-vf', 'scale=216:384', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    return Image.frombytes('RGB', (216, 384), r.stdout)
mp1, mp2 = os.path.join(A, 'ep02_animatic_v1.mp4'), os.path.join(A, 'ep02_animatic.mp4')
mostrar = [p for p in V2 if p in ALTERADOS or (V1[p]['t0'], V1[p]['t1']) != (V2[p]['t0'], V2[p]['t1'])]
folhas = []
for k in range(0, len(mostrar), 4):
    grupo = mostrar[k:k + 4]; W = 4 * 216 + 3 * 4; H = len(grupo) * (2 * 384 + 34 + 10)
    fo = Image.new('RGB', (2 * W + 24, H), (18, 20, 26)); d = ImageDraw.Draw(fo); y = 0
    for pid in grupo:
        d.text((6, y + 6), f"{pid} · v1 {V1[pid]['t0']:.2f}–{V1[pid]['t1']:.2f} s → v2 {V2[pid]['t0']:.2f}–{V2[pid]['t1']:.2f} s · {V2[pid]['narrado'][:70]}", font=fonte, fill=(246, 244, 236))
        for lin, (mp, P, nome) in enumerate(((mp1, V1, 'ANTES (v1)'), (mp2, V2, 'DEPOIS (v2)'))):
            for j, f in enumerate((0.10, 0.37, 0.63, 0.90)):
                im = quadro(mp, P[pid]['t0'] + f * (P[pid]['t1'] - P[pid]['t0'])); fo.paste(im, (lin * (W + 24) + j * 220, y + 34))
            d.text((lin * (W + 24) + 6, y + 34 + 6), nome, font=fonte, fill=(255, 214, 90), stroke_width=2, stroke_fill=(0, 0, 0))
        y += 2 * 384 + 34 + 10
    # layout: antes à esquerda, depois à direita (uma linha por plano)
    fo = fo.crop((0, 0, 2 * W + 24, y)); nome = os.path.join(REL, f'antes_depois_v2_{k // 4 + 1}.jpg'); fo.save(nome, quality=82); folhas.append(nome)
print(json.dumps(dict(mesmos_tempos=[{k: v for k, v in r.items() if k in ('plano', 'bytes_identicos', 'quadros', 'dif_media', 'dif_max', 'pct_pixels_acima_8_pior', 'alterado_de_proposito', 'motivo')} for r in res['mesmos_tempos']],
                      folhas=folhas), ensure_ascii=False, indent=0))
# vídeo lado a lado
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp1, '-i', mp2, '-filter_complex',
                "[0:v]drawtext=text='v1':x=20:y=20:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.6[a];[1:v]drawtext=text='v2':x=20:y=20:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.6[b];[a][b]hstack=inputs=2[v]",
                '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '26', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '128k', '-shortest',
                os.path.join(A, 'ep02_animatic_v1_x_v2.mp4')], check=True)
print('lado a lado ok')
