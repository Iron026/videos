# Ep. 02 · Entrega definitiva R12: garrafa corrigida e música +5 dB

"Como a geladeira esfria sem produzir frio?" — 1080 × 1920, 30 fps, 4.537 quadros, 151,233 s.

Seus pedidos foram:
- "em 1:53 a água da garrafa fica branca de repente, conserte";
- "aumente mais a música", com a escolha "+5db" no A/B.

Só isso mudou, e o resto foi medido.

Eu meço, mas não assisto nem escuto como uma pessoa. A aprovação final é sua.

**Nada foi publicado.** O Episódio 01 não foi alterado.

## 1. Arquivos

| Arquivo | Onde | Tamanho | SHA-256 |
|---|---|---|---|
| **Episódio definitivo R12** | `episodio/definitivo_r12/ep02_definitivo_r12_1080x1920.mp4.parte00-01` | 160.040.293 B | `53cb24f5abaf06806f6f50d05708e0d69171a95f29fc62e8c0aa96e0ac6aa6b9` |
| **Master sem legendas R12** | `episodio/definitivo_r12/ep02_master_imagem_sem_legendas_r12_1080.mp4.parte00-01` | 161.177.250 B | `92a178704c6ede957e1531ab996b0deacdc6e8c4c26eb0ba27c510f547fb1c93` |
| Mixagem +5 dB, FLAC sem perdas | `som/preservado_r12/audio_ep02_r12_musica_m5.flac` | 28,7 MB | `5c3b593e…` (WAV de origem `b34885b3…`) |
| Comparativo da garrafa (folha) | `episodio/previas_r12/garrafa_antes_depois_r12.png` | 2,0 MB | — |
| Comparativo da garrafa (vídeo lado a lado do 1:53) | `episodio/previas_r12/ab_garrafa_1m53_r11_x_r12.mp4` | 3,1 MB, 5,2 s, sem áudio | — |
| A/B da música (aprovada × +3 × +5) | `episodio/previas_r12/ab_musica_aprovada_x_3db_x_5db.mp4` | — | — |

- A remontagem e a troca de áudio estão em `episodio/definitivo_r12/LEIA-ME.md`.
- O registro completo, com hashes, comandos e números, está em `relatorios/manifesto_producao_r12.json`.
- A entrega da R11 continua intacta em `episodio/definitivo/`; as partes foram conferidas.

## 2. A garrafa em 1:53

### Causa

O motor (three.js r170) desenha os objetos transparentes do mais distante para o mais próximo. Para isso, mede a distância só do **centro** de cada objeto.

- No H2, a câmera se move. Num certo quadro, o centro da garrafa passa a ficar "mais perto" que o centro da prateleira de vidro.
- A ordem de desenho então se inverte de um quadro para o outro.
- A parte de baixo da garrafa, vista através do vidro da prateleira, passa a ser misturada ao contrário e fica esbranquiçada.

Não era um problema de material, de luz nem de modelo. Por isso nenhuma cor nem objeto foi mexido.

### Correção

- Criei uma opção nova no motor que fixa a ordem dos transparentes do primeiro ao último quadro do plano.
- A opção vem **desligada por padrão**. Ligada, ela não muda nada nos quadros anteriores à troca.
- O motor novo sem a opção dá o mesmo resultado do aprovado: diferença de 1,38–1,39 entre os dois, contra 1,37 de variação natural entre dois renders idênticos.

### Escopo

Varri **todas** as cenas atrás de trocas de ordem entre transparentes sobrepostos na tela e achei cinco. Medi cada uma ligando e desligando a correção, em 540:

| Plano | Tempo | Quadro da cena | Par | O que a correção muda | Decisão |
|---|---|---|---|---|---|
| **H2** | **1:53,1** | 48 | garrafa × prateleira | 1.592 px, só na garrafa: é o defeito relatado | corrigido |
| C4 | 0:44,4 | 52 | garrafa × prateleira | 1.723 px, só na garrafa: o mesmo efeito | corrigido |
| H1 | 1:49,6 | 75 | água × prateleira | 181 px na garrafa cortada pela borda de baixo, ≈3 níveis de cor | corrigido (mesmo mecanismo) |
| C2 | 0:36,4 e 0:37,4 | 83 e 111 | prateleira × prateleira | nada acima da variação natural | mantido como aprovado |
| F1 | 1:26,7 | 8 | casca × água da garrafa | 9 px | mantido como aprovado |

No C2 e no F1, a troca existe, mas não muda a imagem. Por isso esses planos ficaram como estavam.

### Render

- Os quadros anteriores à troca foram **reaproveitados com prova**: 48 no H2, 52 no C4 e 75 no H1.
- Foram renderizados 291 quadros em 3,0 h:
  - H2: 48–130;
  - C4: 52–184, com o obturador nos quadros 126–184;
  - H1: 75–149.
- Os quadros antigos foram movidos para `_descartados/`, sem apagar nada.
- O render não teve nenhuma parada. Os saltos do C4 nos quadros 155–157 também existem na V10 aprovada.

### Antes × depois no vídeo montado

Brilho médio da água em 4 quadros seguidos. A troca de ordem acontecia entre o 2º e o 3º quadro.

| Emenda | R11 (antes) | R12 (depois) |
|---|---|---|
| **H2 · 1:53,1** | 106,5 · 106,4 → **121,4** · 121,3 | 106,5 · 106,4 → 106,3 · 105,9 |
| C4 · 0:44,4 | 107,2 · 107,3 → **120,8** · 120,8 | 107,4 · 107,1 → 106,9 · 106,6 |
| H1 · 1:49,6 | 125,0 · 113,5 · 113,5 · 103,9 | 125,0 · 113,6 · 113,6 · 103,9 |

No H1, a variação é o movimento da própria garrafa, igual nas duas versões.

## 3. A música +5 dB

- Ganho da música relativo à voz: −13,5 dB, contra −18,5 dB antes. O abaixamento sob a fala continua em −8 dB, com 0,15 s de antecipação.
- Prova de que só a música mudou:
  - os stems de efeitos e de mecanismo diferem 0;
  - a música subiu exatamente +5,0 dB, com resíduo de −133 dBFS;
  - voz e ambiências são os mesmos stems.
- O áudio do definitivo é **idêntico, depois de decodificado**, ao do teste 540 com +5 dB que você ouviu e escolheu (`583b3d43…`).

## 4. Testes e resultados

### Quadros e render

| Teste | Resultado |
|---|---|
| Integridade dos 5.638 quadros 1080 (manifesto, SHA-256, decodificação, tamanho, não-preto) | **5.638 ok, 0 problemas** |
| Simulação de retomada | **0 a renderizar** |
| Cintilação nos planos re-renderizados (detector absoluto, 1080 reduzido a 540) | H2 6, C4 52 e H1 95 quadros com blocos. R11: 6, 51 e 95, com os mesmos piores quadros |

O quadro a mais do C4 é o q122:
- é um bloco no alto da imagem, longe da garrafa;
- ocupa 0,250 do bloco, contra 0,238 na R11, e o limiar é 0,25;
- os pixels alternando são 1.337 contra 1.331.

É variação natural do render.

### R11 × R12, quadro a quadro em resolução cheia

| Classe | Quadros |
|---|---|
| Idênticos byte a byte | **3.914** |
| Planos corrigidos depois da emenda, mais as fusões de saída deles | 284 |
| Só codificador (média ≤ 1,6 de 255) | 339 |
| **Inesperados** | **0** |

- **32 planos saíram idênticos byte a byte:** A1–C3, D3–G3 e I3–J4. Isso inclui o A4, então a transição C não mudou.
- Os quadros-chave são os mesmos nas duas versões.
- Diferenças "só codificador":
  - antes da emenda, até 40 quadros antes (C4, H1, H2): é a antecipação do x264;
  - depois do plano corrigido (D1, D2, I1, I2): a diferença termina exatamente no quadro-chave seguinte, 1594 e 3577.
- Por que D1, D2, I1 e I2 só mudaram por causa do codificador:
  - os quadros-fonte desses planos são iguais aos manifestos e foram gravados antes da R12;
  - montagem, grade de cor, decupagem, cenas e pontes de transição não mudaram desde a R11;
  - então a imagem que entrou no codificador é a mesma.

### Vídeo montado (definitivo R12)

| Teste | R12 | R11 |
|---|---|---|
| Fluxo: 1080 × 1920, 30 qps, 4.537 quadros, H.264 + AAC 48 kHz, título sem marcação | ok | ok |
| Quadros pretos | 0 | 0 |
| Definitivo × revisão 540 (correlação mín / mediana / dif. máx) | 0,973 / 0,9975 / 5,7 | 0,973 / 0,9975 / 5,6 |
| Saltos fora dos cortes | 284 | 285 |
| Master × definitivo | diferenças só na faixa de 64,1–78,1 % da altura (legendas); 373 quadros idênticos | igual |

Detalhe dos saltos fora dos cortes:
- 278 aparecem iguais na revisão 540 aprovada.
- 6 estão no limite do critério nas duas versões: são os mesmos da R11.
- **Nenhum salto novo.** O que sumiu foi o do quadro 1436 (C4), que estava no limite.

### Áudio, medido no AAC do definitivo R12

| Medida | R12 | R11 | Meta |
|---|---|---|---|
| Loudness | **−14,09 LUFS** | −14,1 | −14 |
| Pico verdadeiro | **−1,52 dBTP** | −1,68 | ≤ −1,5 |
| Voz − resto no celular simulado (p5 / mediana) | **10,3 / 23,3 dB** | 12,2 / 25,8 | ≥ 10 |
| Perda em mono | −0,02 dB | −0,01 | ~0 |
| Último 0,5 s | −45,6 dBFS | −45,6 | silêncio |

Pops nas apresentações. A voz continua dominante em todos (critério ≥ 6 dB), com atraso AAC × WAV de 0 amostra:

| Evento | Voz − resto | R11 |
|---|---|---|
| Pouso da garrafa (B5) | 12,0 dB | 12,0 |
| Fluido refrigerante (C3) | 8,9 dB | 8,9 |
| Evaporador (D1) | 8,9 dB | 9,0 |
| Compressor (E2) | 8,8 dB | 8,9 |
| Condensador (F1) | 9,0 dB | 9,0 |
| Capilar (G2) | 8,0 dB | 8,6 |

## 5. O que não mudou

- **Imagem:** 32 dos 39 planos do vídeo estão byte a byte iguais.
- **Montagem:** legendas, rótulos, cartões, avisos, lupa, grade de cor, cortes e fusões. O código de montagem é o mesmo e o master × definitivo dá o mesmo resultado da R11.
- **Som:** voz, efeitos, mecanismo, ambiências e pops são os mesmos stems.
- **Narração:** o MP3 original não foi tocado.
- **Decisões aprovadas:** garrafa no B5, transição C, trilha Spice Intrigue, pop, obturador no C2 e no C4.
- **Entrega R11:** intacta e conferida, assim como os registros de validação aprovados da R11. Os validadores agora gravam com sufixo `_r12`.

## 6. Problemas encontrados no caminho

1. **O H1 trocava de ordem sem efeito visível.**
   - Corrigi assim mesmo, porque é o mesmo mecanismo e a correção não muda os quadros anteriores.
   - A garrafa sai igual nas duas versões.
2. **Os validadores gravavam sempre o mesmo nome de arquivo** e sobrescreveriam os registros aprovados da R11.
   - Eles ganharam um sufixo opcional; sem ele, o comportamento é o da R11.
   - Conferi que os registros da R11 estão intactos.
3. **O script de comparação R11 × R12 falhou na primeira vez**, ao ler a lista de quadros-chave: o ffprobe devolve uma vírgula sobrando.
   - Corrigi a leitura, passei essa etapa para antes do laço longo e rodei de novo do zero.
4. **Montagens em paralelo.** Para ganhar ~30 min, o master sem legendas foi montado ao mesmo tempo que o definitivo, com nome temporário.
   - A montagem não grava arquivos intermediários.
   - A etapa repetida da fila sequencial foi interrompida de propósito; ela tinha deixado um arquivo parcial, que foi substituído.
   - O master final tem 4.537 quadros, e a comparação com o definitivo repete o resultado da R11.

## 7. Pendências e avisos

- **Aprovação final é sua:** assistir e escutar o `ep02_definitivo_r12_1080x1920.mp4` no celular.
- **Dois pontos para escutar com atenção:**
  1. **1:44,2, "…bruscamente, *e* parte do líquido evapora".**
     - É a pior janela de voz × resto: a música fica 8,7 dB acima da voz numa janela de 0,4 s (na R11, 4,0 dB).
     - Quase toda a janela é a pausa depois de "bruscamente,", e a palavra curta "e" entra no fim dela.
     - Na fala, a voz volta a dominar (p5 de 10,3 dB), mas o "e" é o ponto mais exposto.
  2. **Margem de pico pequena:** −1,52 dBTP para uma meta de ≤ −1,5. Passa, mas por 0,02 dB. Qualquer nova mudança no áudio exige medir de novo no AAC final.
- **Licença da narração:** plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória. Para monetizar, a voz precisa de licença compatível antes da publicação.
- **Licença da trilha:** "Spice Intrigue", de RomanSenykMusic, no Pixabay, sob a Pixabay Content License.
  - A conferência da página da faixa e do Content ID é sua.
  - *Correção registrada em 25/11: os documentos da R11 diziam "Mixkit" por engano.*
- **Contêiner temporário:** os quadros 1080 (`quadros_final/`, 1,7 GB, com manifestos e descartados) não estão no git e **se perdem quando a sessão acabar**. Os MP4 definitivos, o master e o áudio estão salvos no git.
- **Publicação:** nada foi publicado.

### Prova de recuperação

Feita em 26/11/2026 a partir do commit `73b8e57`, numa pasta vazia, com clone parcial (`--filter=blob:none --sparse --depth 1`) só das pastas de entrega:

- `sha256sum -c partes.sha256`: as 4 partes da R12 **OK**;
- remontagem com `cat`:
  - definitivo `53cb24f5…`, **igual**;
  - master `92a17870…`, **igual**;
  - 4.537 quadros decodificados em cada um;
- o FLAC da mixagem +5 dB tem SHA-256 `5c3b593e…`, **igual**;
- as partes da R11 no mesmo clone: **OK**.
