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
