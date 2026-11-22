"""Rodada 8: testes CURTOS em 1080 × 1920 com a configuração PROPOSTA para o congelamento (perfil 'final' de
config/producao.json; cenas da rodada 8 com AO com corte + máscara das tampas + folgas; C2 com obturador de 180°).
UM processo de render por vez. Quadros em quadros_final_r8/<plano>/ — os da rodada 6/7 (configuração aprovada) ficam
intactos em quadros_final/ para o comparativo nos MESMOS quadros. NÃO é o render definitivo.
Uso: python3 teste_1080_r8.py [planos...]  → log em quadros_final_r8/_teste.log"""
import os, sys, json, time, subprocess, shutil
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
C = json.load(open(os.path.join(A, '..', 'config', 'producao.json'))); CFG = C['perfis']['final']; OBT = C.get('obturador', {})
# (plano, primeiro quadro, n): pontos críticos — mesmos quadros da rodada 6 onde existem (C2 q97, G3 q71, J3 q84)
TRECHOS = {'C2': (97, 20), 'C4': (8, 30), 'C3': (58, 30), 'G3': (71, 30), 'H2': (40, 30), 'J3': (84, 30)}
OUT = os.path.join(A, 'quadros_final_r8'); os.makedirs(OUT, exist_ok=True); LOG = os.path.join(OUT, '_teste.log')
def integrar(src, dst, js):
    lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
    acc = sum(lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in js) / len(js)
    Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(dst, quality=95)
for pid in (sys.argv[1:] or list(TRECHOS)):
    i0, n = TRECHOS[pid]; i1 = i0 + n - 1; d = os.path.join(OUT, pid)
    if os.path.isdir(d) and all(os.path.exists(os.path.join(d, f'q{i:04d}.jpg')) for i in range(i0, i1 + 1)): continue
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={CFG['escala']}&{CFG['consulta']}{C['por_plano'].get(pid, '')}"
    t = time.time()
    if pid in OBT:
        m = OBT[pid]['sub']; dsub = d + '_obt'
        r = subprocess.run(['node', 'render_anim.mjs', q.replace(f'/cenas/{pid}/', f'/cenas/{pid}_obt/'), dsub, '1', str(i0 * m), str(i1 * m + m - 1)], cwd=MOTOR, capture_output=True, text=True)
        os.makedirs(d, exist_ok=True)
        if r.returncode == 0:
            for i in range(i0, i1 + 1): integrar(dsub, os.path.join(d, f'q{i:04d}.jpg'), range(i * m, i * m + m))
    else:
        r = subprocess.run(['node', 'render_anim.mjs', q, d, '1', str(i0), str(i1)], cwd=MOTOR, capture_output=True, text=True)
    sub = f" ({OBT[pid]['sub']} sub-quadros)" if pid in OBT else ''
    estado = 'ok' if r.returncode == 0 else 'ERRO ' + r.stderr[-200:]
    open(LOG, 'a').write(f"{time.strftime('%H:%M:%S')} {pid} q{i0}–q{i1}: {estado} em {time.time() - t:.0f} s{sub} · {q}\n")
open(LOG, 'a').write('FIM\n')
