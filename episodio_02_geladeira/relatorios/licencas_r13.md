# Ep. 02 · Licenças do som da rodada 13 (teste)

Este documento vale para a mixagem de teste R13 (`som/som_r13.py`). As licenças das rodadas anteriores continuam em `relatorios/licencas_r10.md`.

**Nada foi publicado.**

## Narração

- Plano gratuito da ElevenLabs: **sem uso comercial** e com atribuição obrigatória.
- O MP3 original continua intocado, assim como os tempos das palavras.
- Para monetizar, a voz precisa de uma licença compatível antes da publicação.

## Música

**"Spice Intrigue"**, de RomanSenykMusic, no Pixabay (item 334566), sob a **Pixabay Content License**.

O que a R13 faz com a faixa:
- estende 9 compassos, com duas emendas no tempo forte;
- automatiza o volume;
- abaixa a música na banda da voz durante a fala.

A licença permite modificar a faixa e usá-la em vídeo, inclusive comercial, sem atribuição. O que ela proíbe é redistribuir o arquivo isolado, por isso ele não está no git.

**Conferência pendente com você:** a página da faixa recusa acesso automático. Falta conferir a licença e o Content ID diretamente na página do Pixabay.

## Efeitos novos ou trocados nesta rodada

### Freesound, CC0 1.0

Domínio público: uso comercial livre e **sem atribuição**. A licença de cada som foi conferida na página dele; o registro está em `som/fontes_freesound.json`.

| Id | Título | Autor | Uso no episódio |
|---|---|---|---|
| 754422 | DSGNImpt_Deep Cinematic Impact 3_ZAZZ | zazz.sound.design | C2: impacto quando o circuito surge |
| 754424 | DSGNImpt_Deep Cinematic Impact 5_ZAZZ | zazz.sound.design | B2: impacto na pausa depois de "não fabrica frio." |
| 669468 | Low Click 1 | CJspellsfish | E3: pistão no fim da compressão (câmera lenta) |
| 453443 | hiss small pipe ext like propane gas | kyles | G3: expansão do líquido ao sair do capilar |
| 553257 | Water Pipe | NachtmahrTV | C3: fluido refrigerante circulando no tubo (discreto, abafado) |
| ~~876593~~ | relay1.wav | Mihacappy | **retirado na verificação da R13**: o clique de partida dizia que o compressor só liga no E2, e ele já funcionava |

### Mixkit, Sound Effects Free License

Licença conferida em https://mixkit.co/license/modal/sfxFree/ em 26/11/2026:
- uso em vídeos do YouTube, redes sociais e projetos comerciais e educacionais;
- **sem atribuição**;
- proibido redistribuir o item isolado ou registrá-lo em serviço de gestão de direitos.

Por isso os arquivos ficam em `som/bib/mixkit_sfx/`, fora do git. O registro está em `som/fontes_mixkit_sfx.json`, e `som/baixar_mixkit_sfx.py` baixa os arquivos de novo.

| Id | Título | Uso no episódio |
|---|---|---|
| 166 | Fast small sweep transition | transição C, aos 5,74 s: empurrão do rosto para o interior (corpo) |
| 175 | Short transition sweep | transição C (ar) |
| 1474 | Transition windy swoosh | C2: o pulso percorre o circuito · E1: a câmera desce com o vapor (o uso no B3 foi retirado na verificação: vinha 1,1 s depois do impacto) |
| 2615 | Mighty mysterious swoosh | C2: aproximação da revelação ("Escondido…") |
| ~~2608~~ | Air zoom vacuum | **retirado na verificação**: o whoosh C4 → D1 vinha 2 s antes do pop do rótulo "Evaporador" |
| 1489 | Air woosh | H1: a câmera se afasta até o circuito inteiro |
| 3005 | Explainer video pops whoosh light pop | apresentação dos 5 componentes, no primeiro quadro de cada rótulo |
| 2857 | Gear fast lock tap | E3: válvulas de descarga e de sucção (pré-clique cortado) |

### Mantidos das rodadas anteriores (Freesound CC0)

| Id | Uso |
|---|---|
| 682744 | porta abrindo |
| 489749 | porta fechando |
| 138052 | passos |
| 635547 | gorgolejo do evaporador |
| 455776 | zumbido do compressor, agora só onde o compressor aparece ou é citado |
| 706115 | mão no puxador |
| 616056 | caixa de leite |
| 624481 | prateleira de vidro e pouso da garrafa |

### Removidos

| Som | Situação |
|---|---|
| 329568, "Room Tone Apartment Small Bachelor" (tom de cômodo) | removido do episódio |
| 776443 (pop das apresentações) | substituído |
| Chiado do capilar sintetizado na V9 | substituído pela gravação real 453443 |

## Representações didáticas, declaradas

Estes sons não reproduzem um som real audível:

| Som | Por que é representação |
|---|---|
| **Pistão e válvulas no E3** | Um compressor real faz cerca de 50 ciclos por segundo, impossíveis de distinguir. Os golpes seguem a animação **em câmera lenta**. |
| **Pulso do C2** | Um sopro de ar que acompanha o pulso; o fluido não faz esse som. |
| **Fluxo no tubo do C3** | Real, porém muito mais baixo que o audível. |

O **chiado do capilar**, o **gorgolejo** e o **zumbido do compressor** são fenômenos audíveis de verdade numa geladeira.

## Referência de linguagem

O canal Desmontando o Mundo foi usado só como referência de intenção, a partir das diretrizes que você escreveu e dos títulos públicos do canal. Nada dele foi baixado, copiado ou usado.

Não analisei o áudio dos vídeos: a instalação do baixador foi bloqueada pela política de permissões desta sessão.
