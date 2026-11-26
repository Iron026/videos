# Ep. 02 · Validação científica e modelo didático

> **Modelo didático.** Usa propriedades termodinâmicas **reais** do isobutano (R600a, biblioteca CoolProp 8.0) com hipóteses
> de operação **típicas e explícitas**. Não representa nenhum aparelho comercial. Os números servem para manter a animação
> coerente; o vídeo não os apresenta como medições de uma geladeira real.

Arquivos: `modelo_ciclo.py` gera `ciclo_modelo.json` (única fonte de dados do fluido para a animação) e `diagrama_ph.png`;
`testes_ciclo.py` verifica a física (resultado em `testes_ciclo_resultado.json`: **10 de 10 passam**).

## 1. Princípio

A geladeira é uma **bomba de calor**. Com trabalho fornecido ao compressor (Ẇ), ela transfere calor de uma região fria
(o interior, Q̇_abs) para uma região quente (a cozinha, Q̇_rej). Em regime permanente, com o compressor ligado, usando
**taxas** (watts):

  **Q̇_rej = Q̇_abs + Ẇ**

O calor não flui espontaneamente do frio para o quente (2ª lei). O trabalho é o "custo" do transporte.
Se a porta fica aberta numa cozinha fechada, o calor que entra na geladeira volta para a mesma cozinha: o efeito líquido
sobre o cômodo é **+Ẇ_elétrico** (ele aquece, não resfria).

## 2. Arquitetura escolhida (genérica, documentada)

Refrigerador doméstico **de uma porta**, comum no Brasil, cerca de 0,60 × 0,65 × 1,50 m:

| Componente | Escolha | Por quê |
|---|---|---|
| Evaporador | Caixa do congelador no alto do compartimento (placas de alumínio com canais, tipo *roll-bond*) | Reconhecível (é onde forma gelo); fica **dentro** do espaço refrigerado |
| Circulação do ar interno | Convecção natural: ar frio desce, ar morno sobe | Mostra como o calor dos alimentos chega ao evaporador |
| Compressor | Hermético alternativo (pistão), no nicho inferior traseiro | Tipo mais comum em geladeiras domésticas; mecanismo visível em corte |
| Condensador | Serpentina de tubo com arames na parede traseira | Explica o "quente por fora"; fácil de reconhecer |
| Filtro secador | Na saída do condensador, antes do capilar | Componente real da linha de líquido |
| Dispositivo de expansão | Tubo capilar (cobre, diâmetro interno ≈ 0,6–0,8 mm, alguns metros, enrolado) | Padrão em refrigeradores domésticos |

Outras arquiteturas existem (condensador embutido nas laterais, *frost-free* com ventilador, compressor rotativo ou
inverter). O vídeo mostra **um** arranjo coerente, sem afirmar que todas as geladeiras são assim.

## 3. Hipóteses do modelo

| Hipótese | Valor | Observação |
|---|---|---|
| Fluido | R600a (isobutano) | Refrigerante usual em geladeiras domésticas novas |
| Ar interno / cozinha | 4 °C / 25 °C | Típicos |
| Saturação no evaporador | −20 °C → **0,73 bar abs.** | Lado de baixa **abaixo da pressão atmosférica** (característica do R600a, citada pela Danfoss) |
| Saturação no condensador | +40 °C → **5,31 bar abs.** | 15 K acima da cozinha |
| Superaquecimento / sucção | saída do evaporador −15 °C; sucção −10 °C | Compressor recebe **só vapor** |
| Sub-resfriamento | saída do condensador 37 °C; entrada do capilar 33 °C | |
| Compressão | eficiência isentrópica 0,60; motor 0,80 | Perdas do motor saem como calor pela carcaça (na cozinha) |
| Carga térmica ilustrativa | Q̇_abs = 80 W | |

Simplificações: sem trocador de calor entre capilar e linha de sucção (existe em muitos modelos; omitido para não
confundir); perdas de pressão desprezadas fora do capilar; capilar adiabático e isentálpico, com queda de pressão
distribuída; termostato (liga/desliga) não modelado.

## 4. Resultados

| Estado | P (bar) | T (°C) | Fase |
|---|---|---|---|
| 1 · sucção do compressor | 0,73 | −10,0 | vapor superaquecido |
| 2 · descarga do compressor | 5,31 | +72,7 | vapor superaquecido |
| saída do condensador | 5,31 | +37,0 | líquido sub-resfriado |
| 3 · entrada do capilar | 5,31 | +33,0 | líquido |
| 4 · saída do capilar | 0,73 | −20,0 | **mistura, 33 % vapor em massa** |
| saída do evaporador | 0,73 | −15,0 | vapor superaquecido |

Balanço (W): Q̇_abs total 82,4 (evaporador 80,0 + linha de sucção 2,4) + Ẇ_elétrico 50,3 = **Q̇_rej total 132,7**
(condensador 119,5 + linha de líquido 3,1 + carcaça 10,1). COP do ciclo 1,99 (Carnot entre −20 e 40 °C: 4,22).

Perfis usados pela animação:
- **Capilar:** a pressão cai pouco no começo e muito no fim. O líquido começa a vaporizar a **53 %** do comprimento (s = 0,53).
  Antes disso, a temperatura sobe **16 mK** (efeito Joule–Thomson de líquidos; invisível, documentado).
- **Evaporador:** título 0,33 → 1,0; o vapor fica 100 % seco a **98 %** do percurso. Temperatura quase constante (−20 °C)
  enquanto há líquido: o calor absorvido vai para a **mudança de fase**, não para o aquecimento.
- **Condensador:** primeiro o vapor esfria de 70 para 40 °C (até s = 0,17); depois condensa a 40 °C constantes
  (s = 0,17–0,98); por fim se sub-resfria.
- **Velocidade do fluido** (mesma vazão mássica, v ∝ 1/(ρ·A)): varia mais de 1.000× (líquido lento, vapor rápido).
  Na tela, a velocidade é **comprimida** (escala logarítmica) e o fluxo aparece em câmera lenta. Isso é indicado com um
  aviso quando for relevante.

## 5. Revisão do roteiro oficial

**Nenhum erro científico encontrado.** O roteiro não foi alterado. Duas observações para a animação, sem mudar o texto:

1. *"A pressão cai bruscamente"* (F27): no capilar, a queda é **distribuída ao longo de metros de tubo**, não acontece num
   ponto. "Bruscamente" vale em relação ao resto do circuito (de 5,3 para 0,7 bar num tubo finíssimo). A animação mostra a
   queda ao longo do capilar, mais forte no fim, e não um "estalo" num ponto.
2. *"parte do líquido evapora, resfriando a mistura"* (F27): correto. A energia para vaporizar sai do próprio fluido, com
   entalpia constante. A animação **não** mostra energia entrando nem saindo do capilar.

Pontos já corretos no texto e que a imagem precisa respeitar:
- F15–F17: o fluido chega como **mistura** e a **parte líquida** evapora (não "o líquido inteiro de uma vez").
- F21–F22: só depois da compressão o fluido fica **mais quente que a cozinha**, o que permite rejeitar calor (F23).
- F32–F33: a geladeira aberta **aquece** a cozinha fechada (+Ẇ). Nenhuma imagem pode sugerir resfriamento do cômodo.

## 6. Linguagem visual (grandezas que não podem se confundir)

| Grandeza | Representação | Cor |
|---|---|---|
| **Temperatura** | Cor do fluido e da "visão térmica" | Escala divergente centrada na **temperatura da cozinha**: azul = mais frio que o ambiente, cinza-claro = igual, laranja/vermelho = mais quente |
| **Fase** | Aparência física no tubo em corte: líquido = preenchimento contínuo; mistura = líquido com bolhas; vapor = névoa rala e rápida | (independente da cor) |
| **Pressão** | Manômetros e faixas "lado de baixa" / "lado de alta" | Neutra (creme e azul-marinho da marca); **nunca** pela cor do fluido |
| **Sentido do fluxo** | Movimento do padrão do fluido e pequenas setas nos tubos | (movimento) |
| **Calor (energia transferida)** | Feixes ondulados e contínuos com setas, sempre do quente para o frio. **Não** partículas | Âmbar-dourado |
| **Trabalho (eletricidade → compressor)** | Pulsos no cabo e no motor | Violeta |

Regra: temperatura e pressão variam de forma independente. Exemplo: na entrada do capilar o fluido está em **alta**
pressão e **morno** (33 °C, laranja-claro); na saída da descarga está em **alta** pressão e **quente** (73 °C, vermelho);
no evaporador está em **baixa** pressão e **frio**. A cor muda dentro do mesmo lado de pressão.

## 7. Fontes consultadas

- Danfoss, *Practical application of refrigerant R600a (isobutane) in domestic refrigerator systems*: lado de baixa
  abaixo da pressão atmosférica com R600a; capacidade volumétrica menor que a do R134a.
  [assets.danfoss.com](https://assets.danfoss.com/documents/latest/27733/AN000086421702en-000101.pdf)
- Danfoss, documento técnico de compressores domésticos.
  [assets.danfoss.com](https://assets.danfoss.com/documents/latest/90305/AB270523412055en-000101.pdf)
- Estudos com R600a em refrigeradores domésticos com compressor hermético alternativo e tubo capilar:
  [core.ac.uk](https://core.ac.uk/download/286851963.pdf) ·
  [UJ](https://pure.uj.ac.za/en/publications/investigation-of-household-refrigerator-system-with-varied-capill/) ·
  [dergipark](https://dergipark.org.tr/en/download/article-file/1905755)
- Trocador capilar–linha de sucção em refrigeradores domésticos (patente US4147037):
  [Google Patents](https://patents.google.com/patent/US4147037)
- Glossário de componentes (capilar, condensador, evaporador): [iFixit](https://www.ifixit.com/Wiki/Refrigerator_Parts_and_Terms_Glossary)
- Geladeira aberta num cômodo fechado aquece o cômodo (balanço de energia): University of Illinois, *Ask the Van*:
  [van.physics.illinois.edu](https://van.physics.illinois.edu/ask/listing/1790)
- Propriedades do R600a: CoolProp 8.0 (equação de estado de referência do isobutano).

**Limites:** as condições típicas (−20/+40 °C) foram escolhidas como representativas. Não encontrei uma única fonte que
fixe "a" temperatura de evaporação de uma geladeira de uma porta (varia com o termostato, o modelo e a carga). Por isso
o vídeo evita números absolutos na tela e usa comparações ("mais frio que o ar", "mais quente que a cozinha"), que valem
para qualquer refrigerador desse tipo.
