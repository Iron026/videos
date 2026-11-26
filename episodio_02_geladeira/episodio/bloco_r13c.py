"""Rodada 13C (2ª parte) — z-fighting bloco do cilindro × placa de válvulas no E3 ("perto de onde o pistão bate").
Causa (provada ocultando peças no quadro 42: só sem o bloco os degraus somem; sem gás, sem palhetas e sem AO, continuam):
o cilindro do bloco termina em x = −58,8 mm, EXATAMENTE na face da placa de válvulas; com o corte (plano 2) a tampa amarela do
bloco e a face escura da placa ficam no mesmo plano e o renderizador alterna entre elas.
Correção: só a malha mec_bloco muda — os vértices do fim do cilindro (x = −58,8 mm) recuam F = 0,02 mm (0,17 px em 1080) para
longe da placa. A fresta fica na borda tampa × placa que já existe. Parte da cena já corrigida da bobina (E3_r13c_faces).
Uso: python3 bloco_r13c.py <cena_origem> <cena_nova> [F_mm]"""
import os, sys, json, shutil, hashlib, numpy as np
A = os.path.dirname(os.path.abspath(__file__)); src, dst = (os.path.join(A, 'cenas', x) for x in sys.argv[1:3]); F = float(sys.argv[3]) / 1000 if len(sys.argv) > 3 else 0.00002
shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
c = json.load(open(os.path.join(src, 'cena.json'))); idx = [i for i, m in enumerate(c['materiais']) if m.get('nome') == 'mec_bloco']; assert len(idx) == 1
arq = c['materiais'][idx[0]]['arquivo']; b = np.fromfile(os.path.join(src, arq), np.float32).reshape(-1, 12).copy()
x = b[:, 0].astype(np.float64); fim = np.isclose(x, -0.0588, atol=1e-6); assert fim.sum() > 0
b[fim, 0] = np.float32(-0.0588 + F)
if np.allclose(np.fromfile(os.path.join(src, arq), np.float32).reshape(-1, 12)[:, 6], x, atol=1e-7): b[fim, 6] = b[fim, 0]
b.tofile(os.path.join(dst, arq))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
print(json.dumps(dict(origem=sys.argv[1], nova=sys.argv[2], F_mm=F * 1000, malha=arq, vertices_movidos=int(fim.sum()),
                      arquivos_diferentes=[f for f in sorted(os.listdir(src)) if sha(os.path.join(src, f)) != sha(os.path.join(dst, f))]), ensure_ascii=False))
