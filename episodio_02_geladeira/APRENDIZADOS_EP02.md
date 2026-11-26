# De Olho no Invisível · Ep. 02 · Aprendizados consolidados

**Episódio:** "Como a geladeira esfria sem produzir frio?"

**Versão aprovada:** **1.0.0 (R13.1), em 26/11/2026.** Registro de congelamento em `VERSAO_1.0.0/`.

Este documento reúne o que as rodadas 1 a 13.1 ensinaram. Para cada aprendizado:
- **Problema:** como apareceu.
- **Causa:** a causa real, provada.
- **Solução:** a solução validada e onde ela está.
- **Prevenção:** como evitar que se repita.
- **Testes:** o que rodar nos próximos episódios.

No fim estão a separação entre **requisitos técnicos obrigatórios** e **preferências criativas** (seção 22), os erros que cometi (seção 23) e, no apêndice, as lições originais rodada a rodada, sem cortes.

Os padrões e checklists que valem para todo episódio foram levados para `../MANUAL_DE_PRODUCAO.md` e resumidos em `../CLAUDE.md`.

---

## 0. Números de referência do Ep. 02

| Item | Valor |
|---|---|
| Duração | 151,233 s, 4.537 quadros a 30 qps, vertical 1080 × 1920 |
| Cenas | 43 planos com render próprio, mais 3 pontes do A4 (46 cenas congeladas) |
| Render 1080 por software (SwiftShader) | ~22–26 s por quadro com um processo sozinho; 30–41 s com análises concorrentes |
| Montagem final 1080 | ~22 min; definitivo e master em paralelo |
| Áudio final | −14,16 LUFS, −1,87 dBTP no AAC; voz − resto no celular: p5 de 11,1 dB, mediana de 23,5 dB |
| Rodadas | 13 rodadas de revisão (R13 em três etapas: B, C e .1), mais de 180 commits |

O episódio levou muitas rodadas porque defeitos de **modelagem** (faces coincidentes), de **montagem** (arredondamento) e de **mixagem** (camadas esquecidas) só apareceram no fim. Quase todos teriam sido pegos cedo pelos testes preventivos de `MANUAL_DE_PRODUCAO.md`.

---

## 1. Roteiro e narrativa científica

**1.1 A contradição move o episódio.**
- **Problema:** "a geladeira é fria por dentro, mas fica quente por fora?" só prende se o espectador vê as duas coisas.
- **Solução:** a abertura mostra a visão térmica com o interior azul e a traseira quente no mesmo quadro (A4). O final retoma a mesma pergunta com a nova compreensão ("não cria frio, dá um destino ao calor").
- **Prevenção:** a estrutura contradição → investigação → mecanismo → experimento → aplicação → consequência → conclusão que retoma a abertura (Ep. 01) virou padrão.
- **Testes:** cada frase tem uma evidência visual listada na decupagem; a última frase retoma a primeira.

**1.2 Modelos científicos que se encontram precisam fechar entre si.**
- **Problema:** o ciclo termodinâmico e o cilindro do compressor davam temperaturas incompatíveis.
- **Causa:** faltava física, o aquecimento do vapor na carcaça. Não era número errado.
- **Solução:** acrescentar o termo físico em vez de ajustar números. Verificação em `ciencia/`.
- **Prevenção:** todo modelo que alimenta duas cenas tem um teste de consistência entre elas.
- **Testes:** testes numéricos da física **antes** da animação (Joule–Thomson, balanço de energia, pressões por trecho).

**1.3 Teste que falha pode ser critério errado.**
- **Problema:** o teste de Joule–Thomson para líquidos "falhava".
- **Causa:** o critério do teste estava errado, não os dados.
- **Prevenção:** investigar o teste antes de mudar dados ou teste.

**1.4 Mudança de fase ao longo de metros não cabe num quadro.**
- **Solução:** um canal esticado e ampliado (corte ilustrativo), alimentado pela MESMA tabela do modelo, com o aviso "Canal ampliado (esquema)", e a lupa no G3.
- **Testes:** verificar a matemática dos shaders didáticos nos extremos (fração de líquido 0 e 1). O limiar do líquido estava invertido.

**1.5 Curva de visualização ≠ estado físico.**
- **Problema:** um som de "partida do compressor" no E2 ensinava errado.
- **Causa:** a curva `uTrab` 0 → 1 desenha o trabalho elétrico. Não é o compressor ligando: ele já funcionava.
- **Prevenção:** antes de sonorizar ou rotular uma curva, documentar o que ela representa fisicamente.

**1.6 Verificar a didática pelo exportado, não pelo código.**
- **Problema:** marcador fora do quadro, lupa adiantada em relação ao marcador, rótulos presos à câmera.
- **Solução:** `ciencia/verificar_g3.py` lê os dados exportados (manômetros, rótulos, câmera por quadro) e os compara com o modelo e as palavras.
- **Prevenção:** rótulo de **estado físico** fica preso ao PONTO do modelo onde aquilo acontece.

**1.7 Narração como referência de tempo.**
- **Solução:** Whisper oficial local (large-v3 → CTranslate2) para a identidade das palavras, mais o ataque acústico medido para o tempo (`voz/refinar_tempos.py`).
- **Causa dos erros evitados:** o Whisper põe o início da palavra depois de uma pausa ~0,3 s dentro do silêncio e alucina em pausas. O alinhamento só por pausas casou a pausa errada (erros de 1,5–2,6 s).
- **Testes:** palavras de duração zero = retranscrever o trecho sem contexto.

---

## 2. Modelagem e animação 3D

**2.1 Decupagem como dados.**
- **Solução:** `decupagem/planos.py`, com planos ancorados em palavras. Trocar a narração recalcula cortes, câmeras e legendas.
- **Prevenção:** prioridade dos tempos = narração aprovada > narração recebida > estimativa.

**2.2 Testes de geometria antes do render.** Continuidade, folgas e invasões acharam colisões que só apareceriam no fim (`verificar_juntas.py`, `testes_v9.sh`).

**2.3 Mecânica que fecha.**
- **Solução:** biela presa ao pino da manivela, pistão no eixo e espaço morto ≥ folga. Medido nos dados exportados do E3: erro < 0,0001 mm, biela a 9,000 mm constantes, espaço morto mínimo de 0,80 mm.
- **Testes:** conferir as juntas de todo mecanismo animado por quadro, a partir do `cena.json`.

**2.4 Exportação não determinística.**
- **Problema:** a ordem dos triângulos muda entre exportações.
- **Solução:** comparar malhas sem ordem, congelar cenas por hash e não reexportar depois. As cenas do definitivo foram arquivadas (`VERSAO_1.0.0/cenas_definitivo_ep02.tar.xz`).
- **Testes:** antes de montar, conferir os manifestos de render contra o hash das cenas atuais. Isso achou o D1 reexportado só nos rótulos.

**2.5 Laços de exportação "padrão" esquecem peças** (as metades de tela dividida). Conferir o hash de toda cena exportada.

---

## 3. Z-fighting e faces coplanares (o defeito mais caro do episódio)

**3.1 Peças que se encostam face a face, dentro de um corte ilustrativo.**
- **Problema:**
  - porta × vedação (C4, H1, H2, J3);
  - degrau × fundo (E2);
  - **bobina × estator** e **cilindro × placa de válvulas** (E3, R13C): listras e regiões que trocam de cor a cada quadro.
- **Causa:** as faces coincidem por definição (o topo de uma peça é a base da outra). A "tampa" do corte é a face interna (back face) da peça cortada, e no mesmo plano há outra face da peça vizinha. O renderizador alterna entre as duas.
- **Diagnóstico que funcionou:** renderizar de novo o MESMO quadro ocultando uma peça de cada vez e desligando passes.
  - O AO desligado não muda nada → não é o AO.
  - Sem a peça A ou sem a peça B, some → é o par A × B.
  - Primeiro, um render de controle igual ao definitivo, para medir a variação natural.
- **Solução, escolhida pela semântica da tampa:**

| Correção | Quando usar | Exemplo |
|---|---|---|
| **Retirar a face de contato** | Quando ela fica escondida pela peça maior: sem fresta, e a tampa da peça cortada ganha | Bobina (r 52 mm) dentro do estator (r 60 mm): `episodio/bobina_r13c.py` |
| **Folga mínima de 0,02 mm** (~0,17 px em 1080) | Quando a fresta cai numa borda que já existe | Cilindro × placa: `episodio/bloco_r13c.py` |
| Sobreposição | Elimina a briga, mas mostra a peça interna através do corte | Opção rejeitada |
| Folga no meio de uma tampa | Vira linha tracejada (0,5 mm visto de quina, em 1080) | Opção rejeitada |

- **Prevenção:**
  - na modelagem, peças adjacentes NÃO compartilham planos;
  - escolher a correção por par;
  - varrer **todos** os pares de faces coplanares da cena cortada (`ferramentas_producao/varrer_faces_coplanares.py`), não só o par denunciado. O usuário achou o segundo par (placa) depois do primeiro.
- **Testes:**
  - detector de listras e de cintilação na região da junção (`episodio/detectar_listras_r13c.py`);
  - quadros-teste de 1080 nos planos em corte **antes** do render;
  - o defeito não muda com a resolução → não é conflito de profundidade (outra causa).

**3.2 Sinais característicos.**
- Região que "troca de cor" entre quadros, amarela num e listrada no outro: z-fighting, não iluminação.
- Listras horizontais em degraus: briga de profundidade.
- **Medida:** cintilação na junção (|Δ| entre quadros na máscara da região).
  - Bobina: de 11,07 para 1,32.
  - Placa: de 16,0 para 3,2. O que sobra é a palheta abrindo de verdade.

**3.3 Correção certa pode revelar defeito antigo.** O AO coerente com o corte escureceu uma face e expôs um z-fighting que já existia. Medir com limiar sensível, e conferir na versão aprovada, antes de chamar de regressão.

**3.4 Escopo provado.** Corrigir só nos planos onde a projeção geométrica da junção mostra que ela aparece, com a mesma família de correção já aprovada.

---

## 4. Ordenação de objetos transparentes

- **Problema:** a água da garrafa "fica branca de repente" em 1:53.
- **Causa:** o three.js ordena os transparentes pela profundidade do CENTRO de cada malha. Com a câmera andando, garrafa × prateleira de vidro trocam de ordem, e a mistura muda de uma vez.
- **Solução:**
  - `ordemtransp=1` congela a ordem no quadro 0 do plano, só nos planos onde a troca muda a imagem;
  - medido com a opção ligada e desligada: das 5 trocas, só 3 mudavam a imagem;
  - equivalência do motor provada e registrada (`config/producao.json → motor_equivalente`).
- **Prevenção:** `varrer_ordem_transparentes.py` em toda cena com mais de um transparente sobreposto na tela.
- **Testes:** varredura de pares sobrepostos com troca de ordem, e medida de cada troca.

---

## 5. Antisserrilhado e cintilação temporal

- **Problemas:** linhas finas e texturas repetitivas piscando; estroboscopia de grades (serpentina, arames) em aproximações rápidas.
- **Causas:**
  - microtextura abaixo do pixel;
  - grade com deslocamento por quadro ≥ 0,5 do passo na tela, que fica ambíguo.
- **Soluções:**
  - MSAA 4× (o supersampling 1,5× custou 2,25× sem ganho consistente; medido contra uma referência em 2160);
  - obturador de 180° (seção 6) para grades.
- **Prevenção:** medir a estroboscopia pela geometria (`medir_estrobo.py`) depois de qualquer aproximação rápida.
- **Testes:**
  - detector absoluto de cintilação no episódio inteiro, em 1080;
  - classificar os falsos positivos: linhas finas em câmera rápida, texturas animadas, feixes, canal animado;
  - quadro parado não revela cintilação: sempre medir a continuidade temporal.

---

## 6. Obturador e desfoque de movimento

- **Problema:** estroboscopia em C2 e C4, e um empurrão lateral de 0,3 s no A4 que precisava de desfoque.
- **Solução:**
  - obturador real: média em luz linear de sub-quadros, 180°;
  - o sub-quadro central coincide com o quadro aprovado;
  - não muda câmera, pulso nem enquadramento.
- **Armadilha:** desfoque na composição com janela só para um lado desloca a imagem n/2 px. A janela deve ser CENTRADA.
- **Testes:**
  - nitidez com a câmera parada (integrado / central ≈ 1);
  - primeiro e último quadros iguais ao aprovado.

---

## 7. Iluminação, materiais e AO

**7.1 O GTAO do three.js ignora os planos de corte.**
- **Problema:** linha fina = vinco invisível.
- **Causa:** o material de substituição do AO não tem `clippingPlanes`.
- **Solução:**
  - `aocorte`: normais e profundidade com o mesmo corte;
  - `aotampa`: as tampas marcadas numa máscara SUAVIZADA (a máscara binária pisca na fronteira).
- **Testes:** linha suspeita → AO desligado antes de concluir. A do E1 persistiu e era o capilar real.

**7.2 Transparentes no GTAO criam halos.** Desenhar os transparentes no passo próprio, com profundidade que respeita os cortes e ignora vidro.

**7.3 Dois modos de luz por plano.**
- A iluminação "cozinha" (ambiente por CubeCamera e sombras das luzes de área) dá realismo, mas escurece metais e interiores em corte.
- O modo "técnico" vale para os planos didáticos.
- Escolhido por diagnóstico, ligando e desligando cada recurso.
- Acne de sombra se corrige com `bias`/`normalBias`, não com geometria.

**7.4 Visão térmica legível.** Ambiente em cinza-ardósia escuro; só o frio e o quente se destacam.

---

## 8. Continuidade entre cenas

- **Problemas:**
  - porta com degrau de 88° → 100° entre A1 e A2;
  - câmera que "freia" nos quadros-ponte;
  - quadro intermediário com câmera interpolada (troca de câmera mais curta que 1 quadro).
- **Soluções:**
  - medir ângulo e velocidade dos dois lados de cada corte;
  - os quadros-ponte continuam a câmera APROVADA (posição e velocidade do último quadro), derivada dos dados exportados (`pontes_camera_continua.py`);
  - procurar nas cenas "dois saltos seguidos".
- **Prevenção:** mudança de animação num plano obriga a conferir o vizinho.
- **Testes:** verificador de render que PARA em salto entre quadros sem prova (efeito da cena mudando naquele quadro, o mesmo salto numa versão aprovada ou um registro investigado).

---

## 9. Interação entre personagem e objetos

**Solução validada:**
- partes rígidas articuladas mais IK de dois ossos;
- a mão usa a MESMA curva do objeto que segura;
- uma peça trocada só num gesto (mão fechada) mantém a dimensão da original, para não mudar contato nem trajetória.

**Preferência criativa:** o personagem só aparece onde é visto agindo. Quando atrapalha o diagrama, sai do plano. O contraplano "de dentro da geladeira" mostra a reação.

**Requisito:**
- o personagem é original, diferente do mascote oficial (2D, sem 3D aprovado);
- as cores dele ficam fora da linguagem didática.

**Testes:** alcance do puxador e contato mão × objeto medidos por quadro (R9-6 e I1 com a caixa de leite).

---

## 10. Transições cinematográficas

- **Fusão entre câmeras diferentes = imagem fantasma.** Exemplo: a carcaça sobreposta ao interior na entrada do E3. É aceitável quando é a linguagem do episódio; o usuário manteve a fusão. Em revelações, corte seco ancorado no ataque da palavra (`ANTECIPA` e `FUSOES` = 0, só naquele plano: C2 "Escondido").
- **A3 → A4:** corte seco aprovado, para evitar a imagem fantasma. Rosto → interior com empurrão lateral de 0,3 s e desfoque de 180° centrado (opção C, aprovada).
- **Prevenção:** decidir por plano o tipo de transição na decupagem e mostrar A/B das alternativas desligadas.

---

## 11. Legendas, rótulos e indicadores

- **Legibilidade exige regras de posicionamento:**
  - candidatos em volta da âncora mais posições fixas;
  - validade = sem cortes, sobreposições ou linhas sobre texto;
  - escolha no plano INTEIRO por programação dinâmica (mínimo de trocas) e fusão curta nas trocas;
  - testar TODOS os quadros com um registro das caixas desenhadas.
- **Cartão de pressão** no lugar de manômetro decorativo, e linhas de chamada só quando necessárias.
- **Avisos:**
  - calculados a partir das curvas gravadas na cena, com a mesma interpolação do motor;
  - só aparecem com o modo ativo.
  - **Preferência do usuário (R13.1):** sem "Visão térmica", "Corte ilustrativo", "Tempo acelerado", "Fluxo desacelerado" e "Câmera lenta". Retirar só o DESENHO (`AVISOS_OCULTOS`) preservou o posicionamento dos rótulos: 3.570 quadros mudaram, e só na faixa dos avisos.
- **Armadilha recorrente** (3 vezes): um comentário `#` dentro de uma lista escrita numa linha só desligou avisos de outros planos.
  - **Teste obrigatório:** depois de qualquer edição na montagem, SHA-256 de todos os quadros compostos contra a versão anterior.

---

## 12. Quadros repetidos e sincronização

- **Problema:** início "travado", como se o fps fosse baixo (R13C).
- **Causa:**
  - a montagem escolhe o quadro com `round((g − g0)·30)`;
  - o `round()` do Python arredonda EMPATES para o par;
  - em 4 planos o g0 caía a meio quadro (A1 −0,25, B7 26,05, H1 107,05, I1 115,35);
  - resultado: índices 8, 8, 10, 10…, ou seja, 15 qps efetivos;
  - erros de ponto flutuante quebravam alguns empates e deixavam o defeito irregular.
- **Solução:** `ARRED_QUADROS=1`, com `floor(x + 0,5 + 1e−6)`.
  - Mudaram só os 125 quadros de empate.
  - Os quadros repetidos caíram de 168 para 111 (−57).
  - A duração não mudou.
- **Prevenção:** padrão de arredondamento único (meio para cima) em TODA conversão tempo → índice. Varrer as cenas por frac(g0·30) = 0,5.
- **Testes** (`episodio/validar_arred_r13c.py`, `ferramentas_producao/detectar_quadros_repetidos.py`):
  - índice com passo único (0 repetições, 0 saltos, 0 retrocessos);
  - nenhum par de quadros idêntico;
  - número de quadros e duração iguais;
  - classificar os falsos positivos: legenda aparecendo, cena parada.

**Sincronização de áudio:**
- a trilha termina no último QUADRO (n/30), com fade de 50 ms;
- os eventos sincronizam pelo ataque PERCEBIDO, medido no som isolado e processado (achados: pré-clique 77 ms antes; pico 314 ms depois em gravação contínua).

---

## 13. Sound design

- **Todo som tem origem e função.** Os mecanismos só soam com o mecanismo na tela e seguem a curva da animação.
- **Densidade:** depois de duas rodadas de corte (R13B e R13C), ficaram 9 acentos em 151 s. O usuário retirou o impacto na pausa, os whooshes de movimento de câmera e o impacto cinematográfico da revelação.
  - **Preferência:** nada de impacto cinematográfico nem whoosh em movimento de câmera comum.
- **Perspectiva:** mesma regra para todo objeto: voz − 18 dB no celular e voz − 18 LU em loudness K, menos 20·log10(d / 2,4 m).
  - Ganho por evento; instante intocado (atraso 0 provado por correlação).
  - Exemplos: passos −5,4 a −12,8 dB; batida da porta −13,5 dB.
- **Representação didática declarada:** pistão e válvulas em câmera lenta, e o pulso do circuito. Ficam registrados como representação, não como som real.

---

## 14. Controle de ruídos e ambiências

- **Problema:** "ruído contínuo" mascarando a música.
- **Causa:** camadas de fundo esquecidas da 1ª mixagem. O tom de cômodo e o compressor "ligado o episódio todo" ficavam a −37 LUFS cada, no nível da música.
- **Solução:** decompor os stems aprovados por fonte, provando que a soma reproduz o stem aprovado (nulo ≤ −150 dBFS). Depois, tirar ou trocar camadas uma a uma.
- **Prevenção:** medir em TODO stem o % do tempo presente e justificar cada camada de fundo por plano.
- **Testes:**
  - presença por camada;
  - nulo da decomposição;
  - ruído isolado como comparativo.

---

## 15. Presença musical e inteligibilidade

- **Problema:** música "inaudível".
- **Causa:**
  - nível calibrado ANTES do abaixamento;
  - abaixamento ligado em quase toda a narração (só 10 pausas ≥ 0,6 s);
  - música − voz durante a fala = −21 LU.
- **Solução:**
  - abaixamento dinâmico só na banda da voz (250 Hz–4 kHz, música ≥ 16 dB abaixo), com retorno de 0,5 s;
  - subida nas pausas 0,3 s depois da palavra;
  - automação por contexto.
- **Limite físico:** no alto-falante de celular, voz e música disputam 450 Hz–4 kHz. A EQ dinâmica por banda ganhou presença à custa da inteligibilidade (índice tipo SII e p5). O usuário escolheu B sem a EQ, e rejeitou C (+3 dB), que falhava na inteligibilidade.
- **Faixa mais curta que o episódio:**
  - estender por frase musical inteira (aqui, 4 compassos), vinda de um trecho distante;
  - nunca repetir o que acabou de tocar nem inserir 1 compasso solto;
  - validar as emendas contra a variação natural da faixa;
  - acorde final depois da última palavra.
- **Testes:**
  - −14 LUFS e ≤ −1,5 dBTP **no AAC**;
  - voz − resto p5 ≥ 10 dB no celular simulado, medindo também só as janelas com fala;
  - simulação de alto-falante (música perceptível na fala);
  - listar as piores janelas por palavra para a escuta do usuário.

---

## 16. Seleção e sincronização de efeitos

- **Fontes:**
  - Freesound CC0, com a licença conferida na página de cada som;
  - Mixkit SFX (comercial ok, proibido redistribuir o arquivo isolado);
  - nunca YouTube.
- **Escolha por medida:** ataque, golpes discretos e espectro. A gravação "Piston sound" foi descartada por ser contínua, sem golpes.
- **Nível relativo à voz:** referência = fala ATIVA em ±0,8 s, com teto em loudness K. Mecanismos repetidos têm nível único no plano.
- **Sons pontuais durante a fala** somem sob o abaixamento: stem próprio, com nível relativo à voz NAQUELE instante.
- **Testes:**
  - por evento: voz − resto ≥ 6 dB na janela sobre a fala;
  - AAC × WAV com correlação ≥ 0,98 e atraso 0;
  - sincronia no som isolado: eventos vizinhos na mesma camada confundem a medida (as válvulas a 100 ms do pistão).

---

## 17. Testes automatizados e controle de regressões

**Princípio:** cada pedido muda só o que foi pedido, e isso é PROVADO.

**Ferramentas que funcionaram:**
- SHA-256 de quadros compostos com uma janela da montagem (`compor_janela_r13c.py`): prova que uma opção desligada não muda nada (201 de 201 idênticos);
- teste de nulo por stem, com regiões onde a diferença passa de −120 dBFS;
- comparação vídeo × vídeo quadro a quadro (`validar_final_r13.py`, `validar_r13_1.py`): quadros esperados × ruído do codificador;
- variação natural medida antes de chamar algo de diferença, porque o renderizador por software não é determinístico nem rodando sozinho;
- diferenças só do x264 terminam em quadro-chave: provar com os quadros-fonte inalterados.

**O validador também erra:**
- leu os stems da 1ª mixagem;
- usou projeção ortográfica numa câmera oblíqua;
- usou um limite de faixa mais apertado que a pilha de avisos;
- marcou a falsa dessincronia das válvulas.

Conferir a entrada de toda métrica e investigar cada falha antes de "corrigir".

**Correção nova fica desligada** (opção no ambiente) até a decisão do usuário; a correção aprovada vira opção registrada no script de montagem da versão.

---

## 18. Renderização, checkpoints e retomada

**Solução:** `render_definitivo.py` e `render_r13c_e3.py`:
- blocos de 40–60 quadros;
- manifesto por quadro: configuração, hash da cena e do motor, SHA-256 e gravação atômica;
- verificação de cada quadro (decodifica, não preto, escala grossa ≥ 0,93, diferença média ≤ 6);
- reaproveitamento só com prova.

**Lições:**
- um processo de render por vez;
- processos longos destacados (`setsid`) mais um Monitor rearmado;
- `run_in_background` tem limite: a mixagem passou de 20 min por causa da carga e foi interrompida;
- re-render localizado: passe a lista de planos; sem ela, o script refaz planos vindos de outros scripts;
- opção nova no motor muda o hash: provar a equivalência e registrar `motor_equivalente`;
- montagens são determinísticas: definitivo e master rodam em paralelo.

---

## 19. Preservação e recuperação de arquivos

**Solução:**
- MP4 em partes de 95 MB com SHA-256 e LEIA-ME de remontagem;
- FLAC 24 bits das mixagens, com erro de −144,5 dBFS;
- stems licenciados fora do git, só com hash;
- **cenas congeladas** em `.tar.xz`: 13 MB para 348 MB de cenas;
- manifestos de render arquivados.

**Prova:** `VERSAO_1.0.0/verificar_recuperacao.py` confere 55 itens. Passou na cópia de trabalho e **lendo só do ramo remoto** (`--git-ref origin/<ramo>`).

**Lições:**
- variantes nunca sobrescrevem registros aprovados (sufixos próprios e hash antes e depois);
- o contêiner é temporário: tudo o que importa vai para o git ou tem hash e receita de reconstrução;
- nunca commitar arquivo ainda sendo gravado.

---

## 20. Licenciamento dos recursos

| Recurso | Licença | Situação |
|---|---|---|
| Narração | ElevenLabs, plano gratuito | **Sem uso comercial, com atribuição. PENDENTE** para monetizar |
| Música "Spice Intrigue" | Pixabay Content License | **Conferência da página e do Content ID PENDENTE** (acesso automático recusado) |
| Efeitos | Freesound CC0 e Mixkit SFX Free | ok; Mixkit isolado fora do git |
| Fontes | Montserrat (OFL) | ok |
| Personagem e modelos | próprios | ok |

**Prevenção:**
- definir a licença da voz ANTES de gravar o Ep. 03;
- preferir música com licença verificável automaticamente ou conferida pelo usuário na escolha;
- registrar procedência de cada som.

---

## 21. Fluxo de trabalho com o usuário

- Entregar comparativos A/B reais (mesma imagem, mesmo trecho, mesmo nível) antes de consolidar.
- Pedidos chegam em instantes de vídeo ("1:18", "0:33"). Localizar o evento exato no stem ou no quadro, por camada, antes de agir.
- O usuário encontra defeitos visuais que os detectores não cobriram (o segundo par coplanar, os quadros repetidos). Depois de corrigir um defeito, varrer a FAMÍLIA inteira.
- Declarar sempre que eu meço, mas não assisto nem escuto como uma pessoa.

---

## 22. Requisitos técnicos obrigatórios × preferências criativas

### Requisitos técnicos obrigatórios (valem para todo episódio)

1. Física correta e modelos que fecham entre si; números do modelo declarados como do episódio.
2. Sem faces coplanares entre peças vizinhas; varredura antes do render.
3. Conversão tempo → índice com um só arredondamento (meio para cima); sem quadros repetidos; passo único verificado.
4. Ordem de transparentes estável onde a imagem depende dela.
5. Continuidade de câmera e animação nos cortes (ângulo e velocidade).
6. Áudio: −14 LUFS, ≤ −1,5 dBTP no AAC, voz − resto p5 ≥ 10 dB no celular, mono sem perda, silêncio no fim, trilha até o último quadro.
7. Prova de "não mudou": hash dos quadros compostos, nulo dos stems, vídeo × vídeo com quadros esperados.
8. Render com manifesto, checkpoints e verificação por quadro; um processo por vez.
9. Preservação: partes com SHA-256, cenas congeladas, FLAC, prova de recuperação pelo remoto.
10. Licenças conferidas e registradas antes da publicação; nada publicado sem pedido.

### Preferências criativas deste usuário (confirmar a cada episódio)

1. Visual rico e cinematográfico, sem efeitos exagerados.
2. Mecanismo visível em vez de rótulos ou fórmulas decorativas.
3. Som natural; poucos acentos; sem whoosh em corte ou movimento de câmera comum; sem impacto cinematográfico; sem ruído de fundo constante; música presente mas sem custar inteligibilidade.
4. Passos e objetos discretos, coerentes com a distância da câmera.
5. **Ep. 02:** sem os avisos de dramatização na tela (R13.1). Perguntar antes de reintroduzir no Ep. 03.
6. Fusões curtas entre planos como linguagem padrão; corte seco nas revelações ancoradas na palavra.
7. Personagem original, que age só onde é visto.

---

## 23. Erros que cometi (e o que fazer diferente)

- Corrigi o par bobina × estator e entreguei sem varrer os outros pares coplanares da mesma cena. O usuário achou o segundo (placa de válvulas). **Fazer:** varredura completa da família de defeito antes de entregar.
- O `round()` com empate para o par passou por 12 rodadas. **Fazer:** detector de quadros repetidos no vídeo final como teste obrigatório desde a 1ª montagem.
- Deixei um monitor esperando com o comando errado (`tail -4` com dois arquivos), o que gerou um falso "falhou". Deixei uma mixagem estourar o limite de 20 min do `run_in_background`. **Fazer:** processos longos sempre destacados e um monitor por condição simples.
- Validador com limite mais apertado que o fenômeno (faixa de avisos de 20 % contra 22 % reais). **Fazer:** calibrar o critério com o caso real antes de declarar falha.
- Medida rápida de sincronia confundida por eventos vizinhos. **Fazer:** medir no som isolado do evento.

---

## Apêndice — lições originais, rodada a rodada (como registradas durante a produção)

### Rodada 1
- **Decupagem como dados ancorados em palavras** (`decupagem/planos.py`): trocar a narração recalcula cortes, câmeras e legendas. Prioridade dos tempos: narração aprovada > narração recebida (alinhada por pausas, não verificada) > estimativa.
- **Testes de geometria antes do render** (continuidade, folgas, invasões) acham colisões que só apareceriam no fim.
- Modelos científicos que se encontram (ciclo × cilindro do compressor) precisam **fechar entre si**; quando não fecham, procurar a física que falta (aquecimento do vapor na carcaça), não ajustar números.
- Teste que falha pode ser critério errado (Joule–Thomson de líquidos): investigar antes de mudar dados ou teste.
- Motor: o GTAO inclui malhas transparentes (feixes) → halos; desenhar transparentes no passo próprio, com profundidade que respeita os planos de corte e ignora vidro.
- **Câmera dentro de geometria** com corte = quadro tomado pela tampa colorida. Conferir posições de câmera contra as paredes (inclusive espuma e teto).
- **Visão térmica** precisa ser reconhecível de imediato: ambiente em cinza-ardósia escuro, só frio e quente se destacam.
- Folha de contato (3 quadros por plano, 270×480) antes do animatic: barata e pega a maioria dos erros de câmera.
- Renderizador por software: ~10 s de inicialização por plano; agrupar renders e evitar reinicializações à toa.
- Download de modelos (Hugging Face) depende de rede liberada **e** de permissão da sessão; sem isso, alinhar por pausas e declarar que as palavras não foram verificadas.

### Rodada 2
- **Whisper oficial local** (openai/whisper-large-v3 → CTranslate2, offline) verifica a narração palavra a palavra. Ele alucina em pausas (palavras de duração zero): retranscrever o trecho sem contexto antes de concluir.
- O Whisper põe o início das palavras pós-pausa ~0,3 s **dentro do silêncio**. Tempo final = identidade pelo Whisper + ataque acústico medido (`voz/refinar_tempos.py`). O alinhamento só por pausas pode casar a pausa errada (erros de 1,5–2,6 s).
- **Mudança de fase ao longo de metros não aparece num quadro:** usar um canal esticado e ampliado (corte ilustrativo) alimentado pela MESMA tabela do modelo, com aviso "Canal ampliado (esquema)".
- Verificar a matemática dos shaders didáticos nos extremos (lf = 0 e 1): o limiar do líquido estava invertido.
- Corrigir a física não pode apagar a linguagem de cor: o vapor deve manter o matiz da temperatura.
- O renderizador por software **não é determinístico nem rodando sozinho** (média até 2,4, picos de 81). Provar "não mudou" com a variação natural medida, não com hash.
- Laços de exportação "padrão" podem esquecer peças (metades de tela dividida). Conferir o hash de toda cena exportada.
- Objetos do cenário na linha de visão (pote) são o defeito mais comum de macro: conferir os quadros de início dos planos.

### Rodada 3
- **Personagem:** consultar a identidade oficial antes. O mascote oficial (2D, `episodio_01_navio_v2/referencias/`) não tem 3D aprovado: um personagem narrativo deve ser original, diferente do mascote, com cores fora da linguagem didática.
- Partes rígidas articuladas + IK de dois ossos bastam para animatic; a mão deve usar a MESMA curva do objeto que segura.
- Personagem só onde ele é visto agindo; quando atrapalha o diagrama (feixes por cima do corpo), tirá-lo do plano. Contraplano "de dentro da geladeira" mostra a reação sem tirar o objeto do centro da história.
- **Pré-visualização também altera dados da montagem** (rótulos/manômetros 2D vêm da cena exportada): reexportar com o código final todo plano que foi pré-visualizado com câmera experimental, e provar com diff do vídeo montado.
- Revelação ancorada no ataque da palavra: corte sem antecipação (`ANTECIPA`) e sem fusão (`FUSOES` = 0) só naquele plano.

### Rodadas 4–5
- **Avisos ("Visão térmica", "Corte ilustrativo") calculados das curvas gravadas na cena**, com a mesma interpolação do motor — nunca por plano inteiro. Aviso só aparece com o modo ativo.
- **Iluminação de cozinha** (ambiente capturado da própria cena por CubeCamera + sombras das luzes de área) dá realismo, mas escurece metais e interiores em corte: dois modos de luz por plano (cozinha × técnico), escolhidos por diagnóstico ligando/desligando cada recurso. Acne de sombra = bias/normalBias, não geometria.
- Polimento global obriga a renderizar tudo de novo, mas a **estrutura** (planos_resolvidos: ids, t0, t1) precisa sair idêntica — medir e mostrar.
- **Verificar a didática pelo EXPORTADO** (manômetros2d, rótulos2d, câmera por quadro) contra o modelo e as palavras, não pelo código (`ciencia/verificar_g3.py`). Achou: marcador fora do quadro, lupa adiantada em relação ao marcador, rótulos presos à câmera em vez do fenômeno.
- Rótulo de **estado físico** ("começa a evaporar", "mistura fria") fica preso ao PONTO do modelo onde aquilo acontece; a lupa só mostra os rótulos que estão dentro do círculo.
- O verificador também erra: projeção ortográfica numa câmera oblíqua deu falso positivo. Usar a perspectiva real e conferir antes de "corrigir" a cena.
- **Som:** Freesound CC0 (licença conferida na página de cada som, prévia HQ) quando Mixkit/Commons limitam (429). A narração tem ~20 dB entre pico e loudness: compressão suave (2,5:1) só na CÓPIA de mixagem reduz o trabalho do limitador; o MP3 não muda. A/B com a narração no mesmo nível = mixagem "só voz" com o MESMO master fixo.

### Rodada 6
- **O GTAO do three.js ignora planos de corte:** ele desenha normais/profundidade com um único material de substituição sem `clippingPlanes`, então o AO "vê" a parte cortada fora (linha fina = vinco invisível). Diagnóstico: ocultar peças uma a uma + desligar passes. Opção `aocorte` no motor (desligada até decisão: muda o sombreado de todo plano em corte).
- Linha fina suspeita: testar com AO desligado antes de concluir — a do E1 persistiu e era o capilar real.
- Detector absoluto em 1080 marca linhas finas em câmera rápida e texturas animadas; mapear os pixels e conferir a câmera exportada (trepidação × órbita suave) antes de chamar de defeito.
- Diferenças pequenas em planos NÃO renderizados (≤ 1,1) que terminam no quadro-chave do x264 são do codificador (mb-tree/lookahead), não da imagem: provar com data dos quadros-fonte + posição dos quadros-chave.
- Trilha de áudio deve terminar no último QUADRO (n/30), não na duração da decupagem; fade de 50 ms evita clique.
- Peça trocada só num gesto (mão fechada): mesma dimensão da peça original, para não mudar contato nem trajetória.

### Rodada 7
- **Camadas 2D legíveis exigem posicionamento com regras**, não só fonte maior: candidatos em volta da âncora + posições fixas, validade = sem cortes/sobreposições/linhas sobre texto, escolha no plano INTEIRO por programação dinâmica (mínimo de trocas) e fusão curta nas trocas. Testar TODOS os quadros com um registro das caixas desenhadas.
- **AO coerente com o corte:** normais/profundidade com os mesmos planos de corte; as "tampas" (faces internas vistas pelo corte) marcadas numa máscara SUAVIZADA para o AO não escurecê-las (máscara binária pisca na fronteira).
- **Correção certa pode revelar defeito antigo:** o AO correto escureceu uma face cinza e expôs z-fighting que já existia (amarelo × cinza de brilho parecido, invisível ao limiar 30). Medir com limiar sensível antes de culpar a correção.
- Peças que encostam face a face (topo/base × laterais, porta × vedação) brigam pelo corte: folga de 0,5 mm.
- Hipótese descartada também se registra (atenuação rasante do AO: sem efeito).
- **Estroboscopia de grades:** medir pela geometria (deslocamento por quadro ÷ passo na tela; ≥ 0,5 = ambíguo). Desacelerar raramente basta com cortes e duração fixos; obturador real (média em luz linear de sub-quadros, 180°) reduz sem mudar câmera, pulso nem enquadramento — o sub-quadro central deve coincidir com o quadro aprovado.

### Rodada 8
- **Detector sensível acha defeitos ANTIGOS escondidos** (porta × vedação em C4/H1/H2, degrau × fundo no E2): conferir na versão aprovada antes de chamar de regressão; corrigir com a mesma família de correção já aprovada, só nos planos onde a **projeção geométrica da junção** mostra que ela aparece.
- Classificar o que pisca **dentro da tampa × na borda**; listar falsos positivos (arames sobre a tampa, feixes, canal animado).
- Um defeito que **não muda com a resolução** (mesma contagem em 540 e 1080 ajustada à escala) não é conflito de profundidade.
- **Folga corrige z-fighting mas pode criar fresta**: 0,5 mm visto de quina vira linha tracejada em 1080. Medir em 1080 e localizar cada linha projetando as faces candidatas; alternativa melhor costuma ser sobreposição (sem faces coplanares).
- **Exportação não determinística na ordem dos triângulos**: comparar malhas sem ordem; congelar cenas por hash e não reexportar depois. Conferir manifestos de render × cenas atuais antes de montar (achou D1 reexportado só nos rótulos).
- Comparar com animatic de passo 2 em trios de 2 quadros; o selo/IDs de revisão contam como diferença em todo plano.
- **Obturador**: validar nitidez com câmera parada (integrado/central ≈ 1) e primeiro/último quadro iguais ao aprovado.
- AAC: mudar um trecho do áudio desloca a quantização segundos depois (pico verdadeiro mudou em 130 s por causa de 118–120 s); medir de novo sempre no AAC final.
- Espera longa: um `run_in_background` tem limite de 2 h; para filas maiores, Monitor re-armado por eventos do log.

### Rodada 9
- **Verificador de render:** salto entre quadros só é aceito com prova (efeito da cena mudando naquele quadro, mesmo salto numa versão aprovada com imagem equivalente ≥ 0,93, ou registro investigado com evidência); fora disso, PARA.
- **Mudança de animação num plano exige conferir a continuidade no corte com o vizinho** (porta física no A1 deixou o A2 com degrau 88° → 100°). Medir ângulo e velocidade dos dois lados do corte.
- Mudança de câmera aprovada pode criar estroboscopia de grade/tubos finos: medir com `medir_estrobo.py` depois de qualquer aproximação rápida e oferecer o obturador de 180° como A/B desligado.
- Composição testada em todos os quadros depois da montagem final, não só na prévia.

### Rodada 10
- **Stems em PCM 24 cortam acima de 0 dBFS:** com master de +5 dB a soma dos stems não reproduz a mixagem. Gravar stems em ponto flutuante e PROVAR "soma = mixagem aprovada" (nulo ≤ −130 dBFS) antes de acrescentar camadas.
- **O validador também erra:** "voz − resto" lia os stems da 1ª mixagem. Validar com os stems da versão medida (STEMS_VOZ/STEMS_RESTO) e conferir o arquivo de entrada de toda métrica.
- Mixagem antiga depende das CÂMERAS com que foi gerada (perspectiva sonora): reproduzir com as cenas da época (CENAS_SOM).
- **Troca de câmera mais curta que 1 quadro** gera um quadro intermediário (câmera interpolada): varrer cenas por "dois saltos seguidos". Corrigir sem mexer na trilha (interpolação suave: chave nova muda os vizinhos) e provar quadro a quadro.
- Reexportação localizada: `provar_quadros_iguais.py` + reuso por prova no render (só os quadros diferentes saem).
- Trilha: Mixkit Music (YouTube/redes ok, sem Content ID, sem arquivo isolado no git). Escolher por medida (percussão, graves, faixa da voz, dinâmica) e deixar a audição para o usuário. Música −8 dB sob a fala com antecipação de 0,15 s.
- Supersampling 1,5× (custo 2,25×) não deu ganho consistente sobre o MSAA 4×: medir contra referência 2160 antes de pagar.
- Picos de AAC mudam de lugar quando qualquer camada muda: medir sempre no AAC final de CADA variante.

### Rodada 11
- **Quadros-ponte de transição** (rosto continuado depois do corte) devem continuar a câmera APROVADA (posição e velocidade do último quadro), derivada dos dados exportados — chaves novas no Blender mudam a curva e fazem a câmera "frear".
- **Desfoque de movimento na composição**: janela CENTRADA no instante do quadro (média só para um lado desloca a imagem n/2 px).
- **Comentário `#` dentro de uma lista numa linha só desligou avisos de outros planos** (3ª vez neste projeto). Depois de qualquer edição na montagem: SHA-256 de todos os quadros compostos contra a versão anterior (`verificar_transicao_a4.py hashes`).
- Sons pontuais que coincidem com a fala (apresentação de componentes, pouso de objeto) somem sob o abaixamento automático: stem próprio com nível relativo à voz NAQUELE instante (−12 dB na faixa do celular) e medir.
- Variantes de mixagem não podem sobrescrever stems nem registros aprovados (sufixo próprio; hash antes/depois).
- Páginas com proteção anti-robô (Pixabay) não se acessam automaticamente: pedir a confirmação da licença ao usuário.
- **Re-render localizado: passar os planos** (`render_definitivo.py --perfil revisao B5`). Sem a lista, o script percorre o episódio e refaz planos cujos quadros de 540 vieram de outros scripts (sem `_manifesto_quadros.json`: D2, D4, E1–E4, F1, F2, G3z, J4) — no Ep. 02 isso re-renderizou o D2 em 540 sem necessidade (conteúdo equivalente; vídeo V10 intacto).

### Rodada 12
- **Transparente que "muda de cor" de um quadro para o outro = ordem de desenho invertida.** O three.js ordena os transparentes pela profundidade do CENTRO de cada malha; com a câmera andando, garrafa × prateleira de vidro trocam de ordem e a mistura muda de uma vez. Varrer todas as cenas por trocas de pares sobrepostos na tela (`varrer_ordem_transparentes.py`) e MEDIR cada uma (opção ligada × desligada): das 5 trocas, só 3 mudavam a imagem. Correção: congelar a ordem no quadro 0 do plano (`ordemtransp=1`, desligada por padrão), só nos planos visíveis.
- Opção nova no motor muda o hash do motor e invalidaria todo o render: provar equivalência (motor novo sem a opção × aprovado = variação natural) e registrar `motor_equivalente`; quadros anteriores à troca são reaproveitados por prova.
- Montagens são determinísticas e não gravam intermediários: definitivo e master podem rodar EM PARALELO (−30 min). Processo destacado com `setsid`; ao matar por padrão use `[.]` na regex para o `pkill -f` não casar com o próprio laço.
- Validadores com nome de saída fixo sobrescrevem registros aprovados: sufixo opcional (`SUF_VALIDACAO`) e conferir antes.
- Diferenças só do x264 podem atravessar quadros-chave intermediários e terminar num quadro-chave adiante (1594, 3577): provar com quadros-fonte inalterados + entradas da montagem inalteradas + posição dos quadros-chave.
- Música mais alta: o p5 passa (10,3), mas o PIOR caso caiu para −8,7 dB numa pausa antes de um "e" curto. Localizar as piores janelas nas palavras e pedir ao usuário que escute esses instantes; pico −1,52 dBTP = margem de 0,02 dB.

### Rodada 13 (som)
- **"Ruído contínuo" = camada de fundo esquecida:** tom de cômodo e compressor "ligado o episódio todo" vinham da 1ª mixagem; a −37 LUFS cada, ficavam no nível da música e a mascaravam. Medir em TODO stem o % do tempo presente e justificar cada cama por plano.
- **Decompor stems aprovados por fonte:** a cadeia é linear depois do ganho de abaixamento → gerar cada camada sozinha com o MESMO abaixamento e provar soma = stem aprovado (nulo ≤ −150 dBFS) antes de tirar ou trocar qualquer camada.
- **Música "inaudível" = nível calibrado ANTES do abaixamento + abaixamento ligado em quase toda a narração** (só 10 pausas ≥ 0,6 s). Medir música − voz DURANTE a fala (era −21 LU). Abaixamento dinâmico só na banda da voz (250 Hz–4 kHz, música ≥ 16 dB abaixo) com retorno de 0,5 s; subida nas pausas só 0,3 s depois da palavra.
- Faixa mais curta que o episódio: estender por compassos inteiros (grade de tempo + semelhança espectral nas emendas) e pôr o acorde final depois da última palavra. Anotar os instantes das emendas para o usuário ouvir.
- **Nível de efeito relativo à voz:** referência = fala ATIVA em ±0,8 s (efeito numa pausa ficava −40 dB); mecanismos repetidos com nível único do plano; teto por loudness K.
- **Sincronia medida no som ISOLADO e processado** (filtro, tom): achou pré-clique 77 ms antes (válvula) e pico 314 ms depois do ataque (gravação "Piston sound" contínua, sem golpes). Eventos vizinhos na mesma camada confundem a medida.
- O p5 de voz − resto é dominado por janelas de pausa e borda de palavra: medir também só nas janelas com fala.
- Baixar vídeo do YouTube para análise foi bloqueado pela política da sessão: não contornar; pedir autorização ao usuário.
- **Emendas musicais respeitam a frase** (aqui, 4 compassos: croma com 4 antes 0,84 × 1 antes 0,72): inserir múltiplos da frase vindos de um trecho DISTANTE, nunca repetir o que acabou de tocar nem 1 compasso solto.
- **Música no alto-falante de celular durante fala contínua** tem teto físico: voz e trilha disputam 450 Hz–4 kHz. EQ dinâmica por banda só ganhou presença cobrando inteligibilidade; medir antes de prometer.
- **Curva de visualização ≠ estado físico:** `uTrab` 0→1 no E2 é o desenho do trabalho elétrico, não o compressor ligando.

### Rodada 13C e 13.1
- **`round()` do Python arredonda empates para o PAR:** plano com g0 a meio quadro escolhe os quadros 8, 8, 10, 10… → 15 qps efetivos. Varrer todas as cenas por frac(g0·30) = 0,5 e usar `floor(x + 0,5)`.
- **Peças que se encostam face a face dentro de um corte** (bobina × estator, cilindro × placa de válvulas) brigam mesmo com a tampa por face interna: provar ocultando peça a peça e varrer TODOS os pares de faces coplanares.
- Escolha da correção pela semântica da tampa: retirar a face de contato quando ela fica escondida; folga mínima (0,02 mm) quando a fresta cai numa borda que já existe.
- A região que "troca de cor" entre quadros é z-fighting, não iluminação.
- Pedido de efeito "mais baixo": mesma regra de perspectiva para todos os objetos, ganho por evento, instante intocado.
- Avisos retirados a pedido: retirar só o DESENHO preserva o posicionamento dos rótulos.
