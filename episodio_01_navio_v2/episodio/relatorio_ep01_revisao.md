# Episódio 01 · Primeira versão completa de revisão

**"Como um navio de aço consegue flutuar?"**

| Item | Valor |
|---|---|
| Arquivo | `episodio/ep01_revisao.mp4` |
| Formato | 1080×1920 (render a 540×960, ampliado), 30 fps, H.264 + AAC 48 kHz |
| Duração | **171,0 s**, abaixo do limite de 180 s |
| Composição da duração | Narração de 170,34 s + 0,66 s de respiro final da assinatura. Sem abertura nem encerramento extras |

Status: versão de revisão, **não publicar**. A etiqueta "VERSÃO DE REVISÃO" está no canto do vídeo. A narração é a amostra de trabalho (Will - Deep); a versão comercial precisa da licença da ElevenLabs.

## 1. Narração

Ver `voz/narracao_ep01/validacao_narracao.md`.

- **Original:** preservado (somente leitura, SHA-256 conferido).
- **Duração:** 170,344 s.
- **Conteúdo:** as 384 palavras e as 49 frases estão presentes e na ordem certa. WER da transcrição automática: 2,3%.
- **Erro relevante:** nenhum. Seis pontos ficam para escuta humana (trechos em `voz/narracao_ep01/pontos_escuta/`). O principal é "ganha (a) forma" na assinatura.
- **Velocidade:** não alterada. A cópia de montagem foi apenas normalizada (−16 LUFS, 48 kHz).

## 2. Mapa de cenas (tempo real da fala)

Os cortes ficam nas pausas entre frases, com fusões de 0,2 s.

| Tempo (s) | Segmento | Fala | O que se vê |
|---|---|---|---|
| 0,00–4,40 | 01 Cais (animatic r2 aprovado) | "Este bloco… ele afunda." | Bloco empurrado do cais, câmera lenta na entrada na água, leito |
| 4,40–15,10 | 02 O gigante | "Mas olha este gigante… Como isso é possível?" | Câmera rente à água junto ao costado, subida revelando a carga, navio inteiro flutuando |
| 15,10–30,30 | 03 Estaleiro | "Vamos descobrir… O casco vai tomando forma." | Aérea; pórtico ergue a chapa (mesmo movimento aprovado e correção de colisão); encaixe em 23,6 s em "soldadas"; faíscas de solda; chapas chegam ao fundo, às laterais e à proa |
| 30,30–41,55 | 04 Não é bloco maciço | "E aqui está o primeiro detalhe… permanece seco." | Casco nos picadeiros; a proa se afasta (vista explodida, **"Corte ilustrativo"**); duplo fundo e tanques ("Compartimentos"); porão seco |
| 41,55–48,00 | 05 Entra na água | "Agora, o casco entra na água… e para. Por quê?" | Elevador de navios em diorama: o casco desce com a plataforma até o calado de equilíbrio (8,0 m) e **para**, enquanto a plataforma continua |
| 48,00–74,85 | 06/07 Pressão, empuxo, Arquimedes | "Repare… ele flutua." | Seção a meia-nau: setas de pressão perpendiculares, maiores com a profundidade; laterais se compensam; o empuxo surge; volume de água deslocada; a cópia desse volume é "pesada" ao lado; peso do navio igual e oposto |
| 74,85–83,85 | 08a O bloco | "Compare com o bloco… Por isso, afunda." | O bloco submerso em câmera lenta com peso e empuxo em escala (E/P = 0,13) e a pouca água que desloca |
| 83,85–94,55 | 08b O casco | "Já o casco… sustentar seu peso." | Cubo de aço maciço com o mesmo peso do navio (aresta de 17,2 m) afunda; o casco desloca água suficiente; empuxo = peso |
| 94,55–117,20 | 09 Carregamento | "Mas o navio ainda está vazio… um novo equilíbrio." | Porto; três portêineres pousam contêineres em 101,6 s, 102,95 s e 104,45 s ("o primeiro", "outro", "mais outro"); close da linha d'água nas marcas; time-lapse por lotes; barras de peso e empuxo |
| 117,20–123,65 | 10 Calado | "Essa profundidade… se chama calado." | Diorama a meia-nau: cota da quilha até a superfície |
| 123,65–134,00 | 11 Marcas | "E aquelas marcas… condições de navegação." | Escala de calado na proa ("Marcas de calado"); marca de linha de carga a meia-nau, com S, T, W, F e TF destacadas em sequência |
| 134,00–154,60 | 12 Avaria | "Agora imagine uma avaria… limitar os danos." | Corte longitudinal ilustrativo; rasgo e entrada de água; o porão enche até o nível de fora; o navio afunda mais e inclina (trim); hipótese grave em vermelho; divisórias estanques destacadas |
| 154,60–166,30 | 13 Conclusão | "No fim, o segredo… todo o peso do navio." | Navio carregado no fim de tarde; volume de água deslocada sob o casco; peso e empuxo |
| 166,20–171,00 | Assinatura | "De Olho no Invisível. O invisível ganha forma." | Mascote 2D oficial; título em 166,50 s; slogan em 168,20 s (a voz em 166,56 s e 168,28 s) |

## 3. Precisão científica (como foi garantida)

| Tema | O que foi feito |
|---|---|
| Hidrostática real do casco (`blender/hidro.py`) | Integração numérica da forma usada na modelagem. V(8,0 m) = 38.690 m³ (Δ = 39.657 t), confere com o projeto. Áreas de flutuação de 5.382–5.622 m². KB de 4,19–5,57 m |
| Empuxo = peso da água deslocada | Volume ciano = volume real abaixo da linha d'água. A cópia "pesada" tem o mesmo volume. Setas de empuxo e de peso iguais, opostas e na mesma vertical (B e G) |
| Pressão | Setas perpendiculares ao casco, comprimento ∝ profundidade (p = ρgh), nos três regimes (costado, bojo, fundo). As horizontais somem quando "se compensam"; sobra a resultante vertical |
| Bloco | Peso e empuxo na razão das densidades, 1.025/7.850 = 0,13. Física da queda (empuxo, massa adicional, arrasto) igual à do animatic |
| Mesmo peso, outra forma | Cubo de 17,2 m de aresta = 39.657 t de aço maciço, o mesmo peso do navio leve |
| Carregamento | 398 contêineres de 20 t (massa média adotada). Calado de 8,0 → 9,42 m. Cada lote de ~57 contêineres afunda ~0,2 m, o espaçamento dos algarismos da escala. A arfagem amortecida mostra o empuxo alcançando o peso ("até surgir um novo equilíbrio") |
| Calado | Cota da quilha até a superfície |
| Escala de calado | Algarismos de 10 cm a cada 20 cm, metros com "M" |
| Linha de carga | Tamanho real: anel de 300 mm, linha de 450 mm, linhas de 230 mm a 540 mm a vante. S no centro do disco (verão, 10,0 m); T e W a ±T/48; F e TF acima pela FWA calculada (0,22 m), para ré |
| Inundação | Método da perda de flutuabilidade com permeabilidade 0,9 e o porão x = 10–37 m. Novo calado a meia-nau 11,08 m (+1,66 m), trim de 0,92° pela proa, borda livre restante na proa de ~5 m. O navio **continua flutuando**; a hipótese grave aparece como hipótese e some, e as divisórias limitam a água a um compartimento |
| Representações ilustrativas | Os cortes estão rotulados ("Corte ilustrativo"). Os dioramas cortam a água para mostrar o que está abaixo da superfície |

## 4. Montagem e sincronização

{{VALIDACAO}}

- **Legendas:** geradas dos tempos reais de cada palavra, com blocos de até 26 caracteres. Não há legendas sobre a assinatura, que já mostra o texto.
- **Rótulos:** poucos, curtos, na identidade da marca, presos a pontos 3D e projetados quadro a quadro.
- **Música:** trilha **original**, sintetizada em `episodio/audio_ep01.py` (pads e arpejo em Ré maior), sem amostras de terceiros. Fica 7 dB abaixo durante a fala.
- **Efeitos:** sintetizados e sincronizados com os eventos das cenas. Os do plano 1 vêm do animatic r2 aprovado.

## 5. Problemas e limitações conhecidos

1. **Qualidade de revisão:** render a 540×960 com GTAO 4 e sem MSAA, ampliado para 1080×1920. Há serrilhado e menos detalhe que no final.
2. **Água:** é um efeito de shader, sem simulação de fluido. Não há espuma persistente nem esteira, e o impacto do cubo e o contato do casco com a água têm respingo discreto.
3. **Vistas submersas em mar aberto:** só funcionam em diorama (corte na água). Por isso os planos subaquáticos são todos "de aquário"; é uma escolha visual, mas vale a revisão artística.
4. **Segmento 03 (07 s, 24,8–28,4 s):** do lado oposto ao sol, a sombra do casco fica azulada no chão e lembra água.
5. **Segmento 09:** o plano "E mais outro" (103–104,5 s) fica carregado de estruturas do portêiner; e o salto de escala do portêiner para o close da linha d'água é brusco.
6. **Elevador de navios (05):** é um time-lapse (~2,5 m/s); um elevador real desce bem mais devagar.
7. **Câmera lenta:** os trechos 08a e 01 estão em câmera lenta, sinalizada pelo movimento das bolhas mas sem texto. Pode precisar de indicação.
8. **Continuidade:** a superestrutura aparece completa a partir do corte (04), mas no estaleiro (03) estava só começando. É um salto de tempo implícito.
9. **Massa média de 20 t por contêiner e calado de verão de 10,0 m:** são valores adotados, plausíveis, mas não de um navio real específico.

## 6. Pontos para revisão

**Artística**
- Ritmo do segmento 06/07 (27 s numa mesma seção).
- Escala dos rótulos.
- A cor vermelha da hipótese grave.
- A trilha original (volume e caráter).
- Os planos citados em 5.4 e 5.5.

**Científica**
- A massa média de contêiner adotada.
- O KG didático de 12,5 m usado para G.
- A representação da pressão só na seção (2D).
- A "cópia pesada" do volume deslocado como metáfora visual de Arquimedes.
- O shiplift como forma de entrada na água (é plausível e didático, mas lançamento lateral ou de popa também são comuns).

**Narração**
- Os seis trechos de escuta, principalmente "ganha (a) forma".

## 7. Custo computacional

| Perfil | Configuração | Por quadro | Quadros 3D | Tempo |
|---|---|---|---|---|
| Prévia | 270×480, sem AO, 10 fps | ~0,8 s | ~1.600 | ~22 min |
| Revisão (esta versão) | 540×960, GTAO 4, 30 fps | ~3 s | ~4.830 | ~4 h |
| **Final (estimativa)** | 1080×1920, GTAO 8, MSAA 4×, 30 fps | 8–12,6 s (medido no animatic) | ~4.830 | **≈ 11–17 h** sem GPU, mais ~5 min de montagem |

O plano 1 já existe em resolução final. A assinatura é capturada em segundos. Cada segmento é independente (`episodio/render_segmentos.sh final s09`), então correções pedem re-render só do trecho afetado. Com GPU, a estimativa cairia para a ordem de 1–2 h (estimativa, não medida).

## 8. Arquivos

- **Cenas (Blender → motor v2):**
  - `blender/ep01_cenas.py` (segmentos);
  - `blender/ep_base.py` (tempo global, trilhas de câmera, rótulos);
  - `blender/hidro.py` (hidrostática).
- **Motor:** `motores/tempo_real_v2/render2.js`, com âncoras animadas, objetos que surgem e oclusor de água para cortes.
- **Montagem e áudio:**
  - `episodio/montar_ep01.py`;
  - `episodio/audio_ep01.py`;
  - `episodio/validar_ep01.py`;
  - `episodio/render_segmentos.sh`.
- **Versões anteriores:** animatics v1 e r2, quadros aprovados e amostra de voz, todos preservados.
