"""Validação dos trechos de teste em resolução definitiva (1080 × 1920) contra a revisão aprovada (540 × 960).
Para cada janela: (1) fidelidade ao aprovado — o quadro 1080 reduzido a 540 × 960 × o quadro 3D da revisão no mesmo índice
(PSNR/SSIM); (2) artefatos — pontos isolados por megapixel e cintilação (média e local, blocos de 2 % da altura) de cada
sequência na sua própria resolução; (3) determinismo — quadros re-renderizados isoladamente × os do lote.
Uso: python3 episodio/validar_teste_final.py [dir_isolados]   → validacao_teste_final.json"""
import os, sys, json, numpy as np
from PIL import Image
from scipy.ndimage import median_filter, uniform_filter
A = os.path.dirname(os.path.abspath(__file__))
JAN = [('experimento 87–90 s', 's08b', 83.85, 95, 184), ('avaria 140–143 s', 's12', 137.0, 90, 179), ('avaria 146–149 s', 's12', 137.0, 270, 359)]
ISO = sys.argv[1] if len(sys.argv) > 1 else None
cinza = lambda im: np.asarray(im.convert('L')).astype(np.float32)
def ssim(a, b):
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2; ma, mb = uniform_filter(a, 7), uniform_filter(b, 7)
    va, vb, cab = uniform_filter(a * a, 7) - ma ** 2, uniform_filter(b * b, 7) - mb ** 2, uniform_filter(a * b, 7) - ma * mb
    return float((((2 * ma * mb + c1) * (2 * cab + c2)) / ((ma ** 2 + mb ** 2 + c1) * (va + vb + c2))).mean())
psnr = lambda a, b: float(10 * np.log10(255 ** 2 / max(np.mean((a - b) ** 2), 1e-9)))
def pontos_mp(x): return float((np.abs(x - median_filter(x, 3)) > 14).sum() / (x.size / 1e6))
def cintil(seq):
    H, W = seq[0].shape; b = max(8, H // 48); h, w = H // b * b, W // b * b; md, lc = [], []
    for i in range(1, len(seq) - 1):
        d = np.abs(seq[i + 1] - 2 * seq[i] + seq[i - 1]); md.append(float(d.mean())); lc.append(float(d[:h, :w].reshape(h // b, b, w // b, b).mean((1, 3)).max()))
    return md, lc
R = {}
for nome, seg, g0, q0, q1 in JAN:
    F, V, ps, ss, pf, pv = [], [], [], [], [], []
    for q in range(q0, q1 + 1):
        f = Image.open(os.path.join(A, 'quadros_final', seg, f'q{q:04d}.jpg')); v = Image.open(os.path.join(A, 'quadros_revisao', seg, f'q{q:04d}.jpg'))
        fr = cinza(f.resize(v.size, Image.LANCZOS)); vv = cinza(v); ps.append(psnr(fr, vv)); ss.append(ssim(fr, vv))
        fc = cinza(f); F.append(fc); V.append(vv); pf.append(pontos_mp(fc)); pv.append(pontos_mp(vv))
    mf, lf = cintil(F); mv, lv = cintil(V)
    # cintilação comparável: a sequência final reduzida (mesma escala de pixels da revisão)
    Fr = [np.asarray(Image.fromarray(x.astype(np.uint8)).resize((540, 960), Image.LANCZOS)).astype(np.float32) for x in F]; mfr, lfr = cintil(Fr)
    r = dict(quadros=q1 - q0 + 1, tempo_s=[round(g0 + q0 / 30, 2), round(g0 + q1 / 30, 2)],
             fidelidade_ao_aprovado=dict(psnr_medio_db=round(float(np.mean(ps)), 1), psnr_min_db=round(float(np.min(ps)), 1), ssim_medio=round(float(np.mean(ss)), 4), ssim_min=round(float(np.min(ss)), 4),
                                         quadro_menos_parecido_s=round(g0 + (q0 + int(np.argmin(ss))) / 30, 3)),
             pontos_isolados_por_mp=dict(final_1080=round(float(np.mean(pf))), revisao_540=round(float(np.mean(pv)))),
             cintilacao_media=dict(final_reduzido=round(float(np.mean(mfr)), 3), revisao=round(float(np.mean(mv)), 3), final_1080=round(float(np.mean(mf)), 3)),
             cintilacao_local_p95=dict(final_reduzido=round(float(np.percentile(lfr, 95)), 2), revisao=round(float(np.percentile(lv, 95)), 2)),
             piscadas_locais_so_no_final=[round(g0 + (q0 + i + 1) / 30, 3) for i in range(len(lfr)) if lfr[i] > lv[i] * 1.5 + 2])
    R[nome] = r
if ISO:   # determinismo: quadros renderizados sozinhos × os mesmos quadros do lote paralelo
    det = []
    for f in sorted(os.listdir(ISO)):
        seg, q = f.split('_')[0], int(f.split('_q')[1][:4])
        a = cinza(Image.open(os.path.join(ISO, f))); b = cinza(Image.open(os.path.join(A, 'quadros_final', seg, f'q{q:04d}.jpg')))
        det.append(dict(segmento=seg, quadro=q, dif_media=round(float(np.abs(a - b).mean()), 3), px_dif_maior_20=int((np.abs(a - b) > 20).sum())))
    R['determinismo_isolado_x_lote'] = det
json.dump(R, open(os.path.join(A, 'validacao_teste_final.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
