"""Rodada 12 — prova de que o definitivo R12 só mudou onde devia. Compara dois MP4 1080 × 1920 QUADRO A QUADRO, em
resolução cheia (luma Y de 8 bits decodificada), e classifica cada quadro diferente:
  esperado     → plano corrigido (C4, H1, H2) a partir do quadro da cena em que a ordem dos transparentes trocava, ou a
                 fusão na entrada do plano seguinte (que mistura a continuação do plano corrigido)
  codificador  → diferença pequena (média ≤ 1,5) no mesmo GOP de um quadro esperado ou até 40 quadros antes dele
                 (rc-lookahead/mb-tree do x264 redistribui bits); não é mudança de imagem
  inesperado   → qualquer outro: PARA e investiga
Uso (em episodio/, PYTHONPATH=../decupagem): python3 comparar_mp4_r11_r12.py antes.mp4 depois.mp4 [saida.json]"""
import os, sys, json, subprocess
import numpy as np
import planos as PL
A = os.path.dirname(os.path.abspath(__file__)); FPS, W, H = 30, 1080, 1920
antes, depois = sys.argv[1], sys.argv[2]
saida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(A, '..', 'relatorios', 'testes_r10', 'comparacao_r11_x_r12_video.json')
# planos corrigidos na R12 e o 1º quadro DA CENA com a ordem nova (antes dele os quadros foram reaproveitados por prova)
MUDOU = {'C4': 52, 'H1': 75, 'H2': 48}
FUSAO, FUSOES = 0.20, {'B1': 0.30, 'C1': 0.30, 'C2': 0.0, 'D1': 0.30, 'E1': 0.30, 'F1': 0.30, 'I1': 0.30, 'J1': 0.30, 'J4': 0.40}  # = montar_ep02.py
PLR = PL.resolvidos()['planos']; ids = [p['id'] for p in PLR]
g0 = {p['id']: json.load(open(os.path.join(A, 'cenas', p['id'], 'cena.json'))).get('g0', p['t0']) for p in PLR}


def plano(i):
    t = i / FPS
    for p in PLR:
        if p['t0'] <= t < p['t1']: return p['id']
    return PLR[-1]['id']


def esperado(i):
    t = i / FPS; pid = plano(i)
    if pid in MUDOU and t >= g0[pid] + (MUDOU[pid] - 1) / FPS: return f'{pid} ≥ q{MUDOU[pid]}'
    k = ids.index(pid)
    # montar_ep02.compor: a fusão é CENTRADA no corte (t0 ± f/2); depois de t0 ela ainda mistura a continuação do plano anterior
    if k > 0 and ids[k - 1] in MUDOU and t < PLR[k]['t0'] + FUSOES.get(pid, FUSAO) / 2 + 1 / FPS: return f'fusão {ids[k - 1]}→{pid}'
    return None


def chaves(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-skip_frame', 'nokey', '-show_entries', 'frame=pts_time', '-of', 'csv=p=0', f],
                       capture_output=True, text=True, check=True).stdout.split()
    return sorted(int(round(float(x.split(',')[0]) * FPS)) for x in r if x.split(',')[0].strip())   # ffprobe pode deixar ',' sobrando


def fluxo(f):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-threads', '2', '-i', f, '-map', '0:v', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE, bufsize=W * H * 4)


ka, kb = chaves(antes), chaves(depois)   # antes do laço longo: uma falha aqui não custa a comparação inteira
fa, fb = fluxo(antes), fluxo(depois); n = 0; linhas = []
while True:
    ba, bb = fa.stdout.read(W * H), fb.stdout.read(W * H)
    if len(ba) < W * H or len(bb) < W * H:
        resto = (len(ba) == W * H) or (len(bb) == W * H); break
    if ba == bb: linhas.append(None)
    else:
        a = np.frombuffer(ba, np.uint8).astype(np.int16).reshape(H, W); b = np.frombuffer(bb, np.uint8).astype(np.int16).reshape(H, W)
        d = np.abs(a - b); m = d > 8; ys, xs = np.where(m)
        linhas.append(dict(media=round(float(d.mean()), 3), maxima=int(d.max()), px_acima_8=int(m.sum()),
                           caixa=[int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())] if len(ys) else None))
    n += 1
fa.wait(); fb.wait()
esp =[i for i in range(n) if linhas[i] is not None and esperado(i)]
gop = lambda i, K: max([k for k in K if k <= i] or [0])


def classe(i):
    if linhas[i] is None: return 'igual'
    if esperado(i): return 'esperado'
    perto = any(gop(i, kb) == gop(j, kb) or 0 < j - i <= 40 for j in esp)
    return 'codificador' if linhas[i]['media'] <= 1.5 and perto else 'inesperado'


cl = [classe(i) for i in range(n)]
por_plano = {}
for i in range(n):
    p = por_plano.setdefault(plano(i), dict(quadros=0, iguais=0, esperados=0, codificador=0, inesperados=0, media_max=0.0, primeiro_dif=None, ultimo_dif=None))
    p['quadros'] += 1; c = cl[i]
    p[{'igual': 'iguais', 'esperado': 'esperados', 'codificador': 'codificador', 'inesperado': 'inesperados'}[c]] += 1
    if linhas[i] is not None:
        p['media_max'] = max(p['media_max'], linhas[i]['media']); p['primeiro_dif'] = p['primeiro_dif'] if p['primeiro_dif'] is not None else i; p['ultimo_dif'] = i
res = dict(antes=os.path.basename(antes), depois=os.path.basename(depois), quadros_comparados=n, sobra_em_um_dos_arquivos=resto,
           criterio='luma Y 8 bits em resolução cheia; "igual" = bytes idênticos',
           totais={c: cl.count(c) for c in ('igual', 'esperado', 'codificador', 'inesperado')},
           planos_com_diferenca={k: v for k, v in por_plano.items() if v['primeiro_dif'] is not None},
           planos_identicos=sorted(k for k, v in por_plano.items() if v['primeiro_dif'] is None),
           quadros_chave_depois=kb, quadros_chave_iguais_nos_dois=ka == kb,
           inesperados=[dict(quadro=i, t=round(i / FPS, 3), plano=plano(i), **linhas[i]) for i in range(n) if cl[i] == 'inesperado'][:50],
           codificador=[dict(quadro=i, t=round(i / FPS, 3), plano=plano(i), media=linhas[i]['media'], maxima=linhas[i]['maxima']) for i in range(n) if cl[i] == 'codificador'],
           esperados_resumo=[dict(quadro=i, t=round(i / FPS, 3), motivo=esperado(i), **linhas[i]) for i in esp[::10]],
           aprovado=cl.count('inesperado') == 0 and not resto)
json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1); print('→', saida)
print(json.dumps({k: v for k, v in res.items() if k not in ('quadros_chave_depois', 'esperados_resumo', 'codificador')}, ensure_ascii=False, indent=1)[:4000])
