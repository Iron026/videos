"""Rodada 13C — correção LOCALIZADA do z-fighting bobina × estator no E3 (corte ilustrativo do compressor).
Causa: as cabeças de bobina (cilindros r = 52 mm, z 58–70 mm e 120–132 mm) encostam FACE A FACE no estator (z 70–120 mm):
as faces z = 70 mm e z = 120 mm coincidem por definição. Com o corte (plano 2, y = 0,18) o raio que entra na tampa do estator
encontra, no MESMO plano, a face interna do estator (tampa amarela) e a face da bobina (cobre) → listras que piscam.
Correção: só a malha da bobina (mec_enrolamento) muda — as duas faces de contato se afastam do estator por F metros
(folga, padrão 0,02 mm = 0,17 px no E3 em 1080) ou entram nele (sobreposição). Nada mais muda na cena (provado por hash).
Uso: python3 bobina_r13c.py <plano> <sufixo> <folga|sobre|faces> [F_mm]"""
import os, sys, json, shutil, hashlib, numpy as np
A = os.path.dirname(os.path.abspath(__file__)); pid, suf, modo = sys.argv[1:4]; F = float(sys.argv[4]) / 1000 if len(sys.argv) > 4 else 0.00002
src, dst = os.path.join(A, 'cenas', pid), os.path.join(A, 'cenas', pid + suf)
shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
c = json.load(open(os.path.join(src, 'cena.json')))
idx = [i for i, m in enumerate(c['materiais']) if m.get('nome') == 'mec_enrolamento']; assert len(idx) == 1
arq = c['materiais'][idx[0]]['arquivo']; b = np.fromfile(os.path.join(src, arq), np.float32).reshape(-1, 12).copy()
z = b[:, 2].astype(np.float64); s = +1 if modo == 'sobre' else -1
inf, sup = np.isclose(z, 0.070, atol=1e-6), np.isclose(z, 0.120, atol=1e-6)   # topo da bobina de baixo / base da de cima
assert inf.sum() > 0 and sup.sum() > 0
if modo == 'faces':   # retira só os triângulos das faces de CONTATO (todos os 3 vértices no plano z = 70 mm ou z = 120 mm): ficam por
    # dentro do estator (r 52 < 60 mm), nunca aparecem por fora; sem eles, o raio que entra na tampa do estator encontra só o estator
    t = b.reshape(-1, 3, 12); zt = t[:, :, 2].astype(np.float64)
    contato = np.all(np.isclose(zt, 0.070, atol=1e-6), 1) | np.all(np.isclose(zt, 0.120, atol=1e-6), 1)
    b = t[~contato].reshape(-1, 12).copy(); inf = sup = np.zeros(len(b), bool); inf_n = int(contato.sum())
else:
    b[inf, 2] = np.float32(0.070 + s * F); b[sup, 2] = np.float32(0.120 - s * F)
# aLocal (colunas 6–8) acompanha a posição só se for a mesma coordenada (bobina não animada: local = mundo)
if modo != 'faces' and np.allclose(np.fromfile(os.path.join(src, arq), np.float32).reshape(-1, 12)[:, 8], z, atol=1e-7): b[inf, 8] = b[inf, 2]; b[sup, 8] = b[sup, 2]
b.tofile(os.path.join(dst, arq))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
dif = [f for f in sorted(os.listdir(src)) if sha(os.path.join(src, f)) != sha(os.path.join(dst, f))]
print(json.dumps(dict(plano=pid, nova=pid + suf, modo=modo, F_mm=F * 1000, malha=arq, vertices_movidos=int(inf.sum() + sup.sum()), triangulos_retirados=(inf_n if modo == 'faces' else 0), triangulos=len(b) // 3,
                      z_novos=([float(b[inf, 2][0]), float(b[sup, 2][0])] if inf.any() else None), arquivos_diferentes=dif), ensure_ascii=False))
