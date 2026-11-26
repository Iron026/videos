"""Rodada 13 — validação técnica do definitivo R13 (medida; NÃO substitui assistir/escutar):
 · fluxo: 1080×1920, 30 qps, 4.537 quadros, H.264 + AAC 48 kHz, duração;
 · integridade: todos os quadros decodificam, nenhum preto;
 · R13 × R12, quadro a quadro: diferenças só nos quadros esperados (E3 corrigido = 2342–2491; quadros de empate corrigidos
   em A1/B7/H1/I1); nos demais, só ruído do codificador;
 · continuidade temporal: saltos (|Δ| > 3 × mediana local e > 4) fora dos cortes/fusões, com foco na ENTRADA e SAÍDA do E3;
 · quadros repetidos (consecutivos quase idênticos): R12 × R13, episódio inteiro;
 · master sem legendas × definitivo: diferença só na faixa das legendas.
Uso: python3 validar_final_r13.py <r13.mp4> <r12.mp4> <master_r13.mp4> → relatorios/testes_r13c/validacao_final_r13.json"""
import os, sys, json, subprocess, math
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); FPS, NQ = 30, 4537
sys.path.insert(0, os.path.join(A, '..', 'decupagem')); import planos as PL
r13, r12, mst = sys.argv[1:4]
def probe(f):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', f], capture_output=True, text=True).stdout)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video'); a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    return dict(largura=v['width'], altura=v['height'], qps=v['r_frame_rate'], quadros=int(v['nb_read_frames']), codec_video=v['codec_name'],
                codec_audio=a and a['codec_name'], audio_hz=a and int(a['sample_rate']), duracao_s=round(float(j['format']['duration']), 4), titulo=j['format'].get('tags', {}).get('title'))
def quadros(f, w=270, h=480):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, h, w).astype(np.float32)
res = dict(arquivo=os.path.basename(r13), fluxo=probe(r13), fluxo_master=probe(mst), referencia_r12=os.path.basename(r12))
a, b, m = quadros(r12), quadros(r13), quadros(mst)
res['integridade'] = dict(quadros_decodificados=len(b), pretos=int((b.reshape(len(b), -1).mean(1) < 8).sum()), master_quadros=len(m))
# quadros esperados
R = PL.resolvidos(); P = {p['id']: p for p in R['planos']}
esperados = set(range(2342, 2492))
for pid in ('A1', 'B7', 'H1', 'I1'):
    g0 = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json')))['g0']
    for q in range(NQ):
        x = (q / FPS - g0) * FPS
        if int(round(x)) != int(math.floor(x + 0.5 + 1e-6)) and P[pid]['t0'] - 0.2 <= q / FPS < P[pid]['t1'] + 0.2: esperados.add(q)
d = np.abs(b - a).reshape(len(a), -1).mean(1)
fora = [q for q in range(len(d)) if q not in esperados]
res['r13_x_r12'] = dict(quadros_esperados=len(esperados), dif_media_esperados=round(float(d[sorted(esperados)].mean()), 3), dif_max_esperados=round(float(d[sorted(esperados)].max()), 3),
                        fora_dos_esperados=dict(quadros=len(fora), dif_media=round(float(d[fora].mean()), 3), p99=round(float(np.percentile(d[fora], 99)), 3), max=round(float(d[fora].max()), 3),
                                                acima_de_1_5=[int(q) for q in fora if d[q] > 1.5]))
# continuidade temporal
def saltos(x):
    s = np.abs(np.diff(x, axis=0)).reshape(len(x) - 1, -1).mean(1); med = np.array([np.median(s[max(0, k - 4):k + 5]) for k in range(len(s))])
    return s, med, [int(k) for k in np.where((s > 3 * med) & (s > 4))[0]]
sa, ma, ja = saltos(a); sb, mb, jb = saltos(b)
cortes = sorted({int(round(p['t0'] * FPS)) for p in R['planos']})
perto = lambda k: any(abs(k + 1 - c) <= 4 for c in cortes)
res['continuidade'] = dict(saltos_r12=len(ja), saltos_r13=len(jb), saltos_r13_fora_de_cortes=[k for k in jb if not perto(k)], saltos_r12_fora_de_cortes=[k for k in ja if not perto(k)],
                           novos_no_r13=[k for k in jb if k not in ja and not perto(k)])
def janela(q0, q1):
    return [dict(par=[k, k + 1], t=round((k + 1) / FPS, 3), dif_r12=round(float(sa[k]), 2), dif_r13=round(float(sb[k]), 2)) for k in range(q0, q1)]
res['entrada_E3'] = janela(2336, 2352); res['saida_E3'] = janela(2484, 2498)
quase = lambda s: int((s < 0.15).sum())
res['quadros_repetidos'] = dict(r12=quase(sa), r13=quase(sb), r12_nos_4_planos=sum(1 for k in range(len(sa)) if sa[k] < 0.15 and k in esperados), r13_nos_4_planos=sum(1 for k in range(len(sb)) if sb[k] < 0.15 and k in esperados))
# master × definitivo: onde diferem
dm = np.abs(b - m); rows = dm.mean(axis=(0, 2)); faixa = np.where(rows > 0.5)[0]
res['master_x_definitivo'] = dict(linhas_diferentes_de_480=[int(faixa.min()), int(faixa.max())] if len(faixa) else None, dif_media_fora_da_faixa=round(float(np.delete(dm, faixa, axis=1).mean()), 3) if len(faixa) else round(float(dm.mean()), 3))
f = res['fluxo']
res['aprovado_tecnico'] = bool(f['largura'] == 1080 and f['altura'] == 1920 and f['quadros'] == NQ and res['integridade']['pretos'] == 0 and not res['continuidade']['novos_no_r13'] and not res['r13_x_r12']['fora_dos_esperados']['acima_de_1_5'])
os.makedirs(os.path.join(A, '..', 'relatorios', 'testes_r13c'), exist_ok=True)
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r13c', 'validacao_final_r13.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('entrada_E3', 'saida_E3')}, ensure_ascii=False, indent=1))
