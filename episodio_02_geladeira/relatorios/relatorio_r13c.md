# Ep. 02 · R13C: correções pontuais depois da escuta da R13B

Situação: **teste para a sua aprovação.**
- Ainda não é o definitivo.
- Os quadros definitivos do E3 não foram substituídos.
- **Nada foi publicado.**
- Eu meço, mas não escuto nem assisto como uma pessoa. A aprovação auditiva e visual é sua.

## Arquivos

Todos ficam em `episodio/previas_r13c/`.

| # | Arquivo | O que mostra |
|---|---|---|
| 1 | `01_efeitos_retirados_014_112_148.mp4` | 0:14, 1:12 e 1:48. **A** = R13B, **B** = sem o efeito (aprovado) |
| 2 | `02_revelacao_033.mp4` | 0:33: R13B × moderada × discreta. **Escolhida: C, discreta** |
| 3 | `03_passos_155.mp4` | 1:55, passos discretos (aprovado) |
| 3b | `11_batida_porta_029.mp4` | **Novo:** a batida da porta fechando (0:29,6). R13B × final |
| 4 | `05_e3_1080_lado_a_lado.mp4`, `06_e3_1080_camera_lenta.mp4`, `07_e3_detalhe_motor.mp4` | 1:18 em 1080: definitivo × corrigido, em velocidade normal, a 1/4 e com o motor ampliado 2× |
| 4b | `08_e2_e3_transicao_opcao.mp4` | Opção, desligada: fusão atual × corte seco no E2 → E3 |
| 4c | `09_quadros_repetidos_lado_a_lado.mp4`, `10_quadros_repetidos_camera_lenta.mp4` | **Novo:** início travado (A1) e os mesmos quadros repetidos em B7, H1 e I1, aprovado × corrigido |
| 5 | `04_previa_combinada_r13c_final_720.mp4` | **Episódio inteiro com o som final:** 0:33 discreta, porta mais baixa e as demais correções |
| — | `ep02_r13C_final_escuta_1080x1920.mp4` | O mesmo, em 1080, para escuta. Fica fora do git (160 MB) |

Nos comparativos de som e nas prévias, a imagem é a do definitivo R12. O fluxo de vídeo é idêntico ao do R12 (MD5 `c0342ad0…`).

## 1. Causa de cada problema

| Instante | O que era (medido no stem, por camada) | Função | O que foi feito |
|---|---|---|---|
| **0:14** | Impacto Freesound 754424 em 14,44 s, na pausa depois de "não fabrica frio.". Era o **único** efeito no trecho: sem ele, os efeitos caem a −150 dBFS | Acento sobre uma frase que já se sustenta | **Retirado** |
| **0:33** | Três camadas somadas: aproximação Mixkit 2615 (de 33,1 s, pico em 34,33 s), **impacto cinematográfico** Freesound 754422 (o mais forte, −19 LUFS momentâneo) e o sopro do pulso, Mixkit 1474 (35,9 s) | Revelação do circuito | **Impacto retirado.** Ficam a aproximação (o circuito aparece) e o pulso (o caminho do circuito), em 2 versões |
| **1:12** | Whoosh Mixkit 1474 em 72,77 s: a câmera desce com o vapor (E1) | Movimento de câmera | **Retirado.** O zumbido do compressor que entra junto é outra camada: ficou, sem mudança (diferença ≤ −162 dBFS) |
| **1:48** | Sopro Mixkit 1489 em 109,88 s. **É do movimento de câmera** (H1 se afastando até o circuito inteiro), não da apresentação de um mecanismo: a apresentação mais próxima é o pop de 1:41,2 | Movimento de câmera | **Retirado.** A transição visual não mudou |
| **1:55** | 6 passos do personagem no I1 (camada passos). Ficavam só **7,7 a 13,2 LU abaixo da voz**, como se estivessem colados no microfone | Presença do personagem na cozinha | **Reduzidos**, cada passo com seu próprio ganho; nada foi retirado |

Nenhum efeito novo entrou no lugar dos retirados.

### 0:33: as duas versões

As duas usam as mesmas fontes, trechos e instantes. Muda só o nível.

| | Camadas | Pico dos efeitos (K, 0,4 s) | Distância até a voz |
|---|---|---|---|
| R13B | aproximação + impacto + pulso | −19,4 LUFS | 7,1 LU |
| **B · moderada** | aproximação (−4 dB) + pulso | −27,4 LUFS | 15,1 LU |
| **C · discreta** | aproximação (−8 dB) + pulso (−2 dB) | −31,4 LUFS | 19,1 LU |

Na janela da revelação, a voz sobre o efeito passou de 13,1 dB para 18,8 dB (moderada) e 22,7 dB (discreta).

**Você escolheu a C, mais discreta.** É a que entra na mixagem final.

### Batida da porta da geladeira (0:29,6), pedido depois da escuta

**O que era:** a porta fechando no C1, Freesound 489749. Na cena, o ângulo da porta chega a zero em 29,577 s, e o som está em 29,569 s: 8 ms de diferença.

**O problema:** era o evento mais forte da camada de porta. Ficava só 6,1 dB abaixo da voz na faixa do celular e 12,0 LU abaixo em loudness K. Era também o que mais forçava o limitador.

**O que foi feito:** apliquei a mesma regra dos passos, com a câmera a 2,9 m da porta. A batida recebeu **−13,5 dB** e ficou 19,6 dB abaixo da voz no celular e 25,6 LU abaixo em K.
- O instante não mudou: atraso de 0 amostras.
- Só o trecho 29,2–30,6 s mudou. As aberturas da porta no A1 e no I1 ficaram intactas.
- A redução máxima do limitador caiu de 4,5 dB para 3,1 dB.

### 1:55: passos pela perspectiva da câmera

O alvo de cada passo é ficar 18 dB abaixo da voz, na faixa do celular e em loudness K. A esse alvo soma-se a atenuação pela distância da câmera ao pé: 20·log10(d / 2,4 m).

Cada passo tem o seu ganho, com rampas de 30 ms fora do contato. **Os instantes não mudaram:** a correlação R13B × R13C dá atraso de 0 amostras nos 6 passos.

| Passo (s) | Câmera → pé | Ganho | Passo − voz, antes | Passo − voz, depois |
|---|---|---|---|---|
| 116,017 | 2,39 m | −9,0 dB | −11,6 LU | −20,6 LU |
| 116,483 | 2,37 m | −10,2 dB | −7,7 LU | −17,9 LU |
| 116,950 | 2,66 m | −12,8 dB | −9,3 LU | −22,1 LU |
| 118,220 | 2,68 m | −7,9 dB | −11,0 LU | −18,9 LU |
| 119,085 | 2,47 m | −6,5 dB | −13,2 LU | −19,7 LU |
| 119,550 | 2,26 m | −5,4 dB | −12,1 LU | −17,5 LU |

Os passos fora de 115,9–120,05 s não mudaram (diferença ≤ −162 dBFS). Isso inclui os da abertura, que acontecem fora do quadro.

## 2. Testes de regressão do som

**Teste de nulo R13C × R13B**, por stem, em janelas de 50 ms, com limiar de −120 dBFS. Só mudam os trechos pedidos:
- 14,4–16,35 s
- 33,1–36,5 s (até 37,85 s na discreta, por causa do pulso)
- 71,8–74,45 s
- 109,25–111,25 s
- 115,9–120,45 s

Os décimos a mais no fim de alguns trechos são a liberação do limitador.

| Stem | Diferença máxima |
|---|---|
| Voz | −150,5 dBFS (o master é o mesmo da R13B, obtido por mínimos quadrados) |
| Música (Spice Intrigue, mixagem B) | −162,6 dBFS |
| Compressor | −162,6 dBFS |
| Gorgolejo | −192,7 dBFS |
| Chiado | idêntico bit a bit |
| Apresentações (pops) | −168,6 dBFS |
| Mecanismos do E3 | −174,6 dBFS |

**Versão final (discreta + porta), medida no AAC:**
- −14,16 LUFS e −1,87 dBTP;
- voz − resto no celular: p5 de 11,1 dB, mediana de 23,5 dB;
- perda em mono de 0,00 dB e último 0,5 s a −71 dBFS;
- os 22 eventos que ficaram passam no critério;
- o nulo contra a discreta só acusa diferença em 29,15–30,65 s, o trecho da porta.

**Variantes intermediárias, medidas no AAC do arquivo de escuta:**

| | Moderada | Discreta | R13B | Meta |
|---|---|---|---|---|
| Loudness | −14,17 LUFS | −14,17 LUFS | −14,15 | −14 |
| Pico verdadeiro | −1,78 dBTP | −1,84 dBTP | −1,87 | ≤ −1,5 |
| Voz − resto no celular (p5 / mediana) | **11,0 / 23,5 dB** | **11,1 / 23,5 dB** | 10,7 / 23,4 | p5 ≥ 10 |
| Perda em mono | 0,00 dB | −0,01 dB | −0,02 | ~0 |
| Último 0,5 s | −71 dBFS | −71 dBFS | −71 | silêncio |

**Os 22 eventos que ficaram:**
- voz sobre a fala de 7,4 a 23,1 dB acima do resto (regra ≥ 6);
- AAC × WAV com correlação ≥ 0,998 e atraso de 0 amostras;
- sincronia sem mudança: as camadas são as da R13B (nulo ≤ −168 dBFS), então vale a medida feita no som isolado na R13B, de −1 a +9 ms.

Uma ressalva sobre a minha medida rápida por camada: ela marca 100 a 134 ms nas válvulas porque a janela pega o pistão vizinho, a 100 ms, na mesma camada. É erro da medida, não da sincronia.

Registros: `relatorios/testes_r13c/verificacao_r13c_{moderada,discreta}.json` e `som/validacao_audio_r13c_*.json`.

## 3. Erro visual em 1:18 (E3, compressor em corte)

### O que eu conferi, item por item

Conferi nos quadros definitivos em 1080, nos quadros brutos do render e nos dados exportados da cena:

| Suspeita | Resultado |
|---|---|
| **Z-fighting / geometria coincidente** | **É o defeito.** Detalhes abaixo |
| Carcaça sobreposta / transparência / fantasma | A fusão padrão de 0,2 s (q2342–q2347, 78,07–78,23 s) mistura a carcaça fechada do E2 com o interior do E3, de outra câmera, com pesos 5 %, 22 %, 45 %, 70 %, 90 % e 99,7 %. É composição, não render. É a mesma transição do resto do episódio. Há uma alternativa de corte seco, desligada, no comparativo `08` |
| Animação do pistão e da biela | Fecha. A biela fica no pino da manivela (erro < 0,0001 mm) e chega ao pistão sempre a 9,000 mm. O pistão não sai do eixo. Espaço morto mínimo de 0,80 mm, sem colisão com a placa de válvulas |
| Continuidade de câmera no E3 | Lisa: no máximo 0,97 mm por quadro, variação do passo ≤ 0,02 mm, sem saltos |
| Oclusão | Sem falha nova. O rotor aparece inteiro dentro do corte, como projetado: peças que giram não são cortadas |
| Barra bege sobre o disco branco | É a marca do rotor (`mec_marca`), que mostra a rotação. É proposital e gira junto com ele |

### Causa demonstrada

As cabeças de bobina de cobre são cilindros de raio 52 mm, nas alturas 58–70 mm e 120–132 mm. O estator é um cilindro de raio 60 mm, de 70 a 120 mm. Por isso as faces z = 70 mm e z = 120 mm das duas peças coincidem por definição.

O corte ilustrativo do E3 (plano y = 0,18) passa exatamente pelo eixo. O raio que entra na tampa do estator encontra, no mesmo plano, duas superfícies: a face interna do estator (amarela) e a face da bobina (cobre, ou cinza na junção de cima). O renderizador alterna entre as duas de um quadro para o outro, e isso gera listras horizontais e uma região que troca de cor:
- amarela no q69;
- laranja listrada no q48;
- amarela listrada no q27.

**A prova foi desligar uma coisa de cada vez** no quadro 48, renderizado de novo na mesma configuração do definitivo:

| Render | Listras |
|---|---|
| Controle (igual ao definitivo, diferença média de 0,58) | **sim** |
| AO desligado | **sim**: não é o AO |
| Sem o rotor | **sim**, e mais visíveis: não é o rotor |
| Sem o estator | não |
| Sem a bobina | não |

**Origem:** está no render 3D. O quadro bruto `quadros_final/E3/q0048.jpg` já tem as listras, antes da composição.

**Extensão:** todo o E3, nos quadros 0–159, que aparecem no vídeo de 1:18,0 a 1:23,0. Só o E3 tem o compressor cortado; nos outros planos a carcaça fecha e esconde essas faces.

### Correção: só a malha da bobina

Saem as duas faces de contato, 68 dos 280 triângulos da `mec_enrolamento`. Elas ficam por dentro do estator, que é mais largo (60 mm contra 52 mm), e nunca aparecem por fora. A cena de origem `cenas/E3` continua intocada; a cena corrigida é `cenas/E3_r13c_faces`, gerada por `episodio/bobina_r13c.py`.

Testei três opções nos quadros 27, 48 e 69:

| Opção | Resultado |
|---|---|
| Folga de 0,02 e 0,05 mm | Sem listras, mas abre uma **fresta tracejada** |
| Sobreposição de 0,3 mm | Sem fresta, mas o cobre aparece através do estator cortado |
| **Retirar as faces de contato (escolhida)** | A tampa do estator fica amarela e estável, como no q69 do definitivo, e a cunha cinza fica com as bordas retas. Sem fresta |

**Re-render só do E3:**
- 160 quadros em `quadros_final_r13c/E3`, na mesma configuração do definitivo (o motor é equivalente pelo registro da R12, conferido de novo com o render de controle);
- blocos de 40 quadros, manifesto com SHA-256 e verificação de cada quadro: semelhança mínima de 0,983 e diferença média máxima de 1,35;
- **os quadros definitivos não foram substituídos.**

### Medidas (todos os 160 quadros)

| | Definitivo | Corrigido |
|---|---|---|
| Listras, pixels por quadro (média / p95 / máx.) | 922 / 2838 / 7622 | 92 / 302 / 568 |
| Variação da contagem de um quadro para o outro | 1105 | 48 |
| Cintilação na junção (\|Δ\| entre quadros, média / máx.) | 11,07 / 23,54 | **1,32 / 3,77** |
| Fora da junção: corrigido × definitivo | — | ≤ 0,32 (abaixo da variação natural, 0,46–0,65) |

A contagem residual no corrigido vem do degradê da faixa laranja grande: é falso positivo do detector, que aparece também no definitivo.

A janela composta de 76,9 a 83,6 s confere com o esperado: só mudam os quadros em que o E3 aparece. Veja os vídeos `05` (normal), `06` (câmera lenta), `07` (detalhe 2×) e, para a transição, `08`.

## 3b. Início "travado" (pedido depois da escuta)

**Causa:** está na montagem, não no render. O quadro é escolhido por `round((g − g0) × 30)`, e o `round` do Python arredonda empates para o par.

Em 4 planos, o g0 cai exatamente a meio quadro: A1 (−0,25 s), B7 (26,05 s), H1 (107,05 s) e I1 (115,35 s). Ali todo instante é empate, e o índice sai 8, 8, 10, 10… Cada quadro aparece duas vezes, o que dá **15 qps efetivos**. Erros de ponto flutuante quebram o empate em alguns trechos, e por isso o travamento é irregular.

Os quadros brutos estão todos diferentes e a animação exportada é lisa. A sequência de quadros repetidos prevista pela conta bate com o vídeo:

| Plano | Pares previstos que batem com o vídeo |
|---|---|
| A1 | 40 de 43 |
| B7 | 64 de 71 |
| H1 | 132 de 135 |
| I1 | 93 de 97 |

As poucas diferenças são quadros em fusão ou com rótulos mudando.

**Correção:** `ARRED_QUADROS=1`, só na montagem. No empate, escolhe sempre o quadro seguinte. Vale para os quadros, rótulos, manômetros, pontes e rosto.

| Plano | Trecho | Sem a chave, igual ao aprovado | Quadros alterados | Repetidos em sequência |
|---|---|---|---|---|
| A1 | 0:00–0:01,4 | 48 de 48 | 23 | 16 → 0 |
| B7 | 0:26,2–0:28,6 | 78 de 78 | 49 | 16 → 0 |
| H1 | 1:47,3–1:51,8 | 140 de 140 | 42 | 16 → 0 |
| I1 | 1:55,9–1:59,1 | 102 de 102 | 11 | 9 → 0 |

O primeiro quadro do vídeo não muda. Sem render 3D. Comparativos: `09` (lado a lado, normal) e `10` (câmera lenta).

O B7, o H1 e o I1 tinham o mesmo defeito, menos visível. A correção é uma regra só e alcança os quatro planos.

## 4. O que não mudou

- **Narração:** o stem da V9, sem nenhuma mudança (diferença ≤ −150 dBFS, vinda só do arredondamento do mesmo master).
- **Música:** Spice Intrigue na mixagem B, com as mesmas emendas, automação e abaixamento (≤ −162 dBFS).
- **Ruído contínuo:** continua removido.
- **Os demais efeitos** que já funcionavam: transição do rosto, 5 pops, pistão e válvulas, fluxo do C3, chiado do capilar, porta, mão, leite e garrafa.
- **Tempos:** os mesmos, e a duração continua 151,233 s.
- **R12 e R13B intactas,** com SHA-256 conferido:
  - mixagem e FLAC da R13B;
  - stems de música e Mixkit da R13B (`4b992e51…` e `762d15c6…`);
  - stem CC0 da R13B;
  - FLAC da R12 (`5c3b593e…`);
  - MP3 da faixa.
- **Stems da R13B:** continuam em `som/stems/r13/`, com a data original. As variantes têm pastas próprias: `stems/r13_r13c_moderada` e `stems/r13_r13c_discreta`.
- **Montagem:** as duas opções novas (`QUADROS_R13C` e `CORTE_E3`) vêm desligadas. Com elas desligadas, os 201 quadros compostos de 76,9 a 83,6 s são idênticos (SHA-256) aos da montagem aprovada.

## 5. Preservação

- **Mixagens em FLAC 24 bits:** `som/preservado_r13c/audio_ep02_r13C_{moderada,discreta,final}.flac`, com erro de −144,5 dBFS em relação ao WAV. A **final** é a escolhida.
  - O registro, com os comandos e os SHA-256 de todos os stems, está em `som/preservado_r13c/preservado_r13c.json`.
- **Reconstrução da final:** `R13C=1 PORTA_R13C=1 C2_REVELA=discreta SUF_R13=_r13c_final MASTER_R13_DB=-0.03170566623698933 SO_VARIANTES=r13_teste python3 som/som_r13.py`
  - Sem `R13C=1`, o mesmo script reproduz a R13B.

## 6. Licenças

- **Narração:** plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória. Para monetizar, a voz precisa de outra licença.
- **Música:** Pixabay Content License. Continua pendente a sua conferência da página da faixa.
- **Efeitos:** só saíram efeitos ou mudaram níveis; nenhuma fonte nova entrou. Os retirados (Freesound 754424, Mixkit 1474 no E1 e Mixkit 1489) deixam de ser usados.
  - O 754422 também sai, porque nenhuma das duas versões de 0:33 o usa.
  - O 1474 continua no pulso do C2.
  - Os arquivos Mixkit isolados continuam fora do git.

## 7. Para consolidar o definitivo R13

Você já aprovou as mudanças de som. Falta aprovar a parte visual:
1. **E3 (1:18):** os quadros corrigidos estão prontos em `quadros_final_r13c/E3`.
2. **Quadros repetidos:** a correção é a opção `ARRED_QUADROS=1`.
3. **Transição E2 → E3:** manter a fusão (como hoje) ou usar o corte seco (`CORTE_E3=1`).

Com a sua aprovação, a montagem definitiva usa as opções aprovadas e o áudio final:

`QUADROS_R13C=E3=quadros_final_r13c/E3 ARRED_QUADROS=1 [CORTE_E3=1] bash montar_r11.sh final <saída> ../som/audio_ep02_r13_r13c_final_r13_teste.wav`

Depois vêm o master sem legendas, as validações e os hashes. Nenhum outro plano é re-renderizado.

**Nada foi publicado.**
