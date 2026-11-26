"""Rodada 6: testes CURTOS de diagnóstico em 1080 × 1920 (perfil 'final' de config/producao.json), 1 s (30 quadros seguidos)
por trecho crítico, UM processo de render por vez. Os quadros vão para quadros_final/<plano>/ (a montagem com JANELA_EP02
compõe rótulos, lupa, manômetros e legendas em 1080). Variantes de diagnóstico do AO no G3 vão para quadros_final_diag/.
NÃO é o render definitivo (que continua aguardando aprovação). Uso: python3 teste_1080.py  → log em quadros_final/_teste.log"""
import os, json, time, subprocess
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
CFG = json.load(open(os.path.join(A, '..', 'config', 'producao.json')))['perfis']['final']
TRECHOS = [('C2', 36.9), ('G3', 104.2), ('G3z', 104.2), ('D4', 65.5), ('E1', 72.3), ('J3', 144.2)]
DIAG = [('G3', 104.5, 'aocorte=1', 'G3_aocorte'), ('G3', 104.5, 'aosem=porta_pivo', 'G3_aosem_porta')]
LOG = os.path.join(A, 'quadros_final', '_teste.log'); os.makedirs(os.path.dirname(LOG), exist_ok=True)
def rodar(pid, t0, n, extra, saida):
    g0 = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json')))['g0']; i0 = int(round((t0 - g0) * 30)); i1 = i0 + n - 1
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={CFG['escala']}&{CFG['consulta']}" + (f'&{extra}' if extra else '')
    t = time.time(); r = subprocess.run(['node', 'render_anim.mjs', q, saida, '1', str(i0), str(i1)], cwd=MOTOR, capture_output=True, text=True)
    fs = [f for f in os.listdir(saida) if f.endswith('.jpg')] if os.path.isdir(saida) else []
    open(LOG, 'a').write(f"{time.strftime('%H:%M:%S')} {os.path.basename(saida)} {pid} q{i0}–q{i1} ({t0:.2f}–{t0 + n / 30:.2f} s): {len(fs)} quadros em {time.time() - t:.0f} s · {q}\n")
for pid, t0 in TRECHOS: rodar(pid, t0, 30, '', os.path.join(A, 'quadros_final', pid))
for pid, t0, extra, nome in DIAG: rodar(pid, t0, 10, extra, os.path.join(A, 'quadros_final_diag', nome))
open(LOG, 'a').write('FIM\n')
