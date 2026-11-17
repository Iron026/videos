# Ep. 01 · Plano de correção da prévia (antes de novo render)

**Base mantida:** a montagem, a narração original (sem nenhuma alteração), as legendas alinhadas às palavras reais, a assinatura oficial, a identidade visual, os modelos e os materiais aprovados.
**Render em andamento:** interrompi o render de revisão. Ele refaria quase todos os segmentos que este plano vai mudar (cerca de 3,5 h de CPU desperdiçadas). O segmento 02 já renderizado foi guardado.

## Diagnóstico (verificado nos arquivos, não só a olho)

| Ponto | O que encontrei |
|---|---|
| 1 · Contêineres antes do carregamento | Contei os grupos de contêiner exportados por segmento. **O único trecho anterior ao carregamento que mostra navio carregado é o SEG02 (4,4–15,1 s)**, o "gigante" da abertura. Os segmentos 04, 05, 06/07, 08a e 08b têm 0 contêineres. Como na abertura é o mesmo navio que depois é construído, a sequência sugere que ele já estava carregado |
| 2 · Lançamento | Um elevador de navios (shiplift) não é compatível com este porte: o navio leve calculado tem ~39.700 t, acima da capacidade dos maiores elevadores. A descida também ficou rápida demais |
| 3 · Empuxo | Até 18 setas de pressão simultâneas, mais empuxo, peso, volume deslocado, a cópia do volume e 5 rótulos. Em tela pequena as setas laterais somem, e B e G ficam pequenos demais |
| 4 · Bloco × casco | O cubo maciço aparece longe, sem corte, e o espaço interno do casco não é destacado. A diferença não é imediata |
| 5 · Trechos estáticos | Detecção automática na prévia (`freezedetect`, área da imagem sem legendas): **125,6–128,0 s (2,3 s)** na escala de calado e **130,1–132,8 s (2,7 s)** na marca de linha de carga. O restante do episódio não tem trechos parados acima de 1 s, exceto a pausa intencional da assinatura (167 s) |
| 6 · Inundação | **Erro científico encontrado.** O cálculo tratou como inundada a seção inteira entre as anteparas, incluindo o duplo fundo e os tanques laterais, que são compartimentos estanques separados. Refeito considerando só o porão (acima do duplo fundo e por dentro dos tanques laterais, permeabilidade 0,95 de porão vazio): calado a meia-nau +**1,17 m** (não +1,66 m), trim de **0,65°** pela proa (não 0,92°), proa 11,8 m, popa 9,5 m, borda livre na proa ~6,2 m. A superfície da água dentro do porão também estava presa ao navio, quando deveria ficar horizontal no mundo |
| 7 · Diferenças entre segmentos | Céu e sol mudam de um segmento a outro sem motivo; a água tem densidades diferentes no mar aberto; a sombra fica azulada no pátio (SEG03); os rótulos são pequenos para celular |

## Plano por segmento

Legenda: **M** = só montagem (sem render) · **R** = nova exportação e novo render do segmento · **N** = cena nova (montagem da cena no Blender e render).

| Segmento | Tempo (s) | Correção | Tipo |
|---|---|---|---|
| 01 Cais | 0–4,4 | Sem mudança (quadros finais já existem) | — |
| 02 O gigante | 4,4–15,1 | **Decisão sua (ver abaixo).** Recomendo um **outro navio**, um porta-contêineres em operação, com pintura diferente (casco cinza-claro e faixa de outra cor). A fala diz "olha este gigante… carregando milhares de toneladas" e depois "vamos descobrir construindo **um** navio": a abertura passa a ser um exemplo, e o nosso navio nasce vazio no estaleiro. Céu e água padronizados | R |
| 03 Estaleiro | 15,1–30,3 | Acabamento: sol girado para tirar a sombra azulada do pátio; mesmo céu do 04 | R |
| 04 Não é bloco maciço | 30,3–41,55 | Destaque do **ar interno** (volume claro no porão, ligado ao ponto 4); mesmo céu | R |
| 05 Entra na água | 41,55–48,0 | **Cena nova: dique seco inundado.** O casco fica nos picadeiros dentro do dique; as válvulas da comporta abrem e a água sobe pelo casco (time-lapse sinalizado). Quando chega a 8,0 m, o casco **sai dos picadeiros e flutua**: a água continua subindo, mas a linha d'água no casco **para** nas marcas de calado. Assim "afunda um pouco… e para" vira a leitura exata do equilíbrio. Diorama com corte na água para ver os picadeiros se afastando | N |
| 06/07 Pressão, empuxo, Arquimedes | 48,0–74,85 | **Simplificação:** 6 setas de pressão (2 rasas e 2 fundas nos costados, 2 no fundo), mais grossas e com intensidade por cor; as laterais pulsam em pares e somem ("se compensam"); as do fundo **convergem numa só seta, o empuxo**. Depois só três elementos: volume deslocado (ciano), **seta do empuxo também ciana** (a mesma cor liga "empuxo = peso da água deslocada") e o peso do navio (azul-marinho), iguais e opostos. A cópia que subia sai. Câmera mais perto, setas 2× mais grossas, no máximo 2 rótulos por vez | R |
| 08a O bloco | 74,85–83,85 | Mesma cena; setas mais grossas e o mesmo código de cores (peso azul-marinho, empuxo ciano curto); o cubo de "água deslocada" ao lado do bloco em vez de sair do quadro | R |
| 08b Casco × bloco | 83,85–94,55 | **Cena reformulada lado a lado no mesmo corte:** à esquerda, um bloco maciço de aço com **o mesmo peso do navio** (17,2 m de aresta), cortado mostrando aço sólido; à direita, a seção do casco com o **interior de ar destacado**. Os dois têm a mesma seta de peso. O empuxo do bloco é curto (13%) e ele afunda; o empuxo do casco iguala o peso e ele flutua. Física igual à já validada | R |
| 09 Carregamento | 94,55–117,2 | Continuidade já correta (vazio → carregado, calado 8,0 → 9,42 m). Ajustes: o plano "E mais outro" sai de dentro das pernas do portêiner; a passagem para o close da linha d'água ganha um movimento de descida de câmera motivado ("Observe a linha d'água") | R (só 103–110 s) |
| 10 Calado | 117,2–123,65 | Sem mudança de cena; padronizar a água | R leve (opcional) |
| 11 Marcas | 123,65–134,0 | **Fim dos trechos parados:** um só movimento motivado, que percorre as marcas de calado de baixo para cima até a linha d'água, segue pelo costado até a meia-nau ("outras…") e acompanha as linhas S → T → W → F → TF conforme acendem. O navio atracado arfa levemente e a água bate nas marcas (movimento real, não artificial) | R |
| 12 Avaria | 134,0–154,6 | **Correções científicas:** hidrostática refeita (+1,17 m e 0,65°); duplo fundo e tanques laterais mostrados como compartimentos **intactos**; água entra pelo rasgo abaixo da linha d'água (jato e bolhas no rasgo) e sobe até o nível de fora, com superfície horizontal no mundo; **linha d'água original pintada no casco**, para ver o quanto afundou; trim legível com referência horizontal. A hipótese grave fica progressiva (antepara por antepara, em vermelho, marcada como hipótese) e é desfeita antes de "divisórias estanques" | R |
| 13 Conclusão | 154,6–166,3 | Cores alinhadas (volume deslocado ciano, empuxo ciano, peso azul-marinho), setas mais grossas | R |
| Assinatura | 166,2–171,0 | Sem mudança | — |
| Montagem e áudio | inteiro | Rótulos ~30% maiores e com contraste de celular; leve correção de cor por segmento para igualar exposição e saturação; efeitos sonoros refeitos para os eventos novos (água entrando no dique, picadeiros, setas). **Narração e legendas intactas.** Duração continua 171,0 s | M |

## Sem reconstruir as cenas (só montagem)

- Tamanho, contraste e posição dos rótulos.
- Correção de cor por segmento.
- Duração e tipo das fusões, e ajuste fino dos cortes entre frases.
- Mixagem e efeitos sonoros.
- Legendas (já corretas; nenhuma mudança prevista).

## Exige nova exportação e novo render

- Segmentos 02, 03, 04, 06/07, 08a, 08b, 09 (parcial), 11, 12 e 13.
- Cena nova: 05 (dique seco).
- Sem render: 01, 10 (opcional) e a assinatura.

## Custo computacional estimado (sem GPU)

| Etapa | O que roda | Estimativa |
|---|---|---|
| Ajustes de cena e hidrostática | Blender + Python | ~15 min de exportação (os segmentos 09 e 11 levam ~2 min cada) |
| **Prévia de baixo custo** (270×480, 10 fps) dos segmentos alterados | ~1.350 quadros × 0,8 s | **~20 min** |
| Montagem da prévia | 5.130 quadros | ~2 min |
| Versão de revisão (540×960, GTAO 4, 30 fps), só depois da sua aprovação | ~4.070 quadros × 3 s | **~3,4 h** |
| Versão final (1080×1920), não incluída nesta etapa | ~4.830 quadros × 8–12,6 s | ~11–17 h |

**Proposta de execução:**
1. Aplicar as correções.
2. Gerar a **prévia de baixo custo** integral (~35 min no total) para você conferir narrativa e ciência.
3. Só então rodar a versão de revisão.

## Decisão pendente

**SEG02, o "gigante" da abertura:**
- **(A) recomendado:** outro navio, carregado e com outra pintura. Coerente com a fala e sem quebrar a continuidade do nosso navio.
- **(B):** o nosso próprio navio já carregado, como antecipação do final, com transição que marque o "salto no tempo".
- **(C):** o nosso navio vazio. Contradiz "carregando milhares de toneladas".

**Opcional, inclinação:** com o porão de bordo a bordo, a inclinação é só longitudinal (trim de 0,65°), discreta mas correta. Se quiser uma inclinação lateral (banda) bem visível, a avaria pode atingir um tanque lateral de um só bordo. Calculo a banda resultante antes de aplicar.
