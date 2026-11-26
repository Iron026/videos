# De Olho no Invisível — manual de produção (padrões e checklists)

Consolida a experiência dos episódios 01 (navio) e 02 (geladeira). Detalhes, causas e números estão em:
- `episodio_01_navio_v2/APRENDIZADOS_EP01.md`;
- `episodio_02_geladeira/APRENDIZADOS_EP02.md`.

O objetivo é que cada episódio novo comece com estes padrões ligados e estas verificações rodando **desde a primeira versão**, e não descobertas na rodada 12.

As ferramentas genéricas de verificação estão em `ferramentas_producao/`:

| Ferramenta | O que faz | Quando rodar |
|---|---|---|
| `varrer_faces_coplanares.py <cena> [prefixos]` | Lista pares de faces coplanares entre peças diferentes, com prioridade para as peças cortadas | Antes de todo render |
| `verificar_g0_meio_quadro.py <pasta_cenas>` | Lista os planos cujo g0 cai a meio quadro | Antes da primeira montagem |
| `detectar_quadros_repetidos.py <video.mp4>` | Acha congelamentos e o padrão alternado "repete/avança" | Em toda montagem |

---

## Parte A — Requisitos técnicos OBRIGATÓRIOS (todo episódio)

### A1. Ciência
- [ ] A física determina a animação. Nunca adaptar a física à cena.
- [ ] Testes numéricos do modelo **antes** da animação: balanço de energia, pressões e temperaturas, extremos dos shaders didáticos (0 e 1).
- [ ] Modelos que se encontram em cenas diferentes fecham entre si. Quando não fecham, procurar a física que falta.
- [ ] Rótulos e cartões de estado físico presos ao ponto do modelo; verificados pelos dados EXPORTADOS (rótulos 2D, manômetros, câmera por quadro).
- [ ] Toda curva sonorizada ou rotulada tem o significado físico documentado (curva de visualização ≠ estado físico).
- [ ] Números declarados como do modelo do episódio, não universais.

### A2. Modelagem e cena
- [ ] Peças vizinhas **não** compartilham planos. Rodar `varrer_faces_coplanares.py` em toda cena com corte ilustrativo.
- [ ] Correção de contato escolhida pela semântica da tampa:

| Situação | Correção |
|---|---|
| A face de contato fica escondida pela peça maior | Retirar a face |
| A fresta cai numa borda que já existe | Folga de 0,02 mm |
| A folga ficaria no meio de uma tampa | Proibido: vira linha tracejada |

- [ ] Mecanismos animados com juntas verificadas por quadro a partir do `cena.json`: comprimento da biela, eixo e espaço morto.
- [ ] Câmera nunca dentro de geometria cortada; folha de contato (3 quadros por plano, 270 × 480) antes do animatic.
- [ ] Toda cena exportada com hash; cena aprovada congelada (exportação não determinística): nunca reexportar depois de aprovada.
- [ ] Mais de um transparente sobreposto: varrer trocas de ordem de desenho (`varrer_ordem_transparentes.py`) e congelar a ordem onde muda a imagem.

### A3. Imagem e render
- [ ] Configuração única para testes e definitivo (MSAA 4×, AO 16, bloom e grade aprovados), registrada em `config/producao.json`.
- [ ] AO coerente com os cortes (normais e profundidade com os mesmos planos; tampas fora do AO com máscara suavizada).
- [ ] Interiores em corte sem sol direto; dois modos de luz por plano (cena × técnico), escolhidos por diagnóstico.
- [ ] Antes do render 1080: testes curtos em 1080 nos planos em corte, macros e aproximações rápidas (z-fighting, cintilação, estroboscopia com `medir_estrobo.py`, legibilidade).
- [ ] Render com manifesto por quadro (configuração, hash da cena e do motor, SHA-256, gravação atômica), blocos e verificação de cada quadro (escala grossa ≥ 0,93, diferença média ≤ 6). **Um processo por vez.**
- [ ] Salto entre quadros só é aceito com prova; senão, PARA.
- [ ] Variação natural medida antes de afirmar diferença (render por software não é determinístico).
- [ ] Opção nova no motor: provar equivalência e registrar `motor_equivalente`.

### A4. Montagem e tempo
- [ ] Toda conversão tempo → índice usa **um só arredondamento: meio para cima** (`floor(x + 0,5 + 1e−6)`). Nunca `round()` do Python.
  - [ ] `verificar_g0_meio_quadro.py` antes da primeira montagem.
  - [ ] `detectar_quadros_repetidos.py` em toda montagem.
- [ ] Continuidade nos cortes: ângulo e velocidade dos dois lados; quadros-ponte continuam a câmera aprovada; procurar "dois saltos seguidos" (troca de câmera com menos de 1 quadro).
- [ ] Desfoque de movimento com janela CENTRADA; obturador de 180° com o sub-quadro central igual ao quadro aprovado.
- [ ] Camadas 2D posicionadas por regras (candidatos, validade, programação dinâmica no plano inteiro); todos os quadros testados com registro das caixas.
- [ ] Depois de QUALQUER edição na montagem: SHA-256 dos quadros compostos contra a versão anterior (`compor_janela`). Uma opção nova desligada tem de dar 100 % de quadros idênticos.
- [ ] Trilha de áudio termina no último QUADRO (n/30), com fade de 50 ms.
- [ ] Master sem legendas gerado junto com o definitivo; montagens em paralelo, porque são determinísticas.

### A5. Som
- [ ] Todo som tem origem e função. A camada de fundo só existe quando a fonte é mostrada ou citada; medir o % do tempo presente de cada stem.
- [ ] Stems em ponto flutuante; provar soma = mixagem (nulo ≤ −130 dBFS). Decompor por fonte antes de mexer em camadas.
- [ ] Nível de efeito relativo à fala ATIVA (±0,8 s), com teto em loudness K. Perspectiva igual para todo objeto: voz − 18 dB no celular e − 18 LU em K, menos 20·log10(d / 2,4 m).
- [ ] Sincronia pelo ataque PERCEBIDO, medido no som isolado e processado; eventos vizinhos na mesma camada confundem a medida.
- [ ] Música: abaixamento dinâmico só na banda da voz, com retorno de 0,5 s; nível calibrado DEPOIS do abaixamento; música − voz medida durante a fala; emendas por frase musical inteira, vindas de trecho distante, validadas contra a variação natural da faixa.
- [ ] Metas medidas **no AAC final de cada variante**:
  - −14 LUFS;
  - ≤ −1,5 dBTP;
  - voz − resto p5 ≥ 10 dB no celular simulado (mono, 350 Hz–7 kHz), também só nas janelas com fala;
  - mono sem perda;
  - silêncio no fim.
- [ ] Por evento: voz − resto ≥ 6 dB sobre a fala; AAC × WAV com correlação ≥ 0,98 e atraso 0.
- [ ] Variantes com sufixo próprio: nunca sobrescrever stems nem registros aprovados; validadores com `SUF_VALIDACAO`.

### A6. Regressão e prova
- [ ] Cada pedido muda só o pedido, provado com:
  - hash dos quadros compostos;
  - nulo por stem (regiões > −120 dBFS);
  - vídeo × vídeo com a lista de quadros esperados, onde o resto é só ruído do codificador.
- [ ] Correção nova fica atrás de uma opção desligada até a decisão do usuário; a correção aprovada vira opção registrada no script de montagem da versão.
- [ ] Validadores conferem o arquivo de entrada e são calibrados com o caso real antes de declarar falha.

### A7. Preservação
- [ ] MP4 em partes de 95 MB com SHA-256 e LEIA-ME; FLAC 24 bits das mixagens; stems licenciados fora do git, com hash.
- [ ] Na aprovação final: diretório `VERSAO_x.y.z/` com manifesto, cenas congeladas (`.tar.xz`), manifestos de render e `verificar_recuperacao.py`, rodado na cópia de trabalho **e** com `--git-ref origin/<ramo>`.
- [ ] Nunca commitar arquivo ainda sendo gravado. Avisar que os quadros renderizados se perdem quando o contêiner termina.

### A8. Licenças e publicação
- [ ] **Licença da voz definida ANTES de gravar.** A narração gratuita da ElevenLabs não permite uso comercial.
- [ ] Música com licença conferida na escolha; se a página recusa acesso automático, pedir a conferência ao usuário.
- [ ] Efeitos: CC0 ou Mixkit (sem arquivo isolado no git); nunca CC BY-NC nem YouTube; procedência registrada por som.
- [ ] Nada publicado, contratado ou gerado com créditos sem pedido explícito.

---

## Parte B — Preferências criativas (confirmar com o usuário a cada episódio)

- Visual rico e cinematográfico, sem efeitos exagerados; mecanismo visível em vez de rótulos ou fórmulas decorativas.
- Estrutura narrativa: contradição → investigação → mecanismo → experimento → aplicação → consequência → conclusão que retoma a abertura.
- Uma mudança visual relevante a cada 2–4 s (ação física, não câmera girando em objeto parado).
- Som natural, poucos acentos. **Detesta:**
  - whoosh em corte ou em movimento de câmera comum;
  - impacto cinematográfico;
  - ruído de fundo constante;
  - excesso de água;
  - graves sintéticos;
  - "cara de videogame".
- Passos e objetos discretos, coerentes com a distância da câmera.
- Música presente sem custar inteligibilidade: no Ep. 02, a mixagem B, sem EQ dinâmica.
- **Avisos de dramatização na tela:** no Ep. 01, sim ("Câmera lenta", "Meses depois"…). No Ep. 02, o usuário pediu SEM ("Visão térmica", "Corte ilustrativo", "Tempo acelerado", "Fluxo desacelerado", "Câmera lenta"), mantendo "Canal ampliado (esquema)" e o aviso da lupa. **Perguntar no início do Ep. 03.**
- Fusões curtas como linguagem padrão; corte seco nas revelações ancoradas na palavra.
- Personagem original, fora da linguagem de cores didática, presente só onde age.
- Encerramento na conclusão científica, sem mascote nem vinheta.

---

## Parte C — Checklist por etapa (ordem de execução)

1. **Pauta:** fenômeno com potencial visual e contradição central; pesquisa (princípios, limites, erros comuns).
2. **Roteiro:** cada frase com evidência visual; final retoma a abertura. **Licença da voz definida.**
3. **Voz aprovada:** Whisper local para identidade, mais ataque acústico para tempo (`palavras.json`); retranscrever trechos com palavras de duração zero.
4. **Decupagem como dados** (`planos.py`): tempos ancorados em palavras; transição por plano decidida (fusão ou corte seco); avisos decididos com o usuário.
5. **Modelos:**
   - testes numéricos da física;
   - `varrer_faces_coplanares.py` em toda cena com corte;
   - juntas de mecanismos;
   - transparentes sobrepostos.
6. **Folha de contato** e câmeras contra paredes → **animatic** → prévia 540 completa, com os mesmos fps e movimentos.
7. **Montagem desde a 1ª versão:**
   - `verificar_g0_meio_quadro.py`;
   - `detectar_quadros_repetidos.py`;
   - continuidade nos cortes;
   - hashes de quadros compostos a cada edição.
8. **Som desde a 1ª versão:**
   - camadas justificadas;
   - perspectiva;
   - sincronia no som isolado;
   - metas no AAC;
   - simulação de celular.
9. **Revisões A/B** com instantes precisos; correções atrás de opções desligadas; prova de "o resto não mudou".
10. **Testes curtos em 1080** nos pontos críticos; detector absoluto de cintilação no episódio todo; listras na junção dos planos em corte.
11. **Render definitivo** com checkpoints → montagem definitivo + master em paralelo → validação vídeo × versão anterior (quadros esperados), continuidade, quadros repetidos, áudio no AAC.
12. **Congelamento** `VERSAO_1.0.0/`: manifesto, cenas, manifestos de render, prova de recuperação pelo remoto; relatório de encerramento; pendências de licença.
13. **Publicação** só com pedido explícito, depois de resolver as pendências de licença.
