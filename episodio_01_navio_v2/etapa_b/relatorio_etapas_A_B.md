# Episódio 01 (reformulação) — Etapas A e B

Canal **De Olho no Invisível** · “Como um navio de aço consegue flutuar?” · 9:16 · 1080×1920 · 30 fps

Este documento cobre só as Etapas A (auditoria) e B (nova direção visual e teste de voz).
Nenhum episódio completo foi produzido, nada foi publicado e os arquivos finais da v1 (`episodio_01_navio/entrega/`) não foram alterados.

---

## 0. Referência criativa — limitação de acesso

**Não consegui examinar o canal Desmontando o Mundo nem o vídeo sobre o processo criativo.**
A rede desta sessão bloqueia `www.youtube.com`. Mesmo liberando esse endereço, os vídeos vêm de servidores `*.googlevideo.com`, e o ambiente não aceita curingas.
A busca na web também não trouxe material sobre o canal.

Por isso, **nenhuma observação deste relatório é atribuída ao canal**. Os critérios usados (modelagem, composição vertical, luz, cenários, câmera, ritmo) são os da Seção 3 do briefing, aplicados com conhecimento geral de animação 3D explicativa.

**Para a próxima etapa:** envie 5 a 10 capturas de tela, ou trechos curtos em MP4, de vídeos que representem o nível desejado. Com o material dentro do repositório, consigo fazer a análise quadro a quadro que o briefing pede.

---

## ETAPA A — Auditoria crítica do Episódio 01 original

Base da análise: folha de contato do MP4 final, com uma amostra a cada 2 s (38 quadros), e o código-fonte em `episodio_01_navio/projeto/src`.

### A1. Modelagem — **reprovada**
- O casco vem de uma única função analítica. É liso e correto na hidrostática, mas não tem bulbo, leme, hélice, borda falsa, marcas de calado, âncoras nem detalhes de convés. O resultado parece um sólido de laboratório, não uma embarcação.
- A superestrutura é um empilhado de caixas sem janelas legíveis, sem asas do passadiço e sem chaminé caracterizada.
- Os contêineres são caixas lisas de cor chapada: sem corrugação, sem quinas e sem variação de material.
- O bloco de aço é um cubo azul-escuro que não parece aço (sem reflexo metálico nem chanfro).
- Não há figuras humanas nem objetos de escala, então o espectador não sente o tamanho do navio.

### A2. Iluminação — **reprovada**
- O WebGL roda por software (SwiftShader), com luz direcional e hemisférica. Não há iluminação global, oclusão de ambiente nem sombras suaves.
- O mapeamento ACES lavou as cores: a paleta saiu pastel e acinzentada.
- A água subaquática é um degradê plano, sem cáusticas, sem raios de luz e sem perda de contraste com a distância.
- Os materiais não se diferenciam: aço, pintura, água e plástico têm praticamente a mesma resposta à luz.

### A3. Cenários — **reprovados**
- Só existe oceano aberto e céu: não há porto, estaleiro, cais nem leito marinho com detalhes. A história não tem lugar.
- O "corte de diorama" do oceano é uma faixa marrom genérica, sem estratos, rochas ou vida.

### A4. Animação — **parcialmente aprovada (física) / reprovada (encenação)**
- A física é coerente: equilíbrio com setas iguais, calado crescendo com a carga e alagamento progressivo. **Isso é reaproveitável.**
- Os contêineres caem do céu sem guindaste (48–53 s). É exatamente o item "contêineres surgindo instantaneamente" que o briefing proíbe.
- Não há movimento secundário (cabos balançando, espuma, marolas no casco, partículas no ar) nem antecipação ou acomodação. Os movimentos são de curva matemática.
- O alagamento é mostrado como caixas azuis subindo: correto, mas sem drama nem leitura física (sem jato d'água nem rombo).

### A5. Câmera — **reprovada**
- **De 28,5 s a 54,5 s, 14 amostras seguidas (cerca de 35% do vídeo) usam quase o mesmo enquadramento lateral, rente à linha d'água, com o casco na diagonal.**
- Não há plano geral de escala, close-up de mecanismo, plano subaquático de baixo para cima nem plano aéreo.
- As trocas de cena são mergulhos na cor da marca. Funcionam, mas se repetem e não são motivadas pela ação.

### A6. Edição e informação na tela — **reprovada**
- Há até três camadas de texto ao mesmo tempo: cartão no topo, rótulos ancorados e legenda karaokê. Isso compete com a imagem e cobre o casco (36–56 s).
- As setas são planas, coladas na imagem, e não objetos do mundo 3D.
- O ritmo é linear: cada frase tem uma cena e não há momento de respiro ou de virada ("Parece impossível").

### A7. Narração — **reprovada**
- Usa Kokoro 82M (q8, voz `pm_alex`, velocidade 0,9). A voz é sintética e plana, e cada frase foi sintetizada isoladamente, o que quebra a entonação entre frases.
- As perguntas não sobem no final, e não há ênfase nas descobertas.
- Houve erro de pronúncia em "De Olho" (corrigido por fonema, mas mostra a fragilidade do motor).

### A8. Limitações técnicas identificadas
| Limitação | Efeito na v1 | Situação agora |
|---|---|---|
| Sem GPU (4 núcleos de CPU, 15 GB) | WebGL por software, cerca de 2,8 s por quadro com qualidade baixa | Continua. Agora uso o Cycles (CPU) com qualidade alta, mas cada quadro custa minutos (ver B5) |
| Blender ausente | Toda a cena foi feita em Three.js | **Resolvido:** Blender 5.1 instalado como módulo Python (`pip install bpy`) |
| YouTube bloqueado | — | A referência não pôde ser analisada (seção 0) |
| HuggingFace bloqueado | Modelos de voz e ASR obtidos via npm | Irrelevante para a ElevenLabs |
| ElevenLabs | — | Host liberado no ambiente; **a chave de API não foi fornecida** (B4) |

### A9. O que reaproveitar (funciona e está validado)
1. **Forma do casco e hidrostática** (`meia_boca`, `volume_ate`; V(8 m) ≈ 38.689 m³), já portadas para o Blender (`navio.py`).
2. **Simulação física** do calado (carga e alagamento) de `fisica.js`, para dirigir a animação na Etapa C.
3. **Pipeline de finalização:** render em segmentos retomáveis, montagem FFmpeg, loudness −14 LUFS, validador (`validar.py`: quadros pretos ou congelados, sincronia, WER), alinhamento palavra a palavra das legendas e SRT.
4. **Efeitos sonoros e trilha originais** (`gerar_audio.py`): a síntese e o ducking servem de base. A estética precisa ser refeita junto com a nova montagem.
5. **Checklist científico** (forças iguais em repouso, mais carga dá mais calado, pouca água não afunda).

### A10. O que precisa ser reconstruído
Modelagem, materiais, iluminação, cenários, câmera, encenação das ações (guindastes e içamento), design de informação (menos texto, setas 3D), transições, narração (nova voz e novo roteiro) e assinatura com o mascote oficial.

### Recomendações por prioridade
1. **(Crítica) Trocar o motor de render** para Blender/Cycles, com materiais físicos, céu e luz controlados e água com volume. *Feito na Etapa B.*
2. **(Crítica) Dar lugar à história:** estaleiro, cais e porto, com objetos de escala. *Feito nos quadros 1, 2 e 5.*
3. **(Crítica) Encenar as ações com causas visíveis:** guindaste iça bloco e contêiner, solda, lançamento. Nada surge do nada.
4. **(Alta) Plano de câmera por frase,** com variedade de escala (geral, médio, detalhe, subaquático, aéreo) e cortes motivados.
5. **(Alta) Reduzir o texto na tela** para no máximo um rótulo curto por vez, além da legenda. As setas passam a ser objetos 3D.
6. **(Alta) Narração humana ou neural de alta qualidade,** gerada por blocos de parágrafo, não frase a frase.
7. **(Média) Movimento secundário:** cabos, espuma, partículas, cardumes e fumaça da chaminé.
8. **(Média) Assinatura** com a imagem oficial do mascote. *Feito (quadro 6).*

---

## ETAPA B — Nova direção visual e teste de voz

### B1. Proposta de direção de arte: "diorama industrial cinematográfico"
- **Mundo coerente:** a história inteira acontece num mesmo lugar, um estaleiro à beira-mar ao lado de um terminal de contêineres. O bloco cai do mesmo cais onde o navio é montado. As chapas do quadro 1 viram o casco do quadro 2. O pórtico amarelo aparece desde o primeiro quadro.
- **Cortes de diorama** só quando explicam algo invisível: a água e o leito também são seccionados, mostrando estratos de areia, cáusticas e o volume da água.
- **Modelagem low-poly trabalhada:**
  - silhuetas reais de navio (bulbo, borda falsa, superestrutura com janelas, chaminé com faixa amarela, baleeira laranja, leme, hélice);
  - chanfros em quase todas as arestas, para que a luz desenhe as formas;
  - cavernas, longarinas, duplo fundo e anteparas na estrutura;
  - contêineres com corrugação e pontes de peação abertas.
- **Materiais distintos:** aço nu escovado e metálico; pinturas com variação de tom e rugosidade; primer vermelho-óxido e cinza de estaleiro; concreto com juntas e limo; areia com ondulações; água refrativa com volume e absorção; borracha das defensas; vidro escuro.
- **Luz:** sol físico com sombras suaves e céu em degradê com direção de arte, mais iluminação global do Cycles (oclusão e rebatimento). A transformação de cor *Khronos PBR Neutral* preserva os matizes da marca, o que o AgX e o ACES não faziam.
  - Paletas por ambiente: estaleiro em fim de tarde quente, porto em luz diurna e mar subaquático turquesa com raios de luz.
- **Cor de marca:** o amarelo `#F3B544` é a cor dos equipamentos (pórticos, portêineres, faixas do cais). O azul `#202B57` aparece na chaminé e na assinatura, e o branco quente `#F6F4EC` nas faces de corte e na superestrutura. A marca fica presente sem engessar os cenários.
- **Informação:**
  - as setas são objetos 3D do mundo, com comprimento físico (pressão proporcional à profundidade);
  - no máximo um rótulo curto por vez;
  - as legendas ficam na faixa segura (y ≈ 1150–1400 px), longe dos objetos principais.

### B2. Os cinco quadros de referência (renderizados pelo motor real, 1080×1920)
Arquivos em `etapa_b/quadros/`, gerados por `blender/quadros.py` (todos determinísticos e reproduzíveis):

| # | Quadro | O que demonstra |
|---|---|---|
| 1 | Bloco de aço afundando junto ao cais | Plano meio dentro, meio fora d'água; aço escovado; bolhas; cáusticas e raios de luz; muralha do cais com limo e defensas; pórtico do estaleiro ao fundo, ligando a cena à construção |
| 2 | Estaleiro com casco em construção | Popa já chapeada em primer; proa em cavernas e longarinas sobre o duplo fundo já montado; pórtico içando um bloco de costado; solda; andaimes; blocos pré-fabricados; operários para dar escala |
| 3 | Corte interno do navio | Seção a meia-nau com duplo fundo e tanques laterais em células, porão com contêineres, antepara e carga no convés. A água e o leito são cortados no mesmo plano. A face de corte muda de tom abaixo da linha d'água, que fica marcada: o calado se lê na própria seção |
| 4 | Vista subaquática do empuxo | Casco visto de baixo; setas de pressão normais ao casco crescendo com a profundidade (as horizontais se anulam, as do fundo empurram para cima) e a resultante em amarelo; cardumes e raios de luz |
| 5 | Portêiner carregando contêineres | Plano de drone sobre o vão entre cais e navio; contêiner suspenso no spreader; baías de vante ainda vazias (o carregamento está em curso); amarras; cabeços e defensas. *As marcas de calado e o disco de Plimsoll estão modelados no costado, mas neste ângulo de raspão não ficam legíveis. Proponho um close-up próprio no animatic.* |
| 6 | Assinatura (extra) | Imagem oficial do mascote, recortada no próprio círculo, com título, slogan e @. Substitui o olho genérico |

Comparação lado a lado com os quadros equivalentes da v1: `etapa_b/comparacao_v1_v2.jpg`.

### B3. Relatório de melhorias visuais (v1 → v2)
| Critério | v1 rejeitada | v2 proposta |
|---|---|---|
| Motor | Three.js por software, sem iluminação global | Blender 5.1 · Cycles com rastreamento de caminhos e redução de ruído OIDN |
| Escala | Sem referência | Operários, cabeços, defensas, contêineres e guindastes |
| Cenário | Mar vazio | Cais, estaleiro, terminal portuário e leito marinho |
| Água | Superfície e degradê | Refração, absorção volumétrica, cáusticas, raios de luz e bolhas |
| Aço | Cor chapada | Metálico, escovado e chanfrado, com primer distinto da pintura |
| Navio | Sólido liso | Bulbo, leme, hélice, superestrutura detalhada, chaminé, baleeira e pontes de peação abertas; marcas de calado e Plimsoll modelados |
| Carga | Cai do céu | Içada pelo portêiner com spreader e cabos |
| Física na imagem | Setas 2D | Setas 3D de pressão com comprimento proporcional a ρ·g·h, mais a resultante |
| Texto | Até 3 camadas | A imagem explica e o texto só complementa |
| Assinatura | Olho genérico | Mascote oficial |

### B4. Teste de voz — **não realizado (credencial não fornecida)**
- **Configuração preparada:**
  - voz Will - Deep, `CstacWqMhJQlnfLPxRG4`;
  - modelo `eleven_multilingual_v2`;
  - stability 0,50, similarity 0,75, style 0, speed 1,0, speaker boost ativo;
  - saída MP3 44,1 kHz a 192 kb/s.
- **Ambiente:** criei o ambiente pessoal "videos" com `api.elevenlabs.io` e `elevenlabs.io` liberados. Ao pedir a chave de API pelo formulário seguro, você optou por não fornecê-la. Respeitei isso: não gerei áudio e **não substituí a voz por outra**.
- **Pronto para rodar:** `voz/teste_voz.py`. Ele gera cerca de 17 s com um trecho aprovado ("Se eu jogar este bloco de aço na água…") mais a assinatura "De Olho no Invisível. O invisível ganha forma.". Também registra:
  - o plano da conta e os caracteres consumidos (antes e depois);
  - a categoria da voz, o *notice period* e se ela está liberada para o plano gratuito.

  A chave entra pela credencial do ambiente ou pela variável `ELEVENLABS_API_KEY`, nunca pelo código. O custo estimado é de 204 caracteres (créditos), mais o multiplicador da voz, se houver.
- **Verificado na documentação e na página pública oficial da ElevenLabs:**
  1. Will - Deep é uma voz da **Voice Library** (Professional Voice Clone compartilhado pela comunidade). A página a descreve como *"Narration voice for Brazilian children, with a friendly and warm touch… Ideal for audiobooks, children's stories, and educational content"*. **Atenção de direção:** ela foi pensada para o público infantil. Vale ouvir a amostra pensando no público do canal.
  2. **O plano gratuito não tem licença comercial.** Conteúdo gerado nele não pode ser usado comercialmente e exige atribuição "elevenlabs.io" no título. Todos os planos pagos incluem licença comercial, e o conteúdo gerado durante a assinatura paga pode ser usado comercialmente por tempo indeterminado (sujeito aos termos específicos do serviço). Recursos em Beta não podem ser usados comercialmente.
  3. Vozes da Voice Library podem: estar indisponíveis no plano gratuito ("This voice is not available for free users"); ter multiplicador de créditos; ter *notice period* de 30 dias a 2 anos, se o dono retirar a voz. O script lê esses campos da API antes de gerar o áudio.
  4. O `eleven_multilingual_v2` suporta português (`pt`).
- **Para destravar:** forneça a chave de API (de preferência de um plano pago, por causa da licença comercial) quando eu pedir de novo, ou cadastre-a nas configurações do ambiente "videos" como segredo de rede para `api.elevenlabs.io`, no cabeçalho `xi-api-key`.

### B5. Limitações técnicas restantes (com números)
- **Custo de render:** sem GPU, o Cycles em 4 núcleos levou de **3,2 a 18,6 min por quadro** em 1080×1920 (160 amostras com redução de ruído OIDN; média de 10,9 min). Os quadros com água volumétrica (1 e 4) são os mais caros.
  - Um episódio de 90 s tem cerca de 2.700 quadros. **No mesmo nível de qualidade, levaria cerca de 490 horas (cerca de 20 dias) neste ambiente. Mesmo com 32 amostras, seriam cerca de 100 h, o que não é viável.**
  - Testei o EEVEE com Mesa por software: 58 s numa cena trivial, contra 6 s do Cycles na mesma cena. Sem GPU, o EEVEE não é alternativa.
  - **Opções para a Etapa C:**
    - (a) usar um computador com GPU NVIDIA ou Apple Silicon para renderizar os mesmos arquivos (`.py`, deterministas): o Cycles na GPU fica 10 a 30 vezes mais rápido;
    - (b) usar o EEVEE (rasterização do Blender), que exige GPU ou EGL;
    - (c) reduzir para 24–48 amostras com redução de ruído e renderizar a 720×1280 com ampliação, o que perde nitidez.

  Recomendo (a). O animatic de 10–15 s da Etapa C (300–450 quadros) cabe neste ambiente em qualidade de prévia.
- O mascote existe só como imagem 2D. Não há modelo 3D fiel, então ele aparece apenas na assinatura, como o briefing permite.
- Os quadros são estáticos por definição. O movimento (cabos, água, partículas) será validado no animatic.
- A referência Desmontando o Mundo não foi analisada (seção 0).

### B6. Recomendações para a Etapa C (após sua aprovação)
1. **Animatic de 12 s:** bloco cai do cais e afunda (plano 1), *match cut* das chapas para o estaleiro (plano 2) e o pórtico desce o bloco de costado no lugar (plano 3).
2. Animação dirigida por simulação: a física de `fisica.js` portada e o içamento com pêndulo amortecido no cabo.
3. Mergulho da câmera pela superfície da água como transição motivada entre os planos 4 e 5.
4. Legendas e rótulos refeitos com no máximo uma informação por vez, na área segura.
5. Gerar a narração aprovada por parágrafos (prosódia contínua) e alinhar as legendas com o mesmo `alinhar_legendas.py`.

**Aguardo sua aprovação explícita da nova direção visual e da voz antes de avançar para a Etapa C.**
