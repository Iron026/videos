"""Rodada 11: quadros-ponte do ROSTO (A4) com a câmera APROVADA continuada (Opção C, empurrão).
A primeira ponte (cenas/A4_h_rosto, chaves novas no Blender) mudava a curva: em q33 a câmera já estava 1,8 cm adiante da
aprovada e, depois, quase parava (Δy −0,0003 m/quadro), enquanto a aprovada chega ao corte ACELERANDO (Δy −0,028 m/quadro).
Aqui a ponte é derivada dos dados exportados aprovados, sem Blender:
  · q ≤ 33: câmera = cenas/A4 (aprovada), quadro a quadro;
  · q ≥ 34: continua com a velocidade de q32→q33 (posição, direção e "up" lineares; direção renormalizada, up ortogonalizado).
Todo o resto (personagem, objetos, luzes, materiais, visão térmica desligada) vem de cenas/A4_h_rosto, que só difere de
cenas/A4 na câmera e na visão térmica — conferido abaixo. Saída: cenas/A4_h_rosto_c (a ponte antiga fica preservada)."""
import os, json, shutil, hashlib
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, 'cenas')
apr = json.load(open(os.path.join(C, 'A4', 'cena.json'))); pon = json.load(open(os.path.join(C, 'A4_h_rosto', 'cena.json')))
QA, QP = apr['animacao']['quadros'], pon['animacao']['quadros']
# 1) a ponte antiga difere da aprovada SÓ na câmera (e na visão térmica) nos quadros do rosto antes do corte?
dif_obj = max(float(np.abs(np.array(QA[f]['objetos'][k], float) - np.array(QP[f]['objetos'][k], float)).max())
              for f in range(0, 34) for k in QA[f]['objetos'])
chaves_quadro = sorted(set(QA[0]) | set(QP[0]))
outros = {k: all(json.dumps(QA[f].get(k), sort_keys=True) == json.dumps(QP[f].get(k), sort_keys=True) for f in range(0, 34)) for k in chaves_quadro if k not in ('camera', 'objetos')}
saida = os.path.join(C, 'A4_h_rosto_c')
if os.path.isdir(saida): shutil.rmtree(saida)
shutil.copytree(os.path.join(C, 'A4_h_rosto'), saida)
n = lambda v: v / np.linalg.norm(v)
c32, c33 = QA[32]['camera'], QA[33]['camera']; reg = []
for f in range(len(QP)):
    if f <= 33: cam = dict(QA[f]['camera'])
    else:
        k = f - 33; P = lambda key: np.array(c33[key]) + k * (np.array(c33[key]) - np.array(c32[key]))
        d = n(P('dir')); u = P('up'); u = n(u - u.dot(d) * d)
        cam = dict(c33); cam.update(pos=P('pos').tolist(), dir=d.tolist(), up=u.tolist())
    QP[f]['camera'] = cam
    if 30 <= f <= 40: reg.append(dict(q=f, pos=np.round(cam['pos'], 4).tolist(), dir=np.round(cam['dir'], 4).tolist()))
pon['camera'] = dict(pon['camera'], **{k: QP[0]['camera'][k] for k in ('pos', 'dir', 'up', 'fov')})
json.dump(pon, open(os.path.join(saida, 'cena.json'), 'w'))
h = hashlib.sha256(open(os.path.join(saida, 'cena.json'), 'rb').read()).hexdigest()
rel = dict(objetos_max_dif_q0_33=dif_obj, outros_campos_iguais_q0_33=outros, camera_por_quadro=reg, sha256_cena=h,
           velocidade_q32_q33=dict(pos=np.round(np.array(c33['pos']) - np.array(c32['pos']), 4).tolist(), dir=np.round(np.array(c33['dir']) - np.array(c32['dir']), 4).tolist()))
json.dump(rel, open(os.path.join(A, '..', 'relatorios', 'testes_r10', 'pontes_camera_continua.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(rel, ensure_ascii=False)[:1500])
