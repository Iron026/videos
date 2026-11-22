"""Geladeira doméstica de uma porta (genérica), cozinha e circuito de refrigeração CONTÍNUO — Ep. 02.

Convenções: metros, Z para cima. Geladeira apoiada no piso (z = 0), centrada em x = 0; FRENTE em y negativo.
  gabinete externo: x ±0,300 · y −0,340 (face frontal, atrás da porta) … +0,310 (face traseira) · z 0 … 1,500
  paredes com espuma isolante de 45 mm; compartimento interno: x ±0,255 · y −0,295 … +0,265 · z 0,10 … 1,455
  nicho do compressor (traseiro inferior, aberto atrás): y +0,040 … +0,310 · z 0 … 0,30
  condensador (serpentina com arames) no plano y = +0,345, atrás do gabinete; parede da cozinha em y = +0,46
Arquitetura documentada em ciencia/validacao_cientifica.md §2. O traçado dos tubos é TODO conectado: o fim de cada trecho é o
início do seguinte (testes_cena.py verifica). O parâmetro global s do circuito (0 → 1, no sentido do fluxo) é proporcional ao
comprimento dos tubos; o compressor é um trecho interno (s dentro da carcaça).
"""
import json, math, os
import bpy
from mathutils import Vector
import lib, mats02 as M

AQUI = os.path.dirname(os.path.abspath(__file__))
CIENCIA = os.path.join(AQUI, '..', 'ciencia', 'ciclo_modelo.json')
GX, GY0, GY1, GZ = 0.300, -0.340, 0.310, 1.500
ESP = 0.045
IX, IY0, IY1, IZ0, IZ1 = GX - ESP, GY0 + ESP, GY1 - ESP, 0.10, GZ - ESP
NICHO_Y0, NICHO_Z1 = 0.040, 0.30
COND_Y = 0.345
PAREDE_Y = 0.46
# tubos (raios visuais próximos dos reais: sucção 6,35 mm, descarga/condensador 4,76 mm, capilar ~2 mm externo)
R = dict(evaporador=0.0042, succao=0.0036, descarga=0.0026, condensador=0.0026, linha_liquido=0.0026, capilar=0.0011)
EVAP = dict(x0=-0.215, x1=0.215, y0=-0.235, y1=0.205, z0=1.185, z1=1.405)   # caixa do congelador (evaporador)
COMP = dict(c=(0.0, 0.180, 0.0), r=0.078, h=0.185)                          # compressor hermético (cúpula)


# ------------------------------------------------------------------ circuito (traçado)
def tracado():
    """Poligonais de cada trecho, na ORDEM DO FLUXO. Pontos coincidentes nas emendas."""
    e = EVAP; zc = [1.380, 1.335, 1.290, 1.245, 1.205]
    ent = (-0.150, 0.245, e['z1'] + 0.012)           # entrada do evaporador (chegada do capilar, alto-fundo-esquerda)
    ev = [ent, (-0.150, e['y1'] - 0.010, e['z1'] + 0.012), (e['x0'] - 0.004, e['y1'] - 0.010, zc[0])]
    # placa lateral esquerda: serpentina horizontal (ao longo de y)
    for i, z in enumerate(zc):
        ya, yb = (e['y1'] - 0.03, e['y0'] + 0.03) if i % 2 == 0 else (e['y0'] + 0.03, e['y1'] - 0.03)
        ev += [(e['x0'] - 0.004, ya, z), (e['x0'] - 0.004, yb, z)]
    # placa de baixo: serpentina ao longo de y, avançando em x
    xs = [-0.165, -0.10, -0.035, 0.035, 0.10, 0.165]
    yl = ev[-1][1]
    ev += [(e['x0'] + 0.02, yl, e['z0'] - 0.004)]
    for i, x in enumerate(xs):
        ya, yb = (yl, e['y1'] - 0.03 if yl < 0 else e['y0'] + 0.03) if i % 2 == 0 else (None, None)
        if i % 2 == 0: ev += [(x, ya, e['z0'] - 0.004), (x, yb, e['z0'] - 0.004)]; ylast = yb
        else: ev += [(x, ylast, e['z0'] - 0.004), (x, yl, e['z0'] - 0.004)]
    ylast = ev[-1][1]
    ev += [(e['x1'] - 0.02, ylast, e['z0'] - 0.004), (e['x1'] + 0.004, ylast, zc[-1])]
    for i, z in enumerate(reversed(zc)):
        ya = ev[-1][1]; yb = e['y1'] - 0.03 if ya < 0 else e['y0'] + 0.03
        if i: ev += [(e['x1'] + 0.004, ya, z)]
        ev += [(e['x1'] + 0.004, yb, z)]
    sai = (0.150, 0.245, e['z1'] + 0.012)
    ev += [(e['x1'] + 0.004, e['y1'] - 0.010, e['z1'] + 0.012), (0.150, e['y1'] - 0.010, e['z1'] + 0.012), sai]
    # linha de sucção: atravessa o forro e desce DENTRO da espuma da parede traseira até o nicho do compressor
    yw = IY1 + 0.022
    cx, cy = COMP['c'][0], COMP['c'][1]
    port_s = (cx + COMP['r'] + 0.012, cy, 0.125)       # tubo de sucção na carcaça (lado +x)
    port_d = (cx - COMP['r'] - 0.012, cy, 0.150)       # tubo de descarga (lado −x)
    su = [sai, (0.150, yw, e['z1'] + 0.012), (0.205, yw, e['z1'] - 0.05), (0.205, yw, NICHO_Z1 + 0.035),
          (0.205, 0.215, NICHO_Z1 - 0.012), (port_s[0] + 0.02, cy, 0.17), (port_s[0] + 0.01, cy, port_s[2]), port_s]
    # compressor (trecho interno, invisível nos planos externos): sucção → câmara → descarga
    co = [port_s, (cx + 0.03, cy, 0.125), (cx, cy, 0.10), (cx - 0.03, cy, 0.14), port_d]
    # descarga: sai pelo lado −x, vai para trás e sobe pela borda esquerda até o alto do condensador
    xl = -0.262
    xd = xl - 0.022                                     # sobe 22 mm por fora das curvas da serpentina (sem colidir)
    de = [port_d, (xl + 0.03, cy, 0.150), (xd, 0.28, 0.17), (xd, COND_Y, 0.22), (xd, COND_Y, 1.472), (xl, COND_Y, 1.472), (xl, COND_Y, 1.425)]
    # condensador: serpentina horizontal de cima para baixo (o líquido escorre para baixo)
    zs = [1.425 - i * 0.072 for i in range(15)]
    cd = [(xl, COND_Y, zs[0])]
    for i, z in enumerate(zs):
        xa, xb = (xl, -xl) if i % 2 == 0 else (-xl, xl)
        if i: cd.append((xa, COND_Y, z))
        cd.append((xb, COND_Y, z))
    # linha de líquido: da saída inferior até o filtro secador (vertical, perto do nicho)
    fx = cd[-1][0]
    fs = (0.245, 0.300, 0.205)                         # topo do filtro secador
    ll = [cd[-1], (fx, COND_Y, zs[-1] - 0.05), (0.245, COND_Y, 0.33), (0.245, 0.30, 0.30), (0.245, 0.30, fs[2] + 0.095), fs]
    # capilar: sai por baixo do filtro, faz um feixe enrolado no nicho e sobe dentro da espuma até a entrada do evaporador
    hc = (0.205, 0.255, 0.0)
    ca = [fs, (0.245, 0.300, 0.18), (hc[0] + 0.03, hc[1], 0.17)]
    ca += M.helice(hc, 0.03, 0.17, 0.265, 7, n=20)
    ca += [(0.125, yw - 0.004, NICHO_Z1 + 0.04), (0.125, yw - 0.004, e['z1'] - 0.03), (-0.150, yw - 0.004, e['z1'] + 0.012), ent]
    return [('evaporador', ev), ('succao', su), ('compressor', co), ('descarga', de), ('condensador', cd), ('linha_liquido', ll), ('capilar', ca)]


def circuito_param(suave=True):
    """Trechos com pontos (suavizados nas quinas) e faixa de s global proporcional ao comprimento."""
    tr = [(n, M.suavizar(p, 0.018 if n != 'capilar' else 0.01) if suave and n not in ('compressor',) else p) for n, p in tracado()]
    Ls = [M.comprimento(p) for _, p in tr]; tot = sum(Ls); out, s = [], 0.0
    for (n, p), L in zip(tr, Ls):
        out.append(dict(id=n, pts=p, comprimento=L, s0=s / tot, s1=(s + L) / tot)); s += L
    return out, tot


def tabela_fluido(n=512):
    """LUT do fluido no s GLOBAL: temperatura, título, lado de pressão e coordenada de fluxo u(s).
    u(s) = ∫ ds / v_vis, com a velocidade VISUAL comprimida (v_vis ∝ v_rel^0,3) — o fluxo real varia > 1.000×."""
    mod = json.load(open(CIENCIA)); tr, tot = circuito_param()
    perfis = {t['id']: t['perfil'] for t in mod['circuito']}
    lado = dict(evaporador=0, succao=0, compressor=0.5, descarga=1, condensador=1, linha_liquido=1, capilar=0.5)
    T, X, LD, V = [], [], [], []
    for i in range(n):
        s = (i + 0.5) / n
        t = next(t for t in tr if t['s0'] <= s <= t['s1'] + 1e-9)
        sl = (s - t['s0']) / max(t['s1'] - t['s0'], 1e-9); p = perfis[t['id']]
        f = sl * (len(p) - 1); k = min(int(f), len(p) - 2); a = f - k
        g = lambda key: p[k][key] * (1 - a) + p[k + 1][key] * a
        T.append(round(g('T_C'), 3)); X.append(round(g('x'), 4)); V.append(g('v_rel'))
        ld = lado[t['id']]
        if t['id'] == 'capilar': ld = 1.0 - (p[0]['P_bar'] - g('P_bar')) / (p[0]['P_bar'] - p[-1]['P_bar'])
        if t['id'] == 'compressor': ld = sl
        LD.append(round(ld, 4))
    vv = [max(v, 1e-4) ** 0.3 for v in V]
    u = [0.0]
    for i in range(n - 1): u.append(u[-1] + (1.0 / n) / vv[i])
    per = u[-1] + (1.0 / n) / vv[-1]
    K = 40.0 / per                                     # 40 períodos do padrão em uma volta: fecha sem emenda em s = 0/1
    U = [round(x * K, 4) for x in u]
    return dict(n=n, T=T, x=X, lado=LD, u=U, u_volta=40.0, comprimento_m=round(tot, 3),
                trechos=[dict(id=t['id'], s0=round(t['s0'], 5), s1=round(t['s1'], 5), m=round(t['comprimento'], 3)) for t in tr],
                T_ambiente=M.AMBIENTE_C, nota='LUT do modelo didático (ciclo_modelo.json) no s global do traçado 3D')


# ------------------------------------------------------------------ materiais da cena
def materiais():
    return dict(
        branco=M.pintura('gab_branco', '#ecebe6', rug=0.22, coat=0.6, temp=26.0),          # polimento: esmalte
        forro=M.pintura('forro', '#f4f4f1', rug=0.28, coat=0.12, temp=5.0),
        espuma=M.pintura('espuma', '#e8c46a', rug=0.85, variacao=0.10, escala_var=40.0, temp=15.0),
        vedacao=M.pintura('vedacao', '#3a3d42', rug=0.7, temp=18.0),
        porta_int=M.pintura('porta_int', '#f2f2ee', rug=0.25, coat=0.2, temp=6.0),
        vidro=M.pintura('prateleira_vidro', '#cfe3e6', rug=0.05, coat=0.8, alfa=0.35, temp=4.0),
        plastico_cinza=M.pintura('plast_cinza', '#c9cbcc', rug=0.4, temp=4.0),
        aluminio=M.pintura('evap_aluminio', '#c3c7cc', rug=0.35, metal=1.0, temp=-18.0),
        compressor=M.pintura('compressor', '#1c2023', rug=0.38, coat=0.5, temp=55.0),      # aço pintado
        arame=M.pintura('arame', '#18191b', rug=0.5, temp=38.0),
        latao=M.pintura('filtro', '#9a7a3e', rug=0.35, metal=1.0, temp=34.0),
        cabo=M.pintura('cabo', '#202124', rug=0.6, temp=25.0),
        chao=M.pintura('piso', '#c4bcb0', rug=0.6, variacao=0.03, escala_var=1.2, temp=25.0),             # rejunte (fica 5 mm abaixo das placas)
        porcelanato=M.pintura('porcelanato', '#ddd6ca', rug=0.26, coat=0.25, variacao=0.04, escala_var=0.7, temp=25.0),
        teto=M.pintura('teto', '#f2efe8', rug=0.95, variacao=0.02, temp=25.0),
        mesa=M.pintura('mesa', '#a4774f', rug=0.45, coat=0.3, variacao=0.06, escala_var=2.5, temp=25.0),
        quadro=M.pintura('quadro_tela', '#5d7f8f', rug=0.7, variacao=0.18, escala_var=1.0, temp=25.0),
        luz_teto=lib.mat_emissivo('luminaria', (1.0, 0.95, 0.86), forca=4.0),
        parede=M.pintura('parede', '#e9e2d4', rug=0.9, variacao=0.03, escala_var=1.5, temp=25.0),
        bancada=M.pintura('bancada', '#4a4c50', rug=0.25, coat=0.4, variacao=0.06, escala_var=6.0, temp=25.0),
        armario=M.pintura('armario', '#6f8a86', rug=0.40, coat=0.15, variacao=0.03, temp=25.0),
        madeira=M.pintura('madeira', '#b98a5c', rug=0.55, variacao=0.08, escala_var=3.0, temp=25.0),
        rodape=M.pintura('rodape', '#cfc6b6', rug=0.6, temp=25.0),
        janela=M.pintura('caixilho', '#f3f1ea', rug=0.4, temp=25.0),
    )


# ------------------------------------------------------------------ geladeira
def gabinete(mt, cortar_parede=False):
    """Paredes da geladeira como sólidos fechados (casca + espuma), forro interno, nicho do compressor e pés."""
    objs = {}
    W = lambda nome, x0, x1, y0, y1, z0, z1, m: lib.caixa(nome, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m)
    # paredes externas: material branco (casca); a espuma fica como camada interna 3 mm afastada (sem faces coplanares)
    objs['lado_e'] = W('gab_lado_e', -GX, -IX, GY0, GY1, 0.0, GZ, mt['branco'])
    objs['lado_d'] = W('gab_lado_d', IX, GX, GY0, GY1, 0.0, GZ, mt['branco'])
    objs['topo'] = W('gab_topo', -IX, IX, GY0, GY1, IZ1, GZ, mt['branco'])
    objs['fundo'] = W('gab_fundo_tras', -IX, IX, IY1, GY1, NICHO_Z1, IZ1, mt['branco'])
    objs['base'] = W('gab_base', -IX, IX, GY0, NICHO_Y0, 0.035, IZ0, mt['branco'])
    objs['degrau'] = W('gab_degrau', -IX, IX, NICHO_Y0, IY1 + 0.0, NICHO_Z1 - 0.004, NICHO_Z1 + 0.032, mt['branco'])
    objs['degrau_frente'] = W('gab_degrau_f', -IX, IX, NICHO_Y0 - 0.004, NICHO_Y0 + 0.030, IZ0 - 0.01, NICHO_Z1 + 0.032, mt['branco'])
    # forro interno (plástico branco), 2 mm para dentro das paredes
    f = 0.002
    for nome, a in [('forro_e', (-IX, -IX + f, IY0, IY1, IZ0, IZ1)), ('forro_d', (IX - f, IX, IY0, IY1, IZ0, IZ1)),
                    ('forro_t', (-IX, IX, IY0, IY1, IZ1 - f, IZ1)), ('forro_f', (-IX, IX, IY1 - f, IY1, NICHO_Z1 + 0.032, IZ1)),
                    ('forro_b', (-IX, IX, IY0, NICHO_Y0 + 0.03, IZ0, IZ0 + f)), ('forro_bt', (-IX, IX, NICHO_Y0 + 0.03, IY1, NICHO_Z1 + 0.032, NICHO_Z1 + 0.032 + f))]:
        x0, x1, y0, y1, z0, z1 = a
        objs[nome] = W(nome, x0 + (0.0004 if x0 == -IX else 0), x1 - (0.0004 if x1 == IX else 0), y0, y1 - 0.0004, z0 + 0.0004, z1 - 0.0004, mt['forro'])
    # pés e grade inferior
    for i, (x, y) in enumerate([(-0.25, -0.30), (0.25, -0.30), (-0.25, 0.27), (0.25, 0.27)]):
        lib.cilindro(f'pe{i}', 0.016, 0.035, (x, y, 0.0175), mt['vedacao'], lados=14)
    W('rodape_gab', -GX + 0.01, GX - 0.01, GY0 - 0.004, GY0 + 0.01, 0.0, 0.034, mt['vedacao'])
    return objs


FOLGA_PORTA = 0.0   # m (0 = geometria da V4)


def porta(mt):
    """Porta com vedação, prateleiras internas e puxador. Articulação em x = +GX, y = GY0 (abre para a direita)."""
    piv = bpy.data.objects.new('porta_pivo', None); lib.ligar(piv); piv.location = (GX, GY0, 0.0); piv['anim'] = 1
    def P(nome, tam, pos, m):
        o = lib.caixa(nome, tam, (pos[0] - GX, pos[1] - GY0, pos[2]), m); o.parent = piv; return o
    # rodada 5: a face de trás do painel (y = GY0 − 0,001) coincide com a face da frente da vedação → z-fighting visível pelo
    # corte (G3, J3). FOLGA_PORTA recua o painel em 0,5 mm; ligada só onde aprovado (episodio02.CORRECAO_PORTA)
    f_ = FOLGA_PORTA
    P('porta_painel', (2 * GX, 0.055 - f_, GZ - 0.02), (0, GY0 - 0.0285 - f_ / 2, (GZ - 0.02) / 2 + 0.03), mt['branco'])
    P('porta_vedacao', (2 * GX - 0.03, 0.012, GZ - 0.10), (0, GY0 - 0.0005 + 0.0055, (GZ - 0.10) / 2 + 0.07), mt['vedacao'])
    P('porta_contraporta', (2 * GX - 0.09, 0.03, GZ - 0.22), (0, GY0 + 0.015 + 0.012, (GZ - 0.22) / 2 + 0.13), mt['porta_int'])
    for z in (0.32, 0.70, 1.08):
        P(f'porta_prat{z}', (2 * GX - 0.13, 0.085, 0.012), (0, GY0 + 0.07, z), mt['porta_int'])
        P(f'porta_grade{z}', (2 * GX - 0.13, 0.006, 0.055), (0, GY0 + 0.112, z + 0.03), mt['vidro'])
    P('puxador', (0.03, 0.035, 0.55), (-GX + 0.045, GY0 - 0.072, 1.05), mt['vedacao'])
    return piv


def interior(mt):
    """Prateleiras, gaveta, caixa do congelador (evaporador) e alimentos."""
    objs = {}
    for z in (0.50, 0.84):
        lib.caixa(f'prat_vidro_{z}', (2 * IX - 0.01, IY1 - IY0 - 0.03, 0.005), (0, (IY0 + IY1) / 2 - 0.01, z), mt['vidro'])
        lib.caixa(f'prat_borda_{z}', (2 * IX - 0.01, 0.012, 0.016), (0, IY0 + 0.012, z), mt['plastico_cinza'])
    lib.caixa('gaveta', (2 * IX - 0.03, 0.40, 0.17), (0, IY0 + 0.24, IZ0 + 0.10), mt['vidro'])
    lib.caixa('gaveta_tampa', (2 * IX - 0.01, IY1 - IY0 - 0.03, 0.006), (0, (IY0 + IY1) / 2 - 0.01, IZ0 + 0.20), mt['vidro'])
    # evaporador: caixa em U de alumínio (laterais + fundo + teto) — os canais do circuito ficam por fora das placas
    e = EVAP; t = 0.0025
    objs['evap'] = [
        lib.caixa('evap_lado_e', (t, e['y1'] - e['y0'], e['z1'] - e['z0']), (e['x0'], (e['y0'] + e['y1']) / 2, (e['z0'] + e['z1']) / 2), mt['aluminio']),
        lib.caixa('evap_lado_d', (t, e['y1'] - e['y0'], e['z1'] - e['z0']), (e['x1'], (e['y0'] + e['y1']) / 2, (e['z0'] + e['z1']) / 2), mt['aluminio']),
        lib.caixa('evap_base', (e['x1'] - e['x0'], e['y1'] - e['y0'], t), ((e['x0'] + e['x1']) / 2, (e['y0'] + e['y1']) / 2, e['z0']), mt['aluminio']),
        lib.caixa('evap_teto', (e['x1'] - e['x0'], e['y1'] - e['y0'], t), ((e['x0'] + e['x1']) / 2, (e['y0'] + e['y1']) / 2, e['z1']), mt['aluminio'])]
    lib.caixa('bandeja_degelo', (e['x1'] - e['x0'] + 0.02, e['y1'] - e['y0'] + 0.01, 0.008), (0, (e['y0'] + e['y1']) / 2, e['z0'] - 0.03), mt['plastico_cinza'])
    # alimentos (formas simples e reconhecíveis)
    garrafa = garrafa_agua(mt, (-0.12, -0.10, 0.505))
    objs['garrafa'] = garrafa
    leite = M.pintura('caixa_leite', '#e9eef2', rug=0.5, temp=5.0); faixa = M.pintura('leite_faixa', '#2f6fb3', rug=0.5, temp=5.0)
    lib.caixa('leite', (0.07, 0.07, 0.19), (0.12, -0.08, 0.84 + 0.098), leite); lib.caixa('leite_rot', (0.072, 0.072, 0.05), (0.12, -0.08, 0.84 + 0.09), faixa)
    pote = M.pintura('pote', '#d94f3d', rug=0.35, coat=0.3, temp=5.0)
    lib.cilindro('pote', 0.055, 0.08, (-0.10, 0.05, 0.84 + 0.045), pote, lados=24)
    fruta = M.pintura('tomate', '#c8362a', rug=0.3, coat=0.4, temp=6.0)
    for i, (x, y) in enumerate([(-0.15, -0.20), (-0.07, -0.17), (0.02, -0.21), (0.11, -0.16)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.034, location=(x, y, IZ0 + 0.045), segments=20, ring_count=12)
        o = bpy.context.active_object; o.name = f'tomate{i}'; o.data.materials.append(fruta); o.scale.z = 0.85
        bpy.ops.object.shade_smooth()
    return objs


def garrafa_agua(mt, base):
    """Garrafa PET de água (perfil de revolução) — temperatura animada pela cena (curva 'temp')."""
    perfil = [(0.0, 0.0), (0.034, 0.0), (0.036, 0.01), (0.036, 0.19), (0.030, 0.215), (0.014, 0.245), (0.0125, 0.27), (0.0125, 0.285), (0.0, 0.285)]
    n = 28; v, f = [], []
    for (r, z) in perfil:
        for i in range(n):
            a = 2 * math.pi * i / n; v.append((base[0] + r * math.cos(a), base[1] + r * math.sin(a), base[2] + z))
    for k in range(len(perfil) - 1):
        for i in range(n):
            j = (i + 1) % n; f.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
    m = M.pintura('garrafa_pet', '#9fd0e8', rug=0.06, coat=0.9, alfa=0.55, temp=25.0)
    o = lib.malha('garrafa', v, f, m, suave=True, angulo=60)
    tampa = M.pintura('garrafa_tampa', '#2f6fb3', rug=0.4, temp=25.0)
    lib.cilindro('garrafa_tampa', 0.0135, 0.018, (base[0], base[1], base[2] + 0.293), tampa, lados=20)
    agua = M.pintura('garrafa_agua', '#7fbfe0', rug=0.1, alfa=0.45, temp=25.0)
    lib.cilindro('garrafa_agua_vol', 0.0335, 0.17, (base[0], base[1], base[2] + 0.095), agua, lados=28)
    rot = M.pintura('garrafa_rotulo', '#2f8fcf', rug=0.5, temp=25.0)
    lib.cilindro('garrafa_rot', 0.0365, 0.05, (base[0], base[1], base[2] + 0.11), rot, lados=28)
    return o


def condensador_arames(mt):
    """Arames verticais soldados nos dois lados da serpentina (espaçamento de 25 mm: legível e sem moiré)."""
    xs = [-0.250 + i * 0.025 for i in range(21)]
    for lado, dy in (('f', -0.0045), ('t', 0.0045)):
        for i, x in enumerate(xs):
            lib.cilindro(f'arame_{lado}{i}', 0.0011, 1.06, (x, COND_Y + dy, 0.425 + 0.53), mt['arame'], lados=6)
    for z in (0.40, 1.45):
        lib.caixa(f'cond_trilho{z}', (0.50, 0.012, 0.010), (0, COND_Y, z), mt['arame'])


def compressor(mt):
    c, r, h = COMP['c'], COMP['r'], COMP['h']
    corpo = lib.cilindro('comp_corpo', r, h * 0.62, (c[0], c[1], 0.045 + h * 0.31), mt['compressor'], lados=32)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(c[0], c[1], 0.045 + h * 0.62), segments=32, ring_count=16)
    cup = bpy.context.active_object; cup.name = 'comp_cupula'; cup.scale.z = 0.55; cup.data.materials.append(mt['compressor']); bpy.ops.object.shade_smooth()
    lib.caixa('comp_base', (0.20, 0.17, 0.008), (c[0], c[1], 0.04), mt['arame'])
    caixa_el = M.pintura('rele', '#2a2b2e', rug=0.6, temp=35.0)
    lib.caixa('comp_rele', (0.05, 0.04, 0.05), (c[0], c[1] - r - 0.01, 0.10), caixa_el)
    return corpo


def filtro():
    m = lib._MATS.get('filtro') or M.pintura('filtro', '#9a7a3e', rug=0.35, metal=1.0, temp=34.0)
    lib.cilindro('filtro_secador', 0.0095, 0.095, (0.245, 0.300, 0.205 + 0.0475), m, lados=18)


def tubos(revela=True, so=None):
    """Tubos do circuito (material 'circuito': aparência normal → fluido quando a curva 'revela' sobe)."""
    bases = dict(evaporador='aluminio', succao='cobre', descarga='cobre', condensador='preto', linha_liquido='cobre', capilar='cobre')
    tr, tot = circuito_param(); objs = {}; lut = tabela_fluido()
    n = lut['n']; U = lut['u']
    def fluxo(s):   # u(s) com interpolação linear na LUT (amostras nos centros das células); fecha em s = 0/1
        f = s * n - 0.5; k = int(math.floor(f)); a = f - k
        u0 = U[k % n] + (lut['u_volta'] if k >= n else 0) - (lut['u_volta'] if k < 0 else 0)
        u1 = U[(k + 1) % n] + (lut['u_volta'] if k + 1 >= n else 0) - (lut['u_volta'] if k + 1 < 0 else 0)
        return u0 * (1 - a) + u1 * a
    for t in tr:
        if t['id'] == 'compressor' or (so and t['id'] not in so): continue
        m = M.circuito(f"circ_{t['id']}", bases[t['id']])
        objs[t['id']] = M.varrer(f"tubo_{t['id']}", t['pts'], R[t['id']], m, t['s0'], t['s1'], lados=10 if t['id'] != 'capilar' else 6,
                                 fluxo=fluxo, passo=0.02)
    return objs, tr


def cabo_forca(mt):
    pts = [(COMP['c'][0], COMP['c'][1] - COMP['r'] - 0.03, 0.10), (0.0, 0.10, 0.05), (-0.18, 0.30, 0.02), (-0.30, PAREDE_Y - 0.01, 0.02), (-0.55, PAREDE_Y - 0.01, 0.02), (-0.55, PAREDE_Y - 0.01, 0.30)]
    m = M.trabalho('cabo_trabalho')
    return M.varrer('cabo', M.suavizar(pts, 0.04), 0.0035, m, 0.0, 1.0, lados=8)


# ------------------------------------------------------------------ cozinha
def cozinha(mt, parede_traseira=True):
    W = lambda nome, x0, x1, y0, y1, z0, z1, m: lib.caixa(nome, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m)
    W('piso', -2.6, 2.7, -4.0, PAREDE_Y + 0.1, -0.02, 0.0, mt['chao'])
    # polimento: porcelanato 60 × 60 cm (rejunte 5 mm, baixo contraste: não cintila em baixa resolução)
    xs = [-2.6 + 0.6 * i for i in range(10)]; ys = [-4.0 + 0.6 * j for j in range(8)]
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            x1, y1 = min(x + 0.6, 2.7), min(y + 0.6, PAREDE_Y + 0.1)
            if x1 - x > 0.01 and y1 - y > 0.01: W(f'placa_{i}_{j}', x + 0.0025, x1 - 0.0025, y + 0.0025, y1 - 0.0025, 0.0, 0.005, mt['porcelanato'])
    W('teto', -2.7, 2.8, -4.1, PAREDE_Y + 0.1, 2.70, 2.75, mt['teto'])
    lib.cilindro('luminaria', 0.17, 0.02, (-0.4, -1.6, 2.69), mt['luz_teto'], lados=32)        # a luz principal passa a ter fonte visível
    W('parede_frente_a', -2.7, -1.05, -4.1, -4.0, 0.0, 2.7, mt['parede'])                   # parede frontal com vão de porta
    W('parede_frente_b', -0.15, 2.8, -4.1, -4.0, 0.0, 2.7, mt['parede'])
    W('parede_frente_c', -1.05, -0.15, -4.1, -4.0, 2.10, 2.7, mt['parede'])
    W('parede_dir', 2.7, 2.8, -4.1, PAREDE_Y + 0.1, 0.0, 2.7, mt['parede'])
    # mesa com duas cadeiras junto à parede da janela (fundo do contraplano de A4; fora de quadro nos demais planos)
    W('mesa_tampo', -2.45, -1.65, -2.75, -1.95, 0.72, 0.75, mt['mesa'])
    for (x, y) in ((-2.40, -2.70), (-1.70, -2.70), (-2.40, -2.00), (-1.70, -2.00)): W(f'mesa_pe{x}{y}', x - 0.02, x + 0.02, y - 0.02, y + 0.02, 0.0, 0.72, mt['mesa'])
    for k, y in enumerate((-2.92, -1.78)):
        W(f'cadeira_ass{k}', -2.25, -1.85, y - 0.18, y + 0.18, 0.44, 0.47, mt['mesa'])
        W(f'cadeira_enc{k}', -2.25, -1.85, (y - 0.18) if k == 0 else (y + 0.15), (y - 0.15) if k == 0 else (y + 0.18), 0.47, 0.90, mt['mesa'])
        for (x, yy) in ((-2.22, y - 0.15), (-1.88, y - 0.15), (-2.22, y + 0.15), (-1.88, y + 0.15)): W(f'cadeira_pe{k}{x}{yy}', x - 0.015, x + 0.015, yy - 0.015, yy + 0.015, 0.0, 0.44, mt['mesa'])
    W('quadro_moldura', -2.60, -2.585, -3.25, -2.45, 1.25, 1.85, mt['madeira'])
    W('quadro_tela', -2.585, -2.578, -3.21, -2.49, 1.29, 1.81, mt['quadro'])
    if parede_traseira:
        W('parede_fundo', -2.6, 1.8, PAREDE_Y, PAREDE_Y + 0.1, 0.0, 2.7, mt['parede'])
    else:   # corte ilustrativo: falta só o trecho atrás da geladeira
        W('parede_fundo_e', -2.6, -0.70, PAREDE_Y, PAREDE_Y + 0.1, 0.0, 2.7, mt['parede'])
        W('parede_fundo_d', 0.75, 1.8, PAREDE_Y, PAREDE_Y + 0.1, 0.0, 2.7, mt['parede'])
    W('rodape_fundo', -2.6, 1.8, PAREDE_Y - 0.012, PAREDE_Y, 0.0, 0.07, mt['rodape']) if parede_traseira else None
    # parede esquerda com janela (vão): x = −2,6
    W('parede_esq_a', -2.7, -2.6, -4.0, PAREDE_Y + 0.1, 0.0, 1.05, mt['parede'])
    W('parede_esq_b', -2.7, -2.6, -4.0, PAREDE_Y + 0.1, 2.15, 2.7, mt['parede'])
    W('parede_esq_c', -2.7, -2.6, -4.0, -1.35, 1.05, 2.15, mt['parede'])
    W('parede_esq_d', -2.7, -2.6, -0.15, PAREDE_Y + 0.1, 1.05, 2.15, mt['parede'])
    for z in (1.05, 2.15): W(f'caixilho_h{z}', -2.66, -2.58, -1.35, -0.15, z - 0.02, z + 0.02, mt['janela'])
    for y in (-1.35, -0.75, -0.15): W(f'caixilho_v{y}', -2.66, -2.58, y - 0.02, y + 0.02, 1.05, 2.15, mt['janela'])
    # bancada e armários à esquerda da geladeira
    W('armario_baixo', -2.55, -0.36, -0.15, PAREDE_Y, 0.10, 0.86, mt['armario'])
    W('armario_rodape', -2.55, -0.36, -0.10, PAREDE_Y, 0.0, 0.10, mt['vedacao'])
    W('bancada', -2.58, -0.34, -0.20, PAREDE_Y, 0.86, 0.90, mt['bancada'])
    for i, x in enumerate([-2.55 + k * 0.438 for k in range(5)]):   # 5 portas de 43,8 cm (2,19 m de armário)
        W(f'porta_armario{i}', x + 0.004, x + 0.434, -0.158, -0.150, 0.13, 0.84, mt['armario'])
        W(f'puxador_arm{i}', x + 0.17, x + 0.27, -0.172, -0.158, 0.78, 0.792, mt['vedacao'])
    W('armario_alto', -2.55, -0.36, 0.10, PAREDE_Y, 1.55, 2.25, mt['armario'])
    W('prateleira_madeira', -1.2, -0.45, 0.20, PAREDE_Y, 1.30, 1.325, mt['madeira'])
    # tomada na parede, atrás e à esquerda da geladeira (o cabo de força chega nela)
    W('tomada', -0.60, -0.50, PAREDE_Y - 0.008, PAREDE_Y, 0.25, 0.33, mt['janela'])


def montar(cena='cozinha', parede_traseira=True, com_interior=True):
    """Monta a cena completa. Devolve dicionário com objetos animáveis e o traçado do circuito."""
    mt = materiais()
    g = gabinete(mt); piv = porta(mt)
    it = interior(mt) if com_interior else {}
    condensador_arames(mt); compressor(mt); filtro()
    tb, tr = tubos()
    cabo = cabo_forca(mt)
    cozinha(mt, parede_traseira=parede_traseira)
    return dict(mt=mt, gab=g, porta=piv, interior=it, tubos=tb, tracado=tr, cabo=cabo)
