"""Rodada 13C — compõe uma JANELA do episódio com a MESMA função compor() da montagem (perfil final, 1080×1920), sem
codificar: grava o SHA-256 de cada quadro composto (prova de "não mudou") e, opcionalmente, os quadros em PNG.
As opções da montagem vêm do ambiente (as mesmas de montar_r11.sh + as de teste QUADROS_R13C / CORTE_E3).
Uso: python3 compor_janela_r13c.py <montar.py> <t0> <t1> <saida.json> [pasta_png]"""
import os, sys, json, hashlib, importlib.util
mod, t0, t1, saida = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]; png = sys.argv[5] if len(sys.argv) > 5 else None
for k, v in dict(COMPOSICAO_R9='1', TRANSICAO_A4='corte', TRANSICAO_A4_INTERNA='empurrao', GARRAFA_B5='1').items(): os.environ.setdefault(k, v)
sys.argv = [mod, 'final', '/dev/null']
spec = importlib.util.spec_from_file_location('montagem', os.path.abspath(mod)); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
if png: os.makedirs(png, exist_ok=True)
res = {}
for i in range(int(round(t0 * M.FPS)), int(round(t1 * M.FPS))):
    im = M.compor(i / M.FPS); b = im.tobytes(); res[i] = hashlib.sha256(b).hexdigest()
    if png: im.save(os.path.join(png, f'c{i:05d}.png'), compress_level=1)
json.dump(dict(modulo=mod, janela=[t0, t1], opcoes={k: os.environ.get(k) for k in ('COMPOSICAO_R9', 'TRANSICAO_A4', 'TRANSICAO_A4_INTERNA', 'GARRAFA_B5', 'QUADROS_R13C', 'CORTE_E3')},
               quadros=res), open(saida, 'w'), indent=0)
print(len(res), 'quadros compostos', saida)
