# Ep. 02 · Decupagem cinematográfica v1

> **Tempos PROVISÓRIOS.** Ainda não existe narração aprovada. Cada plano começa numa **palavra** do roteiro
> (`planos.py`); os tempos vêm de `roteiro/palavras_provisorio.json`, calibrado na voz real do Ep. 01. Quando o áudio
> aprovado chegar, o alinhamento real substitui o provisório e **todos** os cortes, movimentos, rótulos e legendas são
> recalculados. Os tempos atualizados ficam em `planos_resolvidos.json`.
> Duração provisória: **171,5 s** (fala 169,9 s + respiro de 1,6 s).

## Convenções

- **Cenas 3D** (uma exportação do Blender cada): `cozinha`, `interior`, `corte`, `evaporador`, `compressor`, `traseira`
  e `capilar`. Os planos da mesma cena compartilham geometria, luz e tempo global.
- **Cores** (ver `ciencia/validacao_cientifica.md` §6):
  - temperatura: azul / cinza-claro / laranja-vermelho, centrada na temperatura da cozinha;
  - calor: feixes âmbar contínuos;
  - trabalho: violeta;
  - pressão: manômetros neutros.
- **Avisos honestos** (canto superior direito): "Visão térmica (ilustrativa)", "Corte ilustrativo", "Tempo acelerado",
  "Câmera lenta" e "Fluxo desacelerado".
- **Som:** sons ligados a ações visíveis (curvas de movimento), ambientes por cena, sem graves cinematográficos e sem som em
  cada seta. O fluido **nunca** usa sons de água.
- **Ritmo:** acontecimento visual novo a cada 2–4 s. A câmera acompanha a ação, não gira em volta de objeto parado.

---

## A · A contradição (0,0–12,3 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| A1 | "Você já reparou que a geladeira" | Situar: objeto comum, reconhecível | Cozinha ao entardecer, luz da janela. A porta se abre e a luz interna acende; garrafa e alimentos na prateleira | Dolly lento para a frente, altura dos olhos, 35 mm | Ambiente da cozinha discreto; zumbido baixo do compressor; estalo da vedação na abertura | — | — |
| A2 | "é fria por dentro, mas" | Mostrar o frio com **evidência** (visão térmica), não com névoa | Uma varredura vertical troca a imagem pela visão térmica: interior azul, cozinha cinza-claro | Continua o dolly | Nenhum efeito na varredura | "Visão térmica (ilustrativa)" | Varredura (dentro do plano) |
| A3 | "pode ficar quente por fora?" | Mostrar o lado quente | A câmera contorna a lateral; a traseira aparece laranja/vermelha (serpentina e compressor) | Arco lateral de ~100°, sem parar | Zumbido do compressor fica mais presente com a proximidade | mantém o aviso | Corte seco |
| A4 | "Parece estranho: … ao mesmo tempo?" | Contradição num quadro só | Plano 3/4 traseiro: porta aberta (interior azul) e traseira quente juntas. Aos ~3 s, a imagem volta ao normal só na metade de cima, reforçando "a mesma máquina" | Lento afastamento | Ambiente | mantém o aviso até voltar ao normal | Fusão 0,3 s |

## B · O calor não desaparece (12,3–32,3 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| B1 | "A resposta é surpreendente." | Pausa e expectativa | Imagem normal; a porta continua aberta | Aproximação frontal lenta | Ambiente | — | Corte |
| B2 | "A geladeira não fabrica frio." | Desfazer a ideia de "frio saindo" | Caixa do congelador em close: nada sai dela (sem névoa, sem partículas) | Estática, leve deriva | Quase silêncio | — | Corte |
| B3 | "Ela transporta calor." | Apresentar a ideia central | Um feixe âmbar sai do interior, atravessa a parede (fantasma) e sai pela traseira | Plano lateral largo, câmera parada para o percurso ficar legível | Sem efeito no feixe | "calor" (só nesta primeira aparição) | Corte |
| B4 | "Imagine uma garrafa … ambiente." | Estado inicial | Garrafa na bancada; visão térmica: cinza-claro, igual à bancada | Macro lateral, 50 mm | Ambiente | "Visão térmica (ilustrativa)" | Corte |
| B5 | "Quando você a coloca … energia térmica." | Transferência de calor: do quente para o frio | Garrafa na prateleira; feixes âmbar saem dela para o ar frio; a cor dela vai de cinza para azul-claro | Close fixo dentro da geladeira | Porta fecha suavemente no início (estalo) | "Tempo acelerado" | Corte |
| B6 | "Mas esse calor não desaparece." | Conservação de energia | Os feixes sobem com o ar morno, sem desbotar | Tilt para cima acompanhando | — | — | Contínuo |
| B7 | "Ele precisa ir para algum lugar." | Destino: o evaporador | Os feixes chegam às paredes da caixa do congelador e entram nela | Continua subindo; enquadra a caixa | — | — | Fusão 0,3 s |

## C · Revelação do circuito (32,3–54,3 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| C1 | "Para descobrir … você nunca viu." | Entrar no mecanismo | Afastamento até a geladeira inteira em 3/4; a porta fecha; um plano de corte varre carcaça e espuma isolante, deixando ver dentro das paredes | Afastamento e órbita lenta (só enquanto o corte acontece) | Porta fecha; o corte é silencioso | "Corte ilustrativo" | Contínuo |
| C2 | "Escondido atrás … circuito fechado de tubos." | O circuito é **fechado** e contínuo | Tubos revelados: evaporador, linhas na parede, compressor, serpentina, capilar. Um pulso luminoso percorre o circuito inteiro e volta ao ponto de partida | Câmera parada (o pulso é o movimento) | Nenhum som no pulso | — | Corte |
| C3 | "Dentro dele circula … fluido refrigerante." | Apresentar o fluido | Close de um tubo em corte longitudinal: o fluido se move dentro dele | Travelling ao longo do tubo | Fluxo quase inaudível: sopro filtrado, **não** água | "fluido refrigerante" | Corte |
| C4 | "Durante o percurso … estado físico." | Três grandezas independentes | Circuito inteiro com cores de temperatura. Em "pressão" surgem os dois manômetros; em "temperatura" a legenda de cores; em "estado físico" aproximação de um trecho com bolhas | Órbita curta e depois aproximação | Nenhum som nos rótulos | Manômetros "baixa"/"alta"; escala "mais frio ↔ mais quente que a cozinha" | Fusão 0,3 s |

## D · Evaporador (54,3–79,9 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| D1 | "Vamos começar pelo evaporador …" | Localizar o evaporador | Caixa do congelador em corte; canais das placas visíveis | Aproximação descendente | Ambiente interno contido | "Evaporador" | Corte |
| D2 | "Ali, o fluido chega frio … líquido e vapor." | Estado de entrada: frio, baixa pressão, mistura | Entrada do evaporador em corte: líquido azul com bolhas; manômetro de baixa ao lado | Macro, travelling lento a favor do fluxo | Borbulhar muito discreto e seco (sem água) | "baixa pressão" no manômetro | Corte |
| D3 | "Como está mais frio … paredes dos tubos." | Mecanismo: diferença de temperatura | Interior em corte: o ar morno sobe dos alimentos e esfria nas placas; feixes âmbar atravessam a parede do canal | Plano médio lateral | Ambiente | Mini comparação: "fluido mais frio que o ar" | Corte |
| D4 | "Ao absorver … a parte líquida evapora." | Mudança de fase com calor entrando | Macro ao longo do canal: as bolhas crescem e o líquido diminui até restar só vapor; a cor quase não muda (a energia vai para a vaporização) | Travelling a favor do fluxo | Borbulhar que rareia até sumir | "Fluxo desacelerado" | Contínuo |
| D5 | "O calor saiu dos alimentos e entrou no refrigerante." | Fechar a etapa | Afastamento: alimentos → ar → fluido num quadro; o vapor sai pela linha de sucção | Afastamento | — | — | Corte |

## E · Compressor (79,9–97,3 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| E1 | "Mas como mandar esse calor para fora?" | Problema: o vapor está frio demais para ceder calor | A câmera acompanha o vapor descendo pela linha de sucção na parede traseira | Travelling descendente | — | — | Corte |
| E2 | "É aqui que entra o compressor, movido por eletricidade." | Fonte de trabalho | Compressor (cúpula preta) no nicho; cabo de força com pulsos violeta; carcaça vibra pouco | Aproximação baixa | Zumbido do compressor (gravação real, licença verificada) | "Compressor" | Corte |
| E3 | "Ele suga o vapor e o comprime …" | Mecanismo real | Corte da carcaça: motor gira o virabrequim; biela e pistão (biela-manivela exata); válvula de sucção abre na admissão e a de descarga perto do fim da compressão; o gás no cilindro passa de azul a vermelho | Close do cilindro | Pulsação mecânica sincronizada às válvulas, baixa | "Câmera lenta"; manômetro de alta sobe | Corte |
| E4 | "Agora, o refrigerante está mais quente que o ar da cozinha." | Condição para ceder calor | Tubo de descarga vermelho em primeiro plano; ar da cozinha cinza ao fundo; duas barras de temperatura lado a lado | Plano fixo | — | "fluido" × "ar da cozinha" | Fusão 0,3 s |

## F · Condensador (97,3–108,5 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| F1 | "Por isso, ao atravessar o condensador …" | Rejeição de calor | Serpentina traseira: feixes âmbar saem dos tubos e arames para o ar, que sobe atrás da geladeira | Plano traseiro 3/4, subida lenta acompanhando o ar | Ambiente | "Condensador" | Corte |
| F2 | "Enquanto perde energia … em líquido." | Condensação | Macro do tubo: gotas nas paredes, depois película, depois tubo cheio de líquido; a cor vai de vermelho a laranja-claro e fica constante durante a condensação | Travelling a favor do fluxo | — | "Fluxo desacelerado" | Corte |

## G · Expansão (108,5–121,0 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| G1 | "Só falta uma etapa." | Transição | Saída da serpentina → filtro secador | Pan curto | — | — | Corte |
| G2 | "Esse líquido passa … chamado capilar." | Mostrar o capilar | Capilar ao lado da linha de sucção: a diferença de diâmetro é evidente; o capilar segue enrolado | Macro lateral | — | "Capilar" | Corte |
| G3 | "A pressão cai bruscamente … resfriando a mistura." | Expansão isentálpica | Macro ao longo do capilar: ponteiro do manômetro desce com a posição (mais rápido no fim); bolhas aparecem a partir da metade; a cor vai de laranja-claro para azul. **Nenhum** feixe de calor entra ou sai | Travelling acelerando | Chiado fino e baixo no fim do capilar (gravação real) | manômetro móvel | Contínuo |

## H · O circuito completo (121,0–130,4 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| H1 | "Assim, ela volta ao evaporador …" | Fechar o ciclo | A mistura azul entra de novo no evaporador; a câmera se afasta até ver o sistema inteiro | Grande afastamento contínuo | — | — | Contínuo |
| H2 | "E tudo recomeça …" | Sistema integrado | Calor âmbar entrando no evaporador; violeta no compressor; âmbar mais largo saindo do condensador; fluido circulando; manômetros estáveis | Plano geral, deriva lenta | Compressor | rótulos curtos dos 4 componentes, juntos | Fusão 0,3 s |

## I · A porta aberta (130,4–153,6 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| I1 | "Agora pense … porta aberta." | Novo cenário | Cozinha normal; a porta se abre e fica aberta | Igual a A1 (rima visual) | Estalo da vedação | — | Corte |
| I2 | "O calor do ambiente entra … trabalhar mais." | Carga térmica maior | Ar frio escapa por baixo e ar da cozinha entra por cima; feixes âmbar entrando sem parar; pulsos violeta mais rápidos; o compressor não desliga | Lateral, porta em perfil | Compressor contínuo | — | Corte |
| I3 | "Se a porta ficar aberta … resfriar o cômodo." | Cômodo fechado | Vista de cima, em corte, da cozinha fechada: o calor entra pela frente e sai pela traseira para o MESMO ar | Plano zenital, deriva | — | "mesma cozinha" | Corte |
| I4 | "No balanço total … usada para funcionar." | 1ª lei (Q̇_rej = Q̇_abs + Ẇ) | **3 tempos**: (1) faixa de entrada com largura Q̇_abs; (2) faixa violeta entrando pelo cabo; (3) faixa de saída mais larga (soma). Termômetro do cômodo sobe um pouco | Zenital, leve aproximação no tempo 3 | — | "calor retirado" + "energia elétrica" = "calor liberado" | Fusão 0,3 s |

## J · Conclusão (153,6–171,5 s)

| Plano | Narração | Objetivo | Acontecimento | Câmera | Som | Rótulos / avisos | Transição |
|---|---|---|---|---|---|---|---|
| J1 | "Então, por que … quente por fora?" | Retomar a pergunta | Rima com A4: visão térmica, porta aberta, frio dentro e quente fora | Igual a A4 | Ambiente | "Visão térmica (ilustrativa)" | Corte |
| J2 | "Porque o frio não está sendo produzido." | Negar o "frio" | Imagem normal; caixa do congelador sem nada saindo | Igual a B2 | Quase silêncio | — | Corte |
| J3 | "O calor está sendo retirado … levado para outro." | Resposta visual | Corte: um feixe âmbar vai do interior, pelo circuito, até a traseira e o ar | Plano lateral largo (rima com B3) | — | — | Fusão 0,4 s |
| J4 | "A geladeira não cria frio. Ela dá um destino ao calor." | Conclusão | Geladeira fechada na cozinha; calor saindo discretamente da traseira; o último movimento termina junto da última palavra | Afastamento lento e parada | Ambiente; compressor desliga suavemente no fim (termostato) | — | Fim (sem vinheta, sem mascote) |

---

## Dependências de render

| Cena 3D | Planos | Elementos novos no motor |
|---|---|---|
| cozinha | A1–A4, B1–B4, I1–I4, J1, J2, J4 | Luz de interior (janela + luzes), **visão térmica** por material, porta animada, feixes de calor, termômetro do cômodo |
| interior | B5–B7, D3 | Convecção do ar (feixes) e garrafa com temperatura animada |
| corte | C1–C4, E1, H1, H2, J3 | Plano de corte animado, **fluido no tubo** (cor por T, aparência por fase, fluxo), pulso ao longo do circuito, manômetros |
| evaporador | D1, D2, D4, D5 | Canais em corte com bolhas (título do modelo) |
| compressor | E2–E4 | Mecanismo biela-manivela, válvulas, gás no cilindro |
| traseira | F1, F2, G1 | Serpentina com arames, gotas e película no condensador |
| capilar | G2, G3 | Capilar enrolado; bolhas a partir de s = 0,53; manômetro móvel |

## Pontos de decisão para o usuário

1. **Visão térmica** como evidência do "frio dentro / quente fora" (A2–A4, B4, J1), sempre com o aviso "ilustrativa".
2. **Paleta de temperatura centrada na cozinha** (azul = mais frio que o ambiente; vermelho = mais quente).
3. Geladeira de **uma porta** com congelador interno (evaporador visível) e **serpentina traseira**.
4. Números absolutos (°C, bar) **fora da tela**; a imagem só mostra comparações relativas.
