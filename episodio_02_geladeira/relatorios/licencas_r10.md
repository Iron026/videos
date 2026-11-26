# Ep. 02 — Rodada 10: registro de licenças dos recursos novos

Os recursos das rodadas anteriores não mudaram. São CC0 do Freesound e Mixkit, registrados em `som/fontes_freesound.json` e
`som/usos_ep02_r9.json`.

## Trilha musical (experimental: versão B)

### Faixa usada: "Rest Now"

| Campo | Valor |
|---|---|
| Título | Rest Now |
| Autor | Eugenio Mininni |
| Fonte | Mixkit (Envato), página do gênero Ambient: https://mixkit.co/free-stock-music/ambient/ |
| Arquivo original | https://assets.mixkit.co/music/584/584.mp3 (MP3 256 kb/s, 44,1 kHz, 4 min 59,8 s) |
| Arquivo baixado | SHA-256 `8ce6e66238546dc29a273a6b50f4e3db6cdb4aab409f7cc366ec31646fcfa675` |
| Licença | **Mixkit Stock Music Free License** (https://mixkit.co/license/#musicFree) |
| Texto da licença | copiado em `relatorios/testes_r10/musicFree.html` em 24/11/2026 |
| Atribuição | não exigida |

**Permitido:** uso comercial e não comercial; YouTube; publicações em redes sociais; anúncios online; uso educacional;
copiar, modificar, distribuir e executar publicamente em qualquer plataforma web ou rede social.

**Não permitido:**
- CD, DVD, TV, rádio e videogames;
- remixar a faixa ou incorporá-la numa faixa só de música;
- reivindicar autoria;
- **registrar a faixa em qualquer serviço de gestão de direitos**, como o Content ID;
- redistribuir o arquivo isolado.

**Reclamações de direitos:** segundo o próprio Mixkit, se o vídeo receber uma reclamação, ela deve ser encaminhada a
team@mixkit.co. Uma reclamação automática de terceiros não é impossível; nesse caso, o procedimento é contestar e encaminhar
ao Mixkit.

**Uso no episódio:**
- faixa recortada a partir de 0,4 s;
- filtro passa-altas de 60 Hz;
- atenuação de cerca de 3 dB entre 0,9 e 3,2 kHz;
- automação de volume por trecho narrativo;
- abaixamento durante a fala;
- saída antes da última frase.

É **edição para sincronia num vídeo**, não remix nem faixa musical independente.

**Fora do git:** o arquivo isolado da música e a audição das candidatas não vão para o repositório, porque a licença proíbe
redistribuir o arquivo isolado. O registro acima permite baixar de novo e conferir o hash.

### Alternativas (mesma licença; só em `previas_r10/trilhas_candidatas_audicao.m4a`, fora do git)

| Ordem na audição | Faixa | Autor | Arquivo | Observação medida |
|---|---|---|---|---|
| 1 (0–25 s) | Rest Now (escolhida) | Eugenio Mininni | assets.mixkit.co/music/584/584.mp3 | percussão 6,8 %, graves 15 %, dinâmica 6,8 dB |
| 2 (26,5–51,5 s) | Staring at the Night Sky | Alejandro Magaña (A. M.) | …/music/168/168.mp3 | sem graves; 142 s (mais curta que o episódio) |
| 3 (53–78 s) | Xanthos | Eugenio Mininni | …/music/633/633.mp3 | "drone", graves 39 % (mais escura) |
| 4 (79,5–104,5 s) | Finding Myself | Michael Ramir C. | …/music/993/993.mp3 | sem graves; 134 s (mais curta) |

- **Seleção:** 391 faixas do catálogo (`testes_r10/musica_catalogo_mixkit.json`), filtradas por gênero e duração.
- **Medição:** 28 candidatas medidas (`testes_r10/musica_medidas_candidatas.json`) por percussão, graves, energia na
  faixa da voz e dinâmica.
- **Eu não escuto:** a escolha estética é sua.

**Fontes não usadas:**
- **Inacessíveis nesta sessão** (bloqueadas pela rede): Free Music Archive, ccMixter, Incompetech e OpenGameArt.
- **Pixabay Music:** respondeu 403.
- **YouTube:** nada foi tirado de lá.

## Efeitos novos (Freesound, CC0 1.0: domínio público, uso comercial livre, sem atribuição)

| Uso | Instante | Som | Autor | Página |
|---|---|---|---|---|
| mão fecha no puxador (A1, I1) | 0,20 s; 117,51 s | ObjectCatchHold.mp3 (1º evento, suavizado > 5 kHz) | RandomWizKid | https://freesound.org/people/RandomWizKid/sounds/706115/ |
| mão fecha na caixa de leite (I1) | 118,44 s | fa!rlife-MilkCarton-BlueTube-SM57.wav (evento em 1,795 s) | PeteHaase | https://freesound.org/people/PeteHaase/sounds/616056/ |
| caixa sai da prateleira de vidro (I1) | 118,62 s | Freezer - fridge floor - glass - take - put down - hit.wav ("take", 0,80 s) | ValentinPetiteau | https://freesound.org/people/ValentinPetiteau/sounds/624481/ |
| válvulas do compressor abrindo (E2, E3) | 13 instantes da cena | relay1.wav, filtrado < 2,2 kHz | Mihacappy | https://freesound.org/people/Mihacappy/sounds/876593/ |

- **Licença de cada som:** conferida na própria página (link CC0 1.0) por `som/buscar_freesound.py`. O arquivo usado é a
  prévia pública em MP3 do Freesound.
- **Válvulas:** são uma **representação**. O som é um clique de relé abafado, não uma gravação da válvula de um
  compressor, e está declarado assim no relatório.


## Rodada 11: trilha escolhida pelo usuário, "Secret Garden" (substitui "Rest Now")

| Campo | Valor |
|---|---|
| Título | Secret Garden |
| Autor | Eugenio Mininni |
| Fonte | Mixkit (Envato), gênero Film Score |
| Página | https://mixkit.co/free-stock-music/film-score/ (item 595) |
| Arquivo original | https://assets.mixkit.co/music/595/595.mp3 (MP3 256 kb/s, 44,1 kHz, 2 min 33 s) |
| Arquivo baixado | SHA-256 `fda04cb4597c1ffd80d14ce82a74f6938c657952647dc50889138cd3e4903034` |
| Licença | **Mixkit Stock Music Free License** (https://mixkit.co/license/#musicFree) |
| Publicação no Mixkit | 28/01/2020 |
| Atribuição | não exigida |

**Confirmação do usuário (24/11):** o arquivo enviado por você (`mixkit-secret-garden-595.mp3`) é **idêntico byte a byte** ao baixado (mesmo SHA-256 `fda04cb4…`, 153,05 s, 256 kb/s). A faixa usada é exatamente a que você escolheu.

**Como a licença foi conferida:**
- os metadados da listagem de Film Score (`relatorios/testes_r10/mixkit_film_score_listagem_secret_garden.html`) trazem
  `"copyrightNotice": "Mixkit Stock Music Free License"` e o link da licença;
- o texto da licença foi baixado de novo em 24/11 e é idêntico ao arquivado (`testes_r10/musicFree.html`);
- o Mixkit não tem página fixa para o item: o endereço `free-stock-music/secret-garden-595/` redireciona para a busca, que
  mostra o mesmo item 595.

**Permitido:** uso comercial; YouTube; redes sociais; anúncios online.

**Não permitido:** TV, rádio, CD, DVD e jogos; remixar a faixa ou incorporá-la numa faixa só de música; registrar em
sistemas de gestão de direitos (Content ID); redistribuir o arquivo isolado.

**Edição para sincronia (não é remix):**
- faixa deslocada em 1,5 s;
- filtro passa-altas de 80 Hz;
- cerca de −3 dB entre 0,9 e 3,2 kHz;
- volume ajustado por trecho do episódio, abaixando sob a fala;
- o final natural da música termina às 145,7 s.

**Fora do git:** o arquivo isolado da faixa fica fora do repositório.

"Rest Now" continua registrada acima, como referência histórica da versão experimental da rodada 10.

## Narração (restrição independente)

- **Origem:** ElevenLabs, plano gratuito: **sem uso comercial**, atribuição obrigatória.
- **Licença da voz:** pendente.
- **Consequência:** a licença comercial da música **não** libera o episódio para monetização enquanto a da narração não
  for resolvida.
- **Arquivo:** o MP3 original está intacto (`fdedd877…`).

**Nada publicado. Nenhum serviço contratado. Nenhuma licença comprada. Nenhuma voz gerada.**

## Rodada 11 (ajuste final): trilha "Spice Intrigue" (proposta, aguardando sua audição)

| Campo | Valor |
|---|---|
| Título | Spice Intrigue |
| Autor | RomanSenykMusic |
| Fonte | Pixabay Music, página https://pixabay.com/music/comedy-spice-intrigue-334566/ (categoria "comedy" no endereço) |
| Arquivo | o que você enviou: `romansenykmusic-spice-intrigue-334566.mp3`, SHA-256 `f31f497a…` (MP3 256 kb/s, 131,58 s) |
| Licença declarada | Pixabay Content License (https://pixabay.com/service/license-summary/) |
| Conferência da página | **não feita por mim:** o Pixabay bloqueia acesso automático (proteção Cloudflare). Não tentei contornar. |

**Pendente:** a confirmação da licença é sua. Confira na página da faixa:
1. a licença (Pixabay Content License);
2. se há aviso de **Content ID**. Algumas faixas do Pixabay são registradas pelos autores, e o vídeo pode receber
   reivindicação automática no YouTube mesmo com uso permitido.

**Termos gerais da Pixabay Content License** (a conferir no texto oficial):
- uso comercial permitido, sem atribuição obrigatória;
- não é permitido vender ou redistribuir o arquivo isolado sem modificação;
- não é permitido sugerir endosso do autor.

**Fora do git:** o arquivo isolado continua fora do repositório.

**Edição para sincronia (não é remix):**
- entra com o rosto às 4,87 s;
- filtro passa-altas de 60 Hz;
- volume ajustado por trecho do episódio, abaixando −8 dB sob a fala;
- termina naturalmente por volta de 128,8 s (a faixa tem 131,6 s). Os ~22 s finais ficam sem música.

**Preservadas:**
- Secret Garden (decisão da rodada 11) e Rest Now continuam registradas acima;
- as mixagens V9, V10 e Secret Garden **não foram alteradas**.
