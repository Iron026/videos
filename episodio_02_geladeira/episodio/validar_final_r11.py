"""Rodada 11 — validação FINAL do Ep. 02 (medida; não substitui assistir/escutar). Subcomandos:
  quadros                       → integridade de todos os quadros de quadros_final (manifesto × SHA-256 × decodificação × 1080×1920)
  video <final.mp4> <ref.mp4> [<sem_legendas.mp4>]
                                → fluxo (1080×1920, 30 qps, 4.537 quadros, H.264 + AAC 48 kHz, título sem marcação de revisão),
                                  quadros pretos/corrompidos, saltos fora dos cortes, semelhança quadro a quadro com a revisão
                                  540 montada com as MESMAS decisões (ref.mp4; faixa do selo de revisão excluída) e, se dado,
                                  o master sem legendas (diferenças só onde há legenda)
Saída: relatorios/testes_r10/validacao_final_r11_<subcomando>.json"""
import os, sys, json, hashlib, subprocess
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); OUTD = os.path.join(RAIZ, 'relatorios', 'testes_r10')
FPS, NQ = 30, 4537
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
MODO = sys.argv[1]


def salvar(nome, obj):
    p = os.path.join(OUTD, f'validacao_final_r11_{nome}.json'); json.dump(obj, open(p, 'w'), ensure_ascii=False, indent=1); print('→', p)


if MODO == 'quadros':
    Q = os.path.join(A, 'quadros_final'); res = dict(planos={}, problemas=[]); tot = 0
    for pid in sorted(d for d in os.listdir(Q) if os.path.isdir(os.path.join(Q, d))):
        mf = os.path.join(Q, pid, '_manifesto_quadros.json')
        if not os.path.exists(mf): res['problemas'].append(f'{pid}: sem manifesto'); continue
        man = json.load(open(mf))['quadros']; ok = 0
        for k, e in sorted(man.items(), key=lambda kv: int(kv[0])):
            f = os.path.join(Q, pid, e.get('arquivo', f'q{int(k):04d}.jpg'))
            if not os.path.exists(f): res['problemas'].append(f'{pid} q{k}: arquivo ausente'); continue
            if sha(f) != e['sha256']: res['problemas'].append(f'{pid} q{k}: SHA-256 ≠ manifesto'); continue
            try:
                im = Image.open(f); im.load()
                if im.size != (1080, 1920): res['problemas'].append(f'{pid} q{k}: tamanho {im.size}'); continue
                if np.asarray(im.convert('L').resize((54, 96)), np.float32).mean() < 3: res['problemas'].append(f'{pid} q{k}: preto'); continue
            except Exception as ex: res['problemas'].append(f'{pid} q{k}: não decodifica ({ex})'); continue
            ok += 1
        sobra = sorted(set(x for x in os.listdir(os.path.join(Q, pid)) if x.endswith('.jpg')) - set(e.get('arquivo', f'q{int(k):04d}.jpg') for k, e in man.items()))
        res['planos'][pid] = dict(no_manifesto=len(man), conferidos=ok, arquivos_fora_do_manifesto=sobra); tot += ok
    res['quadros_conferidos'] = tot; res['aprovado'] = not res['problemas']
    salvar('quadros', res); print(tot, 'quadros conferidos;', len(res['problemas']), 'problemas'); sys.exit()

# ---------------------------------------------------------------- vídeo
sys.path.insert(0, os.path.join(RAIZ, 'decupagem')); import planos as PL
PLR = PL.resolvidos()['planos']
cortes = sorted(set(int(round(p['t0'] * FPS)) for p in PLR[1:]))
TC_A4I = 4.62 + 33.5 / 30   # transição C (empurrão) dentro do A4 — igual a montar_ep02.TC_A4I


def probe(f):
    r = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', f], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in r['streams'] if s['codec_type'] == 'video'); a = [s for s in r['streams'] if s['codec_type'] == 'audio']
    return dict(arquivo=os.path.basename(f), bytes=os.path.getsize(f), sha256=sha(f), largura=v['width'], altura=v['height'], codec=v['codec_name'], pix_fmt=v['pix_fmt'],
                fps=v['r_frame_rate'], quadros=int(v['nb_read_frames']), duracao_video_s=float(v.get('duration', 0)), duracao_s=float(r['format']['duration']),
                audio=[dict(codec=s['codec_name'], taxa=int(s['sample_rate']), canais=s['channels'], duracao_s=float(s.get('duration', 0))) for s in a],
                titulo=r['format'].get('tags', {}).get('title', ''))


def ler(f, w=108, h=192):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={w}:{h}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, h, w, 3).astype(np.float32)


def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


fin, ref = sys.argv[2], sys.argv[3]; semleg = sys.argv[4] if len(sys.argv) > 4 else None
res = dict(final=probe(fin), referencia_540=probe(ref)); pf = res['final']
res['fluxo_ok'] = dict(resolucao=(pf['largura'], pf['altura']) == (1080, 1920), fps=pf['fps'] == '30/1', quadros=pf['quadros'] == NQ, h264=pf['codec'] == 'h264',
                       aac_48k=bool(pf['audio']) and pf['audio'][0]['codec'] == 'aac' and pf['audio'][0]['taxa'] == 48000,
                       sem_marcacao_no_titulo=not any(s in pf['titulo'].lower() for s in ('revis', 'animatic', 'não publicar')))
F = ler(fin); R = ler(ref); n = min(len(F), len(R)); res['quadros_decodificados'] = dict(final=len(F), referencia=len(R))
G = F.mean(3); res['luma_min'] = round(float(G.mean((1, 2)).min()), 2)
res['quadros_pretos'] = [int(i) for i in np.where(G.mean((1, 2)) < 3)[0]]
# saltos entre quadros vizinhos fora dos cortes/fusões (escala grossa 32×56, mesmo critério do render: corr < 0,93 E dif > 6)
gros = np.stack([np.asarray(Image.fromarray(g.astype(np.uint8)).resize((32, 56), Image.BILINEAR), np.float32) for g in G])
saltos = []
for i in range(1, len(gros)):
    c, d = corr(gros[i], gros[i - 1]), float(np.abs(gros[i] - gros[i - 1]).mean())
    if c < 0.93 and d > 6:
        perto = min(abs(i - k) for k in cortes + [int(round(TC_A4I * FPS))])
        saltos.append(dict(quadro=i, t=round(i / FPS, 3), corr=round(c, 3), dif=round(d, 1), distancia_corte=perto))
res['saltos'] = dict(total=len(saltos), em_cortes_ou_fusoes=sum(s['distancia_corte'] <= 10 for s in saltos), fora_dos_cortes=[s for s in saltos if s['distancia_corte'] > 10])
# final (1080 reduzido) × revisão 540 com as mesmas decisões, quadro a quadro; faixa do selo (base ~10 %) excluída
corte_selo = int(192 * 0.90); cs, ds = [], []
for i in range(n):
    a, b = F[i, :corte_selo].mean(2), R[i, :corte_selo].mean(2); cs.append(corr(a, b)); ds.append(float(np.abs(a - b).mean()))
cs, ds = np.array(cs), np.array(ds)
ruins = [int(i) for i in np.where((cs < 0.93) & (ds > 6))[0]]
res['final_x_revisao'] = dict(quadros=n, corr_min=round(float(cs.min()), 3), corr_mediana=round(float(np.median(cs)), 4), dif_max=round(float(ds.max()), 2),
                              dif_media=round(float(ds.mean()), 2), abaixo_do_limiar=ruins,
                              piores=[dict(quadro=int(i), t=round(i / FPS, 3), corr=round(float(cs[i]), 3), dif=round(float(ds[i]), 2)) for i in np.argsort(cs)[:8]])
if semleg:
    res['sem_legendas'] = probe(semleg); S = ler(semleg); m = min(len(S), len(F)); linhas = np.zeros(192); iguais = 0
    for i in range(m):
        dd = np.abs(F[i] - S[i]).mean(2) > 12
        if not dd.any(): iguais += 1
        linhas += dd.any(1)
    faixa = np.where(linhas > 0)[0]
    res['sem_legendas_x_final'] = dict(quadros=m, quadros_sem_diferenca=iguais,
                                       linhas_com_diferenca_pct_altura=[round(100 * faixa.min() / 192, 1), round(100 * (faixa.max() + 1) / 192, 1)] if len(faixa) else None)
res['aprovado'] = all(res['fluxo_ok'].values()) and not res['quadros_pretos'] and not res['saltos']['fora_dos_cortes'] and not ruins
salvar('video', res); print(json.dumps({k: v for k, v in res.items() if k not in ('final', 'referencia_540', 'sem_legendas')}, ensure_ascii=False, indent=1)[:3000])
