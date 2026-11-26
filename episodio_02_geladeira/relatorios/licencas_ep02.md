# Ep. 02 · Registro de arquivos e licenças (mixagem da rodada 5)

**Nada publicado.** Gerado de `som/usos_ep02.json` e `som/fontes_freesound.json`.

## Narração

- `voz/ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3`: SHA-256 `fdedd87772aee9d4dac5d0193db3b9e1ef97c4b699c8ce01b0c8de7ae05726ee`. Arquivo **intocado**: a mixagem lê uma cópia decodificada.
- **Licença PENDENTE.** O plano da ElevenLabs não foi confirmado. Até lá vale o tratamento do plano gratuito: **sem uso comercial**,
  atribuição obrigatória. Nada foi gerado nem gasto nesta rodada.

## Gravações (Freesound, todas CC0 1.0)

CC0 = domínio público: uso comercial permitido e atribuição dispensada. Mesmo assim, os créditos ficam registrados aqui por
procedência. A licença de cada som foi **conferida na página do som** no momento do download. O arquivo usado é a prévia HQ
(MP3 128 kb/s) que o próprio Freesound serve. A pasta `som/bib/` fica fora do git: os arquivos são de terceiros e podem ser
baixados de novo pelo id.

| id | Título | Autor | Licença | Uso na mixagem | Página |
|---|---|---|---|---|---|
| 329568 | Room Tone Apartment Small Bachelor | leonelmail | CC0 1.0 | ambiência da cozinha (tom do cômodo) | https://freesound.org/people/leonelmail/sounds/329568/ |
| 455776 | fridge compressor soft rumbly bubbly close.flac | kyles | CC0 1.0 | zumbido do compressor (ligado); zumbido em câmera lenta (E3) | https://freesound.org/people/kyles/sounds/455776/ |
| 682744 | Refrigerator door open; short.WAV | thomasanthony321 | CC0 1.0 | porta abrindo (A1) — vedação descola no início do giro; porta abrindo (I1) — vedação descola no início do giro | https://freesound.org/people/thomasanthony321/sounds/682744/ |
| 489749 | fridge_door_close 01.wav | ShadowSilhouette | CC0 1.0 | porta fechando (C1) — batida no instante em que o ângulo chega a zero | https://freesound.org/people/ShadowSilhouette/sounds/489749/ |
| 138052 | walking_footsteps_tennis _shoes_tile_floor_2.wav | daboy291 | CC0 1.0 | passo — entrada (I1); passo — recuo (I1); passo — recuo fora de quadro (A3) | https://freesound.org/people/daboy291/sounds/138052/ |
| 635547 | fridge freezer standing internal gurgle noise.flac | kyles | CC0 1.0 | gorgolejo do fluido evaporando (planos do evaporador) | https://freesound.org/people/kyles/sounds/635547/ |

## Síntese (gerada aqui, sem terceiros)

- chiado da expansão no capilar (G3) — SÍNTESE: chiado sintetizado (ruído filtrado) (5.63 s, ruído filtrado 2,5–7 kHz, semente fixa 2026)

## Não usados

- **Mixkit:** nenhum arquivo (a busca deu erro 429, limite de acesso). **Wikimedia Commons:** nenhum arquivo (429).
- **Música:** nenhuma. Nenhum som do YouTube, nenhuma licença CC BY-NC ou CC BY-SA.
- **Reverb da cozinha:** resposta ao impulso **sintetizada** pelo módulo de síntese do Ep. 01 (`sintese.py`, lido sem
  alteração; o ambiente "cozinha" é acrescentado em tempo de execução).

## Honestidade sobre os sons

- O zumbido é de **um** compressor de geladeira real (gravação CC0), não do modelo mostrado. O som não é apresentado como
  gravação do equipamento do episódio.
- O chiado do capilar é **síntese** (não havia gravação real adequada entre os candidatos) e fica discreto (−24 dB no evento).
