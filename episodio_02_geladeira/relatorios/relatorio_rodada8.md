# Ep. 02 — Rodada 8: validação técnica e proposta de congelamento

**Prévia completa:** `episodio/ep02_v8_revisao.mp4` (V8, revisão 540 × 960, 30 fps, 4.537 quadros, 151,233 s).
**V6 aprovada intacta:** `episodio/ep02_animatic.mp4`.
**Render definitivo em 1080 × 1920: NÃO iniciado** (aguarda sua aprovação do congelamento). Nada publicado, nenhuma voz
gerada, nenhum serviço contratado. O Episódio 01 não foi alterado.

Eu meço; não assisto nem escuto como uma pessoa. A aprovação estética e auditiva é sua.

| Arquivo | O que é |
|---|---|
| `episodio/ep02_v8_revisao.mp4` | V8 completa (540, com áudio da mixagem R8) |
| `episodio/testes_1080_r8/ep02_1080_r8_{C2,C3,C4,G3,H2,J3}.mp4` | testes curtos em 1080 com a configuração proposta |
| `episodio/testes_1080_r8/r6_x_r8_{C2,G3,J3}.mp4` | rodada 6 aprovada × rodada 8, nos MESMOS quadros, lado a lado |
| `relatorios/comparativos_r8/*.jpg` | folhas V6 × V8 (42 planos), A4, I1, porta, juntas, AO A/B, costuras em 1080 |
| `relatorios/congelamento_proposto_r8.json` | configuração e hashes propostos para o congelamento |
| `som/audio_ep02_v8.flac` · `som/audio_ep02_v6.flac` | mixagem da V8 e mixagem V6 aprovada (para reverter), sem perdas |

---

## 1. Validação do AO em todos os planos em corte (540)

Configuração validada: `aocorte=1` + `aotampa=1` + `FOLGA_GAB = 0,5 mm` nos 19 planos em corte (C2, C3, C4, D1–D5,
E1–E4, G1, G2, G3, G3z, H1, H2, J3). Quadros consecutivos, detector padrão (|Δ| > 30) e detector sensível (|Δ| > 12)
dentro das tampas (máscara erodida) e na faixa de 8 px em volta.

**A/B controlado** (mesma cena, mesmos 12 quadros em volta do pior trio; só muda o AO). A = AO aprovado (`aocorte=0`),
B = AO com corte + máscara das tampas. Arquivo: `relatorios/ao_ab_cortes.json` (19/19 planos).

| Plano | trios c/ blocos padrão A/B | px sensíveis dentro das tampas A/B | granulado das tampas A → B | faixa vizinha (B − A, luma) |
|---|---|---|---|---|
| C2 | 10/10 | 3.726 / 5.617 | 12,66 → 11,53 | −9,97 |
| C3 | 10/10 | 3.486 / 35 | **11,37 → 4,43** | −1,00 |
| C4 | 9/9 | 682 / 459 | 9,67 → 9,83 | −17,75 |
| D1 | 0/0 | 25 / 28 | 5,08 → 4,13 | −21,65 |
| D2 | 10/10 | 0 / 0 | 2,66 → 3,05 | −0,67 |
| D3 | 9/9 | 0 / 0 | 3,11 → 3,42 | −30,29 |
| D4 | 10/10 | 0 / 0 | 4,15 → 4,14 | 0,00 |
| D5 | 10/10 | 36 / 11 | 4,47 → 5,43 | −17,12 |
| E1 | 10/10 | 5 / 4 | 2,00 → 2,51 | −1,54 |
| E2 | 0/0 | 232 / 576 | 16,37 → 14,69 | −9,36 |
| E3 | 10/10 | 43 / 208 | 6,24 → 6,28 | −5,93 |
| E4 | 0/0 | 0 / 0 | — | 0,00 |
| G1 | 4/6 | 1.666 / 2.580 | 12,03 → 9,00 | −4,20 |
| G2 | 0/0 | 187 / 223 | **11,48 → 6,80** | +11,95 |
| G3 | 0/0 | 4 / 7 | 5,06 → 5,89 | −14,89 |
| G3z | 10/10 | 0 / 0 | 0,65 → 0,65 | 0,01 |
| H1 | 10/10 | 167 / 145 | 5,73 → 5,91 | −15,58 |
| H2 | 0/0 | 460 / 47 | 6,48 → 6,49 | −17,00 |
| J3 | 0/0 | 42 / 42 | 6,51 → 6,77 | −13,19 |

**Leitura:**
- **Estabilidade:** os trios do detector padrão são os mesmos em A e B em 18 de 19 planos. O G1 tem 4 → 6, e a diferença
  é a costura antiga (abaixo), não o AO.
- **Granulado:**
  - Cai bem no C3 (−61 %), no G2 (−41 %), no G1 (−25 %) e no D1 (−19 %).
  - Sobe pouco no D5 (+21 %), no G3 (+16 %) e no E1 (+26 %, valor absoluto baixo: 2,5).
- **Faixa vizinha mais escura (−1 a −30):** é a sombra de contato que o AO aprovado não fazia, porque "via" a parte cortada.
  É o efeito esperado da correção; ela muda o sombreado perto do corte, não a cor das tampas.
- **Picos dos detectores, classificados (não são z-fighting):**
  - arames do condensador passando sobre as tampas (C2, E3, H1);
  - feixes de calor amarelo-laranja (D4, D5, G3z);
  - canal animado do evaporador (D2, D4).
- **Detector padrão alto no C3 (28/28 trios):** a quantidade é idêntica em 540 e em 1080 (13,96 mi × 13,94 mi de px,
  ajustada a escala). Conflito de profundidade mudaria com a resolução; isto não muda, então é a animação da cena.

**Defeitos antigos achados pelo detector sensível (também presentes na V6) e corrigidos com a mesma família de folga já
aprovada:**

| Defeito | Correção | Pior quadro (px piscando) antes → depois |
|---|---|---|
| Porta × vedação (painel e vedação coplanares) em C4, H1, H2 | `CORRECAO_PORTA` += {C4, H1, H2} (já aprovado: G3, J3) | C4 17.988 → 274 · H1 7.603 → 356 · H2 13.544 → 228 |
| Degrau × fundo traseiro no E2 | `CORRECAO_DEGRAU` = {E2}, folga de 0,5 mm só no E2 | total 144.421 → 1.144 px; trios com blocos dentro das tampas 10 → 0 |

Verificação geométrica (projeção da junção por quadro): `relatorios/porta_vedacao_r8.json`,
`relatorios/juntas_gabinete_r8*.json`. Imagens: `comparativos_r8/c4_porta_v6_antes.jpg` × `c4_porta_r8_depois.jpg`,
`comparativos_r8/juntas.jpg`.

**Costuras finas antigas (não corrigidas, registradas):**
- C2, G1 e o resto do C4: folgas de 0,4–1 mm vistas de quina viram uma linha tracejada.
- Ficam como estão até você decidir.

## 2. Testes curtos em 1080 × 1920 (configuração proposta)

Seis trechos nos pontos críticos, **um processo de render por vez**. Comparação com a rodada 6 aprovada nos MESMOS
quadros onde ela existe. Arquivo: `relatorios/teste_1080_r8.json`.

| Plano | Quadros | s/quadro 1080 | Resultado |
|---|---|---|---|
| C2 | q97–116 (obturador) | 92,9 | alternação −35 % × R6 (2,04 mi × 3,16 mi px); ver item 4 |
| C3 | q58–87 | 19,9 | igual ao 540 (não depende da resolução); granulado das tampas 0,97 |
| C4 | q8–37 | 18,4 | 0 trios com blocos padrão; faixa da porta: ver abaixo |
| G3 | q71–100 | 9,8 | **igual à R6**: 0 trios padrão; faixa da porta: 7 px em 28 trios |
| H2 | q40–69 | 19,0 | 0 trios com blocos padrão; faixa da porta: ver abaixo |
| J3 | q84–113 | 19,0 | **igual à R6**: 0 trios padrão (27.750 × 27.370 px); faixa da porta: 2 px |

**Coerência 1080 × 540** (1080 reduzido × render de revisão, mesma cena): diferença média de 1,5 a 3,9. Não aparece
nenhum defeito só em 1080.

**Achado em 1080: linha tracejada escura na tampa da porta do C4 e do H2**
- Imagem: `comparativos_r8/costura1080.jpg`. Medida: `relatorios/porta_vedacao_1080_r8.json` — C4 até 1.053 px por quadro,
  H2 até 831 px; em 540 o equivalente era C4 274 e H2 228.
- A projeção da geometria coloca cada linha no pixel exato de uma folga:
  - **linha escura** = a folga NOVA de 0,5 mm entre painel e vedação (a correção desta rodada), vista de quina;
  - **linha clara** = a folga ANTIGA de 1 mm entre vedação e contraporta, que já existia na V6.
- **Balanço honesto:** a correção trocou uma área grande piscando (z-fighting) por uma linha fina e estável na posição.
  Ainda assim, cria uma linha nova. É **efeito colateral da correção**, não defeito antigo.
- **Correção possível, não aplicada e desligada até a sua decisão:** em vez de abrir folga, fazer painel e vedação se
  sobreporem 0,5 mm. Assim não há faces coplanares nem fresta à vista. Ela troca geometria em 5 planos (G3, J3, C4,
  H1, H2) e exigiria novo teste em 540 e 1080 nesses planos.

## 3. Correção das sobreposições do G3 (106,13–106,17 s)

- **R7 aprovada:** 9 problemas no G3 em 613 quadros testados:
  - 2 texto do manômetro × legenda;
  - 2 mostrador × legenda;
  - 5 linhas sobre texto.
- **R8, com o cartão de pressão:** **0 problemas** nos mesmos 613 quadros.
- Ponteiros idênticos aos da R7 em 845/845 comparações: os valores e o movimento não mudaram.
- Arquivo: `relatorios/teste_manometros.json`.

## 4. C2 — obturador de 180° (integração temporal)

- **Como funciona:** 5 sub-quadros em [−¼, +¼] de quadro, média em luz linear (cena `cenas/C2_obt`,
  `config/producao.json → obturador`).
- **Corte em 33,92 s:** preservado (`C2.t0 = C1.t1 = 33,92`).
- **Duração:** preservada (139 quadros renderizados, o mesmo número de antes).
- **Câmera e pulso:** os mesmos. O sub-quadro central é o quadro aprovado; com a câmera parada, a diferença é
  0,03–0,19, o ruído do renderizador.
- **Enquadramento final:** idêntico. No último quadro, integrado × central = 0,18.
- **Nitidez preservada onde a câmera está parada:** 20 quadros parados, nitidez integrado/central = **0,99**, diferença
  média 0,21. O desfoque só aparece durante o movimento rápido da câmera, que é o objetivo (`relatorios/c2_obturador_nitidez_540.json`).
- **Estroboscopia dos arames em 1080:** −35 % de pixels piscando em relação à R6 nos mesmos quadros
  (`testes_1080_r8/r6_x_r8_C2.mp4`).
- **Pixels sensíveis dentro das tampas no C2 em 1080:** 74 mil px, contra 1,8 mil na R6. Classificação pelo mapa
  (`comparativos_r8/c2_1080_sens_q106.jpg`):
  - arames do condensador borrados passando sobre a tampa direita;
  - a costura antiga da tampa esquerda.
  - Nenhum bloco de z-fighting.
- **C4:** sem desfoque, como pedido.

## 5. Comparativos antes × depois

- **V6 × V8, quadro do meio de cada plano:** `comparativos_r8/folha_v6_v8_1.jpg` e `folha_v6_v8_2.jpg`. A diferença
  média por plano está em `relatorios/v6_x_v8_por_plano.json`.
- **Estrutura idêntica:** 4.537 quadros, 151,233 s, 30 fps, os mesmos 42 planos com os mesmos t0/t1.
- **Todos os planos mudam um pouco:**
  - o selo trocou de "ANIMATIC" para "VERSÃO DE REVISÃO";
  - a V6 tinha quadros duplicados (passo 2);
  - entraram os itens novos na geladeira.
  - O que mais muda são os planos em corte, por causa do AO e dos cartões de pressão: C3 22,0, H2 24,3, D5 22,0.
- **A4 por volta de 0:05:** `comparativos_r8/a4_transicao.jpg`. Mesma fusão e mesmo instante (4,87 s); cabeça e olhar
  ajustados.
- **I1 — leite:** `comparativos_r8/i1_leite.jpg`. Aproxima → abre → pega a caixa → sai com a porta aberta.
- **Continuidade I1 → I2:** `comparativos_r8/i1_i2_continuidade.jpg`. A caixa de leite **não está mais** na prateleira
  no I2, coerente com a ação.
- **Rótulos no ataque da palavra:** auditados na cena exportada final (`relatorios/rotulos_x_narracao_r8_final.json`):
  - 24 rótulos, 0 antes da palavra;
  - B3, B4 e D1 entram de +0,04 a +0,06 s depois do início da palavra.
- **1080, rodada 6 × rodada 8 lado a lado:** `testes_1080_r8/r6_x_r8_{C2,G3,J3}.mp4`.

## 6. Regressões, efeitos colaterais e correções

| Item | Tipo | Situação |
|---|---|---|
| Linha tracejada escura na porta (C4, H2; folga nova) | efeito colateral da correção | registrado; alternativa (sobreposição) desligada até decisão |
| Pico verdadeiro do áudio −1,68 → −1,52 dBTP | efeito colateral da mudança dos passos do I1 | dentro da meta (≤ −1,5), folga de 0,02 dB; ver item 9 |
| Manifesto do D1 divergente da cena atual | não é regressão | ver abaixo |
| Granulado das tampas sobe em D5, G3, E1 | variação pequena do AO correto | aceito; valores absolutos baixos (≤ 5,9) |

**D1:**
- Os quadros do D1 foram renderizados às 22:50. A cena foi reexportada às 23:17, junto com a correção da porta.
- Diferenças entre as duas exportações:
  - **cena.json:** idêntico;
  - **malhas m008 e m054:** só a ordem dos triângulos (comparados sem ordem: idênticos);
  - **rotulos2d.json:** o "Evaporador" passou a entrar no ataque da palavra (49,69 s), e não 0,2 s antes. É a correção de
    rótulos aprovada para esta rodada.
- Os rótulos são composição, então a V8 já mostra o rótulo certo.
- No render definitivo, o checkpoint por hash vai renderizar o D1 de novo, o que é correto.

## 7. Configuração proposta para o congelamento

Detalhe e hashes: `relatorios/congelamento_proposto_r8.json`.

- **Perfil `final`:** escala 1,0 (1080 × 1920), `aoamostras=16&msaa=4&bloom=0.18`, x264 CRF 17. O selo de revisão, os
  ids dos planos e o tempo ficam fora do `final`; os avisos científicos continuam.
- **Obturador:** C2, 180°, 5 sub-quadros. Nenhum outro plano.
- **AO:** `ao_corte` (aocorte + aotampa) nos 20 cenários em corte, incluindo C2_obt.
- **Folgas:** `FOLGA_GAB` 0,5 mm em todo corte real; `CORRECAO_PORTA = {G3, J3, C4, H1, H2}`; `CORRECAO_DEGRAU = {E2}`.
  - As duas últimas são **extensões de uma correção já aprovada**, reversíveis (é só tirar os ids do conjunto).
- **Montagem:** `MANOMETRO_LEGIVEL=1`, `MANOMETRO_CARTAO=1`, mixagem `audio_ep02_v8.flac`.
- **Cenas congeladas por hash.** Não reexportar depois do congelamento, porque a exportação varia a ordem dos triângulos.
- **Auditoria:**

  | Item | Resultado |
  |---|---|
  | Configuração | única: todos os 41 manifestos de render com a mesma consulta e o mesmo motor (`79b25d43…`) |
  | fps e tempos | 30 fps; tempos globais idênticos à V6 |
  | Narração (MP3) | SHA-256 `fdedd877…`, intacta |
  | `palavras.json` | sem mudança desde a rodada 2 |
  | Episódio 01 | última alteração anterior ao início do Ep. 02 |

## 8. Custo estimado do render definitivo (tempos reais)

Medido: o tempo de cada plano em 540 nesta rodada × a razão 1080/540 dos 6 testes (3,38–3,92; média 3,59).
Arquivo: `relatorios/custo_render_1080_r8.json`.

- **Quadros renderizados:** 5.638. São 4.537 quadros no vídeo; o restante são as margens das fusões. O C2 renderiza
  695 sub-quadros.
- **540 completo:** 7,3 h.
- **1080 completo: ≈ 26 h (provável) a 28 h (conservador)**, um processo por vez, sem contar a verificação por quadro.
- **Só o C2 com obturador:** ≈ 3,6 h.
- **Armazenamento:** o contêiner é temporário. O render precisa terminar, ser montado e verificado e ter o master
  guardado no git na mesma sessão (vídeo final dividido em partes < 95 MB se precisar).

## 9. Pendências e decisões

1. **Aprovar o congelamento técnico** (item 7) antes de qualquer render definitivo.
2. **Porta, C4 e H2:** aceitar a linha tracejada fina da folga ou testar a alternativa de sobreposição (5 planos).
3. **Costuras finas antigas** (C2, G1 e o resto do C4): aceitar ou tratar numa rodada própria.
4. **Áudio:**
   - A única mudança em relação à mixagem V6 aprovada são os passos do I1 (118–120 s), porque a caminhada mudou.
     Fora desse trecho, a diferença no WAV é ≤ −69,9 dBFS.
   - Por causa dessa mudança, o codificador AAC desloca o pico verdadeiro para 130 s: −1,52 dBTP, ainda dentro da meta.
     O mesmo WAV codificado de novo dá o mesmo resultado (o codificador é determinístico).
   - Não mexi no master. Se quiser mais folga, um ajuste de −0,2 dB no master é decisão sua.
   - **Outras medidas:** loudness −14,1 LUFS; voz acima do resto no celular, mediana 28,8 dB (igual à V6); perda em mono
     −0,01 dB.
   - O pior caso de voz, −0,8 dB numa janela, é o mesmo da V6.
5. **Licença da narração:** pendente. **Sem uso comercial nem monetização** até ela ser definida (registro em
   `relatorios/licencas_ep02.md`).
6. **Rodada 9:** a análise de impacto e o plano vêm a seguir, separados deste relatório. Nada da Rodada 9 foi executado.

**O que não mudou:**
- a narração e o MP3 (SHA-256 igual);
- o roteiro e o `palavras.json`;
- a duração (151,233 s) e a estrutura dos planos;
- o modelo científico e os valores e ponteiros dos manômetros (845/845 iguais);
- o corte em 33,92 s e o pulso;
- os parâmetros de mixagem (master, ganhos, compressão, ducking);
- a V6 (`ep02_animatic.mp4`);
- o Episódio 01.

**Nada publicado. Render definitivo não iniciado.**
