# Ep. 01 · Prévia integral v2: relatório das correções

| Item | Valor |
|---|---|
| Arquivo | `episodio/ep01_previa.mp4` (prévia de baixo custo: render a 270×480, montagem a 540×960) |
| Versão anterior preservada | `episodio/ep01_previa_v1.mp4` |
| Comparativo | `episodio/comparativo_previa_v1_v2.jpg` (18 momentos corrigidos, v1 acima e v2 abaixo) |
| Validação científica | `episodio/validacao_cientifica_ep01.md` |

**O que não mudou:** a narração (original intacta, velocidade inalterada), as legendas (mesmos tempos das palavras reais), a assinatura oficial e a duração de **171,0 s**.

## Correções realizadas

| # | Pedido | O que foi feito |
|---|---|---|
| 1 | Continuidade | A abertura mostra **outro** porta-contêineres, reaproveitando o modelo com outra pintura: casco cinza-claro, faixa e chaminé verdes, superestrutura cinza, pontes de peação cinza e 5 camadas de carga. O navio do episódio (casco azul-marinho, faixa creme, estruturas amarelas) aparece **vazio** do estaleiro até 94,55 s, com 0 contêineres nos segmentos 03–08b, verificado nos arquivos exportados. Recebe a carga a partir de 100,1 s, com mudança de calado de 8,00 para 9,42 m |
| 2 | Lançamento | O elevador de navios foi substituído por um **dique seco inundado**: comporta, picadeiros e água subindo (tempo acelerado). Com 8,0 m de água sobre a quilha o casco deixa os picadeiros ("Começa a flutuar") e passa a **acompanhar o nível** com calado constante: a linha d'água fica parada na marca 8M enquanto o dique continua enchendo. Não há oscilação ou afundamento após flutuar |
| 3 | Empuxo | São 6 setas de pressão em vez de até 18, mais grossas, com cor e tamanho por profundidade. As laterais somem quando se compensam; as do fundo **convergem e viram uma única seta**, o empuxo. Código de cores único: empuxo e água deslocada em ciano, peso em azul-marinho. A cópia do volume foi removida. No máximo 2 rótulos por vez, câmera mais próxima |
| 4 | Bloco × casco | Lado a lado no mesmo corte: bloco maciço de aço de 17,2 m com o rótulo "**Mesma massa do navio vazio**" e a face "Aço maciço", contra o casco com o interior destacado "**Ar**". Pesos iguais; empuxo do bloco 13% (afunda), empuxo do casco igual ao peso (flutua). O bloco de 1,6 m da abertura continua só no seu trecho, com as mesmas cores |
| 5 | Trechos estáticos | Segmento 11 refeito com um movimento motivado: sobe pela escala de calado até a linha d'água, desliza pelo costado até a meia-nau ("outras…") e acompanha cada linha de carga quando acende. O navio atracado arfa levemente. A detecção automática (área da imagem sem legendas) **não acusa nenhum trecho parado acima de 1 s** fora da assinatura (antes: 2,3 s e 2,7 s) |
| 6 | Inundação | Hidrostática refeita: duplo fundo e tanques laterais **estanques e secos**, rombo no costado simples, só o porão alaga (μ = 0,95), efeito de superfície livre e GM documentados. Resultado: **+1,27 m** a meia-nau, **trim 0,71° pela proa**, GM 1,50 → 0,74 m, borda livre na proa de 6,0 m. Na cena: jato pelo rombo, água subindo com superfície horizontal até o nível de fora, **linha d'água anterior** desenhada no navio contra o **nível do mar**, e "Proa: +2,6 m" / "Popa: +0,0 m". A hipótese grave avança porão a porão e é desfeita antes das divisórias |
| 7 | Acabamento | Mesmo céu diurno e mesma água de mar nos segmentos de mar. Estaleiro filmado do lado iluminado (sem sombra azulada). Nivelamento automático de exposição e saturação por segmento na montagem. Rótulos 30% maiores. Algarismos das marcas na fonte Montserrat (antes 9 e 0 se confundiam). Avisos "Tempo acelerado" e "Câmera lenta" nos trechos que alteram o tempo |
| — | Carregamento | Contêineres descem 7 m até a pilha no time-lapse; o plano "E mais outro" foi refeito fora das pernas do portêiner; a câmera desce do convés até a linha d'água em "Observe a linha d'água" |

## Validação técnica e de sincronização (MP4 da prévia v2)

| Verificação | Resultado |
|---|---|
| Duração | **171,0 s**, abaixo de 180 s |
| Narração no MP4 | Correlação com a narração original em 10, 85 e 160 s: desvio de **+3 ms** nos três pontos, sem deriva |
| Legendas | Mesmos blocos da v1, gerados dos tempos de cada palavra |
| Eventos sincronizados | Encaixe da chapa 23,6 s; casco flutua 46,1 s; empuxo 61,45 s; peso 71,2 s; bloco toca o leito 82,1 s; pousos dos contêineres 101,6 · 102,95 · 104,45 s; rombo 136,6 s; divisórias 151,05 s |
| Quadros pretos / congelamentos ≥ 1,5 s | nenhum / nenhum |
| Loudness | −14,0 LUFS, pico −1,9 dBTP |
| Música | Original, sintetizada no projeto |

## Custo desta rodada

- Exportações no Blender: ~10 min.
- Render da prévia dos 11 segmentos alterados: **~21 min** (1.560 quadros a 0,45–1,33 s).
- Retoques de 04 e 11: ~4 min.
- Montagens: ~2 min cada.
- Nenhum render de revisão nem definitivo foi executado.

**Próximos renders (aguardando sua autorização):**
- Revisão a 540×960: ~4.830 quadros × ~3 s ≈ **4 h**. O segmento 02 de revisão anterior não serve mais, porque o navio mudou.
- Final a 1080×1920: **≈ 11–17 h**.

## Problemas que ainda persistem

1. **Resolução da prévia:** a 270×480 os textos das marcas e alguns detalhes ficam serrilhados. Devem ser conferidos no render de revisão.
2. **Dique seco:** a separação entre quilha e picadeiros acontece debaixo d'água e não aparece em close. A leitura vem da linha d'água parada na marca 8M e do rótulo "Começa a flutuar". Um plano em corte (diorama) mostraria o vão, mas é uma cena nova.
3. **Trim de 0,71°:** é pequeno em tela vertical. A leitura depende das duas linhas de referência e dos rótulos de proa e popa. No plano aberto o navio fica fino; vale avaliar se você prefere um plano mais próximo da proa.
4. **Superestrutura:** aparece já completa a partir do corte (04), mas no estaleiro (03) estava em montagem. Há um salto de tempo implícito.
5. **Vistas submersas:** continuam em diorama (corte na água), coerentes entre os segmentos, mas é um estilo a confirmar.
6. **Água:** é um efeito de shader, sem simulação de fluido. O jato no rombo e a entrada no dique são formas translúcidas simplificadas.
7. **Massa média de 20 t por contêiner, KG e GM intacto (1,50 m):** são hipóteses adotadas e documentadas, não dados de um navio real.
8. **Estrutura da avaria (tanques laterais até 6 m e costado simples acima):** é uma hipótese necessária para o rombo alagar só o porão. Também está documentada.
