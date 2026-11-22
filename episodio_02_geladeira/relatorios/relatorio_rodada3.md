# Ep. 02 · Relatório da rodada 3 (personagem na abertura e revelação do circuito)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado.
Render em 1080 p **não iniciado**, sem polimento definitivo e sem sound design. A narração aprovada está intacta (SHA-256
`fdedd877…`, conferido). O roteiro não mudou e a duração continua **151,23 s**.

## Entregas
| Arquivo | O que é |
|---|---|
| `episodio/ep02_animatic.mp4` | Animatic **V3** (540 × 960, 30 qps, 151,23 s, 24,6 MB, narração aprovada, −16,4 LUFS de prévia). SHA-256 `08847f26…` |
| `episodio/ep02_v2_x_v3_trechos.mp4` | **V2 \| V3 lado a lado**, só os trechos alterados (abertura 0–10,6 s; revelação 28,2–38,5 s; porta aberta 115,2–119,6 s), com áudio |
| `episodio/ep02_v3_revelacao_circuito.mp4` | **Demonstração da revelação** (28,2–43,2 s da V3) |
| `relatorios/revelacao_circuito_v3.jpg` | A revelação quadro a quadro, com a palavra falada em cada instante |
| `relatorios/personagem_referencia_v3.jpg` | **Referência do personagem**: giro (frente, 3/4, perfil, costas), 3 expressões, visão térmica e paleta |
| `relatorios/antes_depois_v3_1.jpg`, `_2.jpg` | Antes (V2) × depois (V3): A1, A2, A4 · C1, C2, I1 |
| `relatorios/v2_x_v3_montado.json` | Comparação quadro a quadro V2 × V3 do vídeo montado |

A V2 continua no git (commit `a05d45f`).

## 1. Identidade do personagem (consultada antes de desenhar)
- **Existe um mascote oficial:** `episodio_01_navio_v2/referencias/mascote_oficial.png` (menino explorador com óculos,
  casaco azul-marinho e lenço amarelo). O protótipo 3D dele nunca foi aprovado ("modelagem 3D suspensa").
- **Decisão:** o personagem do Ep. 02 é **original e deliberadamente diferente** do mascote, que **não foi usado nem
  redesenhado**. Motivos:
  - o pedido foi um "bonequinho 3D original" que represente o espectador, não uma assinatura do canal;
  - usar o mascote exigiria um modelo 3D aprovado, que não existe.
- **"O morador":** adulto com proporções levemente estilizadas, formas arredondadas e materiais foscos, no estilo do episódio.
  - **Cores neutras:** suéter cinza-mescla, calça grafite, tênis claro. Não usa azul, laranja, âmbar, violeta nem
    amarelo, que são a linguagem didática do episódio.
  - **Expressão sem fala:** olhar, pálpebras, sobrancelhas, inclinação da cabeça e postura.
  - **Visão térmica:** o corpo aparece morno (pele 33 °C, roupa 30 °C).
- **Construção:** partes rígidas articuladas (`blender/personagem.py`), animadas pelo exportador existente.
  - A mão **segue o puxador por cinemática inversa**, com a mesma curva de ângulo da porta (`blender/encenacao02.py`).
  - Os gestos estão ancorados nos instantes verificados das palavras.

## 2. O que mudou
| Plano | V2 | V3 |
|---|---|---|
| **A1** (0–1,35 s) "Você já reparou que a geladeira" | Geladeira sozinha; a porta abria sozinha | O personagem, na cozinha, **abre a porta**: a mão segura o puxador, puxa até ~38° e solta. Plano médio com ele e a geladeira |
| **A2** (1,35–2,73 s) "é fria por dentro" | Interior com varredura térmica | Por cima do ombro dele: o interior em primeiro plano e a mão dele apoiada no batente. A varredura térmica revela o frio |
| A3 (2,73–4,87 s) | — | **Inalterado** (o personagem recua fora de quadro) |
| **A4** (4,87–10,14 s) "Parece estranho… ao mesmo tempo?" | Tela dividida frente × traseira | Tela dividida igual. Nos momentos de tela inteira, um **contraplano de dentro da geladeira** mostra o rosto dele. Em "Parece estranho", ergue as sobrancelhas e inclina a cabeça. Em "ao mesmo tempo?", leva a mão ao queixo. O olhar alterna entre o interior e o alto da traseira |
| **C1** (28,46–33,92 s) "…de um jeito que você nunca viu." | Corte ilustrativo já começava aqui | **Externo, com a cozinha.** A porta fecha e a câmera se aproxima pelo lado. Nada é cortado ainda |
| **C2** (33,92–38,02 s) "Escondido atrás das paredes, existe um circuito fechado de tubos." | Mesmo ângulo de C1; circuito já revelado; fusão de 0,2 s | **Corte seco no ataque real de "Escondido"** (33,92 s; medido: salto de 0,1 → 75 entre quadros em 33,933 s), para um **ângulo traseiro-lateral**. Detalhes abaixo |
| **I1** (115,6–119,18 s) "…quando você deixa a porta aberta." | Geladeira sozinha | O personagem entra, abre a porta em "deixa", solta e **sai de quadro**: a porta fica aberta (rima com A1) |

**Detalhes da revelação em C2:**
- **Posições reais respeitadas:** compressor e condensador já estão à vista na traseira, porque são **externos**. O corte
  varre a lateral e expõe só o que estava escondido: a linha de sucção **dentro** da parede traseira e o evaporador no
  congelador.
- **A câmera segue o fluido:** um pulso sai do compressor e percorre o circuito inteiro. A câmera acompanha
  (condensador → capilar → evaporador → sucção) e termina no circuito todo, **fechado**.

Montagem:
- Corte de C1 para C2 sem antecipação (os demais cortes mantêm os 0,25 s).
- Corte seco em C2, sem fusão.
- O aviso "Corte ilustrativo" passa a começar em C2.

## 3. O que foi preservado (medido)
- **35 dos 41 planos renderizados têm quadros idênticos byte a byte aos da V2.** Não foram renderizados de novo; só A1,
  A2, A4, C1, C2 e I1 mudaram.
- **No vídeo montado, fora dos trechos pedidos:** diferença média de **0,077** (escala 0–255), máximo de 1,02. Só 4
  quadros isolados passam de 1,0 (12,33, 48,43, 48,5 e 124,3 s, todos colados em cortes): é ruído da compressão H.264,
  não conteúdo.
- **Também iguais:**
  - narração, roteiro, legendas (mesmos tempos verificados) e duração;
  - ciência, modelo do ciclo, shaders e configuração de render;
  - todos os planos de B a J, exceto C1, C2 e I1.

### Defeito meu, encontrado e corrigido nesta rodada
Na primeira montagem da V3, I3 aparecia diferente da V2 entre 127,3 e 129,6 s, embora os quadros fossem idênticos.

- **Causa:** as pré-visualizações tinham reexportado A3, I2, I3 e I4 com câmeras experimentais (depois revertidas). Os
  rótulos 2D, que a montagem lê da cena, ficaram com as posições daquelas câmeras.
- **Correção:** reexportei os quatro planos com o código final e a diferença sumiu.
- **Lição:** pré-visualização também altera dados que a montagem usa.

## 4. O personagem ajuda ou disputa atenção com a geladeira?
Eu meço; a avaliação final é sua. Pela análise dos quadros:

- **Ajuda em A1 e I1.** Dá motivo humano e escala ao gesto mais cotidiano ("abrir a geladeira"). Em I1, torna literal o
  "você deixa a porta aberta". A geladeira segue no centro do quadro e a ação é sobre ela.
- **Neutro em A2.** Aparece só o braço apoiado no batente; o interior domina.
- **Disputa atenção em A4, por desenho e por pouco tempo:** ~1,9 s somando o início e o fim, no momento da pergunta.
  Durante os ~3,5 s da tela dividida, que é o argumento visual, ele não aparece.
- **Presença total:** ~7 s de 151 s (≈ 5 %), só na abertura e na porta aberta. Ausente de toda a explicação científica
  (C a H) e da conclusão (J), para não virar assinatura.
- **Ponto fraco:** no início de A4 ainda está em visão térmica, e o corpo morno (30–33 °C, só ~8 K acima da cozinha)
  sai bege e apagado. É física correta, mas a leitura do rosto em "Parece estranho" fica fraca. Opções:
  1. manter;
  2. começar A4 já em imagem normal;
  3. tirar o contraplano do início e deixar só o do fim.

## 5. Problemas ainda existentes
- O início de A4 em visão térmica (acima).
- O personagem é de animatic: articulações rígidas e caminhada simples. Mãos e roupa precisam de polimento se ele for
  aprovado.
- No contraplano de A4, o fundo (parede lateral com janela) está simples.
- Os pendentes da rodada 2 continuam: B7 (paleta abaixo de 0 °C), arames em E1 e o fundo liso de G3.

## 6. Licença
- **Narração:** plano da ElevenLabs **não confirmado**. Até você informar, a narração fica tratada como plano gratuito
  (sem uso comercial, atribuição obrigatória).
- **Personagem e cenários:** modelados do zero neste projeto, sem recursos de terceiros.
- **Mascote oficial:** não usado.
