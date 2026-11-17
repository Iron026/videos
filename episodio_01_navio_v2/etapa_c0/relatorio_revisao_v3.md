# Episódio 01: revisão v3 (correções obrigatórias antes da Etapa C)

Esta revisão responde à aprovação parcial da direção visual. **O animatic não foi iniciado e nenhum episódio foi produzido.**

| Entregável | Arquivo |
|---|---|
| Quadros 2, 3 e 4 refeitos (1080×1920, Cycles com 128 amostras) | `etapa_c0/quadros/quadro{2,3,4}_v3.png` |
| Protótipo 3D do mascote (3 vistas, 1080×1080) | `mascote/mascote_{34,frente,perfil}_100.png` |
| Mesmo quadro nos dois motores | `motores/resultados/comparacao_motores.jpg` e `comparacao_motores_detalhe.jpg` |
| Dados brutos do benchmark | `motores/resultados/bench_*.json` |
| Código | `blender/quadros.py`, `navio.py`, `mascote.py`, `exportar_tempo_real.py`, `bench_cycles.py`, `motores/tempo_real/` |

Os arquivos aprovados foram preservados: `etapa_b/quadros/` (v2), `referencias/mascote_oficial.png` e a assinatura atual não foram alterados.

---

## 1. Quadro 2: estaleiro

**Pedido:** silhueta naval reconhecível, proa, curvatura do costado e detalhes da construção.

**O que mudou:**
- **O casco é montado em blocos.** Cada chapa de costado é uma superfície curva que segue a forma real do casco, a mesma função usada na hidrostática. Antes, o costado era um conjunto de caixas retas.
- **Proa reconhecível:** o bloco de proa está inteiro, com bulbo, roda de proa e cinta do convés. O fundo e o bojo estão chapeados até a proa.
- **Construção em andamento:** o costado alto vai rareando da meia-nau para vante, e as cavernas e longitudinais aparecem pelos vãos.
- **Ação na cena:** o pórtico iça exatamente o painel que falta no costado, logo acima do vão onde ele vai entrar. Isso dá uma ação clara para o animatic.
- **Câmera:** a três quartos da proa, baixa, em escala humana. Foi escolhida por busca numérica, para que proa, painel, gancho e viga caibam na área útil do quadro.
- **Cenário mais vivo:** operários, empilhadeira, pilhas de chapas, árvores, bandeiras e galpões com portões e janelas.

**Limitação que continua:** o casco ainda não tem as linhas de solda finas nem a numeração dos blocos. São texturas de detalhe que entram na fase de animação.

## 2. Quadro 3: corte interno

**Pedido:** mostrar que o casco envolve um grande volume que não é aço maciço, com estrutura e linha d'água evidentes.

**O que mudou:**
- **Porão vazio e aberto**, sem contêineres e sem tampa de escotilha.
- **Estrutura à mostra:** cavernas e longitudinais nas paredes, guias de célula, escada e braçolas amarelas.
- **Escala:** dois operários no piso do porão e um no convés lateral.
- **Leitura do corte:** o aço aparece como uma casca fina (costado, duplo fundo em células, tanques laterais) em volta do grande espaço vazio.
- **Linha d'água amarela atravessando a seção inteira.** Ela mostra que o piso do porão fica cerca de 7 m abaixo do nível do mar e que, mesmo assim, o porão está seco. Abaixo da linha, a face de corte muda para um tom frio.
- **Câmera elevada**, olhando para dentro do porão.

**Ponto para decidir:** os contêineres no convés ficaram só nas baías de ré, como contexto de "navio de carga". Se preferir, removo todos para a leitura ficar ainda mais limpa.

## 3. Quadro 4: empuxo

**Pedido:** navio submerso legível e relação clara entre volume deslocado, pressão e empuxo, com física precisa.

**Por que mudou de abordagem:** testei duas alternativas antes da versão final.
- Vista diagonal por baixo da proa: as setas ficavam escondidas atrás do casco.
- Raio-X do casco inteiro: o volume deslocado ficava pequeno e longe.

**Versão final:** corte a meia-nau no mesmo plano do oceano, com o navio flutuando.
- **A área submersa da seção fica em ciano translúcido.** É o volume deslocado por metro de comprimento, e através dele se vê a estrutura (duplo fundo e tanques).
- **Linha d'água amarela no corte e ao longo do costado.**
- **Setas de pressão** perpendiculares ao casco, com comprimento proporcional à profundidade (p = ρ·g·h):
  - no costado são horizontais, curtas perto da superfície e longas embaixo, e as de bombordo anulam as de boreste;
  - no fundo são todas iguais e verticais, porque o fundo está todo na mesma profundidade;
  - a soma delas é o empuxo.
- **Empuxo (amarelo) e peso (azul):** mesmo comprimento, mesma vertical e sentidos opostos, ou seja, equilíbrio.
- **Iluminação:** casco e corte iluminados, água límpida e setas que não refletem nem projetam sombra.

**Verificação física:** calculei o centro de carena para 9 m de calado com a mesma função de forma do casco: V = 44.125 m³, centro em x = 0,4 m e z = 4,7 m. O corte fica a 2,8 m do centro de carena, então desenhar as duas forças na seção é uma representação fiel.

## 4. Protótipo 3D do mascote (etapa separada)

**O que foi feito:** busto modelado por código a partir da imagem oficial, renderizado em três vistas (três quartos, frente e perfil) com luz principal quente e contraluz azul, como na arte.

**O que está fiel:**
- paleta (pele, castanho, azul-marinho, amarelo);
- cabelo castanho espetado e facetado;
- óculos de exploração com lentes âmbar sobre a cabeça e tira amarela;
- olhos grandes e castanhos, olhando para cima e para a direita, com brilho;
- sobrancelhas grossas, sorriso aberto com dentes e língua;
- capuz e casaco azul-marinho, lenço amarelo, alças marrons com fivelas amarelas.

**O que ainda não está fiel. É um protótipo, não um modelo aprovável:**
- **Cabeça e expressão:** o rosto é mais redondo e "bonecão" que a arte. O queixo e o maxilar precisam ser mais definidos, e o sorriso está mais largo e mais baixo que o original.
- **Cabelo:** o volume está bom, mas a franja precisa cair mais sobre a testa. As mechas da arte são mais longas e curvas.
- **Corpo:** o tronco está largo e "inflado". Na arte, o capuz e a gola do casaco são mais altos e o lenço é dobrado em triângulo.
- **Peso dos óculos:** na arte eles são mais grossos e aparecem mais, à frente do cabelo.

**Recomendação:** para chegar a um modelo aprovável, o caminho mais confiável é escultura manual (Blender sculpt) por um artista, usando este protótipo como base de proporções e cores. Também é possível continuar por código, iterando com você por partes (rosto → cabelo → roupa).

Conforme pedido: o modelo **não foi incluído em nenhum quadro**, a imagem oficial não foi substituída e a assinatura atual foi preservada.

## 5. Comparação entre motores e benchmark

**Teste controlado:**
- **Mesmo quadro:** o Quadro 2 v3 foi exportado do Blender para o motor em tempo real (`exportar_tempo_real.py`).
- **Mesmos elementos:** geometria idêntica (117.774 triângulos), mesma câmera (posição, direção e FOV), mesmo sol, mesmo degradê de céu, mesmas cores e rugosidades, mesmo mapeamento de tons (Khronos PBR Neutral).
- **Ambiente:** os dois motores rodaram na mesma máquina (4 núcleos de CPU, **sem GPU**), com a CPU ociosa e um motor por vez.
- **Medição:** cada benchmark renderiza quadros consecutivos com a câmera deslocando como num movimento real, e o tempo foi medido quadro a quadro.

**Motores:**
- **Cycles:** traçado de caminhos com redução de ruído OIDN.
- **Tempo real:** Three.js r170 (WebGL2) com:
  - sombras PCF suaves (mapa 4096²);
  - iluminação de ambiente gerada do próprio céu (PMREM);
  - oclusão de ambiente GTAO;
  - MSAA 4×.

  Rodou no Chromium com WebGL por software (SwiftShader), porque não há GPU.

### Tempos medidos e projeções
| Configuração | Por quadro (medido) | Animatic de 12 s (360 quadros) | Episódio de 93 s (2.790 quadros) |
|---|---|---|---|
| Cycles, 128 amostras, 1080×1920 (qualidade dos quadros entregues) | 190,2 s | 19,0 h | 147 h |
| Cycles, 32 amostras, 1080×1920 | 68,0 s | 6,8 h | 52,7 h |
| Cycles, 32 amostras, 540×960 (prévia) | 18,5 s | 1,9 h | 14,4 h |
| **Tempo real + AO, 1080×1920** | **5,8 s** | **0,6 h** | **4,5 h** |
| Tempo real + AO, 540×960 (prévia) | 2,1 s | 0,2 h | 1,6 h |
| Tempo real sem AO, 540×960 | 1,35 s | 0,13 h | 1,0 h |

- **Diferença de velocidade:** o tempo real foi **12 vezes mais rápido** que o Cycles com 32 amostras e **33 vezes** que o Cycles com 128, na mesma CPU.
- **Por que o tempo real fica lento aqui:** sem GPU, ele é emulado na CPU. **Numa GPU comum, ele roda em menos de 0,05 s por quadro.** Esse número é estimativa, não medição.
- **Quadros com água volumétrica** (os antigos 1 e 4) custaram de 15 a 19 min no Cycles, contra cerca de 3 min deste quadro. A tabela acima mede o caso mais leve do Cycles.

### Qualidade visual: o que se vê na comparação
**Cycles com 128 e com 32 amostras ficaram praticamente idênticos neste quadro**, graças à redução de ruído. Se o Cycles for usado, 32 amostras bastam: o render fica 2,8 vezes mais rápido sem perda visível.

**O tempo real reproduz composição, cores, formas e sombra principal com fidelidade.** As perdas visíveis estão no recorte de detalhe:
1. **Sem luz rebatida:** o interior do casco e as faces na sombra ficam mais escuros e mais uniformes. O Cycles mostra o rebatimento quente do primer no próprio casco.
2. **Sombras com serrilhado:** há serrilhado e listras finas nas sombras das cavernas sobre o chão. Pode ser corrigido com cascatas de sombra e ajuste de bias.
3. **Materiais mais lisos:** a exportação levou só a cor média de cada material. O ruído de pintura, a escovação do aço e o relevo ficaram de fora. É uma limitação do exportador deste teste, não do motor: esses efeitos podem ser recriados em shader.
4. **Água volumétrica e cáusticas:** o tempo real não as tem prontas. Seria preciso um shader estilizado de água (absorção por profundidade e cáusticas animadas), como o que já existe na v1.

## 6. Recomendação técnica

**Recomendo usar o tempo real (Three.js) como motor de produção da animação e manter o Blender e o Cycles como ferramenta de modelagem e de quadros de referência.**

1. **Viabilidade:** é o único caminho viável neste ambiente.
   - Episódio completo: 4,5 h, contra 53 a 147 h.
   - Animatic: 35 min, contra 7 a 19 h.
   - Com GPU, vira tempo real de fato e permite várias iterações por dia.
2. **Aderência à direção pedida:** a aparência "estilizada de alta qualidade", com cores chapadas, formas bem definidas, luz clara e sombras suaves, depende mais de modelagem, cor e composição que de iluminação global fisicamente exata. É também o tipo de visual observado nos quadros da referência.
3. **Mesmo conteúdo nos dois motores:** a cena é construída uma vez no Blender (`quadros.py`) e exportada. O Cycles continua disponível para miniaturas, quadros de destaque e conferência de aparência, sem retrabalho de modelagem.
4. **Validação já feita:** o render em segmentos, a montagem com FFmpeg, as legendas e a validação técnica já foram testados nesse motor na v1.

**Antes do animatic, para fechar as diferenças de qualidade:**
- shaders de material com ruído, relevo e anisotropia do aço;
- água estilizada (absorção, espuma, cáusticas animadas);
- sombras sem serrilhado (cascatas e bias);
- luz de rebatimento simulada (luz hemisférica com a cor do chão e luzes de preenchimento por plano).

Sugiro validar isso com **um quadro de teste no motor em tempo real refeito**, comparado lado a lado com o Cycles, antes de qualquer animação.

**Alternativa, se você preferir o acabamento do Cycles:** renderizar em um computador com GPU NVIDIA RTX ou Apple Silicon, com 32 amostras e redução de ruído. Os mesmos scripts rodam lá, e a aceleração típica do Cycles em GPU frente a esta CPU de 4 núcleos fica entre 10 e 30 vezes (estimativa, não medida aqui), o que daria cerca de 2 a 5 h por episódio.

## 7. Pendências
- **Voz Will - Deep (ElevenLabs):** continua pendente, como você pediu. Não pedi chave nem a coloquei no código. Uma amostra gerada no site, com licença comercial (plano pago), pode ser adicionada em `voz/` para testar a integração no animatic.
- **Referência Desmontando o Mundo:** a análise segue limitada aos 75 quadros estáticos públicos. Movimento, ritmo e narração não foram observados.
- **Quadros 1 e 5:** aprovados no conceito. Os refinamentos pedidos (impacto e movimento do bloco; modelagem do navio e do portêiner com carregamento animado) ficam para a fase de animação, junto com a escolha do motor.

**Aguardo sua aprovação dos quadros 2, 3 e 4, do caminho para o mascote e da escolha do motor antes de iniciar o animatic.**
