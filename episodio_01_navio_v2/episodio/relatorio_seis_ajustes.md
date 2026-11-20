# Ep. 01 · Seis ajustes de áudio, narrativa e imagem

## Entregas

| # | Entrega | Arquivo |
|---|---|---|
| 1 | Comparativo visual da correção 2:20–2:34: avaria lado a lado + 6 detalhes ampliados (39 s) | `episodio/ep01_comparativo_artefatos_avaria.mp4` (detalhe em imagem: `ep01_artefatos_s12_detalhe.jpg`) |
| 2 | Comparativo do plano do dique, sem rótulo de calado (4 s) | `episodio/ep01_comparativo_calado_dique.mp4` |
| 3 | Comparativos sonoros dos quatro ajustes, antes × depois, mesma imagem e mesmo ganho de master (44 s) | `episodio/ep01_comparativo_audio_seis_ajustes.mp4` |
| 4 | **Nova revisão integral** (540 × 960, 30 fps, 168,000 s) | `episodio/ep01_revisao_seis_ajustes.mp4` |
| 5 | Este relatório e as validações | `som/validacao_seis_ajustes_audio.json`, `validacao_s12_quadros.json`, `som/validacao_audio_final.json` |

Foi preservada a revisão anterior (`ep01_revisao_audio_final.mp4`) e os quadros anteriores da avaria (`quadros_revisao_antes7/s12`). O master de imagem (`ep01_master_imagem_sem_legendas.mp4`) foi recomposto a partir dos quadros já renderizados. Só os 529 quadros da avaria foram renderizados de novo; nenhum outro segmento 3D.

> ⚠️ **Não consigo escutar nem assistir como você.** Os itens de áudio foram validados por medição: sincronia, níveis, bandas e trechos alterados. Os de imagem foram validados por quadros extraídos e métricas. Nada disso prova a qualidade percebida, então vale a sua conferência nos comparativos.

---

## Áudio

**Mudou só o que foi pedido.** Comparada com a mixagem aprovada, a nova difere apenas em:

| Trecho | Ajuste |
|---|---|
| 5,8–7,0 s | buzina inicial |
| 29,8–42,9 s | transição do estaleiro e caudas de reverberação |
| 130,4–133,6 s | linhas |
| 166,1–167,9 s | buzina final |

Fora desses trechos, a mixagem é **idêntica bit a bit**.

- Loudness −14,03 LUFS e ganho de master (−0,915 dB) iguais.
- A síntese aleatória do resto do episódio foi mantida idêntica de propósito: os sons novos usam gerador próprio.

### 1 · Buzina inicial mais presente (0:05–0:10)

| | Antes | Depois |
|---|---|---|
| Na pausa após "gigante:" (6,05–6,28 s) | −34,1 dBFS | **−32,1 dBFS (+2,0 dB)** |
| Pico momentâneo da buzina | −31,4 LUFS | −29,6 LUFS |
| Sob a fala (7,0–9,5 s) | −40,93 dBFS | **−40,93 dBFS (igual)** |
| Margem da voz em "um" (6,5 s), celular simulado | 7,3 dB | 7,3 dB (igual) |

- Só o trecho principal subiu.
- O recuo continua terminando antes de "um" (6,43 s). Ficou 2 dB mais fundo, para que o nível sob a narração não aumente.
- Timbre, perspectiva e dissipação são os mesmos: mesma gravação, filtros e posição.

### 2 · Fim do estaleiro na transição (0:30)

**O que estava ativo depois da fusão de imagem (29,85–30,75 s):**
- **Ambiente do galpão** (Mixkit 3074): era reinserido em 30,3 s e ia até ~35,5 s.
- **Guindastes distantes** (Mixkit 2504): de 30,3 a ~35,5 s.
- **"Zumbido do casco vazio"** (35–41,55 s): era a própria gravação de guindaste (2504), apenas filtrada.

**O que a imagem mostra:**
- O casco pronto sobre os picadeiros, ao ar livre, sem guindastes, sem galpão e sem obra.
- Depois, o corte ilustrativo e o porão vazio.

**Correção:**
- O galpão e os guindastes terminam **na própria fusão de imagem**, com o fade de ~1 s que já existia.
- Entra só um **vento discreto de ar livre** (Mixkit 1201, a mesma gravação de vento do episódio).
- No interior, um **ar parado abafado** (o mesmo vento, filtrado em 700 Hz e com reverberação interna) substitui o motor de guindaste.

**Sons preservados, todos ações visíveis:**
- proa se separando no corte (33,15 s);
- estrutura rangendo (33,25 s);
- células acendendo (37,0 e 39,2 s);
- estalo no porão (39,6 s).

**Medidas:**

| | Antes | Depois |
|---|---|---|
| Maior salto de ambiência em 100 ms (29–42 s) | 13,1 dB | **5,0 dB** |
| Ambiência 31–35 s | −40,9 dBFS | −43,5 dBFS |
| Ambiência 35,5–41,5 s | −46,4 dBFS | −56,4 dBFS |
| Voz ≥ 10 dB acima do resto (30–41 s) | 98,8 % | 100 % |

### 3 · Um brilho para cada linha (≈2:10)

- **Antes:** um único sopro sintético de 2,6 s para as cinco linhas.
- **Depois:** **cinco brilhos curtos**, um por linha (S, T, W, F, TF).
- **Sincronia:** cada brilho entra no **primeiro quadro em que a linha aparece**, medido nos quadros renderizados: 130,517 / 131,050 / 131,617 / 132,150 / 132,717 s. O som começa 0,5–1,4 ms depois de cada quadro.
- **Timbre**, em síntese original e não bipe:
  - um sopro curto de ar filtrado (2,5–7 kHz);
  - um "tilintar" vítreo inarmônico (parciais 1 / 2,32 / 3,9);
  - ataque suave de 8 ms e decaimento de ~0,1 s.
- **Variações** de afinação (2,29–2,66 kHz, levemente ascendente como as linhas), de nível (±0,75 dB) e de posição no estéreo.
- **Sem graves:** 0,0 % da energia abaixo de 500 Hz.
- **Nível:** 20–28 dB abaixo da narração (brilho −35,5 a −39,5 LUFS momentâneo; voz −10 a −17). A margem da voz no celular fica ≥ 13,9 dB em todos os blocos de 130–134 s.

### 4 · Buzina final imediata (≈2:46)

**Causa do atraso:** o início da buzina usava o trecho de 3,15 s da gravação, que é a **subida de pressão antes do toque**, cerca de 17 dB abaixo do toque. O som só ficava pleno ~0,8 s depois. O **toque real** da gravação começa em ~5,55 s e sobe ~15 dB em ~55 ms.

**Correção:**
- A buzina final passa a usar esse ataque real, a partir de 5,52 s da mesma gravação.
- Começa em 166,167 s.

| | Antes | Depois |
|---|---|---|
| Primeiro som após o fim de "navio." (166,12 s) | +140 ms (ainda baixo) | **+47 ms** |
| Nível a −6 dB do pico | +770 ms (166,89 s) | **+80 ms (166,20 s)** |
| Sobreposição com a voz | nenhuma | nenhuma (−148 dB antes de 166,12 s) |
| Pico momentâneo | — | −31,1 LUFS, 1,5 dB abaixo da abertura, com passa-baixa de 2,5 kHz (mais distante) |
| Fim | — | dissipação natural: −46 dBFS em 167,5 s, −61 dBFS em 167,75–168 s, silêncio no último quadro |

A narração e a duração (168,000 s) não mudaram.

---

## Imagem e narrativa visual

### 5 · O "calado" aos 0:40 (dique, 0:44–0:48)

**O que é:**
- No plano do dique, a proa mostra a **escala de marcas de calado** (números 2-4-6-8 M). Isso é correto: navios reais têm essa escala pintada.
- Em 47,05–48,0 s havia o rótulo **"Calado: 8 m"**. Esse rótulo é, sim, a apresentação do conceito de calado.
- A narração nesse momento diz *"Ele afunda um pouco... e para. Por quê?"*. Ela só apresenta o calado em ~117 s (*"Essa profundidade… se chama calado"*), na sequência de carregamento.

**Decisão:**
- **Retirado o rótulo "Calado: 8 m"** do dique, no código da cena (`blender/ep01_cenas.py`) e nos dados de rótulos.
- As marcas pintadas continuam: são o que permite ver que a linha d'água **parou** no casco ("e para").
- O conceito de calado fica inteiro para a sequência de carregamento, que já mostra "Marcas de calado" e a explicação. Assim não há apresentação dupla.
- Os rótulos "Corte ilustrativo", "Picadeiros" e "Começa a flutuar" continuam.
- O rótulo é desenhado na composição, então **nada foi renderizado** para isso.

Antes, aos 37–41 s, a cena mostra o corte do casco ("Compartimentos", "Ar: espaço interno seco"). Esses elementos são estruturais e não foram alterados.

### 6 · Artefatos da avaria (2:20–2:34)

**Investigação, sem presumir a causa.** O mesmo quadro (146,0 s e 152,0 s) foi renderizado em 12 variantes.

- **Passes:**
  - atual;
  - sem oclusão ambiente;
  - sem MSAA;
  - sem bloom;
  - configuração antiga (AO 4, sem MSAA, sem bloom);
  - sem nenhum passe.
- **Objetos:**
  - sem água do alagamento;
  - sem jato;
  - sem fantasmas;
  - **sem a água do mar**;
  - sem sombras;
  - sem oclusor.

**Resultados:**
- **O padrão de pontos aparece em todas as variantes de passes**, inclusive sem AO, MSAA, bloom e correção de cor. Os passes novos da revisão de beleza **não** são a causa.
  - Os quadros anteriores a essa revisão (`quadros_revisao_antes6`) já tinham o defeito.
- **Só some ao ocultar a água do mar.**

**Causa:**
- No corte ilustrativo, o mar também é cortado, e tem uma face lateral **no mesmo plano do corte do navio**.
- Para o mar não aparecer dentro do navio, um **oclusor** (só profundidade) é desenhado nesse mesmo plano.
- Duas superfícies coplanares, comparadas por uma textura de profundidade com precisão limitada, criam um **conflito de profundidade (z-fighting)**: em cada pixel, a água do mar aparece ou não quase ao acaso.
- O resultado eram grades de pontos e uma faixa vertical clara (os "feixes de luz" do mar) sobre a parede do porão, a antepara, o costado e a borda da água do alagamento.

**Correção** (`motores/tempo_real_v2/render2.js`):
- O oclusor é desenhado **0,6 % mais perto da câmera**, ao longo do próprio raio de visão: a posição na tela não muda, só a profundidade.
- A folga cresce com a distância, como a imprecisão.
- Nada mais foi alterado: materiais, luz, AO, bloom, cor, física, linha d'água, estrutura do porão, enquadramentos e rótulos são os mesmos.

**Re-render:** os 529 quadros do segmento da avaria (137,0–154,6 s), porque o defeito estava presente em todo ele.
- Num dos três lotes paralelos, o renderizador por software produziu, só em 146,2–147,8 s, janelas da superestrutura erradas.
- Testes isolados mostraram que **não** era efeito da correção: o quadro sozinho, com ou sem correção, reproduz as janelas certas.
- Esses 61 quadros (270–330) foram renderizados de novo num processo próprio e conferidos.

**Verificação quadro a quadro dos 529 quadros** (`validacao_s12_quadros.json`):

| | Antes | Depois |
|---|---|---|
| Quadros com mais pontos isolados que antes | — | **0** |
| Quadros com menos pontos | — | 300 |
| Cintilação temporal média | 3,30 | **3,11** |
| Cintilação, percentil 99 | 51,0 | 50,7 |

- Maior diferença média por quadro: 0,89 nível de 255, só nas regiões em que o mar vazava.
- Os detalhes ampliados no comparativo mostram a parede, a antepara, o costado e o compartimento antes × depois.

**Master recomposto:** comparado com o anterior, os quadros-fonte só mudaram em 47,1–48,0 s (rótulo) e 137,0–154,6 s (avaria). Nos trechos vizinhos, a diferença é só de compressão (PSNR ≥ 47 dB).

**Fora do pedido, para sua decisão:**
- O mesmo oclusor existe no experimento casco × bloco (s08b, 83,85–94,55 s).
- Ali o efeito é bem mais fraco: um leve véu azulado do mar no fundo duplo, em ~87–90 s.
- Como esse trecho não foi indicado, **não foi re-renderizado**. Com a correção já feita, isso leva cerca de 15 minutos, se quiser.

---

## Validação técnica da revisão integral

| Item | Resultado |
|---|---|
| Duração | 168,000 s · 5.040 quadros · 540 × 960 · 30 fps |
| Integridade | 0 quadros pretos, 0 trechos parados, 0 erros de decodificação |
| Sincronia da narração | +3 ms, constante (21 janelas) |
| Impactos | maior desvio 23 ms (inalterados) |
| Loudness (AAC final) | −14,1 LUFS · LRA 2,3 LU |
| Pico verdadeiro (AAC final) | −2,0 dBTP · nenhuma amostra saturada |
| Clareza da voz (celular simulado) | 96,6 % dos blocos com voz ≥ 10 dB acima do resto (antes 96,4 %) · pior bloco +1,4 dB |
| Mono | perda 0,01 dB · correlação L/R 0,988 |
| Água | inalterada (`som/auditoria_agua_refinado_buzina.json`) |
| Final | silêncio no último quadro, sem corte seco |

## Licenças

- **Sem fontes novas.** O vento é a gravação Mixkit 1201, já usada no episódio, e os brilhos são síntese própria. O registro foi regenerado em `som/fontes_efeitos_refinado_buzina.md`, e os créditos não mudaram.
- **Narração:** "Narração ep 1.mp3" original, sem alteração. Plano gratuito da ElevenLabs, portanto **sem licença para exploração comercial** (`voz/LICENCA_NARRACAO.md`).

## O que não foi feito

- Narração, roteiro, legendas, física e duração não foram alterados.
- Nenhuma renderização completa.
- Nada publicado.
- O render definitivo em 1080 × 1920 não foi iniciado.
