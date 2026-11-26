# Ep. 02 · Relatório da rodada 7 (decisões antes do render definitivo)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado.
O render completo em 1080 p **não foi iniciado**. Nesta rodada só rodaram testes e comparativos, sem re-renderizar o
episódio.
- **Preservados:**
  - narração (SHA-256 `fdedd877…`), roteiro, palavras, modelo científico;
  - duração (151,23 s, 4.537 quadros);
  - mixagem da V6 (stems, ganhos, fontes, licenças: nada mudou no áudio).

## Entregas (somente o necessário para decidir)
| Arquivo | O que é |
|---|---|
| `relatorios/manometros_atual_x_novo_1.jpg`, `_2.jpg` | Manômetros atual × novo em C4, D2, E3, G3 e H2 (vários instantes) |
| `episodio/testes_r7/manometros_novos_5_planos.mp4` | Os 5 planos com manômetro, completos, com o novo layout (prévia, com áudio) |
| `relatorios/teste_manometros.json` | Teste automático de todos os quadros: cortes, sobreposições, linhas, ponteiros, estabilidade |
| `relatorios/ao_comparativo_540.jpg` | AO: atual × `aocorte` × corte + máscara × plana + máscara em G3, J3, C4 e D4 (mesmos quadros, câmeras e luz) |
| `relatorios/g3_ao_1080.jpg`, `j3_ao_folga_1080.jpg`, `episodio/testes_r7/j3_ao_1080_atual_x_corrigido.mp4` | Confirmação em 1080 (J3 em velocidade real e 0,5×) |
| `relatorios/comparativo_ao.json` | Medidas do AO (granulado, sombreamento, cintilação) |
| `episodio/testes_r7/c2_atual_x_obturador.mp4`, `relatorios/c2_obturador_quadros.jpg`, `c2_estrobo.json` | C2: atual × obturador 180° × 270° (velocidade real e 0,5×) |

## 1. Manômetros: implementado e testado (agora padrão)
- **Implementado:** mostrador 25 % maior (raio 80 px em 1080).
  - Textos "pressão", "baixa" e "alta" com 30 px, contorno escuro, **fora do anel**.
  - "Pressão" fica no topo; "baixa" e "alta" ficam nas laterais, na altura das pontas da escala.
  - A parte de baixo fica livre para a linha de ligação.
- **Posicionamento com regras** (o simples aumento do mostrador criava cortes e sobreposições):
  - candidatos em volta da âncora e posições fixas;
  - escolha no plano inteiro por programação dinâmica, com o mínimo de trocas de lugar;
  - pares lado a lado, na ordem horizontal das âncoras.
- **Reversível** com `MANOMETRO_LEGIVEL=0`.

**Teste automático em todos os 613 quadros com manômetro, composto em 1080:**
| Verificação | Atual | Novo |
|---|---|---|
| Texto encostando ou saindo do anel | 1.690 ocorrências | **0** |
| Texto cortado pela borda do quadro | 0 | **0** |
| Mostrador ou texto × lupa | 122 | **0** |
| Sobreposição com legenda, avisos ou rótulos | 0 | **0** |
| Mostrador × mostrador (pares) | 0 | **0** |
| Linha de ligação sobre texto | 40 | **2** (G3, 106,13–106,17 s, durante a única fusão) |
| Altura dos textos em 1080 | 16–27 px | **33–41 px** (meta ≥ 30) |
| Ponteiros (valor e ângulo) | — | **845 de 845 idênticos**: a ciência não mudou |

- **Estabilidade:**
  - **C4, D2, E3 e H2:** nenhuma troca de lugar; o mostrador acompanha a âncora (até 5 px por quadro em 1080).
  - **G3:** o marcador atravessa a tela inteira (da base até sob a lupa), por isso há **1** troca de lugar, feita como
    fusão de 0,3 s.
- **Demais planos:** em 117 quadros compostos (3 por plano), os que não têm manômetro saem **idênticos pixel a pixel** à
  V6.

## 2. AO nos cortes: comparativo controlado
**Variantes**, com os mesmos quadros, câmeras e luz (12 quadros seguidos em 540, e 30 em 1080 para J3 e G3):
1. **atual:** o AO "vê" a metade cortada fora (defeito antigo; linha fina no G3 e no J3);
2. **`aocorte`:** AO com os planos de corte;
3. **corte + máscara:** como a 2, mas o AO não escurece as tampas amarelas. A tampa é tratada como a face plana de um
   sólido cortado, não como fenda. A máscara é suavizada (5 × 5) para não piscar na fronteira;
4. **plana + máscara:** as tampas viram faces planas no plano de corte no G-buffer do AO.

**Granulado** (alta frequência, luma 0–255; menor é mais limpo):
| Plano | Região | atual | aocorte | corte + máscara | plana + máscara |
|---|---|---|---|---|---|
| G3 | tampas | 3,18 | 7,61 | 3,68 | 3,27 |
| G3 | faixa vizinha | 15,28 | 17,93 | 17,46 | 16,54 |
| J3 | tampas | 2,56 | 4,39 | 2,82 | 2,60 |
| C4 | tampas | 2,75 | 5,38 | 3,07 | 2,94 |

**Sombreamento** (faixa junto aos cortes, brilho relativo ao atual):
- `aocorte`: −13 a −16;
- corte + máscara: −11 a −13;
- plana + máscara: −12 a −15.

Esse escurecimento é a profundidade correta: sombras de contato sob prateleiras, gavetas e evaporador, que o AO atual
não calculava.

**D4:** as quatro variantes são **idênticas**. O canal ampliado não tem peças cortadas, então nenhuma opção o altera.

**Estabilidade entre quadros e regressões encontradas no caminho:**
1. **Máscara binária:** cintilava na fronteira tampa/interior (J3: 12 blocos). Suavizada, caiu para **1** em 540.
2. **Em 1080, o J3 com corte + máscara mostrou 13 quadros piscando.**
   - **Investigação:** a atenuação em superfícies rasantes **não teve efeito**. Diagnóstico errado, opção descartada.
   - **Causa real:** z-fighting **antigo** na parede de cima do gabinete. O topo, a base, o fundo e os degraus encostam
     face a face nas laterais (x = ±IX), e pelo corte a tampa de uma peça e a face da outra coincidem.
   - **Já existia no J3 aprovado:** 21.424 pixels alternando com limiar sensível. Ficava invisível porque amarelo e
     cinza têm brilho parecido (8 pixels no limiar padrão). O AO correto escurece o cinza e o revela.
   - **Correção (mesma família da porta):** essas peças recuam **0,5 mm** nas pontas (`FOLGA_GAB`). Testada só no J3,
     numa cena separada.

**Resultado em 1080** (30 quadros seguidos, mesma configuração do definitivo):
| J3 | Quadros com blocos | Pixels que vão e voltam (quadro todo) | Faixa do topo (limiar 12) |
|---|---|---|---|
| atual (aprovado) | 0 | 27.370 | 21.424 (z-fighting antigo, sutil) |
| corte + máscara, sem folga | 13 | 40.952 | 94.194 |
| folga, AO atual | 0 | 27.364 | 16 |
| **folga + corte + máscara** | **0** | **27.730** | **40** |

| G3 | Quadros com blocos | Pixels que vão e voltam |
|---|---|---|
| atual | 0 | 734 |
| corte + máscara | **0** | 768 |

**Recomendação para o AO:** **corte + máscara suavizada + folga do gabinete** (`aocorte=1`, `aotampa=1`,
`FOLGA_GAB = 0,5 mm`), em **todos os planos em corte**.
- **Por que é superior:**
  - corrige a linha fina e o sombreado errado do interior;
  - tampas tão limpas quanto as atuais;
  - elimina o z-fighting antigo do topo;
  - estabilidade igual à atual onde foi medida (G3 e J3 em 1080).
- **Ressalvas, com evidência:**
  - a folga foi testada só no J3, e a variante "plana" teve um pouco menos de granulado mas mais cintilação em 540;
  - a faixa vizinha às tampas tem um granulado um pouco maior que o atual (+1,4 a +2,2);
  - o chão perto da base do J3 mostra um pouco de textura de AO.
- **Antes de congelar:** depois da sua aprovação, rodar em 540 todos os planos em corte com essa configuração e passar o
  detector (também com limiar sensível). Nada foi aplicado aos planos aprovados.

## 3. C2: risco de estroboscopia
- **Medida geométrica** (`medir_estrobo.py`): projeta os arames reais do condensador (25 mm) com a câmera exportada.
  - **No C2, 40 quadros (36,2–37,5 s):** os arames andam mais da metade da distância entre eles (razão até 2,8), e o olho
    perde o sentido do movimento (efeito roda-de-carroça).
  - **36,7–36,9 s:** a grade é vista de topo.
  - **Outros planos com o condensador:** E1, H2, J3 e G3 ficam ≤ 0,08, sem risco. O **C4** tem risco moderado (19
    quadros, razão até 0,84, em 47,1–47,7 s); não foi pedido, fica registrado.
- **Por que não só desacelerar a câmera:** com o corte, a duração e o enquadramento final fixos, o trecho rápido pode ser
  alongado no máximo ~1,5×, e seria preciso ~2,6× para sair do risco.
- **Alternativa testada: desfoque de movimento de obturador real.**
  - Cada quadro é a média, em luz linear, dos sub-quadros dentro do tempo de exposição (8 sub-quadros por quadro).
  - Mesma câmera, mesmo pulso, mesmo corte: o sub-quadro central é idêntico ao quadro aprovado (diferença 0,18–1,07,
    dentro do ruído do renderizador).

| C2 36,07–37,74 s | Pixels que vão e voltam | Pior quadro (blocos) | Variação entre quadros (quadros de risco) |
|---|---|---|---|
| atual | 1.926.607 | 425 | 20,6 |
| obturador 180° | 1.115.154 (−42 %) | 254 | 16,4 |
| obturador 270° | 844.000 (−56 %) | 153 | 15,3 |

**Recomendação para o C2:** **obturador de 180°** (o padrão de cinema) no plano C2 inteiro.
- Reduz a ambiguidade dos arames sem apagar o circuito: serpentina azul, pulso branco e cobre continuam legíveis nos
  quadros mais rápidos.
- Com 270° a redução é maior, mas a serpentina de cobre fica mais apagada em 37,4 s.
- Corte em 33,92 s, duração, pulso e enquadramento final ficam inalterados (o desfoque só existe onde há movimento).
- **Custo no definitivo:** cerca de 5× o tempo de render do C2 (~140 quadros × 5 sub-quadros).
- O efeito real de conforto visual precisa da sua avaliação a olho, no vídeo.

## 4. O que não mudou (medido)
- **Montagem:** só os 5 planos com manômetro mudaram. Os demais são idênticos pixel a pixel à V6 (117 quadros
  verificados).
- **Cenas aprovadas:** nenhuma foi reexportada. As variantes ficaram em pastas próprias (`cenas/C2_sub8`, `cenas/J3_gab`).
- **Motor:** todas as opções novas (`aotampa`, `aoplana`, `aomasc`, `aorasante`, `aosem`) estão **desligadas por
  padrão**. Sem elas, o motor produz a mesma imagem: o mesmo quadro do G3 renderizado na rodada 6 e na 7 difere em 0,052,
  igual ao ruído natural entre dois renders idênticos (0,053).
- **Áudio:** mixagem, narração, stems e licenças sem nenhuma alteração.

## 5. Pendências e decisões
1. **AO:** aprovar a configuração recomendada (corte + máscara + folga do gabinete) para todos os planos em corte? Se
   sim, faço a validação em 540 de todos os planos em corte antes de congelar.
2. **C2:** aprovar o obturador de 180° no C2 inteiro? Aplicar também no C4 (risco moderado)?
3. **Manômetros:** já são padrão. Confira a fusão de lugar no G3 (~106,15 s) no vídeo dos 5 planos.
4. **Licença da narração:** continua pendente. O episódio não está liberado para uso comercial.
5. **Limites:** eu meço; não assisto nem escuto como uma pessoa. Os quadros de teste ficam no contêiner temporário.
