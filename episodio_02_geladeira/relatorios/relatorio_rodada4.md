# Ep. 02 · Relatório da rodada 4 (estrutura visual consolidada)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado.
Render em 1080 p **não iniciado**, sem polimento definitivo nem sound design.
- **Preservados:** narração (SHA-256 `fdedd877…`, conferido), roteiro, alinhamento das palavras (`roteiro/palavras.json`)
  e modelo científico.
- **Duração:** **151,23 s**.

## Entregas
| Arquivo | O que é |
|---|---|
| `episodio/ep02_animatic.mp4` | Animatic **V4** (540 × 960, 30 qps, 151,23 s, 24,5 MB, −16,4 LUFS de prévia). SHA-256 `3fbae7be…` |
| `episodio/ep02_v3_x_v4_trechos.mp4` | **V3 \| V4 lado a lado**, só os trechos alterados (A2–A4, B4–B7, C2, E1, G3, J1), com áudio |
| `relatorios/antes_depois_v4_1…3.jpg` | Antes × depois: A4, A2, B7 · C2, E1, G3 · B5, B6, J1 |
| `relatorios/v3_x_v4_planos.json`, `v3_x_v4_montado.json` | Medidas por plano e do vídeo montado, mais a linha do tempo dos avisos |

A V3 continua no git (commit `7cfe119`).

## 1. O que mudou
| Pedido | Correção |
|---|---|
| **A4 em imagem normal** | O contraplano do rosto (início e fim) agora é imagem normal. A visão térmica fica só durante a tela dividida (interior frio × traseira quente, preservada). A troca acontece enquanto a divisória desliza |
| **Avisos só com o modo ativo** | "Visão térmica" e o "Corte ilustrativo" da tela dividida são calculados das **curvas gravadas em cada cena**, com a mesma interpolação do motor, e não mais por plano inteiro (tabela abaixo) |
| **Mão no queixo** | O alvo da mão vem da cabeça **já posicionada**: ponto de contato sob o queixo, mão apontando para cima, o cotovelo cai naturalmente. Ajustes discretos: olhar para o alto da traseira (o "quente por fora"), uma sobrancelha um pouco mais alta e cabeça inclinada. Modelo, roupas e proporções **inalterados** |
| **Fim da revelação (C2)** | Corte seco em 33,92 s, ângulo traseiro-lateral e pulso **mantidos**. Só os dois últimos pontos da câmera mudaram: termina em **3/4 traseiro alto**, com condensador de frente, interior em corte, evaporador no alto, sucção, compressor e capilar embaixo, todos no mesmo quadro, e o pulso voltando ao compressor. Mesma duração |
| **B7** | (a) Enquadramento de frente e abaixo do congelador: a caixa ocupa o alto do quadro e os feixes sobem até ela. (b) Paleta: o degrau de +10 °C passou de azul médio para **azul-gelo**. O interior (+4 a +6 °C) clareia; o congelador e o evaporador (−18 a −20 °C) ficam com a **mesma cor de antes**, e o contraste entre os dois aumenta. É uma **função única** para tudo, então a paleta continua consistente |
| **E1** | A câmera olha a linha de sucção pelo **lado em corte**: os arames do condensador ficam só ao fundo, nunca entre a câmera e o tubo. A descida acompanhando o vapor foi mantida |
| **G3** | A câmera fica entre a parede traseira e o condensador (sem arames na frente), mais afastada e com lente mais aberta. O capilar no centro, com o líquido mudando de cor ao esfriar. Ao fundo: prateleiras, a borda da parede em corte e, no fim, o evaporador (o destino). Nenhum objeto novo. O pote continua oculto, como na V2 |

**Linha do tempo dos avisos (medida na montagem):**

| Trecho | Avisos |
|---|---|
| 1,50–4,90 s (varredura de A2 + A3) | Visão térmica (+ "Corte ilustrativo" em A3, traseira com a parede em corte) |
| 4,90–5,47 s (rosto, imagem normal) | nenhum |
| 5,47–9,70 s (tela dividida) | Visão térmica + Corte ilustrativo |
| 9,70–10,14 s (rosto, mão no queixo) | nenhum |
| 17,27–28,47 s (B4 a partir da troca para térmica, até B7) | Visão térmica |
| 135,33–139,0 s (J1) | Visão térmica; + Corte ilustrativo a partir de 135,77 s |

**Defeitos antigos corrigidos junto:**
- **B4:** o aviso "Visão térmica" aparecia antes de a visão térmica ligar.
- **J1:** a metade traseira mostrava a parede em corte **sem** o aviso "Corte ilustrativo".

## 2. O que foi preservado (medido)
- **26 dos 41 planos renderizados têm quadros idênticos byte a byte aos da V3.** Os 15 renderizados de novo:

  | Motivo | Planos |
  |---|---|
  | Pedidos | A4, B7, C2, E1, G3 |
  | Visão térmica, onde a paleta aparece | A2, A3, A4b, B4, B5, B6, J1, J1b |
  | Closes do capilar | G1, G2 |

- **Ruído natural do renderizador** (mesma cena, renderizada duas vezes): diferença média de até 2,37.
  - **Dentro do ruído**, iguais na prática: A3 1,32 · A4b 1,65 · J1b 1,82 · G1 0,68 · G2 1,20.
  - **Mudaram pela paleta** (o interior mais claro, como pretendido): A2 8,7 · B4 5,8 · J1 22 · B5 25 · B6 32.
- **Planos gerais em que o capilar aparece pequeno** (C4, H2, D1): testei com a paleta nova antes de decidir. A diferença
  ficou dentro do ruído (0,07–0,38), então **não** foram renderizados de novo.
- **No vídeo montado, fora dos planos renderizados de novo:** diferença média de 0,35 e máxima de 1,03. Só um quadro, colado
  a um corte, passa de 1,0: é ruído de compressão.
- **Não mudaram:**
  - narração, roteiro, legendas, cortes e duração;
  - o corte seco e o pulso de C2;
  - o personagem (aparência e participação em A1, A2, A4 e I1);
  - C1, I1 a I4 e todos os planos de D a J, exceto E1, G1–G3 e J1.

## 3. Problemas ainda existentes
- **G3:** o fundo melhorou (prateleiras, borda do corte e, no fim, o evaporador), mas ainda é o interior claro. A linha de
  sucção não entra no quadro: dos ângulos que a incluem, ou ela tapa o capilar ou os arames do condensador ficam na frente.
- **Contraplano de A4:** o fundo é a parede lateral lisa com céu, porque a cozinha não tem parede frontal. É cenário, para
  o polimento.
- **Personagem:** articulações rígidas, caminhada simples, materiais sem detalhe (previstos para o polimento).
- **A imagem em geral** continua "limpa e diagramática". Iluminação, materiais e som entram depois da aprovação desta
  estrutura.
- Eu meço, não assisto como uma pessoa. A aprovação visual é sua.

## 4. Licença
- **Narração:** o plano da ElevenLabs **ainda não foi confirmado**. Até lá, a narração fica tratada como plano gratuito
  (sem uso comercial, atribuição obrigatória).
- **Personagem e cenários:** feitos do zero neste projeto, sem recursos de terceiros.
