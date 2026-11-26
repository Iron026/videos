"""Rodada 10: testes CONTÍNUOS em 1080 × 1920 com a configuração PROPOSTA para o congelamento (perfil 'final' de
config/producao.json, incluindo os obturadores: C2 inteiro e C4 SÓ na faixa 126–178). UM processo de render por vez;
sequências contínuas (estabilidade temporal, não quadros isolados). Quadros em quadros_final_r10/<plano>/ + manifesto com
SHA-256 e a consulta usada. NÃO é o render definitivo. Uso: python3 teste_1080_r10.py [planos...]"""
import os, sys, json, time, subprocess, hashlib, shutil
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
C = json.load(open(os.path.join(A, '..', 'config', 'producao.json'))); CFG = C['perfis']['final']; OBT = C.get('obturador', {})
TRECHOS = {   # plano: (primeiro, último) — pontos críticos pedidos na rodada 10
    'C4': (120, 184),   # fim da aproximação: borda sem/com obturador (125→126 e 178→179), arames, evaporador
    'D1': (0, 20),      # início do D1 (fusão C4 → D1)
    'C2': (90, 119),    # circuito revelado com obturador (mesmos quadros da rodada 8)
    'G3': (60, 89), 'G3z': (60, 89),   # capilar e lupa
    'F1': (60, 89),     # condensador (grade de arames)
    'D4': (60, 89),     # evaporador (mudança de fase)
    'E3': (60, 89),     # compressor em corte
    'H1': (90, 119),    # porta e vedação no corte
    'A2': (20, 49),     # personagem + visão térmica + porta (curva física)
    'A4': (60, 89),     # rosto do personagem
}
OUT = os.path.join(A, 'quadros_final_r10'); os.makedirs(OUT, exist_ok=True); LOG = os.path.join(OUT, '_teste.log')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
def integrar(src, dst, js):
    acc = sum(lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in js) / len(js)
    Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(dst, quality=95)
def logar(m): open(LOG, 'a').write(time.strftime('%H:%M:%S ') + m + '\n'); print(m, flush=True)
for pid in (sys.argv[1:] or list(TRECHOS)):
    i0, i1 = TRECHOS[pid]; d = os.path.join(OUT, pid); os.makedirs(d, exist_ok=True); mf = os.path.join(d, '_manifesto.json')
    man = json.load(open(mf)) if os.path.exists(mf) else {}
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={CFG['escala']}&{CFG['consulta']}{C['por_plano'].get(pid, '')}"
    o = OBT.get(pid); faixa = (o or {}).get('quadros'); em = lambda i: bool(o) and (faixa is None or faixa[0] <= i <= faixa[1])
    falta = [i for i in range(i0, i1 + 1) if not (os.path.exists(os.path.join(d, f'q{i:04d}.jpg')) and man.get(str(i), {}).get('sha256') == sha(os.path.join(d, f'q{i:04d}.jpg')))]
    grupos = []
    for i in falta:
        if grupos and i == grupos[-1][-1] + 1 and em(i) == em(grupos[-1][-1]): grupos[-1].append(i)
        else: grupos.append([i])
    for g in grupos:
        t = time.time(); tmp = os.path.join(d, '_tmp'); shutil.rmtree(tmp, ignore_errors=True)
        if em(g[0]):
            m = o['sub']; r = subprocess.run(['node', 'render_anim.mjs', q.replace(f'/cenas/{pid}/', f'/cenas/{pid}_obt/'), tmp, '1', str(g[0] * m), str(g[-1] * m + m - 1)], cwd=MOTOR, capture_output=True, text=True)
            if r.returncode == 0:
                for i in g: integrar(tmp, os.path.join(d, f'q{i:04d}.jpg'), range(i * m, i * m + m))
        else:
            r = subprocess.run(['node', 'render_anim.mjs', q, tmp, '1', str(g[0]), str(g[-1])], cwd=MOTOR, capture_output=True, text=True)
            if r.returncode == 0:
                for i in g: os.replace(os.path.join(tmp, f'q{i:04d}.jpg'), os.path.join(d, f'q{i:04d}.jpg'))
        if r.returncode != 0: logar(f'ERRO {pid} q{g[0]}–q{g[-1]}: {r.stderr[-300:]}'); sys.exit(2)
        for i in g: man[str(i)] = dict(sha256=sha(os.path.join(d, f'q{i:04d}.jpg')), obturador=em(i), consulta=q)
        tmpj = mf + '.tmp'; json.dump(man, open(tmpj, 'w'), indent=1); os.replace(tmpj, mf); shutil.rmtree(tmp, ignore_errors=True)
        logar(f'{pid} q{g[0]}–q{g[-1]}: ok em {time.time() - t:.0f} s' + (f' (obturador {o["sub"]} sub-quadros)' if em(g[0]) else ''))
logar('FIM')
