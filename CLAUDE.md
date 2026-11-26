# De Olho no Invisível — manual de trabalho

Este arquivo é lido no início de toda sessão neste repositório. Ele reúne o que foi
aprendido na produção do Ep. 01 ("Como um navio de aço consegue flutuar?").
Detalhes técnicos, números e histórico: `episodio_01_navio_v2/APRENDIZADOS_EP01.md`.
Arquivos-chave (em `episodio_01_navio_v2/`): `episodio/decupagem_ep01_v3.md` (decupagem de referência),
`episodio/registro_final_ep01.md` e `episodio/relatorio_render_definitivo.md` (definitivo),
`voz/narracao_ep01/trabalho/palavras.json` (tempos das palavras), `motores/tempo_real_v2/render2.js`,
`episodio/montar_ep01.py`, `episodio/trocar_audio.py`, `blender/ep01_cenas.py`.

## O canal

- Nome **De Olho no Invisível**, assinatura "O invisível ganha forma". Ciência, engenharia
  e curiosidades em animação 3D, pt-BR, vertical 9:16 (YouTube Shorts e Instagram Reels,
  @deolhonoinvisivel).
- Proposta: tornar **visível o mecanismo**, não só contar a curiosidade. O espectador deve
  enxergar *por que* algo é verdade.
- A marca aparece pelo estilo de produção, não por logotipos. Encerramento sem mascote nem
  vinheta: termina na conclusão científica (no Ep. 01, navio + buzina).

## Regras inegociáveis (restrições do usuário)

- Não publicar, não contratar serviços, não gerar vozes nem gastar créditos sem pedido
  explícito. Nunca pedir nem expor chaves.
- Não alterar arquivos aprovados. Não iniciar render em resolução final sem aprovação.
- Cada pedido muda só o que foi pedido; o resto deve sair idêntico (bit a bit quando
  possível) e isso precisa ser **medido e mostrado**.
- Correções localizadas, com causa, evidência e comparativo. Nada de reconstruir o projeto.
- Separar regressão de defeito antigo; correção nova fica desligada até a decisão do usuário.
- Se um diagnóstico meu estava errado, dizer isso e corrigir a causa real.
- Declarar o que não posso verificar: eu meço, mas não escuto nem assisto como uma pessoa.
  A aprovação estética e auditiva final é do usuário.
- Toda entrega leva: arquivo, comparativo antes × depois, relatório com números, o que não
  mudou, aviso de licença e "nada publicado".

## Preferências do usuário

- Visual rico e cinematográfico, sem efeitos exagerados. Precisão científica acima de tudo.
- Quer ver o mecanismo funcionando, não fórmulas/rótulos como enfeite.
- Som natural e interativo. Detesta: excesso de água, graves sintéticos constantes, whoosh em
  cortes comuns, sons para preencher silêncio, cara de "interface de videogame".
- Valoriza comparativos reais A/B e preservação do que já foi aprovado.

## Narrativa e roteiro

- Estrutura que funcionou: contradição → investigação → mecanismo → experimento controlado →
  aplicação → consequência → conclusão que **retoma a abertura** com nova compreensão.
- Escrever para imagens: cada frase precisa de uma evidência visual. Alguma mudança visual
  relevante a cada 2–4 s (ação física, não câmera girando em objeto parado).
- A narração aprovada é a referência de tempo. Sincronizar por `palavras.json` (instantes
  reais das palavras), nunca por segundos redondos. O roteiro define o conteúdo; a
  transcrição (Whisper) só verifica.
- Ordem dos conceitos: nada na tela antes da explicação (ex.: "Calado: 8 m" saiu do dique).
- Avisos honestos quando a cena dramatiza: "Câmera lenta", "Tempo acelerado", "Meses depois",
  "Corte ilustrativo".
- Ritmo varia por função (impacto, escala, clareza, risco, compreensão). Continuidade é
  imagem + som + significado mudando juntos.

## Ciência

- A física determina a animação; nunca adaptar a física para justificar uma cena (ex.: elevador
  de navios trocado por dique seco).
- Empuxo = resultante das componentes verticais da pressão (p = ρgh, normal à superfície) em
  **toda** a superfície molhada, não "seta saindo do fundo". F_E = ρ·g·V_deslocado; flutuação
  F_E = P. Mais carga → mais calado.
- Comparações precisam isolar a variável (bloco maciço com a **mesma massa** do casco) e
  aparecer juntas, grandes e legíveis na tela.
- Mecânica plausível: cargas seguem trajetórias livres de colisão, balanço θ ≈ −a/g (≤ ~2°),
  rotações em torno do centro do objeto.
- Inundação: só o compartimento realmente alagado; superfície livre horizontal; avaria não
  implica naufrágio automático.
- Mesma fórmula na cena e no shader. Números são do modelo do episódio, não universais —
  dizer isso.
- Distinguir conceitos visualmente parecidos (marcas de calado ≠ linha de carga S/T/W/F/TF).
- Cores são linguagem didática e precisam ser consistentes (ciano = água deslocada/empuxo).

## Direção, câmera e arte

- Muitos "problemas de modelo" são de enquadramento. A câmera responde: o que precisa ser
  visto, por que agora, qual ponto de vista demonstra o funcionamento.
- Projetar para celular: rótulos, medidas e setas legíveis na escala real; nada cortado na borda.
- Detalhe só vale se melhora escala, material, estrutura ou funcionamento. Microtextura de alta
  frequência vira cintilação em vídeo (aço escovado, ruído de espuma abaixo do pixel).
- Efeitos convincentes têm fonte de luz identificável, partículas coerentes, som que começa e
  termina com a ação.
- Correção de cor unifica cenas sem mudar cores com significado.

## Pipeline de imagem

- Blender 5.1 como módulo Python (`blender/ep01_cenas.py`) → `cena.json` + malhas `.bin` +
  `rotulos2d.json` → Three.js r170 headless (`render2.js`, Chromium/SwiftShader, sem GPU) →
  `montar_ep01.py` (fusões, grade, rótulos, legendas, loudness).
- Perfis: `revisao` 540×960; `final` 1080×1920 CRF 17; `SEM_LEGENDAS` (master para trocar
  áudio com `trocar_audio.py`). Selo de revisão só fora do `final`.
- Config aprovada do definitivo: MSAA 4×, AO 16 amostras, bloom 0,22, grade aprovada,
  `janoff=1`, `fantoff=1` só no s08a. Testes e definitivo usam **a mesma** configuração.
- `uTempo` nos shaders é tempo global. Rótulos são composição (mudam sem render).
- Interiores em corte: sem sol direto. Corte ilustrativo não é abertura física para a luz.
- Re-renderizar só o necessário: legenda → montagem; mixagem → áudio; shader → segmento/faixa.
- Alta resolução é etapa de entrega, não de experimentação. Antes: trechos curtos em 1080 nos
  pontos críticos.

## Defeitos conhecidos e como evitar

- **Z-fighting** (pontos em grade, fronteira que pula entre quadros, muda com a resolução):
  superfícies que coincidem por definição sempre brigam — volume deslocado = objeto, corte do
  mar = corte do casco, decalques/janelas colados na parede. Prever na modelagem; corrigir com
  offset mínimo de profundidade, localizado.
- Diagnóstico: ligar/desligar passes (AO, MSAA, bloom, sombras) e ocultar objetos um a um.
  A causa raramente é a mais óbvia.
- Renderizador por software não é determinístico em lotes paralelos → **um processo por vez**.
- Medir a variação natural entre renders idênticos antes de chamar algo de diferença.
- Quadro parado não revela cintilação: validar continuidade temporal com detector absoluto
  (e classificar falsos positivos: sol na água, faíscas, cortes, linhas finas).
- Comparação com referência não enxerga defeito que a referência já tem.

## Render definitivo

- Blocos de 60 quadros, manifesto com checkpoint por quadro (config, hash da cena e do
  renderizador, SHA-256 do arquivo, gravação atômica). Reaproveitar só com prova; descartados
  vão para pasta, nunca apagar.
- Verificar cada quadro (integridade, não-preto, semelhança). Calibrar limiares com casos
  difíceis (texturas repetitivas): escala grossa ≥ 0,93 e diferença média ≤ 6.
- Defeito persistente → parar, investigar, corrigir localmente, depois continuar.
- Processos longos destacados + monitor re-armado; análises concorrentes com `nice`.
- Contagem: quadros renderizados ≠ quadros do vídeo (fusões). Ep. 01: 5.148 → 5.040.

## Som

- Todo som tem origem e função. Mecanismos seguem velocidade/aceleração/carga reais e ficam
  em silêncio parados. Perspectiva pela distância real da câmera, suavizada.
- Gravações reais dão o corpo; síntese é complemento discreto.
- Ambiente muda junto com a fusão de imagem quando o cenário muda.
- Menos camadas = mais realismo. Cortar redundância por camada, não só comprimir/duckar.
- **Diagnosticar por camada antes de afirmar a causa** (o "guincho" aos 17 s era batida no
  ambiente do galpão).
- Sincronizar o evento **percebido**, não o início do arquivo (ataque real da buzina; analisar
  envoltória na banda tonal). Efeitos de brilho no primeiro quadro visível medido.
- Voz tem prioridade: efeitos recuam antes das palavras (via `palavras.json`).
- Técnica: `ganhos_fixos_db` por stem; `master_fixo_db` nas comparações A/B; gerador aleatório
  isolado para sons novos (não mudar os existentes).
- Metas: −14 LUFS, pico verdadeiro ≤ −1,5 dBTP **medidos no AAC codificado**; voz ≥ 10 dB
  acima do resto no celular simulado (mono, 350 Hz–7 kHz); mono sem perda; silêncio no fim.
- Métrica técnica ≠ aprovação auditiva.

## Licenças

- Narração Ep. 01: ElevenLabs plano gratuito → **sem uso comercial**, atribuição obrigatória.
  Nunca apresentar como licenciado para monetização. MP3 original intocado (conferir SHA-256).
  Definir a licença da voz **antes** de gravar o próximo episódio.
- Efeitos: Mixkit (comercial ok, sem atribuição, proibido redistribuir arquivo isolado),
  Commons CC0, CC BY só com créditos; nunca CC BY-NC; evitar CC BY-SA; nada do YouTube.
- Registrar procedência e substituições (Commons limita por IP, erro 429). Não apresentar um
  som genérico como gravação autêntica do equipamento.

## Armazenamento e git

- O contêiner é temporário: quadros renderizados se perdem no fim da sessão — avisar.
- GitHub recusa > 100 MB: dividir em partes de 95 MB com SHA-256 e instruções de remontagem.
- `*.log` é ignorado (usar `git add -f`); nunca commitar arquivo ainda sendo escrito.
- Saída 137 = falta de memória: rodar sozinho.

## Publicação

- Título, miniatura, descrição, créditos e configurações de plataforma são planejados junto
  com a produção. Miniatura comunica a contradição central em uma fração de segundo,
  elementos no centro.
- Horário (ex.: 19h) é hipótese até haver métricas próprias do canal.

## Pipeline para o próximo episódio

1. Fenômeno com potencial visual e pergunta/contradição central.
2. Pesquisa científica (princípios, limites, interpretações erradas comuns).
3. Roteiro validado → voz aprovada (timbre, pronúncia de nomes da marca, **licença**).
4. Alinhamento palavra a palavra → decupagem (objetivo, ação, câmera, transição, modelos).
5. Modelos de referência aprovados → testes numéricos da física **antes** da animação.
6. Animatic → prévia completa em 540 (mesmos movimentos e fps).
7. Sound design interativo desde a primeira versão, ligado às curvas de movimento.
8. Revisões controladas com instantes precisos e A/B → congelar a parte criativa.
9. Teste em 1080 nos trechos críticos (z-fighting, cintilação, legibilidade) → detector
   absoluto no episódio todo.
10. Render com checkpoints → montagem e validação → master sem legendas → preservar fontes,
    parâmetros, versões e licenças → preparar publicação (sem publicar sem pedido).

## Lições novas do Ep. 02 (rodada 1)

- **Decupagem como dados ancorados em palavras** (`decupagem/planos.py`): trocar a narração recalcula cortes, câmeras e
  legendas. Prioridade dos tempos: narração aprovada > narração recebida (alinhada por pausas, não verificada) > estimativa.
- **Testes de geometria antes do render** (continuidade, folgas, invasões) acham colisões que só apareceriam no fim.
- Modelos científicos que se encontram (ciclo × cilindro do compressor) precisam **fechar entre si**; quando não fecham,
  procurar a física que falta (aquecimento do vapor na carcaça), não ajustar números.
- Teste que falha pode ser critério errado (Joule–Thomson de líquidos): investigar antes de mudar dados ou teste.
- Motor: o GTAO inclui malhas transparentes (feixes) → halos; desenhar transparentes no passo próprio, com profundidade
  que respeita os planos de corte e ignora vidro.
- **Câmera dentro de geometria** com corte = quadro tomado pela tampa colorida. Conferir posições de câmera contra as
  paredes (inclusive espuma e teto).
- **Visão térmica** precisa ser reconhecível de imediato: ambiente em cinza-ardósia escuro, só frio e quente se destacam.
- Folha de contato (3 quadros por plano, 270×480) antes do animatic: barata e pega a maioria dos erros de câmera.
- Renderizador por software: ~10 s de inicialização por plano; agrupar renders e evitar reinicializações à toa.
- Download de modelos (Hugging Face) depende de rede liberada **e** de permissão da sessão; sem isso, alinhar por pausas
  e declarar que as palavras não foram verificadas.

## Lições novas do Ep. 02 (rodada 2)

- **Whisper oficial local** (openai/whisper-large-v3 → CTranslate2, offline) verifica a narração palavra a palavra. Ele
  alucina em pausas (palavras de duração zero): retranscrever o trecho sem contexto antes de concluir.
- O Whisper põe o início das palavras pós-pausa ~0,3 s **dentro do silêncio**. Tempo final = identidade pelo Whisper +
  ataque acústico medido (`voz/refinar_tempos.py`). O alinhamento só por pausas pode casar a pausa errada (erros de 1,5–2,6 s).
- **Mudança de fase ao longo de metros não aparece num quadro:** usar um canal esticado e ampliado (corte ilustrativo)
  alimentado pela MESMA tabela do modelo, com aviso "Canal ampliado (esquema)".
- Verificar a matemática dos shaders didáticos nos extremos (lf = 0 e 1): o limiar do líquido estava invertido.
- Corrigir a física não pode apagar a linguagem de cor: o vapor deve manter o matiz da temperatura.
- O renderizador por software **não é determinístico nem rodando sozinho** (média até 2,4, picos de 81). Provar
  "não mudou" com a variação natural medida, não com hash.
- Laços de exportação "padrão" podem esquecer peças (metades de tela dividida). Conferir o hash de toda cena exportada.
- Objetos do cenário na linha de visão (pote) são o defeito mais comum de macro: conferir os quadros de início dos planos.

## Lições novas do Ep. 02 (rodada 3)

- **Personagem:** consultar a identidade oficial antes. O mascote oficial (2D, `episodio_01_navio_v2/referencias/`) não
  tem 3D aprovado: um personagem narrativo deve ser original, diferente do mascote, com cores fora da linguagem didática.
- Partes rígidas articuladas + IK de dois ossos bastam para animatic; a mão deve usar a MESMA curva do objeto que segura.
- Personagem só onde ele é visto agindo; quando atrapalha o diagrama (feixes por cima do corpo), tirá-lo do plano.
  Contraplano "de dentro da geladeira" mostra a reação sem tirar o objeto do centro da história.
- **Pré-visualização também altera dados da montagem** (rótulos/manômetros 2D vêm da cena exportada): reexportar com o
  código final todo plano que foi pré-visualizado com câmera experimental, e provar com diff do vídeo montado.
- Revelação ancorada no ataque da palavra: corte sem antecipação (`ANTECIPA`) e sem fusão (`FUSOES` = 0) só naquele plano.

## Lições novas do Ep. 02 (rodadas 4–5)

- **Avisos ("Visão térmica", "Corte ilustrativo") calculados das curvas gravadas na cena**, com a mesma interpolação do
  motor — nunca por plano inteiro. Aviso só aparece com o modo ativo.
- **Iluminação de cozinha** (ambiente capturado da própria cena por CubeCamera + sombras das luzes de área) dá realismo,
  mas escurece metais e interiores em corte: dois modos de luz por plano (cozinha × técnico), escolhidos por diagnóstico
  ligando/desligando cada recurso. Acne de sombra = bias/normalBias, não geometria.
- Polimento global obriga a renderizar tudo de novo, mas a **estrutura** (planos_resolvidos: ids, t0, t1) precisa sair
  idêntica — medir e mostrar.
- **Verificar a didática pelo EXPORTADO** (manômetros2d, rótulos2d, câmera por quadro) contra o modelo e as palavras, não
  pelo código (`ciencia/verificar_g3.py`). Achou: marcador fora do quadro, lupa adiantada em relação ao marcador, rótulos
  presos à câmera em vez do fenômeno.
- Rótulo de **estado físico** ("começa a evaporar", "mistura fria") fica preso ao PONTO do modelo onde aquilo acontece;
  a lupa só mostra os rótulos que estão dentro do círculo.
- O verificador também erra: projeção ortográfica numa câmera oblíqua deu falso positivo. Usar a perspectiva real e
  conferir antes de "corrigir" a cena.
- **Som:** Freesound CC0 (licença conferida na página de cada som, prévia HQ) quando Mixkit/Commons limitam (429).
  A narração tem ~20 dB entre pico e loudness: compressão suave (2,5:1) só na CÓPIA de mixagem reduz o trabalho do
  limitador; o MP3 não muda. A/B com a narração no mesmo nível = mixagem "só voz" com o MESMO master fixo.

## Lições novas do Ep. 02 (rodada 6)

- **O GTAO do three.js ignora planos de corte:** ele desenha normais/profundidade com um único material de substituição
  sem `clippingPlanes`, então o AO "vê" a parte cortada fora (linha fina = vinco invisível). Diagnóstico: ocultar peças
  uma a uma + desligar passes. Opção `aocorte` no motor (desligada até decisão: muda o sombreado de todo plano em corte).
- Linha fina suspeita: testar com AO desligado antes de concluir — a do E1 persistiu e era o capilar real.
- Detector absoluto em 1080 marca linhas finas em câmera rápida e texturas animadas; mapear os pixels e conferir a câmera
  exportada (trepidação × órbita suave) antes de chamar de defeito.
- Diferenças pequenas em planos NÃO renderizados (≤ 1,1) que terminam no quadro-chave do x264 são do codificador
  (mb-tree/lookahead), não da imagem: provar com data dos quadros-fonte + posição dos quadros-chave.
- Trilha de áudio deve terminar no último QUADRO (n/30), não na duração da decupagem; fade de 50 ms evita clique.
- Peça trocada só num gesto (mão fechada): mesma dimensão da peça original, para não mudar contato nem trajetória.

## Lições novas do Ep. 02 (rodada 7)

- **Camadas 2D legíveis exigem posicionamento com regras**, não só fonte maior: candidatos em volta da âncora + posições
  fixas, validade = sem cortes/sobreposições/linhas sobre texto, escolha no plano INTEIRO por programação dinâmica
  (mínimo de trocas) e fusão curta nas trocas. Testar TODOS os quadros com um registro das caixas desenhadas.
- **AO coerente com o corte:** normais/profundidade com os mesmos planos de corte; as "tampas" (faces internas vistas
  pelo corte) marcadas numa máscara SUAVIZADA para o AO não escurecê-las (máscara binária pisca na fronteira).
- **Correção certa pode revelar defeito antigo:** o AO correto escureceu uma face cinza e expôs z-fighting que já existia
  (amarelo × cinza de brilho parecido, invisível ao limiar 30). Medir com limiar sensível antes de culpar a correção.
- Peças que encostam face a face (topo/base × laterais, porta × vedação) brigam pelo corte: folga de 0,5 mm.
- Hipótese descartada também se registra (atenuação rasante do AO: sem efeito).
- **Estroboscopia de grades:** medir pela geometria (deslocamento por quadro ÷ passo na tela; ≥ 0,5 = ambíguo). Desacelerar
  raramente basta com cortes e duração fixos; obturador real (média em luz linear de sub-quadros, 180°) reduz sem mudar
  câmera, pulso nem enquadramento — o sub-quadro central deve coincidir com o quadro aprovado.

## Lições novas do Ep. 02 (rodada 8)

- **Detector sensível acha defeitos ANTIGOS escondidos** (porta × vedação em C4/H1/H2, degrau × fundo no E2): conferir na
  versão aprovada antes de chamar de regressão; corrigir com a mesma família de correção já aprovada, só nos planos onde a
  **projeção geométrica da junção** mostra que ela aparece (escopo provado, não "todos os planos").
- Classificar o que pisca **dentro da tampa × na borda**; listar falsos positivos (arames sobre a tampa, feixes, canal animado).
- Um defeito que **não muda com a resolução** (mesma contagem em 540 e 1080 ajustada à escala) não é conflito de profundidade.
- **Folga corrige z-fighting mas pode criar fresta**: 0,5 mm visto de quina vira linha tracejada em 1080. Medir em 1080 e
  localizar cada linha projetando as faces candidatas; alternativa melhor costuma ser sobreposição (sem faces coplanares).
- **Exportação não determinística na ordem dos triângulos**: comparar malhas sem ordem; congelar cenas por hash e não
  reexportar depois. Conferir manifestos de render × cenas atuais antes de montar (achou D1 reexportado só nos rótulos).
- Comparar com animatic de passo 2 em trios de 2 quadros; o selo/IDs de revisão contam como diferença em todo plano.
- **Obturador**: validar nitidez com câmera parada (integrado/central ≈ 1) e primeiro/último quadro iguais ao aprovado.
- AAC: mudar um trecho do áudio desloca a quantização segundos depois (pico verdadeiro mudou em 130 s por causa de 118–120 s);
  medir de novo sempre no AAC final.
- Espera longa: um `run_in_background` tem limite de 2 h; para filas maiores, Monitor re-armado por eventos do log.

## Lições novas do Ep. 02 (rodada 9)

- **Verificador de render:** salto entre quadros só é aceito com prova (efeito da cena mudando naquele quadro, mesmo salto
  numa versão aprovada com imagem equivalente ≥ 0,93, ou registro investigado com evidência); fora disso, PARA.
- **Mudança de animação num plano exige conferir a continuidade no corte com o vizinho** (porta física no A1 deixou o A2
  com degrau 88° → 100°). Medir ângulo e velocidade dos dois lados do corte.
- Mudança de câmera aprovada pode criar estroboscopia de grade/tubos finos: medir com `medir_estrobo.py` depois de
  qualquer aproximação rápida e oferecer o obturador de 180° como A/B desligado.
- Composição testada em todos os quadros depois da montagem final, não só na prévia.

## Lições novas do Ep. 02 (rodada 10)

- **Stems em PCM 24 cortam acima de 0 dBFS:** com master de +5 dB a soma dos stems não reproduz a mixagem. Gravar stems em
  ponto flutuante e PROVAR "soma = mixagem aprovada" (nulo ≤ −130 dBFS) antes de acrescentar camadas.
- **O validador também erra:** "voz − resto" lia os stems da 1ª mixagem. Validar com os stems da versão medida
  (STEMS_VOZ/STEMS_RESTO) e conferir o arquivo de entrada de toda métrica.
- Mixagem antiga depende das CÂMERAS com que foi gerada (perspectiva sonora): reproduzir com as cenas da época (CENAS_SOM).
- **Troca de câmera mais curta que 1 quadro** gera um quadro intermediário (câmera interpolada): varrer cenas por "dois
  saltos seguidos". Corrigir sem mexer na trilha (interpolação suave: chave nova muda os vizinhos) e provar quadro a quadro.
- Reexportação localizada: `provar_quadros_iguais.py` + reuso por prova no render (só os quadros diferentes saem).
- Trilha: Mixkit Music (YouTube/redes ok, sem Content ID, sem arquivo isolado no git). Escolher por medida (percussão,
  graves, faixa da voz, dinâmica) e deixar a audição para o usuário. Música −8 dB sob a fala com antecipação de 0,15 s.
- Supersampling 1,5× (custo 2,25×) não deu ganho consistente sobre o MSAA 4×: medir contra referência 2160 antes de pagar.
- Picos de AAC mudam de lugar quando qualquer camada muda: medir sempre no AAC final de CADA variante.

## Lições novas do Ep. 02 (rodada 11)

- **Quadros-ponte de transição** (rosto continuado depois do corte) devem continuar a câmera APROVADA (posição e velocidade
  do último quadro), derivada dos dados exportados — chaves novas no Blender mudam a curva e fazem a câmera "frear".
- **Desfoque de movimento na composição**: janela CENTRADA no instante do quadro (média só para um lado desloca a imagem n/2 px).
- **Comentário `#` dentro de uma lista numa linha só desligou avisos de outros planos** (3ª vez neste projeto). Depois de
  qualquer edição na montagem: SHA-256 de todos os quadros compostos contra a versão anterior (`verificar_transicao_a4.py hashes`).
- Sons pontuais que coincidem com a fala (apresentação de componentes, pouso de objeto) somem sob o abaixamento automático:
  stem próprio com nível relativo à voz NAQUELE instante (−12 dB na faixa do celular) e medir.
- Variantes de mixagem não podem sobrescrever stems nem registros aprovados (sufixo próprio; hash antes/depois).
- Páginas com proteção anti-robô (Pixabay) não se acessam automaticamente: pedir a confirmação da licença ao usuário.
- **Re-render localizado: passar os planos** (`render_definitivo.py --perfil revisao B5`). Sem a lista, o script percorre o
  episódio e refaz planos cujos quadros de 540 vieram de outros scripts (sem `_manifesto_quadros.json`: D2, D4, E1–E4,
  F1, F2, G3z, J4) — no Ep. 02 isso re-renderizou o D2 em 540 sem necessidade (conteúdo equivalente; vídeo V10 intacto).

## Lições novas do Ep. 02 (rodada 12)

- **Transparente que "muda de cor" de um quadro para o outro = ordem de desenho invertida.** O three.js ordena os
  transparentes pela profundidade do CENTRO de cada malha; com a câmera andando, garrafa × prateleira de vidro trocam de
  ordem e a mistura muda de uma vez. Varrer todas as cenas por trocas de pares sobrepostos na tela
  (`varrer_ordem_transparentes.py`) e MEDIR cada uma (opção ligada × desligada): das 5 trocas, só 3 mudavam a imagem.
  Correção: congelar a ordem no quadro 0 do plano (`ordemtransp=1`, desligada por padrão), só nos planos visíveis.
- Opção nova no motor muda o hash do motor e invalidaria todo o render: provar equivalência (motor novo sem a opção ×
  aprovado = variação natural) e registrar `motor_equivalente`; quadros anteriores à troca são reaproveitados por prova.
- Montagens são determinísticas e não gravam intermediários: definitivo e master podem rodar EM PARALELO (−30 min).
  Processo destacado com `setsid`; ao matar por padrão use `[.]` na regex para o `pkill -f` não casar com o próprio laço.
- Validadores com nome de saída fixo sobrescrevem registros aprovados: sufixo opcional (`SUF_VALIDACAO`) e conferir antes.
- Diferenças só do x264 podem atravessar quadros-chave intermediários e terminar num quadro-chave adiante (1594, 3577):
  provar com quadros-fonte inalterados + entradas da montagem inalteradas + posição dos quadros-chave.
- Música mais alta: o p5 passa (10,3), mas o PIOR caso caiu para −8,7 dB numa pausa antes de um "e" curto. Localizar as
  piores janelas nas palavras e pedir ao usuário que escute esses instantes; pico −1,52 dBTP = margem de 0,02 dB.
