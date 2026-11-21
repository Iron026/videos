"""Testes científicos do modelo do ciclo (ciclo_modelo.json). Cada teste corresponde a um item da lista do pedido.
Itens 8–10 (interpenetração de geometria, z-fighting, contradição com a narração) são testados na cena 3D
(blender/testes_cena.py) e na decupagem. Uso: python3 testes_ciclo.py  → código 0 se tudo passar."""
import json, os, sys
import CoolProp.CoolProp as CP
A = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(A, 'ciclo_modelo.json')))
C = M['circuito']; E = M['energia_W']; H = M['hipoteses']
ORDEM = ['evaporador', 'succao', 'compressor', 'descarga', 'condensador', 'linha_liquido', 'capilar']
falhas, ok = [], []
def teste(nome, cond, det=''):
    (ok if cond else falhas).append(f'{nome}: {det}')


# 1. sentido de circulação: a ordem dos trechos é a do ciclo, e o último trecho alimenta o primeiro
teste('1 sentido de circulação', [t['id'] for t in C] == ORDEM, ' → '.join(t['id'] for t in C) + ' → evaporador')

# 6. continuidade: o fim de cada trecho = início do seguinte (P, h); o ciclo fecha
salto = []
for i, t in enumerate(C):
    a, b = t['perfil'][-1], C[(i + 1) % len(C)]['perfil'][0]
    if abs(a['P_bar'] - b['P_bar']) > 1e-3 or abs(a['h_kJkg'] - b['h_kJkg']) > 0.05: salto.append(f"{t['id']}→{C[(i+1)%len(C)]['id']}")
teste('6 continuidade do circuito', not salto, 'saltos: ' + (', '.join(salto) or 'nenhum'))

# 3. compressor recebe só vapor (superaquecido) na sucção
s1 = C[2]['perfil'][0]
Tsat = CP.PropsSI('T', 'P', s1['P_bar'] * 1e5, 'Q', 1, 'R600a') - 273.15
teste('3 sucção só com vapor', s1['fase'] == 'vapor' and s1['T_C'] > Tsat + 2, f"fase={s1['fase']}, T={s1['T_C']:.1f} °C, Tsat={Tsat:.1f} °C, superaq.={s1['T_C']-Tsat:.1f} K")

# 2. mudanças de fase compatíveis: título monotônico no evaporador (sobe), no condensador (desce), no capilar (sobe);
#    trechos de pressão constante não mudam de fase sem troca de calor
def mono(p, sinal): return all(sinal * (p[i + 1]['x'] - p[i]['x']) >= -1e-6 for i in range(len(p) - 1))
fases_ok = (mono(C[0]['perfil'], +1) and C[0]['perfil'][0]['fase'] == 'mistura' and C[0]['perfil'][-1]['fase'] == 'vapor'
            and mono(C[4]['perfil'], -1) and C[4]['perfil'][0]['fase'] == 'vapor' and C[4]['perfil'][-1]['fase'] == 'liquido'
            and mono(C[6]['perfil'], +1) and C[6]['perfil'][0]['fase'] == 'liquido' and C[6]['perfil'][-1]['fase'] == 'mistura'
            and all(d['fase'] == 'vapor' for i in (1, 2, 3) for d in C[i]['perfil'])
            and all(d['fase'] == 'liquido' for d in C[5]['perfil']))
teste('2 mudanças de fase coerentes', fases_ok,
      f"evap {C[0]['perfil'][0]['x']:.2f}→{C[0]['perfil'][-1]['x']:.2f}; cond {C[4]['perfil'][0]['fase']}→{C[4]['perfil'][-1]['fase']}; capilar x 0→{C[6]['perfil'][-1]['x']:.2f}")

# 4. condensação só com rejeição de calor: no condensador h cai e o fluido está mais quente que o ar em todo ponto
c = C[4]['perfil']
teste('4 condensação com rejeição de calor', all(c[i + 1]['h_kJkg'] <= c[i]['h_kJkg'] for i in range(len(c) - 1)) and min(d['T_C'] for d in c) > H['T_cozinha_C'],
      f"h {c[0]['h_kJkg']:.1f}→{c[-1]['h_kJkg']:.1f} kJ/kg; T mín. no condensador {min(d['T_C'] for d in c):.1f} °C > cozinha {H['T_cozinha_C']} °C")

# 5. expansão sem ganho de energia: no capilar h constante (isentálpico) e P só desce. A temperatura do trecho ainda LÍQUIDO
#    pode subir alguns milésimos de kelvin (coeficiente de Joule–Thomson negativo de líquidos — física real, não erro);
#    a partir do início da vaporização (flash), T precisa cair.
k = C[6]['perfil']
iso = max(abs(d['h_kJkg'] - k[0]['h_kJkg']) for d in k)
p_desce = all(k[i + 1]['P_bar'] <= k[i]['P_bar'] + 1e-9 for i in range(len(k) - 1))
liq = [d for d in k if d['fase'] == 'liquido']; mis = [d for d in k if d['fase'] == 'mistura']
aq_liq = max(d['T_C'] for d in liq) - k[0]['T_C']
t_desce_mis = all(mis[i + 1]['T_C'] < mis[i]['T_C'] for i in range(len(mis) - 1))
s_flash = mis[0]['s'] if mis else None
teste('5 expansão sem ganho de energia', iso < 1e-6 and p_desce and aq_liq < 0.1 and t_desce_mis,
      f"variação de h = {iso:.1e} kJ/kg; P {k[0]['P_bar']:.2f}→{k[-1]['P_bar']:.2f} bar; líquido +{aq_liq*1000:.0f} mK (Joule–Thomson); "
      f"vaporização começa em s={s_flash} do capilar; T {k[0]['T_C']:.1f}→{k[-1]['T_C']:.1f} °C")

# 7. sentido da troca de calor compatível com as temperaturas locais
erros = []
for t in C:
    if t['troca'] in '+-' and t['T_meio_C'] is not None:
        for d in t['perfil']:
            if t['troca'] == '+' and not d['T_C'] < t['T_meio_C']: erros.append(f"{t['id']} T={d['T_C']:.1f}")
            if t['troca'] == '-' and not d['T_C'] > t['T_meio_C']: erros.append(f"{t['id']} T={d['T_C']:.1f}")
teste('7 calor do quente para o frio', not erros, 'violações: ' + (', '.join(erros[:5]) or 'nenhuma'))

# balanço de energia (1ª lei): Q̇_rej = Q̇_abs + Ẇ_elétrico
bal = E['Q_rej_total'] - (E['Q_abs_total'] + E['W_eletrico'])
teste('balanço Q̇_rej = Q̇_abs + Ẇ', abs(bal) < 0.05, f"{E['Q_rej_total']} W = {E['Q_abs_total']} + {E['W_eletrico']} W (resíduo {bal:+.3f} W)")
# 2ª lei: COP abaixo do de Carnot entre as temperaturas de saturação
Tl, Th = H['T_evap_C'] + 273.15, H['T_cond_C'] + 273.15
teste('COP < Carnot', E['COP_ciclo'] < Tl / (Th - Tl), f"COP {E['COP_ciclo']} < Carnot {Tl/(Th-Tl):.2f}")
# lados de pressão
teste('lados de pressão', all((d['P_bar'] < 1.0) == (t['lado'] == 'baixa') for t in C if t['lado'] in ('baixa', 'alta') for d in t['perfil']),
      f"baixa {M['pressoes']['baixa_bar']} bar (abaixo da atmosférica) · alta {M['pressoes']['alta_bar']} bar")

for s in ok: print('PASSOU  ', s)
for s in falhas: print('FALHOU  ', s)
print(f'{len(ok)} passaram, {len(falhas)} falharam')
json.dump(dict(passaram=ok, falharam=falhas), open(os.path.join(A, 'testes_ciclo_resultado.json'), 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if falhas else 0)
