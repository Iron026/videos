"""Rodada 9 (teste, DESLIGADO na V9): obturador de 180° no fim do C4 (aproximação aprovada ao evaporador), onde a grade do
condensador passa a ter razão deslocamento/passo até 3,6 (V8: 0,84). Mesma técnica aprovada no C2 (rodada 8): 5 sub-quadros em
[−¼, +¼] de quadro, média em luz linear; o sub-quadro central é o quadro da V9. Perfil revisão (540), quadros K0–K1.
Saída: quadros_teste_r9/C4_obt/ (não substitui nada). Uso: python3 teste_obturador_c4_r9.py [k0 k1]"""
import os, sys, json, subprocess, time
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
C = json.load(open(os.path.join(A, '..', 'config', 'producao.json'))); P = C['perfis']['revisao']
K0, K1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (126, 178); M = 5
OUT = os.path.join(A, 'quadros_teste_r9', 'C4_obt'); SUB = OUT + '_sub'; os.makedirs(OUT, exist_ok=True)
q = f"cena=/episodio_02_geladeira/episodio/cenas/C4_obt/&escala={P['escala']}&{P['consulta']}{C['por_plano'].get('C4', '')}"
t = time.time(); r = subprocess.run(['node', 'render_anim.mjs', q, SUB, '1', str(K0 * M), str(K1 * M + M - 1)], cwd=MOTOR, capture_output=True, text=True)
if r.returncode: print('ERRO', r.stderr[-400:]); sys.exit(1)
lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
for k in range(K0, K1 + 1):
    acc = sum(lin(np.asarray(Image.open(os.path.join(SUB, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in range(k * M, k * M + M)) / M
    Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'q{k:04d}.jpg'), quality=95)
print('ok', K1 - K0 + 1, 'quadros em', round(time.time() - t), 's')
