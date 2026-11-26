# Ep. 02 — Rodada 10: validação final, polimento e preparação do render definitivo

## Resumo

- **Imagem:**
  - Obturador de 180° no C4, quadros 126–178, como você autorizou.
  - Um defeito antigo corrigido no A4, quadro 34.
  - Nenhum outro defeito que precise de correção.
- **Antisserrilhado:** o MSAA 4× aprovado foi mantido, porque o supersampling não mostrou ganho consistente.
- **Som:** efeitos novos ligados à animação e uma trilha experimental, com licença verificada. Tudo em camadas separadas
  sobre a mixagem V9; a V9 em si não muda.
- **Duas falhas minhas, achadas e corrigidas nesta rodada:**
  1. O validador de áudio media a voz contra o resto com stems antigos.
  2. Os stems da V9 estavam cortados em 0 dBFS.

  A V9 foi regenerada idêntica bit a bit e todas as medidas foram refeitas.
- **Status:**
  - **Nada publicado.** Nenhuma voz gerada, nenhum serviço contratado, Episódio 01 intacto.
  - **Render 1080 completo: não iniciado.**

Eu meço, mas não assisto nem escuto como uma pessoa. A aprovação estética e auditiva é sua.

## Arquivos para avaliar

As quatro versões da V10 em 540 têm o **mesmo vídeo**: o stream de imagem é idêntico byte a byte. Muda só o áudio.

| Arquivo | Áudio |
|---|---|
| `episodio/ep02_v10_revisao_audio_v9.mp4` | **A:** mixagem V9 aprovada |
| `episodio/ep02_v10_revisao_efeitos.mp4` | **B1:** V9 + efeitos novos |
| `episodio/ep02_v10_revisao_trilha.mp4` | **B2:** V9 + trilha |
| `episodio/ep02_v10_revisao_efeitos_e_trilha.mp4` | **B:** V9 + efeitos novos + trilha (versão experimental completa) |

**Comparativos A/B** (`episodio/previas_r10/`). Em cada trecho, A toca e depois B, com o rótulo na tela.

| Arquivo | Compara |
|---|---|
| `ab_audio_v9_x_nova.mp4` | A × B em 5 trechos: abertura, revelação, válvulas, puxador e leite, conclusão |
| `ab_so_trilha.mp4` | B1 × B: só a contribuição da trilha (os mesmos efeitos dos dois lados) |
| `ab_so_efeitos.mp4` | A × B1: só os efeitos novos |
| `trilhas_candidatas_audicao.m4a` | as 4 trilhas candidatas, 25 s cada, no mesmo nível (fica fora do git, por causa da licença) |

**Imagens:** `relatorios/comparativos_r10/` contém:
- C4 com e sem obturador;
- bordas da faixa do obturador e passagem C4 → D1;
- A4 q34 antes × depois;
- mapas dos testes em 1080 e do antisserrilhado.

## 1. C4 com obturador de 180° (quadros 126–178)

**No pipeline:**
- A faixa entrou em `config/producao.json`.
- O render reaproveitou, conferidos por SHA-256, os quadros 0–125 e 179–184 sem mudança. Só a faixa foi renderizada,
  com 5 sub-quadros por quadro.
- Câmera, trajetória, tempos e enquadramento final são os mesmos.

**Teste contínuo em 1080** (q120–184, mais D1 q0–20): `relatorios/testes_r10/c4_1080_obturador.json`

| Medida | V9 (sem) | V10 (com) |
|---|---|---|
| Arames do condensador: pixels piscando, q156–183 | 244.777 | **121.181 (−50 %)** |
| Pior quadro (arames) | 45.959 | **17.575 (−62 %)** |
| Quadro todo, pior quadro | 139.748 | 86.381 (−38 %) |
| Blocos que piscam em ≥ 3 quadros seguidos | 373 | 156 |

- **Legibilidade do evaporador:** a nitidez fica entre 0,75 e 0,97 da V9 na fase rápida e em 0,99–1,0 quando a câmera
  desacelera. O evaporador continua legível (`c4_1080_r9_x_r10_q160_q170.jpg`).
- **Continuidade nas bordas da faixa:**
  - **125 → 126:** salto de 4,64, igual aos vizinhos (3,81 e 4,85). Sem degrau.
  - **178 → 179:** salto de 0,91, contra 0,27 dos vizinhos, em 0,8 % dos pixels. É a troca de "5 amostras integradas"
    para "1 amostra": fica só em contornos finos e no granulado do AO.
  - **Opção:** estender o obturador até 184, o fim do plano. São 30 sub-quadros a mais, cerca de 15 min em 1080.
- **Conflitos de profundidade:** nenhum novo. O que pisca são bordas em movimento, e isso cai com o obturador.
- **C4 → D1:** o evaporador fica na mesma posição dos dois lados (`c4_d1_1080.jpg`). O D1 começa estável: no máximo 1
  bloco piscando por quadro.

## 2. Auditoria visual do episódio

**Defeito corrigido: A4, quadro 34 (5,77 s)** — `comparativos_r10/a4_quadro34_v9_x_v10.jpg`

- **Sintoma:** na tela dividida, um quadro mostrava uma parede vazia da cozinha entre o rosto e o interior térmico.
- **Causa:** a troca de câmera tinha duas chaves separadas por 26 ms, menos que um quadro (33 ms). O quadro 34 caía
  entre elas, com a câmera interpolada. Existia desde a V8.
- **Correção localizada:**
  - dentro dessa janela, a câmera usa a posição do fim da janela, sem alterar a trilha nem as chaves;
  - a visão térmica liga no mesmo instante;
  - a chave `CAM_A4_R10=0` reproduz a V9.
- **Prova, quadro a quadro:** `provar_quadros_iguais.py` → `relatorios/testes_r10/prova_reuso_A4.json`.
  - Câmera, objetos, curvas, malhas, materiais, rótulos e manômetros comparados: **só o q34 muda**.
  - O render reaproveitou os outros 173 quadros e **renderizou 1 quadro** (26 s).
- **Varredura do mesmo padrão em todas as cenas:** nenhum outro caso.

**Cintilação nos 42 planos** (`testes_r10/cintilacao_540_todos.json`):
- **Igual à V9** em todos os planos, menos o C4, que melhorou (pior quadro: 280 → 157 blocos).
- **Picos classificados pelo mapa, nenhum é conflito de profundidade:**
  - arames e tubos em movimento (C2, E1, F1, H1);
  - feixes e canal animado (D2, D4, D5, G3z);
  - porta e câmera em movimento (A1, C1, I1);
  - pistão do compressor (E3).

**Testes contínuos em 1080** (11 trechos: C4, D1, C2, G3, G3z, F1, D4, E3, H1, A2, A4) — `testes_r10/testes_1080_r10.json`

- **1080 × 540:** pixels piscando em 1080 ÷ 540, na mesma área de tela = **0,69 a 1,22**. Conflito de profundidade mudaria
  com a resolução; isto não muda.
- **C2:** igual à rodada 8 aprovada nos mesmos quadros (pior quadro: 950 × 952 blocos).
- **Nenhum defeito aparece só em 1080.**

**Antisserrilhado** (`testes_r10/antisserrilhado_1080.json`):
- **Método:** MSAA 4× em 1080 contra uma referência de 2160 reduzida para 1080, em F1, A2, G3, H1 e E1, 8 quadros
  contínuos cada. Comparei também com a escala 1,5× (custo 2,25×).
- **Resultado da escala 1,5×:**
  - cintilação de borda: −10 a −22 % em quatro trechos e **+19 % no H1**;
  - erro espacial: pior em 4 de 5.
- **Sem ganho perceptível consistente:** o **MSAA 4× aprovado fica**, sem aumento de custo.
- **O que sobra:** está nos arames e tubos mais finos que 1 pixel (mapas em `comparativos_r10/antisserrilhado/`).

**Quadros duplicados** (`testes_r10/quadros_duplicados.json`):
- O perfil final renderiza a 30 fps com passo 1.
- **0 quadros duplicados no trecho visível.** Os 130 idênticos ficam nas margens de fusão, antes da câmera começar.

**V10 × V9, imagem inteira** (`testes_r10/v9_x_v10_imagem.json`):
- Só mudam o A4 q34 e o C4 126–178.
- O resto das diferenças, ≤ 1,6, fica nos grupos de quadros do x264 que contêm essas mudanças. Elas terminam nos
  quadros-chave de 12,43 s e 56,90 s.
- Os quadros-fonte desses trechos são os mesmos da rodada 9 (SHA-256). **É o codificador, não a imagem.**

**Composição em todos os 4.537 quadros da V10:** 0 problemas; 865 de 865 ponteiros iguais ao modelo.

## 3. Materiais, luz e cor (avaliação medida, sem mudanças)

Medido por plano (`testes_r10/luz_cor_por_plano.json`): luminância (p1, p50, p99), áreas estouradas, áreas pretas,
croma e neutros.

- **Realces estourados:** ≤ 0,5 % em todos os planos (máximo no D5).
- **Pretos:** acima de 10 % só no C3, E1 e E2. São arames, tubos e fundo escuros por desenho, não sombras esmagadas
  (folha conferida).
- **Correção de cor:** a aprovada, uniforme. As cores didáticas não mudaram.

**Conclusão:** não achei defeito de material ou luz que justifique mexer. Um ajuste de aparência obrigaria a renderizar
de novo o episódio inteiro e é escolha criativa; não fiz.

## 4. Som: efeitos novos (B1)

**Arquitetura:** os 4 stems da V9 são somados **sem alteração**, e as camadas novas entram em stems próprios, com o mesmo
master fixo e o mesmo limitador. Prova: sem as camadas novas, a saída difere da V9 em **−136,7 dBFS**, o que é só
arredondamento numérico.

| Evento | Instante (da cena) | Gravação (Freesound CC0) |
|---|---|---|
| Mão fecha no puxador | A1 0,20 s; I1 117,51 s (mão a ≤ 1 mm do puxador) | ObjectCatchHold (RandomWizKid) |
| Mão fecha na caixa de leite | 118,44 s | manuseio de caixa de leite (PeteHaase) |
| Caixa sai da prateleira de vidro | 118,62 s (ergue 3,2 cm) | "Freezer – glass – take" (ValentinPetiteau) |
| Válvulas do compressor abrindo | 13 instantes no E2/E3, os únicos planos com as válvulas de perto | clique de relé abafado (representação; declarado) |

- **Sincronia:** o ataque medido fica 1–5 ms depois do instante da animação.
- **Nível:** as válvulas seguem a distância real da câmera.
- **Prioridade da voz:** todos os efeitos novos abaixam sob a fala.
- **O que eu não acrescentei:**
  - sons em setas, textos, cortes ou feixes;
  - "whoosh";
  - movimento de recipientes da porta, porque eles não se movem na imagem;
  - ruído industrial.

## 5. Trilha (B2, B)

**"Rest Now", Eugenio Mininni** (Mixkit Stock Music Free License). Licença completa em `relatorios/licencas_r10.md`.

- **Seleção:** 391 faixas do catálogo → 28 candidatas medidas (percussão, graves, faixa da voz, dinâmica) → 4 finalistas
  para você ouvir (`trilhas_candidatas_audicao.m4a`).
- **Por que "Rest Now":** é a que tem menos percussão (6,8 %), pouco grave (15 %), volume estável (6,8 dB) e é marcada no
  Mixkit como tecnologia e ciência.
- **Tratamento:**
  - corte de graves abaixo de 60 Hz;
  - −3 dB entre 0,9 e 3,2 kHz, a faixa da voz;
  - abaixamento de −8 dB sob a fala real, começando 0,15 s antes da palavra;
  - em média, 26 dB abaixo da voz.
- **Automação por trecho:**
  - **Abertura:** entra suave.
  - **Revelação:** −3 dB a partir dos 33,92 s.
  - **Explicação:** −7 dB.
  - **Compressor e condensador:** −12 dB, o mecanismo fala mais alto.
  - **"E tudo recomeça":** −5 dB.
  - **Porta aberta:** −6 dB.
  - **Conclusão:** −7 dB.
  - **Saída:** termina entre 145,0 e 147,6 s, então a última frase, "Ela dá um destino ao calor.", fica **sem música**.
  - **Fim:** sem vinheta.

## 6. Validação de áudio no AAC final (`testes_r10/validacao_audio_r10_*.json`)

| Versão | LUFS | Pico verdadeiro | Voz − resto no celular (pior / p5 / mediana) | Mono | Fim |
|---|---|---|---|---|---|
| A (V9) | −14,10 | −1,68 dBTP | −0,8 / 16,2 / 28,8 dB | −0,01 | −45,6 dBFS |
| B1 efeitos | −14,10 | −1,52 | −0,8 / 16,1 / 28,8 | −0,01 | −45,6 |
| B2 trilha | −14,11 | −1,52 | −0,9 / 13,6 / 25,7 | 0,00 | −45,6 |
| **B completo** | −14,11 | −1,56 | −0,9 / **13,4** / 25,7 | 0,00 | −45,6 |

- **Inteligibilidade:** a trilha reduz a margem da voz no celular de 16,2 para 13,4 dB (p5). A meta é ≥ 10 dB. Uma
  primeira versão da trilha, mais alta, dava 10,8 dB; abaixei a música e antecipei o abaixamento sob a fala.
- **Pico verdadeiro:** dentro da meta (≤ −1,5), mas com pouca margem.
  - **Causa:** o AAC redistribui a quantização quando o áudio muda. Os picos aparecem em instantes sem efeito novo, como
    85,9 s e 130,7 s.
  - **Opção:** teto do limitador de −2,0 dB **só nas versões novas** → −1,60 a −1,66 dBTP. Altera 3 % das amostras, em no
    máximo −34,7 dBFS.
  - **O que entreguei:** os arquivos usam o teto da V9 (−1,8), para o A/B mostrar só o que foi acrescentado.
- **Narração:** o MP3 original está intacto (`fdedd877…`) e os tempos das palavras não mudaram.

**Erros meus, corrigidos:**
1. **Validador de áudio:** a medida "voz − resto" lia sempre os stems da **primeira** mixagem, não os da versão validada.
   Corrigido (`STEMS_VOZ`, `STEMS_RESTO`). Refazendo a medida da V9 com os stems certos, o resultado é **idêntico** ao
   informado na rodada 9 (16,2 / 28,8 dB); nenhum número entregue estava errado.
2. **Stems da V9 cortados:** estavam gravados em PCM de 24 bits, que corta acima de 0 dBFS, e por isso não somavam a V9.
   Regenerei a mixagem V9 com stems em ponto flutuante, usando as câmeras da V8 com que ela foi feita (`CENAS_SOM`).
   O resultado é **idêntico à V9 aprovada, bit a bit**.

## 7. O que não mudou (preservação)

**Imagem:**
- roteiro, narração e duração (4.537 quadros, 30 fps, 151,233 s);
- modelo científico, personagem, interação com a caixa de leite e produtos;
- câmeras, legendas e rótulos;
- corte seco no A4 (4,87 s) e corte em 33,92 s;
- obturador do C2 e AO aprovados;
- encerramento sem vinheta;
- todos os quadros fora de A4 q34 e C4 126–178.

**Som:** todos os stems da V9.

**Versões anteriores:**
- V8, V9a e V9 intactas (hashes em `relatorios/versoes_preservadas_r9.json`).
- O `episodio02.py` e o `producao.json` mudaram; as versões anteriores estão nos commits da rodada 9.

**Episódio 01:** intacto.

## 8. Congelamento técnico

`relatorios/manifesto_congelamento_r10.json` registra:
- **Versões:** three.js 0.170.0, Node v22, FFmpeg 6.1.1, Chromium com SwiftShader.
- **Hashes:** do motor e dos scripts.
- **Configuração única:** MSAA 4×, AO 16, bloom 0,18, correção de cor, obturadores do C2 inteiro e do C4 126–178,
  JPEG q95, x264 CRF 17, AAC 192k.
- **Cenas:** o hash de cada uma das 44 cenas.
- **Correções localizadas**, **arquivos de áudio** e **critérios de validação**.
- **Licenças:** `relatorios/licencas_r10.md`.

O render definitivo confere o hash da cena, do motor e da consulta por plano, e não muda parâmetro no meio sem invalidar
os quadros afetados.

**Custo estimado em 1080:** 30 a 36 h no total.
- Episódio inteiro: cerca de 29 h, um processo por vez (≈ 4× o tempo de 540, medido nos testes).
- Obturador do C2: cerca de 3,6 h.
- Obturador do C4: cerca de 2 h.

## 9. Pendências reais e decisões para você

1. **Música:** usar a trilha (B ou B2) ou ficar sem trilha (A ou B1)? Se usar, "Rest Now" ou uma das alternativas da
   audição?
2. **Efeitos novos:** aprovar todos, ou retirar algum? As válvulas são uma representação.
3. **Pico verdadeiro:** manter o teto −1,8 (−1,52 a −1,56 dBTP) ou usar −2,0 nas versões novas (−1,60 a −1,66 dBTP)?
4. **C4:** manter o obturador em 126–178, como você autorizou, ou estender até 184 para eliminar a pequena troca em 178 → 179?
5. **Autorizar o render definitivo em 1080** com o manifesto acima.
6. **Licença da narração:** é a única pendência que impede a monetização. A voz ElevenLabs do plano gratuito é sem uso
   comercial.

## Licenças

- **Narração:** ElevenLabs, plano gratuito: **sem uso comercial**, atribuição obrigatória. Pendente.
- **Trilha:** Mixkit Stock Music Free License. YouTube e redes sociais permitidos, inclusive comercial. TV, rádio e
  DVD proibidos, assim como registrar a faixa em sistemas de direitos.
- **Efeitos:** Freesound CC0 e Mixkit, como nas rodadas anteriores.

**Nada publicado. Nenhuma voz gerada. Nenhum serviço contratado. Nenhuma licença comprada. Episódio 01 intacto. Render
1080 completo não iniciado.**
