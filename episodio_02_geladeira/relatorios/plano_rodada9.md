# Ep. 02 — Rodada 9: análise de impacto (Etapa B) e plano (Etapa C)

**Situação:** a V8 está concluída, verificada e preservada (`episodio/ep02_v8_revisao.mp4`, commit `1fc440f`).
**Nada da Rodada 9 foi executado.** Nenhum código, cena ou tempo foi alterado. Este plano aguarda a sua aprovação.

As medidas abaixo foram tiradas da **V8 e das cenas exportadas**: `rotulos2d.json`, `manometros2d.json`, as câmeras e
os blocos de legenda gerados pelo código atual. Eu meço; não assisto nem escuto como uma pessoa.

---

## Etapa B — Análise de impacto

### B.1 Classificação de cada diretriz

Legenda: **P** = problema comprovado por medida · **C** = melhoria criativa (nova) · **OK** = já correto na V8 ·
**R** = risco de regressão se mexer.

| # | Diretriz | Como está na V8 (medido) | Classe | Tipo de mudança |
|---|---|---|---|---|
| 2 | Transição do A4 (~0:05) | O corte cai na pausa entre "quente por fora?" e "Parece" (A4 t0 = 4,87 s); fusão curta (~0,2 s). Olhar para a câmera = para a geladeira (contraplano de dentro); mão sob o queixo (R6); a tela dividida continua no A3. Folha: `comparativos_r8/a4_transicao.jpg` | **OK** (refino opcional) | composição (só o tipo de fusão) |
| 3 | Leite em 7 etapas | Aproxima (115,55–116,95) → abre ("deixa") → pega (118,66) → recolhe → sai (começa 118,80). **O plano termina em 119,18 s: a saída aparece só 0,38 s.** A caixa segue a matriz da mão desde a pega, sem salto. **Não há teste numérico de colisão** da caixa (prateleira, borda, porta) nem do contato mão × caixa. | **P** (saída curta) + teste que falta | 3D: I1 |
| 3 | Continuidade do leite | No I1, a caixa está na **frente esquerda** da prateleira de cima. Nos outros planos ela fica à **direita** (posição de sempre). Some de I2 a I4, como deve, mas **volta a aparecer em J1–J3**. | **P** (continuidade) | 3D: posição única + J1–J3 |
| 4 | Geladeira mais cheia | Hoje: garrafa de água, leite, pote vermelho, pote baixo, suco, tomates, 2 frascos na porta (só na prateleira do meio), forma de gelo + 1 caixa no congelador. Faltam: produtos nas prateleiras da porta, frutas e verduras variadas, mais itens no congelador. | **C** | 3D: ~29 planos com interior visível |
| 5 | Rótulos no ataque da palavra | 24/24 rótulos entram no início da palavra ou logo depois (+0,00 a +0,06 s), nunca antes (`rotulos_x_narracao_r8_final.json`). | **OK** | — |
| 5 | Rótulos que se soltam do elemento | Âncora **fora do quadro** e rótulo preso na borda, longe do que nomeia: C3 "fluido refrigerante" 48/48 quadros; D1 "Evaporador" 109/109; D4 "entra: líquido + vapor" 57/91; E4 "ar da cozinha" 24/24; F2 "entra: vapor quente" 25/48 (e ali o rótulo cai sobre o canal laranja, com pouco contraste). | **P** | composição*, ver B.3 |
| 6 | Linguagem da pressão | Cartões com valores e ponteiros idênticos aos do modelo (845/845). Texto do cartão em **30 px** (1080), menor que o dos rótulos (44 px). | **OK** na física; **C/P** na legibilidade (medir no celular simulado) | composição |
| 7 | Linhas de chamada | Só 6 rótulos têm linha. **D3 "fluido mais frio que o ar": a âncora fica fora do quadro em 97/97 quadros, então a linha aponta para fora da tela.** G3z "começa a evaporar": âncora fora em 14/38 quadros. | **P** | composição*, ver B.3 |
| 8 | Transformações do fluido | Evaporador (D4: entra líquido + vapor → sai só vapor), condensador (F2: entra vapor quente → sai líquido) e capilar (G3/G3z, lupa: "começa a evaporar", "mistura fria") já estão nas cenas, ligados ao modelo e verificados (`verificar_g3`). | **OK** (só os rótulos soltos do item 5) | — |
| 9 | Continuidade plano aberto ↔ fechado | Mudanças bruscas de escala em corte seco, por exemplo C4 (corte aberto) → D1 (evaporador de perto), E4 → F1, F2 → G1. A revelação do circuito, o corte em 33,92 s e o pulso estão preservados. | **C** (medir antes de mexer) | 3D: câmera de 2–4 planos |
| 10 | Legendas | **31 de 123 blocos terminam em palavra fraca** ("Você já reparou que a", "geladeira é fria por", "Escondido atrás das"…); **24 blocos duram menos de 0,6 s**. As frases finais estão quebradas: "A geladeira não / cria frio" e "Ela dá um destino ao / calor". | **P** | composição |
| 10 | Áreas seguras | Legenda centrada a 74 % da altura (≈ 1.421 px de 1.920): dentro da margem inferior conservadora citada para Reels (≈ 670 px). Avisos no canto superior direito, a 70–250 px do topo: dentro da margem superior citada (≈ 250–270 px). *Os guias divergem; não confirmei o número oficial da Meta.* | **P provável** | composição |
| 10 | Versão final sem selo nem IDs | O perfil `final` já tira o selo, o id do plano e o tempo; os avisos científicos continuam. | **OK** | — |
| 11 | Encerramento | J4 termina na frase aprovada, sem vinheta, mascote, logotipo nem tela promocional. Só a legenda quebra a frase (item 10). | **OK** | composição (legenda) |

\* Os rótulos são composição, mas a posição deles vem da cena exportada. Mudar âncoras exige reexportar o plano.
A reexportação muda a ordem dos triângulos, não a geometria, então os quadros já renderizados podem ser
**reaproveitados com prova**: cena.json igual e malhas iguais comparadas sem ordem, como no D1 nesta rodada.

### B.2 Planos afetados

| Grupo | Planos | Mudança |
|---|---|---|
| Só composição (sem render 3D) | todos (legendas); C4, D2, E3, G3, H2 (cartões); A4 (tipo de fusão) | montagem |
| Reexportar rótulos, reaproveitar quadros com prova | C3, D1, D3, D4, E4, F2, G3z | âncoras e linhas dos rótulos |
| Render 3D de novo | ~29 planos com o interior visível (A1, A2, A4, A4b, B1–B7, C2, C4, D1, D3, D5, G1, G2, G3, H1, H2, I1–I4, J1, J1b, J2, J3) | itens, posição única do leite, leite fora de J1–J3 |
| Render 3D de novo (câmera) | 2–4 planos a escolher entre C4, E4, F2 e G3 | aproximações motivadas, se aprovadas |
| Render 3D de novo (ação) | I1 | saída visível + volta da câmera à geladeira |

### B.3 Riscos de regressão

1. **Itens novos sobre prateleiras de vidro:** o fundo do item coincide com o topo do vidro, que é transparente, e isso
   gera z-fighting visto de baixo. Prevenção: elevar 0,5 mm na modelagem. A mesma checagem vale para os itens que já
   existem.
2. **Itens cortados pelo plano x = 0** nos planos em corte (C2, C4, D1, D3, D5, G1, G2, G3, H1, H2, J3): viram tampas
   amarelas e poluem a leitura didática. Prevenção: posicionar os itens fora do corte, ou ocultá-los só nos planos técnicos
   (a diretriz permite).
3. **AO com corte:** itens novos perto das tampas mudam o sombreado. É preciso repetir a validação do AO (detector
   sensível) nos 11 planos em corte com interior.
4. **Visão térmica:** cada item precisa de uma temperatura coerente (geladeira ~5 °C, congelador −18 °C). Item na
   temperatura errada vira erro científico na tela.
5. **Cores:** os itens não podem usar a linguagem didática (laranja = calor, azul/ciano = frio, amarelo = tampa do corte,
   violeta = energia elétrica).
6. **Mudança de câmera (item 9):** altera rótulos, cartões, faixa da porta, juntas e estroboscopia. Exige revalidação do
   AO, da porta e das juntas e um teste em 1080 nesses planos.
7. **Saída do I1:** os passos do personagem estão sincronizados com o som. Mudar a caminhada obriga a refazer os passos
   do I1 na mixagem; o resto da mixagem fica idêntico, medido como nesta rodada. A narração não muda.
8. **Legendas mais altas na tela:** podem colidir com rótulos e cartões. A montagem já tem o posicionador com regras
   (programação dinâmica) e o registro de caixas. É preciso testar todos os quadros.
9. **Exportação não determinística:** congelar as cenas por hash depois da Rodada 9 e não reexportar mais.

---

## Etapa C — Plano da Rodada 9

### C.1 Mudanças propostas, por ordem (cada uma desligável)

**Fase 1 — só composição (barata, sem render 3D):**
1. **Legendas semânticas:** blocos que terminam em fim de frase, vírgula ou unidade de sentido. Nunca terminar em
   artigo, preposição ou conjunção. Mínimo de ~0,8 s por bloco, até 2 linhas curtas. Tempos sempre pelo `palavras.json`.
   As duas frases finais aparecem inteiras: "A geladeira não cria frio." / "Ela dá um destino ao calor."
2. **Áreas seguras para celular:**
   - legenda subir de 74 % para ~64–66 % da altura;
   - avisos descerem para abaixo da faixa superior;
   - nada útil na coluna direita de ~120 px (botões);
   - validado contra os gabaritos de margem (os mais conservadores).
3. **Cartões de pressão:**
   - texto de 30 → ~40 px;
   - escala e ponteiro mais claros, sem linhas supérfluas.
   - Valores, estados e movimento dos ponteiros **idênticos** (teste 845/845 de novo).
4. **A4 (opcional):** trocar a fusão de ~0,2 s por corte seco na pausa (mesmo instante, 4,87 s). Fica como A/B para você
   escolher.

**Fase 2 — rótulos e linhas (reexportação com prova, sem render):**

5. Âncoras **visíveis** em todos os rótulos:
   - **C3:** "fluido refrigerante" no tubo de cobre visível;
   - **D1:** "Evaporador" nas serpentinas à direita;
   - **D4 e F2:** "entra:" na boca visível do canal;
   - **E4:** "ar da cozinha" no lado visível do ar.
   - Regra nova no código: **nenhuma linha com a âncora fora do quadro**. Nesses casos, reposicionar o rótulo ou ocultar
     a linha.
   - D3 fica sem linha (rótulo encostado no fluido visível).
   - G3z: a linha só aparece com a âncora dentro do quadro e da lupa.
   - Contraste: o rótulo nunca sobre fundo da mesma cor (F2).

**Fase 3 — 3D (render de revisão só dos planos afetados):**

6. **Geladeira mais cheia e coerente:**
   - **Prateleiras da porta:** 3, com garrafas e frascos (giram com a porta).
   - **Gaveta:** frutas e verduras, como tomates, folhas verdes e maçã verde/vermelha.
   - **Potes com tampa.**
   - **Congelador:** 2–3 itens.
   - **Proporções reais em cm** e cores fora da linguagem didática.
   - **Física:** elevação de 0,5 mm sobre os vidros e temperaturas coerentes na visão térmica.
   - **Planos técnicos:** os itens que atrapalham são ocultos (com registro de quais).
7. **Leite:**
   - **Uma posição só em todos os planos:** a frente da prateleira de cima, alcançável.
   - **Sai de cena em I2–I4 e J1–J3**, porque foi levado.
   - **I1, dentro dos mesmos 3,58 s e com a narração intacta:**
     - a pega fica um pouco antes, para a **saída** ganhar ~0,7–0,8 s;
     - no fim do plano, a câmera **volta para a geladeira aberta**, motivando o corte para o I2.
   - **Mão e caixa:** a mão continua usando a mesma curva da caixa.
8. **Aproximações motivadas (item 9), só onde a medida mostrar salto de escala:**
   - primeiro meço a escala do elemento no último quadro de um plano × o primeiro do seguinte;
   - aproximação lenta no fim do plano aberto, em direção ao elemento do próximo plano;
   - sem novo corte e sem mudar t0/t1.
   - **Proposta inicial:** C4 → D1 e E4 → F1. A revelação (C1/C2), o corte em 33,92 s e o pulso ficam intocados.

### C.2 Dependências

- A Fase 1 não depende de nada e pode ser entregue primeiro, como uma V9a só de composição sobre os quadros da V8.
- A Fase 2 depende da Fase 1 (o posicionador de rótulos e legendas é o mesmo).
- **Itens:** a mudança 6 precisa vir antes de qualquer validação de AO e antes da 7 (o leite é um dos itens).
- **Câmera:** a mudança 8 é independente, mas troca câmeras, então vem antes da revalidação do AO e do teste em 1080.
- **Som:** a mixagem só é refeita no I1 (passos) se a mudança 7 mudar a caminhada.

### C.3 Testes (antes e depois)

- **Legendas:**
  - 0 blocos terminando em palavra fraca;
  - 0 blocos < 0,8 s, salvo justificativa;
  - texto **idêntico** ao roteiro, palavra a palavra;
  - início de cada bloco no ataque da primeira palavra.
- **Caixas:** registro de tudo o que é desenhado em todos os quadros, sem sobreposições, sem cortes e sem linha sobre
  texto, dentro das áreas seguras.
- **Pressão:** valores e ponteiros 845/845 idênticos; texto ≥ 38 px em 1080; legível no celular simulado (redução para
  a escala de tela).
- **Rótulos e linhas:**
  - 0 linhas com a âncora fora do quadro;
  - 0 rótulos com a âncora fora do quadro sem regra explícita;
  - auditoria rótulo × palavra de novo (24/24).
- **Leite e I1:**
  - folga caixa × prateleira, borda, porta e vedação ≥ 3 mm em toda a trajetória;
  - mão × caixa: distância constante depois da pega;
  - pés sem escorregar;
  - nenhuma interpenetração braço × porta;
  - 7 etapas visíveis, com instantes medidos;
  - leite ausente em I2–I4 e J1–J3.
- **Itens:**
  - sem colisões entre itens, prateleiras e paredes;
  - folga ≥ 0,5 mm sobre o vidro;
  - temperatura térmica coerente;
  - itens cortados pelo x = 0 só onde aprovado.
- **Imagem:**
  - validação do AO (padrão + sensível) nos planos em corte re-renderizados;
  - verificadores de porta e juntas;
  - folha de contato antes do render completo dos planos.
- **Estrutura:**
  - planos_resolvidos idênticos (ids, t0, t1);
  - 4.537 quadros, 151,233 s;
  - os planos não alterados saem **idênticos** à V8 ou dentro da variação natural medida.
- **1080:** testes curtos nos planos críticos que mudarem (C4/H2/G3/J3 se tiverem itens novos no corte; I1).
- **Áudio:** se o I1 mudar, a diferença fica só em 118–120 s; o resto ≤ −69,9 dBFS; validação no AAC (−14 LUFS,
  ≤ −1,5 dBTP).

### C.4 Custo de render (tempos reais da Rodada 8, revisão 540)

| Fase | Planos | Quadros | Tempo |
|---|---|---|---|
| 1 e 2 (composição + reexportação com prova) | — | 0 render | ~10–20 min (montagens + testes) |
| 3: itens + leite (interior visível) | ~29 | ~3.700 | **~5,3 h** |
| 3: aproximações (ex.: C4, E4) | 2 | ~280 | ~0,4 h (já incluídas se o plano também tiver itens) |
| Validações (AO, porta, juntas, folhas) | — | — | ~1 h |
| Testes em 1080 dos planos críticos alterados | 4–6 trechos | ~170 | ~1–1,5 h |

- **Total Fase 3:** ~7–8 h. A prévia completa nova (V9) sai em 540.
- **Render definitivo em 1080:** continua estimado em ~26–28 h e **só com autorização expressa**.

### C.5 O que não muda

- **Voz e texto:** narração (MP3, SHA-256 `fdedd877…`), roteiro e `palavras.json`.
- **Estrutura:** duração de 151,233 s e os 42 planos com os mesmos t0/t1.
- **Ciência:**
  - o modelo científico;
  - os valores e ponteiros de pressão;
  - as cores didáticas;
  - os avisos científicos ("Corte ilustrativo", "Tempo acelerado", "Câmera lenta", "Visão térmica").
- **Momentos aprovados:** a revelação do circuito, o corte em 33,92 s, o pulso, o obturador do C2 e o C4 sem desfoque.
- **Configurações validadas da Rodada 8:** AO com corte, folgas e correções de porta e degrau.
- **Personagem:** identidade (modelo, roupa, cores, proporções).
- **Som:** a mixagem aprovada; só os passos do I1, se a caminhada mudar.
- **Encerramento:** a frase final, sem vinheta, mascote ou logotipo.
- **Fora do escopo:** o Episódio 01.
- **Planos sem interior visível e sem rótulo alterado:** não são re-renderizados (ex.: A3, C1, C3, D2, D4, E1–E4, F1,
  F2, G3z, J4).

### C.6 Decisões que preciso de você

1. **Aprovar o plano** como um todo, ou por fase (posso entregar a Fase 1 antes, como V9a, para você conferir legendas
   e áreas seguras sobre a V8).
2. **Leite em J1–J3:** tirar (continuidade estrita; recomendo) ou manter (o J funciona como recapitulação).
3. **Aproximações (item 9):** medir primeiro e propor só onde houver salto, ou já incluir C4 → D1 e E4 → F1.
4. **A4:** manter a fusão curta da V8 ou testar o corte seco (A/B).
5. **Pendências da Rodada 8** que podem entrar junto, porque os mesmos planos serão re-renderizados: a sobreposição
   painel × vedação no lugar da folga (C4, H1, H2, G3, J3) e as costuras finas antigas.

**Nada publicado. Nenhuma voz gerada. Nenhum serviço contratado. Episódio 01 intacto. Render definitivo não iniciado.**

Fontes das margens de área segura (guias de terceiros; a Meta não foi confirmada diretamente):
[Lilach Bullock](https://www.lilachbullock.com/instagram-reels-safe-zone/),
[Hopper HQ](https://www.hopperhq.com/blog/instagram-reel-size/),
[Socialync](https://www.socialync.io/tools/safe-zones/instagram-reels).
