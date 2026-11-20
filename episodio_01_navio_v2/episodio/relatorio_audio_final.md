# Ep. 01 · Finalização do sound design (som refinado + buzinas)

## Ajustes pontuais (última rodada)

Só o áudio foi remontado, pelo master de imagem existente. Nenhum 3D foi renderizado.

### 1. Buzina de abertura, recuo antes de "um navio" (6,46 s)

- O recuo agora **termina 30 ms antes** de "um", que começa em 6,46 s (o tempo vem de `palavras.json`). Ele usa uma rampa cossenoidal de 0,15 s, entre 6,28 e 6,43 s.
- O nível sob a fala passou de −8 para **−12 dB**, porque −8 dB ainda cobria a sílaba fraca "um".
- **Na pausa (6,05–6,25 s) a buzina é idêntica** à versão aprovada (diferença 0,0 dB).
- O timbre não mudou: mesma gravação, mesmos filtros e mesma perspectiva.
- Margem da voz no celular simulado, bloco de "um":
  - **5,1 → 7,3 dB**;
  - o teto possível é 9,0 dB, que é o valor desse bloco sem buzina nenhuma;
  - as sílabas seguintes subiram de 14–20 para 16–20 dB.

### 2. "navio," no estaleiro (≈17 s)

- **Correção do diagnóstico anterior:** atribuí o mascaramento ao guincho de içamento, mas a medição por camada mostra outra coisa.
  - Na banda da fala, o guincho, o motor do pórtico, as rodas e os cabos somam só −69 dB, contra a voz a −33 dB.
  - Quem cobria a palavra era uma **batida metálica que já existe na gravação da ambiência do galpão** (Mixkit 3074) em ~17,0 s.
- A automação suave foi aplicada nessa ambiência: −8 dB entre 16,86 e 17,16 s, com rampas cossenoidais de 0,12 s.
  - A batida desce até o nível do próprio galpão ao redor.
  - O galpão não para e não abre buraco.
- A automação no guincho chegou a ser aplicada, mas foi **retirada**: não tinha efeito mensurável, e um ajuste sem função não fica na mixagem.
- Os motores, o guincho, as rodas e os cabos seguem exatamente como aprovados.
- Margem da voz em "navio,":
  - blocos de 17,0 e 17,1 s: **−3,4 → 4,6 dB** e **−0,6 → 7,1 dB**;
  - o pior bloco do episódio passou de −3,4 para **+1,4 dB**.

### O que não mudou

- **Trechos alterados** (diferença > −100 dBFS contra a mixagem aprovada): 6,2–10,1 s e 16,7–19,8 s, este último incluindo a cauda de reverberação do galpão. Nada mais mudou.
- Buzina da conclusão, água, efeitos interativos, trilha, narração, legendas e imagem: **iguais**.
- Loudness −14,03 LUFS, mesmo ganho de master.


## Entregas

| Entrega | Arquivo |
|---|---|
| **Revisão completa com o áudio final** (168 s, 540 × 960, 30 fps) | `episodio/ep01_revisao_audio_final.mp4` |
| **Comparativo das buzinas A × B** (30 s) | `episodio/ep01_comparativo_buzinas.mp4` |
| **Ajustes pontuais, antes × depois** (16 s: buzina em ~6,46 s; "navio," em ~17 s) | `episodio/ep01_ajustes_pontuais_audio.mp4` |
| Validação dos ajustes pontuais | `som/validacao_ajustes_pontuais.json` |
| Mixagem final | `episodio/audio_ep01_refinado_buzina.wav` (48 kHz/24 bits, fora do git) |
| Mixagem A, sem buzina | `episodio/audio_ep01_refinado.wav` (fora do git) |
| 4 stems | `episodio/stems/ep01_{narracao,efeitos,ambiencias,musica}_refinado_buzina.wav` |
| Stems por grupo e por categoria (inclui a buzina isolada) | `stems/grupos/`, `stems/categorias/ep01_efeitos_buzina_refinado_buzina.wav` |
| Fontes, licenças e usos | `som/fontes_efeitos_refinado_buzina.md` / `.json` |
| Créditos | `som/creditos_descricao.txt` |
| Validação (números brutos) | `som/validacao_audio_final.json` |
| Medidas das buzinas | `som/medidas_buzina.json` |
| Medidas do comparativo | `som/comparativo_buzina_medidas.json` |

**Imagem:**
- Veio do master aprovado `ep01_master_imagem_sem_legendas.mp4`, com legendas queimadas pelo `trocar_audio.py`.
- Nenhuma cena 3D foi renderizada de novo, e nenhum dos 5.040 quadros foi refeito.
- A revisão anterior, `ep01_revisao_visual.mp4`, foi mantida para comparação, assim como `ep01_comparativo_buzina.mp4` da rodada anterior.

> ⚠️ **Não consigo escutar.** Tudo abaixo vem de medições e da análise dos sinais. Elas encontram erros como dessincronia, clipping, corte seco ou excesso, mas **não provam** que o som está bom ao ouvido. A escuta final é sua: de preferência no celular e em fones.

## 1. O que mudou

**Mixagem**
- A trilha antiga da `ep01_revisao_visual.mp4` foi trocada pela mixagem do `som_refinado.py`.
- Ela traz:
  - menos água;
  - motores, guinchos e cabos que seguem o movimento e param com ele;
  - pausas na solda;
  - contatos metálicos no quadro exato;
  - bolhas que acompanham a descida;
  - inundação progressiva;
  - perspectiva pela distância da câmera;
  - ducking moderado;
  - gravações reais com síntese discreta.
- A mixagem A (sem buzina) é **idêntica bit a bit** à da rodada de refinamento.

### Buzina de abertura (5,85 s)

| | |
|---|---|
| Fonte | gravação real CC0 de buzina de navio (abaixo), um toque montado só com ela: ataque real, sustentação breve e dissipação real com eco |
| Tom e filtro | 0,9× (~104 Hz, timbre grave de cargueiro); passa-alta em 80 Hz tira o vento do microfone |
| Momento | <ul><li>O ataque começa sob o fim de "gigante:" (a subida de pressão é baixa).</li><li>O som chega ao **nível pleno na pausa entre "gigante:" e "um navio"** (6,04–6,46 s), quando o navio aparece.</li></ul> |
| **Novo nesta rodada** | <ul><li>Quando a fala volta, a buzina **recua 12 dB** (rampa que termina antes de "um"; ver Ajustes pontuais) e segue baixa até se dissipar.</li><li>Não há bombeamento.</li><li>Antes, ela tirava margem de várias sílabas no celular simulado.</li></ul> |
| Duração e perspectiva | audível de 5,85 a ~9,8 s; volume e agudos seguem a distância real da câmera ao navio |

### Buzina de conclusão (166,25 s)

| | |
|---|---|
| Fonte e caráter | a **mesma gravação**, mais distante: passa-baixa de 2,5 kHz, mais reverberação e pico 3–4 dB abaixo da abertura |
| **Novo nesta rodada** | <ul><li>Antes ela nascia em 165,6 s, **sob** a palavra "navio.".</li><li>Agora entra **depois** do fim da última frase científica, em 166,25 s; "navio." termina em 166,12 s.</li></ul> |
| Duração e fim | toque curto (~1,6 s) que termina pelo **próprio corte real e eco**, inaudível em ~167,9 s, junto com a resolução da trilha |
| Como foi feito | o fade geral do encerramento é desfeito só no trecho da buzina, para não "afogá-la" artificialmente |

### A × B honestos
- A mixagem B usa o **mesmo ganho de master** da A (−0,915 dB), em vez de renormalizar.
- Novo parâmetro `master_fixo_db` em `som_ep01.mixar()`, ativado por `MASTER_DE=mix_refinado.json`.
- **Diferença B − A:**
  - fora das janelas das buzinas e do ajuste de 17 s, no máximo −117 dBFS (arredondamento numérico);
  - na narração, no máximo −124 dBFS;
  - dentro dessas janelas, até −29,5 dBFS (é a buzina).
- O comparativo não ajusta nenhum nível por versão.
- Nos trechos do comparativo, o loudness do mix é igual em A e B: −13,4 LUFS na abertura e −12,8 na conclusão. A buzina não muda o volume do resto.

## 2. Fontes e licenças

| Som | Origem | Licença | Atribuição |
|---|---|---|---|
| **Buzina (abertura e conclusão)** | "Cruise ship Albatros ship horn" — Tvabutzku1234, Wikimedia Commons, https://commons.wikimedia.org/wiki/File:Cruise_ship_Albatros_ship_horn.ogg | **CC0 (domínio público)**: uso comercial permitido | não exigida; registrada mesmo assim |
| Demais efeitos | 49 gravações Mixkit (Mixkit Sound Effects Free License: uso comercial e monetizado permitido) e 13 complementos sintéticos próprios | ver `som/fontes_efeitos_refinado_buzina.md` | não exigida |
| Trilha | composição sintetizada no projeto | própria | — |
| **Narração** | "Narração ep 1.mp3", voz *Will - Deep* (ElevenLabs, plano gratuito); SHA-256 `79e1e8f2…49ba0`, **inalterado** | **plano gratuito: uso não comercial, com atribuição** | "Voz: ElevenLabs" (em `creditos_descricao.txt`) |

Nenhuma fonte é CC BY-NC ou CC BY-SA, e não houve extração de vídeos.

> ⚠️ **Pendência de licença:** enquanto a narração vier do plano gratuito da ElevenLabs, o episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`). A buzina e os efeitos não têm essa restrição.

## 3. Validação

Os números brutos estão em `som/validacao_audio_final.json`.

| # | Item | Resultado |
|---|---|---|
| 1 | Duração | vídeo 168,000 s · áudio 168,000 s · 5.040 quadros · 540 × 960 |
| 2 | Integridade da imagem | <ul><li>PSNR médio 43,6 dB (mínimo 39,4) contra `ep01_revisao_visual.mp4`: mesmo master e mesmas legendas, só a recodificação difere.</li><li>0 quadros pretos, 0 trechos parados, 0 erros de decodificação.</li></ul> |
| 3 | Sincronia da narração | +3 ms, **constante** nas 21 janelas ao longo do episódio (igual às revisões anteriores) |
| 4 | Impactos e buzinas | <ul><li>13 impactos medidos no stem de efeitos: maior desvio 23 ms (comporta do dique); os outros entre 0 e 21 ms.</li><li>Buzina de abertura: início audível 5,85 s, pico na pausa (6,3 s), fim ~9,8 s.</li><li>Buzina de conclusão: início 166,25 s (depois de "navio." terminar em 166,12 s), pico 167,1 s, fim 167,9 s.</li></ul> |
| 5 | Clipping | <ul><li>WAV: pico de amostra −1,81 dBFS.</li><li>AAC: −1,99 dBFS.</li><li>0 amostras ≥ 0,999 nos dois.</li></ul> |
| 6 | Loudness (AAC final) | **−14,1 LUFS** integrado · LRA 2,3 LU |
| 7 | Pico verdadeiro (AAC final) | **−2,0 dBTP** (meta ≤ −1,5) |
| 8 | Clareza da voz (celular simulado: mono, 350 Hz–7 kHz) | <ul><li>Voz ≥ 10 dB acima do resto em 96,4 % dos 1.210 blocos de 100 ms com fala; mediana 22,8 dB.</li><li>Pior bloco: **+1,4 dB** (antes do ajuste em 17 s: −3,4).</li></ul> |
| 9 | Água | idêntica à versão refinada aprovada em todas as 8 seções (ex.: estaleiro sem água; carregamento −26,8 dB abaixo da voz) · `som/auditoria_agua_refinado_buzina.json` |
| 10 | Entradas e saídas | <ul><li>Buzinas: subida de ~14 dB em 100 ms no ataque real, queda gradual no fim.</li><li>Música: maior variação 7,5 dB em 100 ms.</li><li>Ambiências: os maiores saltos (14–18 dB em 100 ms, em 15,4 / 21,5 / 25,3 / 27,3 s) são **arrancadas de ações** do estaleiro, como cabos e guincho com a carga, e não trocas de cama; as camas usam fusões.</li></ul> |
| 11 | Mono | perda de 0,01 dB (−14,03 → −14,04 LUFS) · correlação L/R 0,988 · a buzina é mono na origem |
| 12 | Final | <ul><li>RMS no AAC: −34 dBFS (166,5 s) → −29 (167,0 s, buzina) → −39 (167,5 s) → −56 (167,75–168 s).</li><li>Últimos 20 ms em −139 dBFS: termina em silêncio, sem corte seco.</li></ul> |

### Pontos para a sua escuta

- **"um navio" (6,46 s) e "navio," (≈17 s):** corrigidos (ver Ajustes pontuais). Vale ouvir `ep01_ajustes_pontuais_audio.mp4`, que mostra antes e depois.
- **Altura das buzinas:**
  - Abertura no nível pleno só na pausa, −12 dB sob a fala.
  - Conclusão no fim, já sem voz.
  - Para mais ou menos presença: `BUZINA_DB` (abertura, conclusão).

## 4. Como refazer

```bash
cd episodio/som
python3 som_refinado.py                                                                          # A (sem buzina)
BUZINA=1 BUZINA_DB=-5,-19 SUFIXO_REFINADO=_buzina MASTER_DE=mix_refinado.json python3 som_refinado.py   # B (com buzinas)
cd ..
python3 som/comparar_buzina.py ep01_revisao_visual.mp4 ep01_comparativo_buzinas.mp4
python3 trocar_audio.py audio_ep01_refinado_buzina.wav ep01_revisao_audio_final.mp4             # ~60 s
python3 som/validar_audio_final.py ep01_revisao_audio_final.mp4 ep01_revisao_visual.mp4
```

## 5. O que não foi feito

- A imagem aprovada não foi alterada.
- Nenhuma cena 3D foi renderizada.
- Nenhuma voz foi gerada.
- Roteiro, velocidade e legendas da narração continuam os mesmos.
- Nenhum serviço contratado.
- Nada publicado.
- O render definitivo em 1080 × 1920 não foi iniciado.
