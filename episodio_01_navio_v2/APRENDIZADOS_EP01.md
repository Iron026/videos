# De Olho no Invisível · Ep. 01 · Tudo o que aprendi produzindo "Como um navio de aço consegue flutuar?"

Este é um registro completo e franco do que aprendi ao produzir o Episódio 01. Cobre técnica, narrativa, som, validação, organização e também os erros que cometi. A ideia é que sirva de manual para os próximos episódios.

---

## 1. Visão geral: o que funcionou como método

1. **Trabalhar por rodadas curtas, com uma base aprovada fixa.** Cada rodada parte da última versão aprovada e muda só o que foi pedido. O resto deve sair idêntico, de preferência bit a bit, e isso precisa ser medido. Foi o que permitiu corrigir detalhes no fim sem medo de estragar o que já estava bom.
2. **Separar imagem e áudio desde o início.** Montei um master de imagem sem legendas, que permite trocar o áudio sem renderizar nada de novo (`trocar_audio.py`). Dezenas de rodadas de som custaram cerca de 75 s cada, e não horas.
3. **Sempre entregar comparativos antes × depois,** com a mesma imagem, o mesmo trecho e o mesmo nível. É assim que alguém decide se uma mudança foi boa. Um relatório sozinho não basta.
4. **Medição não é percepção.** Eu não consigo escutar nem assistir como uma pessoa. Precisei dizer isso explicitamente toda vez e tratar as medidas como detectores de erro, não como prova de qualidade.
5. **Investigar antes de corrigir.** Nas três vezes em que apareceu um defeito visual sério, a causa real não era a mais óbvia. Testar variantes isoladas, ligando e desligando passes e objetos, foi o que achou a causa.
6. **Corrigir de forma localizada e provar que o resto não mudou.** Toda correção vinha acompanhada de uma medida: em quais trechos o arquivo mudou e quanto.

---

## 2. Pipeline de imagem

### 2.1 Arquitetura

**Etapa 1: cenas no Blender.**
- O Blender 5.1 é usado como módulo Python (`PYTHONPATH=…/blender/site`), sem interface gráfica.
- Cada segmento do episódio é uma função em `blender/ep01_cenas.py` (`seg02`, `seg03`, … `seg13`).
- Essas funções montam geometria, materiais, câmera animada, rótulos e objetos que "surgem" ou "somem".
- Saída: um diretório por segmento (`episodio/cenas/sNN/`) com `cena.json` (materiais, câmera por quadro, sol, céu, animação, surgimentos), malhas `.bin` e `rotulos2d.json`.

**Etapa 2: render em tempo real (Three.js r170).**
- O motor é `motores/tempo_real_v2/render2.js`, executado headless pelo Chromium/Playwright com SwiftShader (`render_anim.mjs`).
- Ele lê a cena e gera JPEGs por quadro.
- Parâmetros via query string: `escala`, `aoamostras`, `msaa`, `bloom`, `sombra`, e outros que fui acrescentando para diagnóstico e correção (`ocultar`, `ocl`, `janoff`, `fantoff`).

**Etapa 3: montagem.**
- `episodio/montar_ep01.py` compõe os quadros por segmento, com fusões entre segmentos.
- Também aplica a correção de cor (`grade_ep01.py`, só na imagem 3D), o nivelamento de cor por segmento, os rótulos 2D projetados, os avisos honestos ("Câmera lenta", "Meses depois", "Tempo acelerado") e as legendas alinhadas às palavras reais da narração.
- Codifica com ffmpeg e aplica o controle de loudness no AAC final.

**Perfis:**
- `revisao`: 540 × 960.
- `final`: 1080 × 1920, CRF 17.
- `SEM_LEGENDAS=1`: gera o master de imagem.
- O selo "VERSÃO DE REVISÃO · não publicar" só aparece fora do perfil final.

### 2.2 Lições do pipeline

- **`uTempo` nos shaders é tempo GLOBAL do episódio.** Um shader que assume "tempo local do segmento" fica invisível ou errado. Foi o caso do jato de água, que só apareceu depois de corrigir `g0 = 0`.
- **Rótulos 2D vêm de dados exportados (`rotulos2d.json`), não do render 3D.** Tirar o rótulo precoce "Calado: 8 m" não exigiu nenhum render: bastou filtrar os dados e corrigir a cena-fonte.
- **O nivelamento de cor por segmento usa médias HSV.** No perfil final, a média de um segmento sem prévia vem dos quadros 1080. Conferi que a diferença era desprezível (fator de brilho 0,9947 contra 0,9934).
- **Montar exige que todos os segmentos tenham pasta de quadros,** porque o nivelamento lê estatísticas de todos. Para montar só um trecho de teste, apontei temporariamente a pasta que faltava e removi o link logo depois, para não contaminar o render definitivo.
- **Fusões entre segmentos geram quadros extras.** O episódio tem 5.040 quadros, mas o render tem 5.148, porque as sobreposições das fusões precisam existir nos dois lados.

---

## 3. Defeitos visuais: como foram encontrados e corrigidos

### 3.1 Conflito de profundidade (z-fighting): o defeito mais recorrente

Apareceu **três vezes**, sempre com a mesma assinatura: pontos em grade, faixas que "pulam" de quadro a quadro, ou uma fronteira que muda de lugar conforme a resolução.

**1. Mar vazando pelo corte ilustrativo (avaria, 137–154,6 s; experimento, 86–90 s)**
- **Sintoma:** pontos em grade e uma faixa vertical clara sobre a parede do porão, a antepara e o fundo duplo.
- **Investigação:**
  - Renderizei o mesmo quadro com cada passe desligado (sem AO, sem MSAA, sem bloom, configuração antiga, sem nada): **o defeito persistia em todas as variantes**. Não era o antisserrilhado nem o bloom, que eram as suspeitas óbvias.
  - Depois ocultei objetos um a um, com o parâmetro de diagnóstico `ocultar=`. Só sumia ao ocultar a **água do mar**.
- **Causa:**
  - O mar é cortado no mesmo plano do corte do navio.
  - Um "oclusor" só de profundidade, desenhado nesse mesmo plano, esconde o mar dentro do casco.
  - Duas superfícies coplanares, mais a comparação `zc < vZv − 0,05` contra uma textura de profundidade com precisão limitada, fazem cada pixel decidir quase ao acaso.
- **Correção:** desenhar o oclusor 0,6 % mais perto da câmera, multiplicando a posição de visão por 0,994. A posição na tela não muda, só a profundidade, e a folga cresce com a distância, como a imprecisão.
- **Prova:** nos pixels alterados, o quadro corrigido ficou igual à cena sem mar (diferença 1,3–3,7, contra 9,6–19,2 antes).

**2. Janelas da superestrutura (~146,5–148,3 s)**
- **Sintoma:** a faixa de vidro escuro aparecia pontilhada e trêmula; em 1080, o padrão só ficava mais fino.
- **Testes:**
  - sem sombras: persistia (não era acne de sombra);
  - sem AO: persistia;
  - sem janelas: sumia.
- **Causa:** a faixa de janelas fica só **6 cm** à frente da parede, e ainda tem chanfro.
- **Correção:** *polygon offset* no material das janelas (`janoff=1`). O offset 4 era excessivo e criava bordas marrons; **o valor mínimo que resolve é o certo**.
- **Validação:**
  - na área das janelas, a cintilação caiu de 41,3 para 9,7 e os pontos isolados de 8.263 para 2.103;
  - fora das janelas, nada mudou;
  - nos planos de navegação, porto e final, só ruído de borda.

**3. Cubo ciano da água deslocada × bloco de aço (s08a, 77,6–83,8 s)**
- **Sintoma:** a fronteira azul/cinza sobre o bloco saltava de lugar a cada quadro, bem no plano que explica o empuxo.
- **Causa:** o cubo, que representa "o volume que o bloco desloca", tem **exatamente** o tamanho do bloco. As faces coincidem.
- **Como foi descoberto:**
  - Não aparecia na comparação com a revisão aprovada, porque o defeito já estava nela.
  - Apareceu porque a semelhança daquele trecho caiu para 0,963 durante o render definitivo e eu fui olhar. **Uma métrica relativa a uma referência não enxerga defeitos que a própria referência já tem.**
- **Correção:** *polygon offset* nos materiais "fantasma" (`fantoff=1`), aplicado **só no s08a**. Nos outros segmentos com volumes semelhantes, o teste não mostrou mudança visível.

**Lição geral:**
- Toda vez que duas superfícies têm a mesma posição por definição (volume deslocado = volume do objeto; corte do mar = corte do navio; janela "colada" na parede), haverá z-fighting.
- É melhor prever isso na modelagem (afastar alguns centímetros, ou dar prioridade explícita) do que descobrir no final.

### 3.2 Detector absoluto de cintilação

- Criei `detectar_cintilacao.py`.
- Ele conta pixels que "vão e voltam" (q−1 → q → q+1 com variações grandes de sinais opostos) e agrupa em blocos de 16 px.
- Calibração no defeito real: 11 de 23 quadros piscando antes da correção, 0 depois.
- Ele também acusa coisas legítimas, que precisam ser classificadas olhando:
  - brilho do sol na água;
  - faíscas de solda;
  - cortes de cena;
  - serrilhado de linhas finas (guarda-corpos, treliças, tracejados).
- Comparar a contagem por segmento entre a versão nova e a aprovada mostra regressões.

### 3.3 Outros defeitos visuais desta produção

- **Piso "bugado" do porão:** o sol entrava pelo lado aberto do corte ilustrativo e projetava sombras serrilhadas e azuladas no interior. Num porão fechado essa luz não existe. Correção: lista `sem_sombra`, com os materiais internos sem receber sol direto.
- **Faces sobrepostas na água do alagamento:**
  - Quando a caixa de baixo enche, o topo dela não é mais desenhado.
  - A face junto ao costado, que coincidia com o chapeamento curvo, foi descartada no shader.
- **Re-render em lotes paralelos é não determinístico no renderizador por software:**
  - Um dos três processos paralelos gerou, só em 146,2–147,8 s, janelas erradas.
  - O mesmo quadro renderizado sozinho saiu certo; um processo começando no quadro 270 também.
  - Conclusão: **renderizar em um único processo** e conferir quadro a quadro.
  - Em 1080, três processos paralelos também ficaram mais lentos no total do que um só (~14 s por quadro cada, contra ~4 s sozinho).
- **Variação natural entre renderizações idênticas:** existe e depende da cena. Na maioria, a diferença média fica entre 0,04 e 0,3 (de 255). No estaleiro (s03), chega a 0,57. Antes de chamar algo de "diferença", meça essa linha de base.

### 3.4 Qualidade de imagem

- **Configuração aprovada:** GTAO 16 amostras, MSAA 4×, bloom 0,22 com limiar alto, correção de cor sutil.
  - A correção de cor tem curva em S leve, saturação +5 %, sombras levemente frias e altas luzes levemente quentes, e vinheta de −10 %.
  - Ela vale só na imagem 3D; rótulos e legendas entram depois.
- **Scripts antigos podem guardar configurações desatualizadas.** O `render_segmentos.sh final` ainda usava AO 8 e não tinha bloom. O render definitivo precisa usar exatamente a configuração dos testes aprovados.
- **Em 1080, texturas finas** (ranhuras dos contêineres) **perdem o moiré do 540.** Isso derruba métricas de semelhança fina sem ser defeito.
- **Variação de pintura** ("primer" manchado): é intencional e aparece em todas as variantes. Não confundir com artefato.

---

## 4. Render definitivo: o que aprendi sobre executar horas de render com segurança

1. **Um processo por vez,** em blocos de cerca de 60 quadros. Cada bloco reabre a cena (cerca de 15–20 s de custo), mas garante retomada.
2. **Manifesto com checkpoint por quadro:**
   - Cada quadro é registrado com a configuração, o hash da cena e do renderizador e o SHA-256 do arquivo.
   - Isso é gravado de forma atômica (arquivo temporário seguido de `os.replace`) depois de cada bloco.
3. **Reaproveitamento só com prova:**
   - O quadro precisa ter a mesma configuração, a mesma cena, o mesmo SHA-256 e decodificar inteiro.
   - Quadros sem registro compatível vão para uma pasta de descartados. Nunca apagar.
4. **Verificação de cada quadro novo:** decodificação completa, tamanho certo, não preto, semelhança com a revisão aprovada.
5. **O critério de semelhança precisa ser calibrado:**
   - SSIM fino (540 × 960) dá **falso positivo** em textura fina (contêineres): duas paradas desnecessárias.
   - SSIM em escala grossa (270 × 480 com leve desfoque) separa bem:

     | Caso | Semelhança grossa | Diferença média |
     |---|---|---|
     | Quadros corretos | ≥ 0,947 | ≤ 4,1 |
     | Quadro deslocado 10 posições | 0,902 | 4,7 |
     | Plano errado | 0,53 | 67,9 |

   - Limite final usado: SSIM grosso ≥ 0,93 e diferença média ≤ 6.
6. **Parar diante de defeito:** o script para sozinho (código 3) se um quadro falhar duas vezes. Investigar antes de continuar.
7. **Mudança de código no meio do render:**
   - Se o renderizador mudou, mesmo que de forma inerte (um parâmetro desligado por padrão), os quadros antigos só valem com **prova de equivalência**.
   - Re-renderize amostras (início, meio e fim de cada segmento) e compare com a variação natural entre renderizações idênticas.
   - Registre a evidência no manifesto (`migrar_manifesto.py`).
8. **Correções locais por segmento** (`SEG_EXTRA = {'08a': '&fantoff=1'}`), com identificador de configuração próprio, deixam claro o que mudou onde.
9. **Processos destacados** (`nohup setsid …`) sobrevivem ao limite de tempo das ferramentas. O acompanhamento é feito por log e monitor, com re-armar a cada 30–60 min, e por um "despertador" de segurança.
10. **Tempos reais em 1080, no renderizador por software:**
    - 4,5 a 12 s por quadro, conforme a cena; as mais pesadas são oceano e porto.
    - Cerca de 12 h de calendário com paradas e investigação.
    - Montagem 1080: cerca de 23 min por arquivo.

---

## 5. Narrativa e ciência

- **A ordem das ideias importa mais que a quantidade.** O rótulo "Calado: 8 m" no dique, aos 47 s, antecipava um conceito que a narração só explica aos ~117 s.
  - A correção foi tirar o rótulo e manter as marcas pintadas, que servem de referência visual de "a linha d'água parou" ("e para. Por quê?").
  - O conceito ficou inteiro na sequência de carregamento. Assim não há explicação dupla.
- **Cada elemento gráfico precisa corresponder à fala do momento.** Antes de mexer, confira os tempos das palavras (`palavras.json`).
- **Avisos honestos de tempo** ("Câmera lenta", "Tempo acelerado", "Meses depois") e o rótulo "Corte ilustrativo" mantêm a ciência correta quando a cena dramatiza.
- **Física coerente:**
  - O nível da água, o trim de 0,71° e o calado são calculados por fórmula, a mesma na cena e no shader.
  - O "volume deslocado" é literalmente o volume do objeto.
  - A razão empuxo/peso do bloco de aço é 1025/7850 ≈ 0,13.
- **O fim do episódio sem mascote, vinheta ou assinatura** foi uma decisão de direção que precisou ser preservada em todas as rodadas.

---

## 6. Narração e licenças

- **Narração:** voz *Will - Deep* da ElevenLabs, **plano gratuito**.
  - Esse plano não dá licença para exploração comercial e exige atribuição.
  - Isso ficou documentado em `voz/LICENCA_NARRACAO.md`.
  - Nenhum material diz que o episódio está licenciado para uso comercial enquanto essa pendência existir.
- **O MP3 original da narração nunca foi alterado,** e o SHA-256 foi conferido várias vezes. A fala de assinatura é cortada só na cópia usada na montagem (166,36 s).
- **Não gerar vozes novas sem pedido explícito,** e não consumir créditos pagos.
- **Efeitos sonoros:**
  - Mixkit (licença própria, uso comercial permitido, atribuição não exigida, mas proibido redistribuir o arquivo isolado).
  - Wikimedia Commons CC0: a buzina, "Cruise ship Albatros ship horn", de Tvabutzku1234.
  - Regras: CC BY só com créditos; nunca CC BY-NC; CC BY-SA evitado; nada extraído de vídeos do YouTube.
- **Um registro de fontes gerado automaticamente** (`registro_hibrido.py`) evita erros.
  - Corrigi um bug que tratava CC0 como "atribuição exigida".
  - Também deixei a linha de CC BY 4.0 condicional: só aparece se algum arquivo CC BY for de fato usado.
- **Downloads do Commons** podem bater em limite de taxa (erro 429) por IP. Tenha reservas compatíveis (Mixkit) e registre a substituição.

---

## 7. Sound design

### 7.1 Princípios que guiaram a mixagem final

1. **Todo som precisa de função narrativa ou de uma ação visível.**
   - Motores, guinchos e cabos seguem o movimento real da animação: velocidade, aceleração e carga, a partir de `movimento.py`.
   - Eles ficam em silêncio quando o objeto para.
2. **Menos é mais com água.** Houve uma auditoria por seção (`auditoria_agua.py`) e redução onde a água competia com a voz.
3. **Ambiente coerente com o cenário mostrado.**
   - Na transição de 0:30, galpão e guindastes continuavam tocando com o navio pronto ao ar livre, e o "zumbido" do porão era a própria gravação de um guindaste.
   - Correção: o estaleiro termina junto com a fusão de imagem, entra vento discreto e, no porão, ar parado abafado.
4. **Perspectiva pela distância real da câmera:** volume e agudos mudam com a distância.
5. **Cenas calmas continuam calmas.** Impactos têm presença, mas sem competir com a voz.
6. **Evitar:** graves cinematográficos frequentes, *whoosh* em cortes comuns, rangidos repetitivos, sons eletrônicos e reverberação excessiva.

### 7.2 Técnica

- **Camadas reais e síntese discreta:**
  - Gravações dão o corpo.
  - A síntese preenche lacunas: grave de impacto, sopros sutis e os brilhos das linhas luminosas.
- **Brilhos das linhas (2:10):**
  - Antes era um sopro único para cinco linhas; agora são cinco sons, um por linha.
  - Cada um entra no **primeiro quadro visível**, medido nos quadros renderizados. A medição detectou os saltos de pixels de brilho em cada linha.
  - Timbre: sopro filtrado de 2,5–7 kHz mais um "tilintar" vítreo inarmônico (parciais 1 / 2,32 / 3,9), com ataque de 8 ms.
  - Variações pequenas de afinação e de nível; nenhuma energia abaixo de 500 Hz.
- **Gerador aleatório com semente fixa:**
  - Trocar um som sintético por outro com sorteios diferentes mudava **todos os sons sintéticos depois dele**.
  - Solução: os sons novos usam um gerador próprio, e o código consome do gerador global exatamente o que o som removido consumia. Assim, o resto do episódio continua idêntico bit a bit.
- **`ganhos_fixos_db`:**
  - Sem ele, o mixador renormalizava cada stem, e cortar camadas não diminuía nada.
  - Com ganhos absolutos fixos, tirar uma camada reduz de fato.
- **Ganho de master fixo para comparações A/B** (`master_fixo_db`): a versão B herda o master da A. Assim, a única diferença é o elemento novo, e a buzina não muda artificialmente o volume do resto.
- **Ducking moderado:**
  - A banda da fala dos outros stems fica cerca de 13 dB abaixo da voz.
  - A redução tem limite próprio para as ambiências, para que o ambiente não suma sob a voz.
- **Automação pontual em vez de mexer no todo:**
  - "navio," aos 17 s estava mascarado.
  - A medição por camada mostrou que a culpa **não** era do guincho, como eu tinha suposto, e sim de uma batida metálica já gravada no ambiente do galpão.
  - Correção: −8 dB só durante a palavra, com rampas cossenoidais.
  - **Lição:** diagnosticar por camada antes de afirmar a causa. Eu tinha errado o diagnóstico e precisei corrigir isso abertamente.
- **Fade geral no fim:**
  - Ele afogava a buzina final quando ela entrava tarde.
  - Solução: compensar o fade só no trecho da buzina, deixando-a terminar pelo próprio decaimento real.

### 7.3 Buzinas

- **Uma única gravação real** (CC0) nas duas buzinas.
  - Montagem: ataque, sustentação breve e dissipação real com eco.
  - Tom 0,9×, para soar grave como um cargueiro.
  - Passa-alta de 80 Hz, para tirar o vento do microfone.
- **Abertura:**
  - Volume pleno na pausa entre "gigante:" e "um navio".
  - Recuo antes da primeira sílaba, numa rampa cossenoidal de 0,15 s que termina 30 ms antes, com o tempo tirado de `palavras.json`.
  - Sob a fala, fica baixa e constante, sem "bombear".
  - O aumento de +2 dB pedido foi aplicado só no trecho principal: o recuo ficou 2 dB mais fundo para que o nível sob a voz não mudasse.
- **Conclusão:**
  - A demora percebida tinha causa concreta: o trecho usado como "ataque" (3,15 s da gravação) era a subida de pressão **antes** do toque, cerca de 17 dB abaixo dele.
  - O ataque real da gravação começa em ~5,55 s e sobe 15 dB em ~55 ms.
  - Com esse ataque, a buzina entra 47 ms depois de "navio." e chega ao nível pleno em 80 ms.
- **Lição:** analise a envoltória da gravação na banda tonal (180–1200 Hz) antes de escolher os trechos. A envoltória de banda larga engana, porque o vento domina.

### 7.4 Metas técnicas do áudio

- **Loudness e pico:** −14 LUFS integrado e pico verdadeiro ≤ −1,5 dBTP, medidos **no AAC codificado**, porque a codificação cria picos entre amostras.
  - A montagem ajusta o teto do limitador até o AAC ficar dentro da meta.
  - Resultado: −14,1 LUFS / −2,0 dBTP.
- **Clareza no celular simulado** (mono, 350 Hz–7 kHz): voz ≥ 10 dB acima do resto em ~96–97 % dos blocos de 100 ms com fala. Os piores blocos são investigados um a um.
- **Mono:** perda de 0,01 dB; correlação L/R de 0,988.
- **Final:** silêncio no último quadro, sem corte seco.
- **Sincronia da narração:** +3 ms, constante, medida por correlação cruzada em 21 janelas.
- **Sincronia de impactos:** ataque medido no stem de efeitos contra o evento da animação, com desvio máximo de 23 ms.
- **Quatro stems** (narração, efeitos, ambiências, música), mais stems por grupo e por categoria (água, buzina). Eles permitem auditar e trocar partes sem refazer tudo.

---

## 8. Validação: métricas úteis, limites e armadilhas

- **"Só mudou o que devia":**
  - **Áudio:** compare a mixagem nova com a aprovada em janelas de 100 ms e liste os trechos com diferença acima de −100 dBFS. Nas rodadas finais, a mixagem mudou só nos trechos pedidos e ficou idêntica no resto.
  - **Imagem:** PSNR quadro a quadro entre os masters. Quadros-fonte não tocados podem variar um pouco depois de um trecho alterado (PSNR ≥ 44–47 dB), por decisões do codificador. Isso é compressão, não conteúdo; para provar, compare os hashes dos quadros-fonte.
- **Comparação com uma referência não enxerga defeitos que a referência já tem.** Use também detectores absolutos.
- **Métricas dependentes de resolução** ("cintilação local relativa" em blocos de 20 px) dispararam milhares de vezes no 1080, só porque há mais detalhe. Saiba quando uma métrica não serve e diga isso no relatório.
- **Limiar em borda:** 29 "saltos" de quadro a quadro existiam só porque os limiares das duas versões diferiam um pouco. A razão real entre as mudanças era 0,99–1,04. Sempre olhe o valor bruto antes de concluir.
- **Autoteste do validador:** rode a validação comparando um arquivo com ele mesmo. O resultado precisa dar 1,0, nenhuma diferença e −240 dB de resíduo.
- **Diga o que não pode ser verificado.** Eu não ouço nem vejo como uma pessoa. A escuta e a visualização finais são do usuário.

---

## 9. Montagem, legendas e master

- **Legendas** queimadas a partir das palavras reais da narração, com o mesmo estilo nos perfis 540 e 1080 (fonte Montserrat 800, contorno escuro).
- **`trocar_audio.py`:** detecta se o master é 540 ou 1080 e escolhe o perfil, a escala das legendas e o CRF. Aplica o mesmo controle de loudness da montagem.
- **Duas rotas para trocar o áudio no futuro:**
  - pelo master sem legendas (uma geração extra de compressão);
  - pelos quadros, com `montar_ep01.py final` e `AUDIO_EP01`, sem perda de qualidade, mas só enquanto os quadros existirem.
- **O título nos metadados** também diferencia revisão e versão final.

---

## 10. Ambiente, armazenamento e git

- **O contêiner é temporário.** O que não estiver no git ou entregue ao usuário se perde, por exemplo os 5.148 quadros 1080 (1,2 GB). Deixe isso explícito para o usuário.
- **O GitHub recusa arquivos acima de 100 MB.**
  - O MP4 definitivo (141,8 MB) e o master (196,6 MB) foram guardados em partes de 95 MB.
  - Cada parte tem SHA-256, assim como o arquivo remontado, e há instruções de remontagem.
  - Os arquivos inteiros ficam no `.gitignore`.
- **`.gitignore` ignora `*.log`:** use `git add -f` quando um log fizer parte da documentação.
- **Padrões em `.git/info/exclude` são relativos à raiz do repositório,** não à pasta atual.
- **Nunca commitar um arquivo que ainda está sendo escrito,** como um MP4 em montagem.
- **Commits frequentes**, com mensagem explicando o porquê, e push para a branch combinada.
- **Faltou memória num worker** (saída 137) durante uma exportação pesada do Blender: rodar sozinho resolveu.
- **Esperas em segundo plano** têm limite de cerca de 2 h. Para trabalhos longos, use processo destacado, monitor re-armado e "despertador".
- **Processos concorrentes** (validadores e detectores) deixam o render mais lento. Use `nice` nas análises.

---

## 11. Trabalho com o usuário

- **Respeitar literalmente as restrições:**
  - não publicar;
  - não contratar serviços;
  - não gerar vozes;
  - não alterar arquivos aprovados sem autorização;
  - não iniciar o render 1080 sem aprovação;
  - não expor chaves de API;
  - não pedir chaves no chat.
- **Quando uma instrução se baseia num diagnóstico meu que estava errado** (por exemplo "reduza o guincho"), dizer isso claramente, corrigir a causa real e explicar por que o pedido literal não teria efeito.
- **Em defeitos que já existiam na versão aprovada,** separar "regressão" de "defeito antigo". Propor a correção com teste e deixá-la desligada até a decisão do usuário, como foi feito com `janoff`.
- **Quando o usuário autoriza parar diante de um defeito significativo,** parar de fato, investigar, corrigir de forma localizada e explicar.
- **Entregáveis sempre com:**
  - o arquivo;
  - um comparativo;
  - um relatório curto com números;
  - a lista do que não mudou;
  - o aviso de licença;
  - a confirmação de "nada publicado".
- **Relatórios** devem dizer o que é medição e o que é limite do método.

---

## 12. Erros que cometi (e o que fazer diferente)

1. **Diagnóstico precipitado do guincho aos 17 s.** Afirmei a causa antes de medir por camada. *Fazer diferente:* medir a contribuição de cada camada na banda da fala antes de propor qualquer correção.
2. **Limiar de verificação calibrado em casos fáceis.** O SSIM fino de 0,90 parou o render por causa de textura fina, e o grosso de 0,95 parou por moiré. *Fazer diferente:* calibrar com casos difíceis conhecidos (planos próximos de texturas repetitivas) antes de lançar horas de render.
3. **Primeiro re-render da avaria em três lotes paralelos,** que geraram um defeito não determinístico. *Fazer diferente:* um processo só, sempre.
4. **Contar com a comparação relativa como prova de ausência de defeitos.** O cubo ciano passou por várias revisões. *Fazer diferente:* rodar um detector absoluto de cintilação e de conflito de profundidade em todo o episódio **antes** da aprovação visual.
5. **Primeira entrada da buzina final** sob a última palavra, e depois tarde demais por causa do fade geral. *Fazer diferente:* medir o início audível real e os tempos das palavras antes de posicionar.
6. **Bugs de ferramentas:**
   - ordem Fortran no DTW (resolvido com `np.ascontiguousarray`);
   - índice negativo no simulador;
   - registro de usos sobrescrito entre versões (sufixo por versão);
   - `__file__` ausente ao executar código com `exec`;
   - `git add` interrompido por arquivo ignorado.
   - *Fazer diferente:* testar ferramentas novas em casos pequenos e conhecidos antes de usar em produção.

---

## 13. Checklist para o próximo episódio

**Pré-produção**
- [ ] Roteiro com os tempos das palavras (`palavras.json`) desde cedo; conferir a ordem dos conceitos contra a imagem.
- [ ] Licença da narração definida antes: se houver intenção comercial, usar um plano que permita.
- [ ] Lista de fontes de som com licença verificada (CC0, Mixkit; CC BY só com créditos).

**Modelagem e cena**
- [ ] Evitar superfícies coplanares: volumes fantasmas, cortes e decalques (janelas, faixas) com folga ou prioridade de profundidade explícita.
- [ ] Interiores em corte sem sol direto (`sem_sombra`).
- [ ] Shaders usam tempo global (`uTempo`).

**Render**
- [ ] Configuração única e explícita: a mesma nos testes e no definitivo.
- [ ] Um processo por vez, com manifesto, checkpoints e verificação por quadro em escala grossa.
- [ ] Detector absoluto de cintilação em todos os segmentos antes de aprovar.
- [ ] Teste curto em resolução final nos trechos críticos.

**Som**
- [ ] Ganhos fixos por stem e master fixo nas comparações A/B.
- [ ] Gerador aleatório isolado para sons novos.
- [ ] Sons ligados a movimento real ou ao primeiro quadro visível do evento.
- [ ] Ambiente encerra junto com a fusão de imagem quando o cenário muda.
- [ ] Loudness e pico verdadeiro medidos no AAC final; clareza no celular simulado; mono.

**Entrega**
- [ ] Master sem legendas para trocar o áudio.
- [ ] Arquivos acima de 100 MB em partes com SHA-256.
- [ ] Relatório com números, limitações, licenças e "nada publicado".

---

## 14. Números de referência do Ep. 01

**Episódio**

| Item | Valor |
|---|---|
| Duração | 168,000 s · 5.040 quadros (5.148 renderizados com as fusões) · 30 fps |
| Revisão | 540 × 960 · ~3 s por quadro |
| Definitivo | 1080 × 1920 · 4,5–12 s por quadro · CRF 17 · 141,8 MB |

**Áudio**

| Item | Valor |
|---|---|
| Loudness / pico (AAC) | −14,1 LUFS · −2,0 dBTP |
| Narração | +3 ms, constante |
| Clareza no celular | voz ≥ 10 dB em ~96,6 % dos blocos |

**Correções e calibrações**

| Item | Valor |
|---|---|
| Oclusor do mar | 0,994 (0,6 % mais perto) |
| `janoff` | 1 |
| `fantoff` | 1 (só s08a) |
| Verificador do render | SSIM grosso ≥ 0,93 e diferença média ≤ 6 |
