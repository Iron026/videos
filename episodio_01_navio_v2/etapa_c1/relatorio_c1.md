# Episódio 01: ajustes v3b, motor em tempo real v2, benchmark e voz

Nesta entrega: correção do Quadro 3, verificação física do Quadro 4, comparação atualizada Three.js × Cycles, novo benchmark e estudo de redução de tempo.
O mascote 3D foi suspenso, como pedido: a imagem oficial 2D e a assinatura aprovada foram preservadas. **O animatic não foi iniciado, a narração completa não foi gerada e nada foi publicado.**

| Entregável | Arquivo |
|---|---|
| Quadro 2 v3 (sem alteração, para avaliação) | `etapa_c0/quadros/quadro2_v3.png` |
| Quadro 3 v3b (sem contêineres no convés) | `etapa_c1/quadros/quadro3_v3b.png` |
| Quadro 4 v3b (setas de pressão por regime) | `etapa_c1/quadros/quadro4_v3b.png` |
| Comparação Cycles × tempo real v2, inteiro e com detalhes ampliados | `motores/resultados_v2/comparacao_q2.jpg` e `comparacao_q3.jpg` |
| Dados do benchmark e SSIM | `motores/resultados_v2/analise.json`, `rt_*.json`, `cycles_q3/cycles.json` |
| Código | `blender/exportar_rt2.py`, `blender/bench_cycles2.py`, `motores/tempo_real_v2/`, `motores/analisar_v2.py` |

---

## 1. Quadros

**Quadro 2:** é o PNG final v3 (1080×1920, Cycles com 128 amostras), sem mudanças desde a última entrega, para a sua avaliação de silhueta, acabamento e composição.

**Quadro 3:** todos os contêineres do convés foram removidos. A cena agora mostra só o casco aberto: porão vazio, estrutura (cavernas, longitudinais, duplo fundo e tanques laterais em células), operários para escala e a linha d'água amarela atravessando a seção.

**Quadro 4, verificação da representação das forças:**
- **Verificação numérica,** feita na seção real a meia-nau com 9 m de calado, integrando a pressão p = ρ·g·h sobre todo o contorno molhado (costado, bojo curvo e fundo):

  | Grandeza | Resultado |
  |---|---|
  | Força horizontal total | **0,0000** (costado e bojo de um lado anulam os do outro) |
  | Força vertical total | **285,098 ρg** por metro |
  | Área submersa da seção | **285,098 m²** |
  | Diferença entre os dois | **0,000%** (princípio de Arquimedes por metro de comprimento) |
- **Correção gráfica:** na versão anterior, as setas eram distribuídas uniformemente pelo contorno. O bojo curvo (raio de 2,6 m) recebia só uma seta por lado, o trecho raso do costado não tinha nenhuma, e as setas do fundo caíam todas no mesmo ponto, porque o fundo plano é um único segmento na malha. Agora as setas seguem os três regimes:
  - **Costado vertical:** setas horizontais a 1,2 m, 3,2 m e 5,2 m de profundidade, crescendo com a profundidade.
  - **Bojo curvo:** setas com a normal a 22,5°, 45° e 67,5°. A direção gira continuamente de horizontal para vertical, e o comprimento acompanha a profundidade de cada ponto.
  - **Fundo plano:** setas verticais e todas iguais, porque o fundo inteiro está na mesma profundidade. O centro fica livre para a seta do empuxo.
- **Em todas:** cada seta é perpendicular à superfície local, aponta para o casco (compressão) e tem comprimento proporcional a ρ·g·h. Empuxo e peso continuam iguais, opostos e na mesma vertical.

## 2. Motor em tempo real v2 (Three.js)

**O que mudou em relação à v1:**

| Aspecto | v1 | v2 |
|---|---|---|
| Materiais | Só a cor média de cada material | Shaders com os mesmos parâmetros do Blender, exportados como metadados: ruído de cor e de rugosidade da pintura, aço escovado, concreto, areia com ondulações, corrugação dos contêineres, faixas de pintura do casco, face de corte com linha d'água, relevo procedural |
| Luz | Sol + céu | Sol + céu com nuvens (mesmo degradê e ruído do Blender) + luz de rebatimento do chão simulada + oclusão de ambiente; sob a água, luz direta e indireta atenuadas pela coluna d'água |
| Água | Superfície semitransparente | Espessura real por pixel (profundidade da cena menos profundidade da água) com absorção Beer-Lambert usando os mesmos coeficientes do volume do Cycles, refração, Fresnel com reflexo do céu, brilho do sol e marolas que somem com a distância |
| Sombras | Mapa fixo, com serrilhado | Mapa de 4096² ajustado à região vista pela câmera |
| Raios de luz | Não havia | Feixes aditivos com o mesmo perfil do Blender |

**Bug corrigido durante o trabalho:** o primeiro ajuste do mapa de sombras usava uma matriz sem translação, e as sombras do sol desapareciam. Encontrei pela comparação com o Cycles e corrigi.

**Comparação visual** (`comparacao_q2.jpg` e `comparacao_q3.jpg`, cada uma com o quadro inteiro e 3 detalhes ampliados):
- **Muito próximos:** composição, cores, sombra do sol (inclusive a do casco no leito e a do piso do porão), linha d'água, absorção da água com a profundidade, céu e textura dos materiais.
- **Diferenças que continuam:**
  1. **Luz rebatida real:** no Cycles, as cores refletem umas nas outras (por exemplo, o primer vermelho no próprio casco). No tempo real isso é aproximado, e as áreas em sombra ficam mais azuladas, como o piso do porão.
  2. **Superfície do mar:** o tempo real fica mais azul-saturado e com marolas mais finas. O Cycles tem reflexos mais suaves e esverdeados.
  3. **Aço estrutural:** ficou um pouco mais granulado de perto.
  4. **Ocultação do céu em grande escala:** sob o casco, o Cycles escurece mais. No tempo real isso é compensado por uma regra de profundidade, não calculado.

## 3. Novo benchmark e custo computacional
**Condições:** mesma máquina (4 núcleos de CPU, **sem GPU**, WebGL emulado na CPU), um motor por vez, 4 quadros consecutivos com a câmera em movimento. Para medir "perda perceptível", cada variante foi comparada com a referência de qualidade máxima do mesmo motor por **SSIM** (1,0 = idêntico; ≥ 0,99 é em geral imperceptível; perto de 0,97 já se nota perda de nitidez).

### Tempo real v2 (1080×1920)
| Variante | Quadro 2 | SSIM | Quadro 3 (água) | SSIM |
|---|---|---|---|---|
| Referência (GTAO com 16 amostras, MSAA 4×) | 9,33 s | 1,000 | 10,87 s | 1,000 |
| Sombra em cache (cena estática) | 8,64 s | 0,998 | 10,31 s | 0,998 |
| Cache + GTAO com 8 amostras | 8,24 s | 0,998 | 10,50 s | 0,997 |
| Cache + GTAO 8 + MSAA 2× | 8,18 s | 0,998 | 10,38 s | 0,997 |
| Sem oclusão de ambiente | 6,57 s | 0,996 | 8,37 s | 0,995 |
| Resolução de 75% ampliada | 5,39 s | **0,974** | 6,56 s | **0,971** |

### Cycles, Quadro 3 com água (540×960; a resolução cheia custa cerca de 4 vezes mais)
| Variante | Tempo | SSIM |
|---|---|---|
| 128 amostras (referência) | 88,9 s | 1,000 |
| 64 amostras | 56,3 s | 0,999 |
| **32 amostras** | **30,7 s** | **0,996** |
| 16 amostras | 17,2 s | 0,993 |
| 32 amostras + limiar adaptativo 0,05 | 30,3 s | 0,996 |
| 32 amostras + menos saltos de luz (4/2/2/4) | 31,1 s | 0,996 |
| 32 amostras + dados persistentes (2º quadro) | 28,1 s | 0,996 |
| 32 amostras a 70% da resolução, ampliada | 15,5 s | **0,979** |

### O que reduz tempo sem perda perceptível
- **Cycles:**
  - **Reduzir amostras de 128 para 32** é o grande ganho: 2,9 vezes mais rápido com SSIM de 0,996. A redução de ruído (OIDN) compensa.
  - Com 16 amostras ainda se mantém SSIM de 0,993, mas é o limite.
  - **Dados persistentes** economizam cerca de 8% por quadro numa animação.
  - Mexer no limiar adaptativo ou no número de saltos de luz não faz diferença mensurável nestas cenas.
- **Tempo real:**
  - **Cache do mapa de sombras** (quando só a câmera se move) e **GTAO com 8 amostras** dão juntos de 4 a 12% de ganho, sem perda visível (SSIM ≥ 0,997).
  - **Desligar a oclusão de ambiente** economiza de 23 a 30% e o SSIM continua alto (0,995), mas perde-se o contato visual entre objetos (pés no chão, cantos). Isso é perda artística que o SSIM subestima, então não recomendo.
- **Nos dois motores, reduzir a resolução não vale:** SSIM entre 0,971 e 0,979, com perda de nitidez visível nas legendas, cabos e bordas.
- **Onde está o grande ganho de verdade:** nesta máquina, mais de 90% do tempo do motor em tempo real é a GPU emulada na CPU. **Com qualquer GPU comum, o mesmo código roda em frações de segundo por quadro** (estimativa, não medida aqui).

### Projeção de custo nesta máquina, com a configuração recomendada
| Motor | Por quadro | Animatic de 12 s (360 quadros) | Episódio de 93 s (2.790 quadros) |
|---|---|---|---|
| Tempo real v1 (anterior) | 5,8 s | 35 min | 4,5 h |
| **Tempo real v2 (cache + GTAO 8)** | **8,2 a 10,5 s** | **≈ 56 min** | **≈ 7,3 h** |
| Cycles, 32 amostras, resolução cheia | 68 a 123 s | 7 a 12 h | 53 a 95 h |

A v2 custa cerca de 60% a mais que a v1 por causa dos shaders mais ricos e da água. Continua 7 a 12 vezes mais rápida que o Cycles otimizado, e cabe neste ambiente.

**Recomendação técnica:**
- Manter o Three.js v2 como motor de animação, com cache de sombras e GTAO de 8 amostras.
- Usar o Cycles com 32 amostras e dados persistentes para quadros de destaque e miniaturas. Não usar mais 128 amostras.
- Antes do animatic, eu atacaria as diferenças 1 e 2 (rebatimento e superfície do mar), se você considerar que elas comprometem a aprovação visual.

## 4. Narração (ElevenLabs)
- **Conector:** está autenticado nesta sessão. Conta no plano **gratuito**, com 0 de 10.000 créditos usados no ciclo, sem cobrança extra (`current_overage` = 0). A voz **Will - Deep** (`CstacWqMhJQlnfLPxRG4`) está acessível pela conta.
- **Preparado no fluxo "De Olho no Invisível · Ep01 · teste de voz":** um nó com `eleven_multilingual_v2`, idioma `pt`, stability 0,50, similarity boost 0,75, style 0, speed 1,0, e exatamente o texto pedido (204 caracteres).
- **Custo estimado antes de gerar:** 204 créditos para 1 geração, dentro do saldo e sem cobrança.
- **Resultado:** tentei a geração única duas vezes, em rodadas diferentes. Nas duas, a ElevenLabs respondeu que **a fila de gerações gratuitas estava ocupada**. A geração não começou e **nada foi cobrado** (o saldo segue em 0 usados). Segui a orientação do serviço e não insisti na mesma rodada.
- **Próximo passo:** basta pedir de novo e eu rodo a mesma geração única. O áudio será salvo em `voz/`, com o relatório de créditos.
- **Licença:** no plano gratuito, a amostra serve para avaliação. Para uso no vídeo monetizado, a ElevenLabs exige plano pago, com o áudio gerado durante a assinatura.

**Aguardo sua aprovação da qualidade visual (quadros 2, 3 e 4 e a comparação dos motores) e, depois, da amostra de voz, antes de avançar.**
