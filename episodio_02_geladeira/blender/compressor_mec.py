"""Mecanismo do compressor hermético alternativo (Ep. 02, plano E3): geometria e cinemática VERIFICÁVEIS.

Biela-manivela exata: pino do virabrequim P = O + e(cos θ a + sen θ b); pino do pistão Q = O + a·(e cos θ + √(l² − e² sen² θ)).
Ciclo do cilindro (modelo politrópico, n = 1,10, entre as pressões do modelo didático):
  compressão (válvulas fechadas) → DESCARGA abre quando p ≥ p_alta → re-expansão do espaço morto (válvulas fechadas)
  → SUCÇÃO abre quando p ≤ p_baixa. Temperatura do gás T = T_entrada·(p/p_baixa)^((n−1)/n), com T_entrada calculada para fechar com a descarga do modelo.
Medidas típicas de compressor doméstico pequeno: excentricidade 8 mm (curso 16 mm), diâmetro 24 mm (≈ 7 cm³), biela 32 mm.
Velocidade real ≈ 50 rotações/s (rede de 60 Hz no Brasil: ~3.500 rpm); o vídeo mostra em CÂMERA LENTA (~0,8 rotação/s)."""
import math, json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
MOD = json.load(open(os.path.join(AQUI, '..', 'ciencia', 'ciclo_modelo.json')))
E, LB, RB = 0.008, 0.032, 0.012          # excentricidade, biela, raio do cilindro (m)
FOLGA = 0.0008                             # espaço morto: pistão no PMS fica a 0,8 mm da placa de válvulas
N_POL = 1.10
PB, PA = MOD['pressoes']['baixa_bar'], MOD['pressoes']['alta_bar']
T_SHELL = MOD['estados']['1_succao']['T_C']         # vapor ao entrar na carcaça (−10 °C)
T2 = MOD['estados']['2_descarga']['T_C']            # descarga do modelo do ciclo (72,7 °C)
# Dentro da carcaça hermética o vapor é aquecido pelo motor antes de entrar no cilindro. Essa temperatura de entrada é
# CALCULADA para que a compressão politrópica termine na temperatura de descarga do modelo do ciclo (coerência entre modelos).
T1 = (T2 + 273.15) / (PA / PB) ** ((N_POL - 1) / N_POL) - 273.15


def pos_pistao(th):
    """Distância do eixo do virabrequim ao pino do pistão (m)."""
    return E * math.cos(th) + math.sqrt(LB * LB - (E * math.sin(th)) ** 2)


def volume_rel(th):
    """Volume do cilindro relativo ao volume no PMI (0 = só espaço morto … 1 = PMI)."""
    xmax, xmin = E + LB, LB - E
    v = (xmax - pos_pistao(th) + FOLGA) / (xmax - xmin + FOLGA)
    return v


def ciclo(n=720):
    """Uma rotação (θ = 0 no PMS: pistão mais perto da placa). Retorna listas por θ: pressão, temperatura, válvulas."""
    vm = volume_rel(0.0)            # volume no PMS (espaço morto)
    out = []; p = PA; fase = 'reexp'
    ths = [2 * math.pi * i / n for i in range(n)]
    # integra duas voltas para o estado convergir e guarda a segunda
    for volta in range(2):
        v_prev = volume_rel(0.0); p = PA; fase = 'reexp'
        for th in ths:
            v = volume_rel(th); dv = v - v_prev
            if fase == 'reexp':
                p = PA * (vm / v) ** N_POL if v > 0 else PA
                if p <= PB: fase = 'succao'; p = PB
            elif fase == 'succao':
                p = PB
                if dv < 0 and th > math.pi: fase = 'comp'; v_ini = v
            elif fase == 'comp':
                p = PB * (v_ini / v) ** N_POL
                if p >= PA: fase = 'descarga'; p = PA
            elif fase == 'descarga':
                p = PA
            T = (T1 + 273.15) * (p / PB) ** ((N_POL - 1) / N_POL) - 273.15
            if volta == 1: out.append(dict(th=th, v=v, p=p, T=T, suc=1.0 if fase == 'succao' else 0.0, des=1.0 if fase == 'descarga' else 0.0, fase=fase))
            v_prev = v
    return out


if __name__ == '__main__':
    c = ciclo()
    for k in range(0, 720, 60):
        d = c[k]; print(f"θ={math.degrees(d['th']):5.0f}°  V={d['v']:.3f}  p={d['p']:.2f} bar  T={d['T']:6.1f} °C  {d['fase']}")
    abre_s = next(d for d in c if d['suc']); abre_d = next(d for d in c if d['des'])
    print(f'vapor na carcaça {T_SHELL:.1f} °C → entrada do cilindro {T1:.1f} °C (aquecido pelo motor)')
    print('sucção abre em', round(math.degrees(abre_s['th'])), '°; descarga abre em', round(math.degrees(abre_d['th'])), '°; T máx', round(max(d['T'] for d in c), 1), '°C')
    vs = math.pi * RB ** 2 * 2 * E * 1e6; print(f'deslocamento {vs:.2f} cm³')


# ------------------------------------------------------------------ geometria (Blender) e posicionamento por θ
def montar(c=(0.0, 0.18), z_eixo=0.180):
    """Mecanismo dentro da carcaça (centro c, plano do virabrequim em z_eixo). Eixo do cilindro a = −x. Peças animadas
    recebem 'anim'; o bloco, a carcaça e o estator são cortados pelo plano 2 (meia carcaça traseira removida)."""
    import bpy, lib, mats02 as M
    from mathutils import Vector
    aco = M.pintura('mec_aco', '#9aa0a6', rug=0.3, metal=1.0, temp=40.0)
    ferro = M.ajustar(M.pintura('mec_bloco', '#6d7177', rug=0.5, metal=0.6, temp=45.0), corte=2)
    cobre = M.ajustar(M.pintura('mec_enrolamento', '#b5652e', rug=0.4, metal=0.8, temp=60.0), corte=2)
    lamina = M.ajustar(M.pintura('mec_estator', '#55595f', rug=0.45, metal=0.7, temp=55.0), corte=2)
    rotor_m = M.pintura('mec_rotor', '#8a8f96', rug=0.35, metal=0.9, temp=50.0)
    marca = M.pintura('mec_marca', '#f3b544', rug=0.4, temp=50.0)
    valv = M.pintura('mec_valvula', '#d9dde2', rug=0.25, metal=1.0, temp=45.0)
    gas = M.ajustar(M.pintura('mec_gas', '#88aaff', rug=0.9, temp=T1), gas=True, corte=2)
    cx, cy = c; o = {}
    # motor (embaixo) e eixo
    o['estator'] = lib.cilindro('mec_estator', 0.060, 0.050, (cx, cy, 0.095), lamina, lados=36)
    lib.cilindro('mec_cabeca_bob_s', 0.052, 0.012, (cx, cy, 0.126), cobre, lados=36); lib.cilindro('mec_cabeca_bob_i', 0.052, 0.012, (cx, cy, 0.064), cobre, lados=36)
    rot = bpy.data.objects.new('mec_rotor_pivo', None); lib.ligar(rot); rot.location = (cx, cy, 0.0); rot['anim'] = 1
    r1 = lib.cilindro('mec_rotor', 0.027, 0.062, (0, 0, 0.095), rotor_m, lados=28); r1.parent = rot
    r2 = lib.caixa('mec_rotor_marca', (0.022, 0.004, 0.064), (0.012, 0, 0.095), marca); r2.parent = rot
    r3 = lib.cilindro('mec_eixo', 0.007, 0.115, (0, 0, 0.13), aco, lados=16); r3.parent = rot
    r4 = lib.caixa('mec_manivela', (E + 0.012, 0.012, 0.008), (E / 2, 0, z_eixo - 0.007), aco); r4.parent = rot
    r5 = lib.cilindro('mec_pino', 0.0045, 0.012, (E, 0, z_eixo), aco, lados=12); r5.parent = rot
    o['rotor'] = rot
    # bloco do cilindro (fixo) ao longo de −x, cortado para mostrar o pistão
    xc = LB + E + 0.018 + FOLGA   # distância do eixo à placa de válvulas (pistão de 18 mm; no PMS sobra só a folga)
    blo = lib.cilindro('mec_bloco_cil', RB + 0.005, xc - 0.020, (cx - (xc + 0.020) / 2, cy, z_eixo), ferro, lados=28, rot=(0, math.pi / 2, 0))
    lib.caixa('mec_bloco_base', (0.07, 0.05, 0.012), (cx - 0.01, cy, z_eixo - RB - 0.012), ferro)
    lib.caixa('mec_placa_valvulas', (0.004, 2 * RB + 0.01, 2 * RB + 0.01), (cx - xc - 0.002, cy, z_eixo), aco)
    lib.caixa('mec_cabecote', (0.014, 2 * RB + 0.012, 2 * RB + 0.012), (cx - xc - 0.011, cy, z_eixo), ferro)
    # pistão, biela e gás (animados)
    pis = bpy.data.objects.new('mec_pistao_pivo', None); lib.ligar(pis); pis['anim'] = 1
    p1 = lib.cilindro('mec_pistao', RB - 0.0003, 0.018, (0, 0, 0), aco, lados=24, rot=(0, math.pi / 2, 0)); p1.parent = pis
    bie = bpy.data.objects.new('mec_biela_pivo', None); lib.ligar(bie); bie['anim'] = 1
    b1 = lib.caixa('mec_biela', (LB, 0.006, 0.005), (-LB / 2, 0, 0), aco); b1.parent = bie
    gv = bpy.data.objects.new('mec_gas_pivo', None); lib.ligar(gv); gv['anim'] = 1
    g1 = lib.cilindro('mec_gas', RB - 0.0006, 1.0, (0.5, 0, 0), gas, lados=24, rot=(0, math.pi / 2, 0)); g1.parent = gv
    # válvulas de palheta (sucção abre para DENTRO do cilindro; descarga abre para FORA, para o cabeçote)
    vs = bpy.data.objects.new('mec_valv_suc', None); lib.ligar(vs); vs['anim'] = 1; vs.location = (cx - xc, cy - 0.006, z_eixo + RB * 0.55)
    v1 = lib.caixa('mec_palheta_suc', (0.0008, 0.010, 0.010), (0.0004, 0, -0.005), valv); v1.parent = vs
    vd = bpy.data.objects.new('mec_valv_des', None); lib.ligar(vd); vd['anim'] = 1; vd.location = (cx - xc - 0.004, cy + 0.006, z_eixo - RB * 0.55)
    v2 = lib.caixa('mec_palheta_des', (0.0008, 0.010, 0.010), (-0.0004, 0, 0.005), valv); v2.parent = vd
    o.update(pistao=pis, biela=bie, gas=gv, valv_suc=vs, valv_des=vd, c=(cx, cy, z_eixo), xc=xc, gas_mat=gas)
    return o


def posicionar(o, th, ciclo_tab=None):
    """Põe o mecanismo no ângulo θ (rad). Retorna o estado do cilindro (p, T, válvulas) para o som e para a cor do gás."""
    from mathutils import Matrix, Vector, Euler
    cx, cy, z = o['c']; xc = o['xc']
    o['rotor'].rotation_euler = (0, 0, math.pi + th)            # θ = 0: pino voltado para o cilindro (−x) → PMS
    P = Vector((cx - E * math.cos(th), cy - E * math.sin(th), z))
    xq = pos_pistao(th); Q = Vector((cx - xq, cy, z))
    o['pistao'].location = Q + Vector((-0.009, 0, 0))
    d = P - Q; ang = math.atan2(d.y, d.x)
    o['biela'].location = P; o['biela'].rotation_euler = (0, 0, ang)
    face = cx - xq - 0.018        # face do pistão (lado do cabeçote)
    largura = max(face - (cx - xc), 0.0003)
    o['gas'].location = (cx - xc, cy, z); o['gas'].scale = (largura, 1, 1)
    tab = ciclo_tab or ciclo()
    k = int(round((th % (2 * math.pi)) / (2 * math.pi) * len(tab))) % len(tab); st = tab[k]
    o['valv_suc'].rotation_euler = (0, -math.radians(22) * st['suc'], 0)
    o['valv_des'].rotation_euler = (0, math.radians(22) * st['des'], 0)
    return st
