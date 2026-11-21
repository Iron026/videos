"""Modelo científico DIDÁTICO do ciclo de refrigeração por compressão de vapor (Ep. 02).

NÃO representa um equipamento comercial específico. Usa propriedades termodinâmicas REAIS do isobutano (R600a, via
CoolProp) com hipóteses de operação típicas e explícitas (HIPOTESES abaixo). Regime permanente durante o funcionamento do
compressor; grandezas energéticas são TAXAS (W): Q̇_abs (evaporador), Ẇ (compressor), Q̇_rej (condensador e carcaça).

Saída: ciclo_modelo.json — estados 1–4, balanço de energia e o PERFIL do fluido ao longo de cada trecho do circuito
(posição normalizada s ∈ [0, 1] → pressão, temperatura, título, fase, entalpia, velocidade relativa). Esse arquivo é a
ÚNICA fonte para a animação do fluido (cores, fase, velocidade) e para os testes (testes_ciclo.py).
Uso: python3 modelo_ciclo.py"""
import json, os, math
import CoolProp.CoolProp as CP

A = os.path.dirname(os.path.abspath(__file__))
F = 'R600a'
K = 273.15
HIPOTESES = dict(
    fluido='R600a (isobutano) — refrigerante usual em refrigeradores domésticos novos',
    T_interior_C=4.0,            # ar do compartimento refrigerado
    T_cozinha_C=25.0,            # ar ambiente
    T_evap_C=-20.0,              # saturação no evaporador (bem abaixo do ar interno: o calor flui do ar para o fluido)
    superaq_evap_K=5.0,          # vapor sai do evaporador levemente superaquecido
    T_succao_C=-10.0,            # vapor ganha um pouco de calor na linha de sucção até o compressor
    T_cond_C=40.0,               # saturação no condensador (15 K acima da cozinha: o calor flui do fluido para o ar)
    subresf_K=3.0,               # líquido sai do condensador levemente sub-resfriado
    T_entrada_capilar_C=33.0,    # a linha de líquido perde mais um pouco de calor até o capilar
    eta_isentropica=0.60,        # compressão real (perdas); compressores herméticos pequenos ~0,5–0,7
    eta_motor=0.80,              # motor elétrico; as perdas viram calor na carcaça (que está na cozinha)
    Q_abs_W=80.0,                # carga térmica ilustrativa absorvida no evaporador
    simplificacoes=[
        'sem trocador de calor entre capilar e linha de sucção (existe em muitos modelos; omitido para não confundir o espectador)',
        'perdas de carga desprezadas em evaporador, condensador e linhas (pressão constante em cada lado), exceto no capilar',
        'capilar adiabático e isentálpico (h constante); a queda de pressão é distribuída ao longo do comprimento',
        'regime permanente com o compressor ligado; o termostato liga/desliga o ciclo (não modelado)',
        'cargas térmicas e temperaturas típicas, não medidas em um aparelho real',
    ])
H = HIPOTESES


def PT(T, Q=None, P=None, h=None, s=None):
    pass


def props_Ph(P, h):
    T = CP.PropsSI('T', 'P', P, 'H', h, F)
    x = CP.PropsSI('Q', 'P', P, 'H', h, F)
    hl, hv = CP.PropsSI('H', 'P', P, 'Q', 0, F), CP.PropsSI('H', 'P', P, 'Q', 1, F)
    if h <= hl: fase, x = 'liquido', 0.0
    elif h >= hv: fase, x = 'vapor', 1.0
    else: fase = 'mistura'
    rho = CP.PropsSI('D', 'P', P, 'H', h, F)
    return dict(P_bar=P / 1e5, T_C=T - K, x=round(float(x), 5), fase=fase, h_kJkg=h / 1e3, rho=rho)


def estados():
    Pe = CP.PropsSI('P', 'T', H['T_evap_C'] + K, 'Q', 1, F)
    Pc = CP.PropsSI('P', 'T', H['T_cond_C'] + K, 'Q', 0, F)
    h_ev_sai = CP.PropsSI('H', 'P', Pe, 'T', H['T_evap_C'] + H['superaq_evap_K'] + K, F)
    h1 = CP.PropsSI('H', 'P', Pe, 'T', H['T_succao_C'] + K, F)                 # sucção do compressor
    s1 = CP.PropsSI('S', 'P', Pe, 'H', h1, F)
    h2s = CP.PropsSI('H', 'P', Pc, 'S', s1, F)
    h2 = h1 + (h2s - h1) / H['eta_isentropica']                                   # descarga real
    h_cd_sai = CP.PropsSI('H', 'P', Pc, 'T', H['T_cond_C'] - H['subresf_K'] + K, F)
    h3 = CP.PropsSI('H', 'P', Pc, 'T', H['T_entrada_capilar_C'] + K, F)          # entrada do capilar
    h4 = h3                                                                        # capilar isentálpico
    return Pe, Pc, dict(h_ev_sai=h_ev_sai, h1=h1, h2=h2, h2s=h2s, h_cd_sai=h_cd_sai, h3=h3, h4=h4)


def perfil_linear(P0, P1, h0, h1, n, p_curva=None):
    """Amostras ao longo de um trecho: h linear em s (fluxo de calor uniforme); P linear ou por curva p_curva(s)."""
    out = []
    for i in range(n):
        s = i / (n - 1)
        P = p_curva(s) if p_curva else P0 + (P1 - P0) * s
        h = h0 + (h1 - h0) * s
        d = props_Ph(P, h); d['s'] = round(s, 4); out.append(d)
    return out


def main():
    Pe, Pc, h = estados()
    m = H['Q_abs_W'] / (h['h_ev_sai'] - h['h4'])                                  # vazão mássica (kg/s)
    W_eixo = m * (h['h2'] - h['h1']); W_el = W_eixo / H['eta_motor']
    Q_cond = m * (h['h2'] - h['h_cd_sai'])                                         # condensador
    Q_linhas = m * (h['h_cd_sai'] - h['h3']) - m * (h['h1'] - h['h_ev_sai'])       # liq. → cozinha; sucção ← cozinha
    Q_carcaca = W_el - W_eixo                                                       # perdas do motor → cozinha
    Q_rej_total = Q_cond + m * (h['h_cd_sai'] - h['h3']) + Q_carcaca
    Q_abs_total = H['Q_abs_W'] + m * (h['h1'] - h['h_ev_sai'])                     # evaporador + linha de sucção
    # perfil do capilar: a pressão cai pouco no trecho líquido e muito no trecho bifásico (o vapor acelera o escoamento);
    # forma didática da curva (exponencial), com o começo da vaporização onde P < Psat(T3)
    Pcurva = lambda s: Pc - (Pc - Pe) * (math.expm1(3.0 * s) / math.expm1(3.0))
    N = 48
    trechos = [   # ordem = SENTIDO DE CIRCULAÇÃO. 'lado' é o lado de pressão; 'troca' é o sentido do calor (+ entra no fluido)
        dict(id='evaporador', nome='Evaporador', lado='baixa', troca='+', meio='ar interno', T_meio_C=H['T_interior_C'],
             perfil=perfil_linear(Pe, Pe, h['h4'], h['h_ev_sai'], N)),
        dict(id='succao', nome='Linha de sucção', lado='baixa', troca='+', meio='ar da cozinha (pouco)', T_meio_C=H['T_cozinha_C'],
             perfil=perfil_linear(Pe, Pe, h['h_ev_sai'], h['h1'], 12)),
        dict(id='compressor', nome='Compressor', lado='baixa→alta', troca='W', meio='trabalho mecânico', T_meio_C=None,
             perfil=None),
        dict(id='descarga', nome='Linha de descarga', lado='alta', troca='-', meio='ar da cozinha', T_meio_C=H['T_cozinha_C'],
             perfil=perfil_linear(Pc, Pc, h['h2'], h['h2'] - 0.08 * (h['h2'] - CP.PropsSI('H', 'P', Pc, 'Q', 1, F)), 12)),
        dict(id='condensador', nome='Condensador', lado='alta', troca='-', meio='ar da cozinha', T_meio_C=H['T_cozinha_C'],
             perfil=None),
        dict(id='linha_liquido', nome='Linha de líquido e filtro secador', lado='alta', troca='-', meio='ar da cozinha', T_meio_C=H['T_cozinha_C'],
             perfil=perfil_linear(Pc, Pc, h['h_cd_sai'], h['h3'], 12)),
        dict(id='capilar', nome='Tubo capilar', lado='alta→baixa', troca='0', meio='(adiabático)', T_meio_C=None,
             perfil=perfil_linear(Pc, Pe, h['h3'], h['h4'], N, p_curva=Pcurva)),
    ]
    hd_fim = trechos[3]['perfil'][-1]['h_kJkg'] * 1e3
    trechos[4]['perfil'] = perfil_linear(Pc, Pc, hd_fim, h['h_cd_sai'], N)
    # compressor: perfil interno (compressão politrópica equivalente: h e P sobem juntos) só para a animação do corte
    comp = []
    for i in range(N):
        s = i / (N - 1); P = Pe * (Pc / Pe) ** s; hh = h['h1'] + (h['h2'] - h['h1']) * s
        d = props_Ph(P, hh); d['s'] = round(s, 4); comp.append(d)
    trechos[2]['perfil'] = comp
    # velocidade relativa do fluido (mesma vazão mássica, área diferente por trecho): v ∝ 1/(ρ·A)
    AREA = dict(evaporador=1.0, succao=1.6, compressor=1.0, descarga=0.9, condensador=0.9, linha_liquido=0.6, capilar=0.06)
    for t in trechos:
        for d in t['perfil']:
            d['v_rel'] = 1.0 / (d['rho'] * AREA[t['id']])
    vref = max(d['v_rel'] for t in trechos for d in t['perfil'] if t['id'] == 'evaporador')
    for t in trechos:
        for d in t['perfil']: d['v_rel'] = round(d['v_rel'] / vref, 4); d['rho'] = round(d['rho'], 3)
    res = dict(
        AVISO='MODELO DIDÁTICO: propriedades reais do R600a com hipóteses típicas; não representa um aparelho comercial.',
        hipoteses=H,
        pressoes=dict(baixa_bar=round(Pe / 1e5, 3), alta_bar=round(Pc / 1e5, 3), atm_bar=1.01325,
                      nota='com R600a o lado de baixa opera abaixo da pressão atmosférica'),
        estados={'1_succao': props_Ph(Pe, h['h1']), '2_descarga': props_Ph(Pc, h['h2']), '3_entrada_capilar': props_Ph(Pc, h['h3']),
                 '4_saida_capilar': props_Ph(Pe, h['h4']), 'saida_evaporador': props_Ph(Pe, h['h_ev_sai']), 'saida_condensador': props_Ph(Pc, h['h_cd_sai'])},
        energia_W=dict(Q_abs_evaporador=round(H['Q_abs_W'], 2), Q_abs_total=round(Q_abs_total, 2), W_eixo=round(W_eixo, 2), W_eletrico=round(W_el, 2),
                       Q_condensador=round(Q_cond, 2), Q_carcaca=round(Q_carcaca, 2), Q_rej_total=round(Q_rej_total, 2),
                       COP_ciclo=round(H['Q_abs_W'] / W_eixo, 3), COP_eletrico=round(H['Q_abs_W'] / W_el, 3),
                       vazao_g_s=round(m * 1e3, 4),
                       nota='Q̇_rej = Q̇_abs + Ẇ (taxas em regime permanente, W). Com a porta aberta na mesma cozinha, o aquecimento líquido do cômodo é Ẇ_elétrico.'),
        circuito=trechos)
    json.dump(res, open(os.path.join(A, 'ciclo_modelo.json'), 'w'), ensure_ascii=False, indent=1)
    e = res['estados']
    for k, v in e.items(): print(f"{k:20s} P={v['P_bar']:.3f} bar  T={v['T_C']:7.2f} °C  x={v['x']:.3f}  {v['fase']:8s} h={v['h_kJkg']:.1f}")
    print(json.dumps(res['energia_W'], ensure_ascii=False, indent=1))
    diagrama(res)


def diagrama(res):
    """Diagrama P–h com a cúpula de saturação e o ciclo do modelo (para o relatório científico)."""
    import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    Tc = CP.PropsSI('Tcrit', F); Ts = np.linspace(-45 + K, Tc - 0.5, 200)
    hl = [CP.PropsSI('H', 'T', t, 'Q', 0, F) / 1e3 for t in Ts]; hv = [CP.PropsSI('H', 'T', t, 'Q', 1, F) / 1e3 for t in Ts]
    Ps = [CP.PropsSI('P', 'T', t, 'Q', 0, F) / 1e5 for t in Ts]
    fig, ax = plt.subplots(figsize=(7, 5), dpi=130)
    ax.plot(hl, Ps, color='#555', lw=1); ax.plot(hv, Ps, color='#555', lw=1)
    cor = dict(evaporador='#2f7fd6', succao='#5aa0e0', compressor='#8b5cf6', descarga='#e2552b', condensador='#f08a2c', linha_liquido='#c9722b', capilar='#16a3a3')
    for t in res['circuito']:
        ax.plot([d['h_kJkg'] for d in t['perfil']], [d['P_bar'] for d in t['perfil']], color=cor[t['id']], lw=2.4, label=t['nome'])
    ax.set_yscale('log'); ax.set_xlabel('entalpia específica h (kJ/kg)'); ax.set_ylabel('pressão (bar, abs.)')
    ax.axhline(1.01325, color='#999', ls=':', lw=1); ax.text(ax.get_xlim()[0] + 5, 1.06, 'pressão atmosférica', fontsize=7, color='#777')
    ax.set_title('Modelo didático · R600a · diagrama pressão–entalpia', fontsize=10); ax.legend(fontsize=7, loc='upper left'); ax.grid(alpha=0.25, which='both')
    fig.tight_layout(); fig.savefig(os.path.join(A, 'diagrama_ph.png')); print('diagrama_ph.png')


if __name__ == '__main__':
    main()
