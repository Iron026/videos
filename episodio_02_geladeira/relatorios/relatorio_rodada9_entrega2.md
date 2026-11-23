# Ep. 02 — Rodada 9, entrega 2: prévias da Fase 3, A1, transição A3 → A4 e áudio

**Nada foi re-renderizado no episódio inteiro.** Esta entrega traz prévias curtas, em 540 e com a composição da V9a, para
você decidir antes do re-render dos ~29 planos afetados.

- **Versões preservadas:** V8 e V9a, com hashes em `relatorios/versoes_preservadas_r9.json`.
  - V8: `ep02_v8_revisao.mp4` `197b81fc…`, cenas em `arquivo/cenas_v8.tgz`.
  - V9a: `ep02_v9a_revisao.mp4` `bd79ab3a…`.
- **Código desligado = V8:** com as chaves `CENA_R9` e `PREVIA_R9` desligadas, o código novo reproduz a V8.
  - Exportação: `cena.json` byte a byte e malhas iguais (comparadas sem considerar a ordem dos triângulos).
  - Montagem: pixel a pixel.

Eu meço; não assisto nem escuto como uma pessoa. A naturalidade dos movimentos é avaliação sua.

## Arquivos para assistir (`episodio/previas_r9/`)

| Arquivo | O que mostra |
|---|---|
| `a4_transicoes.mp4` | fusão atual · passagem pelo escuro · corte seco, lado a lado, em velocidade real e depois 4× mais lento |
| `a4_fusao_atual.mp4`, `a4_passagem_pelo_escuro.mp4`, `a4_corte_seco.mp4` | cada opção sozinha, com som |
| `a1a2_lado_a_lado.mp4` | A1–A2: V9a × Rodada 9 (alcance do puxador, mão no batente) |
| `i1i2_lado_a_lado.mp4` | I1 → I2: V9a × Rodada 9 (leite, saída, câmera de volta à geladeira, passos novos no som) |
| `c4d1_lado_a_lado.mp4` | C4 → D1: V9a × Rodada 9 (aproximação ao evaporador) |

Quadros: `relatorios/previas_r9/` (`a4_transicoes_quadros.jpg`, `a1_r9_quadros.jpg`, `i1_r9_quadros.jpg`,
`c4d1_r9_quadros.jpg`, `previas_estaticas.jpg`, `h2_zoom.jpg`).

## 1. Transição A3 → A4 (~4,87 s)

**Diagnóstico confirmado:** na fusão de 0,2 s, a serpentina do A3 fica visível sobre o rosto entre 4,80 e 4,93 s. É o
efeito natural de uma fusão entre imagens muito diferentes.

| Opção | Duração | Imagem fantasma | Observação |
|---|---|---|---|
| Fusão atual | 0,2 s | sim | a V8/V9a |
| **Passagem pelo escuro** | 0,2 s, mesmo intervalo | não | o A3 escurece (~0,1 s) e o A4 surge (~0,1 s); suave, sem sobreposição |
| **Corte seco** | 0 | não | em 4,87 s, na pausa da fala (a legenda "quente por fora?" já saiu); é a gramática clássica do contraplano de reação |

- **O que não muda:** a atuação, a duração e o tempo da narração, nas três opções. É só montagem.
- **Recomendação:** corte seco, ou a passagem pelo escuro se você quiser manter alguma suavidade. Fica para você escolher
  no comparativo.

## 2. A1: puxador fora do alcance

Teste numérico (`blender/testar_a1.py`; `relatorios/teste_a1.json` × `teste_a1_r9.json`):

| Medida | V8/V9a | Rodada 9 |
|---|---|---|
| Distância mão → puxador durante a pega e o puxão | até **145 mm** (a mão não chegava) | **≤ 5,6 mm** |
| Braço × porta depois de soltar | **−22,5 mm** (atravessava o painel) | **+11,2 mm** |
| Tronco × porta | 267 mm | 132 mm (sem contato) |
| Mão esquerda × batente no A2 (achado novo) | até **111 mm** (solta no ar) | **0 mm** (apoiada) |

**Correção mínima:**
- **Posição:** o personagem fica **15 cm mais perto do puxador** no A1 e no A2, ainda fora do arco da porta. A câmera não
  muda. No A3, que é fora de quadro, ele recua a partir desse ponto. O A4 fica igual.
- **Puxão:** ele solta o puxador a ~20° e o braço recua primeiro para fora do giro da porta. É a mesma regra do I1.
- **O que se mantém:** a encenação aprovada — o olhar, a postura, a inclinação para trás ao puxar e os tempos.

## 3. Elementos da geladeira

**Itens novos:**
- prateleiras da porta: garrafa de vidro verde e caixa bege embaixo; bandeja com 5 ovos em cima;
- gaveta: alface e duas limas;
- prateleira do meio: pote com tampa;
- congelador: saco de ervilhas.

**Cores:** fora da linguagem didática (sem laranja, azul ou ciano, amarelo de tampa ou violeta).

**Temperaturas na visão térmica:**
- geladeira 5 °C;
- porta 6 °C;
- congelador −18 °C.

**Teste geométrico** (`blender/testar_itens.py`; `relatorios/teste_itens_r9.json`), com a porta fechada:
- nenhuma invasão dos itens novos;
- nenhum fundo coplanar com o vidro (folga de 0,5 mm);
- **Defeito antigo corrigido:** com a porta fechada, os frascos de molho da porta, da Rodada 8, invadiam a prateleira de
  vidro de cima e a borda dela, em até 4 cm³. Eles ficaram mais baixos (9,5 cm).

**Ajuste depois da prévia:** retirei o pote de sorvete do congelador. No close do D1 ele ficava grande, no centro, e
competia com o evaporador.

**Planos técnicos:** nos cortes, os itens ficam onde não tapam evaporador, condensador, capilar nem feixes (folha
`previas_estaticas.jpg`).

**Consequência a decidir (D3):** com o leite na posição única, a caixa saiu do enquadramento do D3, que antes a mostrava
no centro. Agora o **pote vermelho** ocupa o centro, e o feixe de calor sai dele. A física é a mesma, pois todos os
alimentos cedem calor. Opções: aceitar, ou reenquadrar o D3 na caixa de leite, o que muda a câmera desse plano.

## 4. Caixa de leite e I1

**Posição única em todos os planos:** frente da prateleira de cima, à esquerda, ao alcance da mão. Ela some do I2 ao I4 e
também do J1 ao J3, como você pediu (conferido nas prévias do J2 e do J3).

**Teste numérico do I1** (`relatorios/teste_leite.json` × `teste_leite_r9.json`):

| Medida | V8/V9a | Rodada 9 |
|---|---|---|
| Mão × caixa depois da pega | mão **13 cm** longe da caixa (a caixa "seguia" a mão de longe) | contato de −3,1 mm (a mão fechada segura a caixa), constante |
| Caixa × prateleira/borda | −2,4 mm (dentro do vidro) | ≥ +0,5 mm (ergue 3 cm e passa sobre a borda) |
| Braço × porta | −30 mm | sem invasão depois de soltar |
| Pega | 118,66 s | **118,44 s** (antecipada) |
| Início da saída | 118,80 s | **118,62 s** (mais tempo de saída dentro do mesmo plano) |

**As 7 etapas visíveis** (`i1_r9_quadros.jpg`):
1. aproxima (116,2 s);
2. mão no puxador e abre (117,3–118,1 s);
3. alcança (118,35 s);
4. pega (118,45 s);
5. ergue e retira (118,6 s);
6. vira e sai com a caixa (118,8–119,1 s);
7. a câmera se volta para a geladeira aberta, e o I2 (sem o leite) entra na fusão.

**Duração:** o I1 continua com 3,58 s, e a narração não mudou.

## 5. Aproximação C4 → D1

**Medição** (`relatorios/escala_cortes_r9.json`): no último quadro do C4 da V8, o evaporador estava fora do quadro. O D1
começava com ele ocupando 75 % da tela.

**Com a aproximação:**
- o evaporador aparece inteiro no fim do C4, na mesma coluna em que o D1 o mostra (x 511 × 506 px);
- os cartões de pressão saem com a palavra "físico", antes de a câmera subir;
- o início e o meio do C4 ficam iguais.

**Prévia:** `c4d1_lado_a_lado.mp4`. O E4 → F1 fica como está, como você decidiu.

## 6. Porta: mantida a folga de 0,5 mm

Medidas em 1080: `relatorios/porta_variantes_1080_r9.json`.
- **Folga de 0,15 mm:** é melhor no H2 (3× menos pixels piscando) e pior no C4 (2× mais).
- **Sobreposição:** cria uma faixa escura em toda a seção do painel.
- **Decisão:** sem vantagem clara, fica a solução aprovada.

## 7. Áudio

**Conferência por trecho** (`relatorios/audio_variantes_r9_diferencas.json`):

| Variante | Onde muda | Fora dos passos |
|---|---|---|
| **Passos novos do I1** | só 117–120 s | diferença máxima −108,6 dBFS (idêntico na prática) |
| **Passos + teto do limitador em −2,0 dB** | 117–120 s **e os picos de 57 segundos espalhados** (3,1 % das amostras) | diferença máxima −34,7 dBFS: é a limitação transparente que você autorizou, mas ela é **global**, não só nos passos |

**Validação no AAC, sobre a imagem da V9a** (`relatorios/validacao_audio_r9.json` e `validacao_audio_r9_teto20.json`):

| Variante | LUFS | Pico verdadeiro | Voz − resto no celular (pior / p5 / mediana) | Mono | Fim |
|---|---|---|---|---|---|
| Aprovada (V8/V9a) | −14,10 | −1,52 dBTP | −0,8 / 16,2 / 28,8 dB | −0,01 dB | −45,6 dBFS |
| Passos novos | −14,10 | **−1,68** dBTP | −0,8 / 16,2 / 28,8 dB | −0,01 dB | −45,6 dBFS |
| Passos + teto −2,0 dB | −14,12 | **−1,78** dBTP | −0,8 / 16,2 / 28,8 dB | −0,01 dB | −45,6 dBFS |

- **Sincronia:** os passos são calculados dos mesmos instantes de pouso da animação nova — 118,22 s, depois 119,09 s e
  119,55 s.
- **Narração:** o MP3 original está intacto (`fdedd877…`). A cópia de mixagem da voz é a mesma; a inteligibilidade no
  celular simulado é idêntica.
- **Recomendação:** **passos novos + teto −2,0 dB**. São 0,28 dB de folga, contra 0,18 dB, com loudness praticamente igual.
  A diferença fora dos passos é pequena, mas existe; se você quiser só os sons do I1 alterados, a variante só com os passos
  também cumpre a meta.

## 8. Verificação final da composição: todos os quadros

`relatorios/teste_composicao_r9_todos_quadros.json`, com a V9a composta em 1080 e **todos os 4.537 quadros** testados:
- **0 problemas:** nenhuma sobreposição, nenhum corte de borda, nada nas zonas de interface, nenhuma linha sobre texto e
  nenhuma legenda sobre o rosto;
- **901 de 901 ponteiros** iguais ao modelo.

## 9. Custo do re-render (se autorizado)

- **Planos com interior visível:** ~29, mais o C4 com a câmera nova, mais o A1 e o A2 com a posição nova. São cerca de
  3.700 quadros, **~5,3 h em 540**, um render por vez.
- **Validações depois do render:** AO e detector sensível nos 11 planos em corte com interior, porta e juntas, folha de
  contato e a verificação de composição em todos os quadros. Cerca de 1–2 h.
- **Testes curtos em 1080** nos planos críticos alterados. Cerca de 1–1,5 h.
- **Planos sem mudança** (A3, C1, C3, D2, D4, E1–E4, F1, F2, G3z, J4) **não são re-renderizados.**

## Decisões para você

1. **Transição A3 → A4:** corte seco, passagem pelo escuro ou manter a fusão?
2. **D3:** aceitar o pote vermelho no centro ou reenquadrar no leite?
3. **Áudio:** passos + teto −2,0 dB (recomendado) ou só os passos?
4. **Re-render dos planos afetados:** autoriza com o conjunto acima (itens, leite, I1, A1/A2, C4 → D1)?

**Nada publicado. Nenhuma voz gerada. Nenhum serviço contratado. Episódio 01 intacto. Render 1080 completo não iniciado.
A licença da narração continua pendente (sem uso comercial).**
