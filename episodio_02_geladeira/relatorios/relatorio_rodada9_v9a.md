# Ep. 02 — Rodada 9, entrega 1: V9a (só composição)

**Arquivo:** `episodio/ep02_v9a_revisao.mp4` (revisão 540 × 960, 30 fps, 4.537 quadros, 151,233 s).
**Comparar com:** `episodio/ep02_v8_revisao.mp4` (V8, preservada; cenas da V8 arquivadas em `arquivo/cenas_v8.tgz`).

A V9a usa **os mesmos quadros 3D da V8**. Mudam só as camadas 2D: legendas, avisos, rótulos, cartões de pressão e lupa.
Tudo fica atrás da chave `COMPOSICAO_R9=1`. Com a chave desligada, a montagem reproduz a V8 pixel a pixel (12 instantes
comparados).

Eu meço; não assisto nem escuto como uma pessoa. A avaliação estética é sua.

## O que mudou

### 1. Legendas por unidades de sentido (`episodio/legendas_r9.py`)

| | V8 | V9a |
|---|---|---|
| Blocos | 123 | 65 (até 2 linhas) |
| Terminam em palavra fraca (artigo, preposição, conjunção) | 31 | **0** |
| Linha terminando em palavra fraca / palavra sozinha na linha | — | 0 / 0 |
| Blocos com menos de 0,6 s | 24 | **0** (penalizados, não forçados) |
| Texto igual à narração, palavra a palavra | sim | **sim** (verificado) |
| Início de cada bloco | ataque da 1ª palavra | ataque da 1ª palavra |

- **Frases finais:** aparecem inteiras, "A geladeira não cria frio" e "Ela dá um destino ao calor". Segue a convenção do
  episódio: sem ponto final na legenda.
- **Pausa longa no meio de um bloco (> 0,45 s):** a parte seguinte entra no ataque da palavra, com a mesma disposição.
  Acontece em 3 blocos.
- **Lista completa dos blocos:** `relatorios/legendas_r9_blocos.txt`.

### 2. Áreas seguras e posição da legenda

- **Zonas usadas:** a soma das margens mais restritivas dos guias de Shorts e Reels.
  - topo 250 px, base 340 px e coluna de botões 120 px à direita (em 1080 × 1920);
  - a margem de 670 px na base, citada por alguns guias de Reels, foi testada à parte e aparece desenhada nas folhas.
  - Não há especificação oficial confirmada; são números de guias de terceiros.
- **Posição da legenda:** não fixei 64 % nem 66 %. A altura é escolhida por bloco, entre 59 % e 74 %, por custo medido:
  - zonas de interface;
  - rosto do personagem (projetado da cena);
  - âncoras de rótulos e cartões, que marcam mecanismos;
  - o próprio compressor e o evaporador, quando estão à vista;
  - a lupa.
  - Mudar de altura custa caro: são **3 mudanças em 64 trocas de bloco**.
  - Resultado: 68 % em 49 blocos, 71 % na abertura (fica abaixo do rosto) e 74 % em 9 blocos.
- **Largura máxima:** 840 px, simétrica e fora da coluna de botões.
- **Avisos ("Corte ilustrativo" etc.):** desceram para baixo da faixa superior. O aviso da lupa ficou preso ao próprio anel.
- **Lupa do G3:** do mesmo tamanho, um pouco abaixo e à esquerda (topo a 280 px), livre dos avisos.
- **Folhas com as zonas desenhadas:** `comparativos_r9/zonas_v8_v9a_1.jpg` e `_2.jpg`.
  - vermelho = Shorts;
  - contorno azul = Reels;
  - tracejado = margem conservadora de 670 px.

### 3. Cartões de pressão (só visual)

- **O que mudou:**
  - título "pressão" em 38 px, sobre extremos "baixa" e "alta" em 29 px, mais discretos;
  - escala com 3 marcas (baixa, meio, alta);
  - arco preenchido até o valor, com marcador maior;
  - fundo opaco (o fundo não vaza mais);
  - linha de ligação mais fina.
- **Alternativa testada e descartada:** ponteiro de agulha. Nos extremos (0 e 1), que são os estados deste episódio, a
  agulha fica deitada sobre a base e lê pior que o arco. Ver `comparativos_r9/zoom_cartoes.jpg`.
- **Física preservada:** em todos os 300 ponteiros desenhados no teste, o valor é idêntico ao de `manometros2d.json` e o
  ângulo vem da mesma fórmula da V8.

### 4. Rótulos e linhas de chamada

**Âncoras corrigidas** (`episodio/rotulos_r9.py`):

| Plano | Rótulo | Antes, na V8 (quadros com a âncora fora) | Agora |
|---|---|---|---|
| C3 | "fluido refrigerante" | 51/51 | 0 — preso ao tubo de cobre visível |
| D1 | "Evaporador" | 111/111 | 0 — na serpentina visível |
| D3 | "fluido mais frio que o ar" | 100/100 (linha para fora da tela) | 0 — linha curta até o tubo do evaporador |
| D4 | "entra: líquido + vapor" | 62/62 | 0 — na boca visível do canal |
| E4 | "ar da cozinha" | 26/26 | 0 |
| F2 | "entra: vapor quente" | 27/27 | 0 |

- **Como foi feito, sem reexportar nem renderizar:** a projeção das âncoras 3D pela câmera gravada em cada quadro
  reproduz o Blender com erro ≤ 0,00005. Os tempos e a opacidade de cada rótulo são copiados da V8, então ele continua
  entrando na palavra.
- **G3z:** a linha "fora do quadro" do G3z nunca aparece no vídeo. Esse plano só é mostrado dentro da lupa, e a lupa só
  desenha os rótulos que estão dentro do círculo. Nada a mudar.
- **Regras novas:**
  - nenhuma linha com âncora fora da tela;
  - rótulos que se encostam se afastam;
  - rótulo que encostaria num aviso desce;
  - linhas de ligação **interrompidas** onde passariam sob a legenda ou um aviso, com um vão de 14 px;
  - os cartões não ficam na coluna de botões.

### 5. Teste da composição em 1.513 quadros (um a cada 3, em 1080)

**0 problemas** (`relatorios/teste_composicao_r9.json`):
- nenhuma sobreposição entre legenda, rótulos, cartões, avisos e lupa;
- nada cortado pela borda;
- nada dentro das zonas de interface;
- nenhuma linha sobre texto;
- nenhuma legenda sobre o rosto;
- 300 de 300 ponteiros iguais ao modelo.

### 6. Divergência do manifesto do D1: resolvida com prova

- `cena.json` idêntico.
- 60 malhas iguais byte a byte e 2 iguais com outra ordem dos triângulos.
- Só `rotulos2d.json` mudou, e ele é composição.
- O manifesto recebeu o registro da prova (`relatorios/prova_reuso_D1_r9.json`). Nenhum manifesto diverge agora.

## O que ficou idêntico (medido)

- **Imagem 3D:** fora das camadas 2D, V9a e V8 têm **0 pixels diferentes** em 152 quadros comparados
  (`relatorios/v8_x_v9a_so_composicao.json`).
- **Áudio:** o áudio decodificado do AAC é **idêntico** ao da V8, amostra por amostra.
  - −14,1 LUFS, −1,52 dBTP, mediana voz − resto no celular de 28,8 dB.
  - A margem de pico entra na entrega 2, junto com os passos novos do I1.
- **Texto e tempo:** narração e MP3 (SHA-256 `fdedd877…`), roteiro, `palavras.json`, duração e os 42 planos com t0/t1.
- **Ciência:** valores de pressão.
- **Momentos aprovados:** corte em 33,92 s, pulso, obturador do C2 e C4 sem desfoque.
- **Personagem:** identidade.
- **Encerramento:** o mesmo.
- **Fora do escopo:** Episódio 01.

## Transição de ~0:05 (A4): verificada, mantida

- Folha `comparativos_r9/a2_a4.jpg`.
- **Olhar:** o A4 começa com o personagem ainda olhando o alto da traseira, que é o que o A3 acabou de mostrar. A
  continuidade de olhar está correta.
- **Expressão:** muda em "Parece estranho".
- **Ação:** ele recuou um passo durante o A3, fora de quadro, o que explica a nova posição.
- **Fusão:** curta, de cerca de 0,2 s.
- **Conclusão:** não achei problema real. A fusão da V8 fica, como você decidiu.

## Pendências desta entrega

- **Fase 3:** prévias curtas em andamento (itens, leite e I1, aproximação do C4, porta). Elas vêm na entrega 2, antes de
  qualquer re-render completo.
- **Licença da narração:** pendente. Sem uso comercial.

**Nada publicado. Nenhuma voz gerada. Nenhum serviço contratado. Render 1080 completo não iniciado.**
