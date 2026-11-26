# Ep. 02 · R13C: correções pontuais depois da escuta da R13B

Situação: **teste para a sua aprovação.**
- Ainda não é o definitivo.
- Os quadros definitivos do E3 não foram substituídos.
- **Nada foi publicado.**
- Eu meço, mas não escuto nem assisto como uma pessoa. A aprovação auditiva e visual é sua.

## Arquivos

| # | Arquivo (em `episodio/previas_r13c/`) | O que mostra |
|---|---|---|
| 1 | `01_efeitos_retirados_014_112_148.mp4` | 0:14, 1:12 e 1:48. **A** = R13B, **B** = sem o efeito |
| 2 | `02_revelacao_033.mp4` | 0:33. **A** = R13B, **B** = redução moderada, **C** = mais discreta |
| 3 | `03_passos_155.mp4` | 1:55. **A** = R13B, **B** = passos discretos |
| 4 | `05`–`08_e3_*.mp4` | 1:18 em 1080. Definitivo × corrigido, em velocidade normal, câmera lenta e detalhe 2×. O `08` mostra a opção da transição |
| 5 | `04_previa_combinada_r13c_{moderada,discreta}_720.mp4` | Episódio inteiro com todas as correções de som |
| — | `ep02_r13C_{moderada,discreta}_escuta_1080x1920.mp4` | Os mesmos, em 1080, para escuta. Ficam fora do git: 160 MB cada |

Nos comparativos de som e nas prévias, a imagem é a do definitivo R12. O fluxo de vídeo é idêntico ao R12 (MD5 `c0342ad0…`).

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

**Medido no AAC do arquivo de escuta:**

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

PENDENTE_VISUAL

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

- **Mixagens candidatas em FLAC 24 bits:** `som/preservado_r13c/audio_ep02_r13C_{moderada,discreta}.flac`, com erro de −144,5 dBFS em relação ao WAV.
  - O registro, com os comandos e os SHA-256 de todos os stems, está em `som/preservado_r13c/preservado_r13c.json`.
- **Reconstrução:** `R13C=1 C2_REVELA=<moderada|discreta> SUF_R13=_r13c_<v> MASTER_R13_DB=-0.03170566623698933 SO_VARIANTES=r13_teste python3 som/som_r13.py`
  - Sem `R13C=1`, o mesmo script reproduz a R13B.

## 6. Licenças

- **Narração:** plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória. Para monetizar, a voz precisa de outra licença.
- **Música:** Pixabay Content License. Continua pendente a sua conferência da página da faixa.
- **Efeitos:** só saíram efeitos ou mudaram níveis; nenhuma fonte nova entrou. Os retirados (Freesound 754424, Mixkit 1474 no E1 e Mixkit 1489) deixam de ser usados.
  - O 754422 também sai, porque nenhuma das duas versões de 0:33 o usa.
  - O 1474 continua no pulso do C2.
  - Os arquivos Mixkit isolados continuam fora do git.

**Nada foi publicado.** O definitivo R13 só será consolidado depois que você aprovar os comparativos.
