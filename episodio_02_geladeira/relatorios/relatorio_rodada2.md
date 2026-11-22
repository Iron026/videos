# Ep. 02 · Relatório da rodada 2 (correções do animatic)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado.
Render em 1080 p **não iniciado**. A narração aprovada está intacta: SHA-256 `fdedd877…05726ee`, conferido.

## Entregas
| Arquivo | O que é |
|---|---|
| `episodio/ep02_animatic.mp4` | Animatic **v2**: 540 × 960 (render 270 × 480 ampliado), 30 qps, **151,23 s**, 24,1 MB, narração aprovada, −16,4 LUFS (normalização de prévia). SHA-256 `1269c4bd…` |
| `episodio/ep02_animatic_v1_x_v2.mp4` | **v1 \| v2 lado a lado**, sincronizados, com o áudio da v2 |
| `relatorios/antes_depois_v2_1…6.jpg` | Antes × depois de cada plano alterado: 4 quadros por versão, com rótulos e legendas |
| `relatorios/contato_animatic_v2.jpg` | Folha de contato: o quadro do meio de cada plano |
| `relatorios/comparativo_v1_v2.json` | Comparação quadro a quadro dos planos que mantiveram os tempos |
| `relatorios/conferencia_legendas_v2.json` | Conferência das legendas contra o áudio |
| `voz/verificacao_whisper.json`, `voz/comparacao_tempos.json` | Verificação da narração e comparação de tempos v1 × v2 |

A v1 continua no histórico do git (commit `e08b526`, SHA-256 `50a12881…`).

## 1. Narração e sincronização
- **Verificação palavra a palavra:**
  - **Modelo:** oficial `openai/whisper-large-v3` (MIT), baixado sem credenciais e rodando **100 % local, offline**. O
    áudio não saiu da máquina.
  - **Resultado:** **384/384 palavras** do roteiro reconhecidas, na ordem (confiança média 0,99).
  - **Única divergência:** "condensador. Veja o", a 116,5 s, com duração zero. Retranscrito sem contexto, o trecho diz
    exatamente o texto do roteiro. Era um artefato do decodificador, não fala.
- **Tempos novos:**
  - a identidade das palavras vem do Whisper;
  - o instante de entrada depois de cada pausa vem do ataque acústico medido, porque o Whisper põe esses inícios ~0,3 s
    dentro do silêncio, e isso foi conferido no sinal;
  - as 78 pausas foram atribuídas;
  - a duração continua **151,24 s**.
- **A sincronia da v1 tinha erros reais**, e eles foram corrigidos:

  | Corte | v1 | v2 | Efeito na v1 |
  |---|---|---|---|
  | E3 ("Ele suga o vapor") | 76,52 s | 78,39 s | o compressor em corte entrava enquanto a narração ainda dizia "movido por eletricidade" |
  | E4 ("Agora, o refrigerante") | 80,62 s | 83,19 s | entrava 2,6 s cedo |
  | H1 ("Assim, ela volta") | 106,07 s | 107,55 s | entrava 1,5 s cedo |
  | A2 / A3 (dentro da 1ª frase) | 2,59 / 3,96 s | 1,60 / 2,98 s | entravam ~1 s tarde |

  Os outros **34 dos 39 cortes caem exatamente no mesmo instante** da v1.
- **Legendas (conferidas depois da revisão):**
  - nenhuma das 384 palavras sai da tela enquanto é falada;
  - os 73 blocos que começam depois de uma pausa entram no ataque medido (desvio de 0 quadro, em parte por construção);
  - os erros das legendas da v1 eram dentro das frases: média de 0,29 s, até 2,6 s em E2/E3 ("É aqui que entra o
    compressor" ficava espremido em 0,15 s).

## 2. O que foi corrigido
| Plano | Problema (v1) | Causa | Correção |
|---|---|---|---|
| A3 | Parede cinza ocupava o plano | Órbita rente à lateral, em 1,2 s | 3/4 traseiro quase fixo; **calor subindo da serpentina** |
| A4b, J1b | — | — | O mesmo calor subindo na metade traseira da tela dividida (abertura e conclusão rimam) |
| B2, J2 | Close sem leitura | Câmera na face inferior do congelador | Plano médio do congelador e da prateleira, sem "névoa" |
| B4 (18–20 s) | A garrafa sumia na visão térmica | Ambiente = garrafa = cinza | Garrafa na bancada **recortada contra o interior azul**; rótulo "temperatura ambiente"; garrafa interna oculta (é a mesma de B5) |
| B7 | Tudo azul | Enquadramento fechado | Plano mais aberto. **Melhora parcial**, ver §4 |
| C1 (30–32 s) | Planos brancos | A porta, ao fechar, passava rente à câmera | Começa de frente: porta aberta → fecha → corte |
| C3 | Pote vermelho tapava metade do quadro | Defeito antigo, achado nesta rodada | Pote oculto neste plano |
| **D4 (64–68 s)** | Mudança de fase invisível | No tubo real, o vapor aumenta ao longo de metros | **Canal do evaporador esticado e ampliado** (aviso "Canal ampliado (esquema)"). O fluido vem da mesma tabela do modelo, ponto a ponto: na entrada o líquido ocupa ~50 % do tubo, com bolhas; afina; **na saída, só vapor**. Feixes de calor entram pela parede. Rótulos "entra: líquido + vapor" / "sai: só vapor" |
| D5 | Começava no macro antigo | — | Plano médio do interior, com o calor dos alimentos chegando ao evaporador |
| F1 | O interior aparecia através da serpentina | Gabinete em corte sem necessidade | Gabinete inteiro atrás da serpentina |
| **F2 (91–96 s)** | Arames tapavam os tubos | Câmera atrás dos arames | **Canal do condensador esticado e ampliado**: vapor quente (escuro) → camada de líquido cresce → só líquido. Calor saindo. Rótulos "entra: vapor quente" / "sai: líquido" |
| G3 | Pote tapava o capilar | Objeto na linha de visão | Pote oculto |
| H1 | Começo escuro | Câmera no vão do congelador | Começa fora, no evaporador, e se afasta |
| H2 | "Compressor" e "Capilar" sobrepostos | Rótulos com o mesmo deslocamento | Os 4 componentes rotulados sem sobreposição |
| **I3, I4 (124–135 s)** | Vista de cima ilegível | A geladeira virava um retângulo; o laço parecia no chão | 3/4 alto com a parede da cozinha. **I3:** laço fechado (entra pela porta, sai pela traseira, volta para a frente) e rótulo "o calor volta para a mesma cozinha". **I4:** mesmo enquadramento; faixas proporcionais ao modelo: calor retirado + energia elétrica (violeta) = **calor liberado, mais largo** |

### Defeitos antigos encontrados e corrigidos
1. **Shader do fluido (macro):** o líquido devia ficar embaixo do tubo com limiar `2·lf − 1`, mas o código usava
   `1 − 2·lf`. Fora da faixa de ~50 % de líquido, isso trocava líquido e vapor: a sucção (vapor) aparecia como líquido e o
   início do capilar (líquido) como vapor. Corrigido.
   - A primeira versão da correção escureceu demais o vapor e apagou o azul de "frio" nos planos gerais (C4, H2). Ajustei
     para o vapor manter o matiz da temperatura, mais escuro e ralo que o líquido.
   - Planos afetados sem mudança de câmera: C2, C4, D1, D2, E1, G1, G2, J3 (tabela abaixo).
2. **Exportação:** o laço padrão não incluía as metades A4b/J1b da tela dividida (J1b estava com a cena da v1). Corrigido.
3. **Exportação não determinística:** a ordem dos objetos e a triangulação de duas malhas variavam entre execuções. Não
   há efeito visível: as posições são as mesmas. A ordem passou a ser fixa; a triangulação continua variando (anotado).

## 3. O que NÃO mudou, com medida
O renderizador por software **não é determinístico**. A mesma cena, com o mesmo motor, renderizada duas vezes (B1)
deu 0/42 quadros idênticos em bytes, diferença média de até **2,37** e picos de 81 (escala 0–255). Esse é o ruído de
fundo.

| Grupo | Planos | Diferença média v1 × v2 |
|---|---|---|
| **Iguais, dentro do ruído** | A4, B1, B3, B5, B6, D3, I1, I2, J1, J4 | 0,63–2,26 |
| Mudança só pelo shader corrigido | C2 2,9 · C4 3,4 · D1 3,7 · D2 3,2 · J3 2,3 · G1 8,8 · E1 9,9 · G2 16,9 | — |
| Alterados de propósito | os 18 da tabela do §2 | 3,1 (H2, só rótulos) a 88 (F2) |

Também não mudaram:
- **A1, A2, E2 e E3:** só os tempos mudaram, pela sincronização; câmera e conteúdo são os mesmos.
- **Roteiro, narração e duração aprovada.**
- Ciência e modelo do ciclo, geometria da geladeira, paleta térmica, grade e configuração de render (iguais à v1).

## 4. Problemas ainda existentes
- **B7:** melhora pequena. Na visão térmica, o interior (+4 °C) e o congelador (−20 °C) saem no mesmo azul, porque a
  paleta satura. O congelador não é nomeado antes de D1, por ordem dos conceitos. Proposta: aprofundar o azul abaixo de
  0 °C, uma mudança de paleta que preciso da sua decisão.
- **E1** (não pedido, não alterado): os arames do condensador ficam na frente da linha de sucção. É candidato à próxima
  rodada.
- **G3:** com o pote oculto, o fundo fica branco e liso. Funciona, mas é plano.
- **D4/F2:** a fração líquida **visual** é exagerada (em volume, o vapor domina) e o canal está fora de escala. Os dois
  pontos estão declarados nos avisos honestos e no código.
- **Imagem ainda "limpa e diagramática";** som só com a narração. O polimento e o som entram depois da sua aprovação.

## 5. Limites
- Eu meço, não assisto nem escuto como uma pessoa. A aprovação visual, do ritmo e do som é sua.
- Os quadros renderizados ficam no contêiner temporário; o vídeo, o código, os dados e os relatórios estão no git.

## 6. Licença
- **Narração:** plano da ElevenLabs **não confirmado**. Até você informar, a narração fica tratada como plano gratuito (sem
  uso comercial, atribuição obrigatória).
- **Whisper:** pesos oficiais da OpenAI, licença MIT, uso só local para verificação.
- Nenhum recurso de terceiros novo na imagem.
