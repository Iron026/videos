"""Rodada 13.1 — prova de que só os avisos retirados mudaram: R13.1 × R13, quadro a quadro.
 · quadros com diferença acima do ruído do codificador ⊆ quadros em que um aviso retirado estava ativo;
 · pixels diferentes só na faixa dos avisos (canto superior direito);
 · fluxo, quadros, duração e áudio (MD5 do AAC) iguais.
Uso: python3 validar_r13_1.py <r13_1.mp4> <r13.mp4> → relatorios/testes_r13c/validacao_r13_1.json"""
import os, sys, json, subprocess, importlib.util
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); novo, ref = sys.argv[1:3]
OCULTOS = ['Visão térmica', 'Corte ilustrativo', 'Tempo acelerado', 'Fluxo desacelerado', 'Câmera lenta']
os.environ.update(COMPOSICAO_R9='1', TRANSICAO_A4='corte', TRANSICAO_A4_INTERNA='empurrao', GARRAFA_B5='1')
sys.argv = ['m', 'final', '/dev/null']; sp = importlib.util.spec_from_file_location('m', os.path.join(A, 'montar_ep02.py')); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
W, H = 270, 480
def quadros(f):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H, W).astype(np.float32)
md5a = lambda f: subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:a', '-c', 'copy', '-f', 'md5', '-'], capture_output=True, text=True).stdout.strip()
a, b = quadros(ref), quadros(novo)
ativos = [q for q in range(len(a)) if any(t.startswith(o) for t in M.avisos_topo(q / 30) for o in OCULTOS)]
d = np.abs(a - b); por = d.reshape(len(d), -1).mean(1)
mud = [int(q) for q in np.where((d > 25).any(axis=(1, 2)))[0]]
fora = [q for q in mud if q not in set(ativos)]
ys, xs = np.where((d[mud] > 25).any(axis=0)) if mud else (np.array([0]), np.array([0]))
res = dict(quadros=dict(r13=len(a), r13_1=len(b)), audio_md5=dict(r13=md5a(ref), r13_1=md5a(novo)),
           quadros_com_aviso_retirado=len(ativos), quadros_que_mudaram=len(mud), mudaram_sem_aviso_retirado=fora,
           regiao_que_mudou_270x480=dict(x=[int(xs.min()), int(xs.max())], y=[int(ys.min()), int(ys.max())]),
           fora_da_faixa_dos_avisos_dif_max=round(float(d[:, int(ys.max()) + 3:, :].max()), 2), dif_media_quadros_sem_aviso=round(float(por[[q for q in range(len(a)) if q not in set(ativos)]].mean()), 3))
res['aprovado'] = bool(len(a) == len(b) and not fora and res['audio_md5']['r13'] == res['audio_md5']['r13_1'] and xs.min() > W * 0.5 and ys.max() < H * 0.2)
os.makedirs(os.path.join(A, '..', 'relatorios', 'testes_r13c'), exist_ok=True)
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r13c', 'validacao_r13_1.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
