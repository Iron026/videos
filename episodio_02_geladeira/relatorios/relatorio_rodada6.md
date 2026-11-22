# Ep. 02 · Relatório da rodada 6 (validação final antes do render definitivo)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado.
O render definitivo de 151 s em 1080 p **não foi iniciado**. Só foram feitos trechos de diagnóstico de 1 s, como autorizado.
- **Preservados:**
  - narração: SHA-256 `fdedd877…05726ee`, conferido;
  - roteiro, palavras e modelo científico;
  - estrutura: 39 planos, mesmos tempos.
- **Vídeo:** 4.537 quadros, 151,233 s.

## Entregas
| Arquivo | O que é |
|---|---|
| `episodio/ep02_animatic.mp4` | **V6**: prévia completa, 540 × 960, mixagem da rodada 5 |
| `episodio/ep02_v5_x_v6_trechos.mp4` | V5 \| V6 lado a lado: A4 (8,6–10,4 s) e J3 (142,5–145,5 s) |
| `relatorios/antes_depois_v6.jpg` | Antes × depois de A4 e J3, nos mesmos instantes |
| `episodio/testes_1080/ep02_1080_{C2,G3,D4,E1,J3}.mp4` | Testes de 1 s em **1080 × 1920**, com rótulos, lupa, manômetro, avisos, legendas e áudio |
| `relatorios/testes_1080_folha.jpg` | Um quadro de cada teste em 1080 |
| `relatorios/g3_linha_ao_1080.jpg` | A linha do G3 em 1080 e as duas correções testadas |
| `relatorios/manometro_proposta_1080.jpg` | Proposta de manômetro legível (**desligada**) |
| `relatorios/cintilacao_1080.json`, `v5_x_v6_montado.json`, `som/validacao_audio.json` | Medidas |

## 1. J3: z-fighting corrigido
- **Correção:** a mesma do G3, só no J3 (`CORRECAO_PORTA = {'G3', 'J3'}`). O painel da porta recua 0,5 mm e deixa de
  coincidir com a vedação. Nos outros planos a geometria **não mudou**.
- **Cintilação no J3** (detector absoluto, quadros seguidos):
  - **antes:** 43 quadros com blocos piscantes (pior: 39 blocos);
  - **540, depois:** 0 quadros;
  - **1080, depois:** 0 quadros.
- **Sem regressão:**
  - a diferença entre o J3 da V5 e o da V6 fica **só na faixa da porta**, na borda esquerda (x 5–129 de 270);
  - a faixa escura que piscava virou a seção amarela da porta cortada, como no G3;
  - fora dela, só a variação natural do renderizador.

## 2. A4: mão fechada sob o queixo
- **Mão fechada:** nova peça, mão fechada e relaxada.
  - Dedos dobrados: o dorso dos nós fica para fora e encosta sob o queixo.
  - Pontas e polegar ficam do lado do pescoço.
  - **Nenhum dedo estendido.**
- **Troca:** substitui a mão aberta só durante o gesto do queixo (a partir de 15 % da subida do braço). Fora dele, continua
  a mão aberta.
- **Mesmo comprimento da mão aberta (0,10 m):** o ponto de contato e a trajetória do braço não mudaram.
- **Inalterados:** cabeça, olhar, sobrancelhas, expressão, respiração e o resto da animação.
- **Medido:**
  - a diferença entre o A4 da V5 e o da V6 fica na região da mão, a partir do quadro do gesto;
  - o resto é ruído do renderizador (média 1,55);
  - cintilação igual à V5 (14 quadros, da troca para a tela dividida térmica, já classificada antes).

## 3. Linha vertical do G3: investigada
**Origem (comprovada):**
1. **Ocultando materiais um a um:** a linha só existe com o **painel da porta e o gabinete juntos**.
2. **Ligando e desligando passes:** some sem o AO; continua sem MSAA e sem bloom.
3. **No código:** o `GTAOPass` do three.js desenha normais e profundidade com um único material de substituição **sem os
   planos de corte**. Por isso o AO "vê" a metade da geladeira **cortada fora**.
4. **Conclusão:** a linha é o vinco invisível entre a porta e a lateral removidas.

**Veredicto:** **artefato**, não borda legítima. Ela passa até por cima da caixa opaca do evaporador, onde não existe peça.
É um **defeito antigo do motor**, presente em todos os planos em corte desde a V1, não regressão.

**Correções testadas** (implementadas no motor, **desligadas por padrão**):
| Opção | Linha | Efeito colateral | Situação |
|---|---|---|---|
| `aocorte`: AO com os mesmos planos de corte da cor | some | Interior com sombras de contato mais profundas e corretas; granulado leve nas bordas das tampas de corte. O granulado não cintila (0 em 12 quadros seguidos). Muda o sombreado de **todo plano em corte** | **para sua decisão** |
| `aosem`: porta fora do AO | some | A porta parece translúcida (fantasma) | **descartada** |

Como nenhuma correção é localizada, a V6 sai com o G3 **como aprovado**: a linha continua, a lupa e a sincronização não
mudaram. Veja `g3_linha_ao_1080.jpg`.
- **Também verifiquei a linha cinza no E1:** ela continua sem AO (contraste igual). É o **capilar real**, uma borda
  legítima.

## 4. Duração do áudio
- **Antes:** a trilha passava 7 ms do último quadro (151,240 contra 151,233 s).
- **Correção na montagem:**
  - a trilha termina no último quadro (4.537 / 30);
  - 50 ms de fade-out em 151,18 s evitam clique. Nesse ponto só há ambiente (a última palavra termina em 149,64 s).
- **Narração e mixagem não foram mexidas.**

**Validação no AAC da V6 (medido):**
| Meta | V6 |
|---|---|
| −14 LUFS ± 0,5 | **−14,1** |
| pico verdadeiro ≤ −1,5 dBTP | **−1,68** |
| mono sem perda | −0,01 dB |
| voz ≥ 10 dB acima do resto no celular (p5) | **16,2 dB** (mediana 28,8) |
| fim | último 0,5 s a −45,6 dBFS |
| duração áudio = vídeo | **151,233 = 151,233 s** |
| integridade | AAC e H.264 decodificam inteiros sem erro |

## 5. Testes em 1080 × 1920
Perfil `final` (escala 1,0, AO 16, MSAA 4×, bloom 0,18), a mesma configuração do definitivo. Foram 30 quadros seguidos
por trecho, cerca de 11–23 s por quadro.

| Trecho | Cintilação (quadros com blocos) | Classificação |
|---|---|---|
| G3 104,2–105,2 s | **0 / 28** | limpo: correção da porta confirmada em 1080 |
| J3 144,2–145,2 s | **0 / 28** | limpo: correção da porta confirmada em 1080 |
| C2 36,9–37,9 s | 28 / 28 | falso positivo: linhas finas em órbita rápida (16–26 px por quadro); a câmera exportada é suave |
| D4 65,5–66,5 s | 28 / 28 | falso positivo: bolhas de vapor e faixas de calor animadas |
| E1 72,3–73,3 s | 28 / 28 | falso positivo: tubos do condensador passando na descida da câmera |
| G3z (lupa) | 28 / 28 | falso positivo: bolhas animadas no canal |

- **Antisserrilhado e materiais:** arames, tubos, bordas de corte e vidro ficam nítidos; sem acne de sombra.
- **Transparências:** garrafa, prateleiras e feixes corretos.
- **Profundidade:** boa, exceto pelo AO com corte (item 3).
- **Legibilidade no celular** (vídeo de 1080 em tela cheia; referência de ~30 px para o menor texto):
  - legenda 58 px, rótulos 44 px, avisos 26 px: legíveis;
  - **manômetro:** "pressão", "baixa" e "alta" têm 22 px, e os dois últimos encostam no anel. Pequeno no celular. É um
    defeito antigo, de todos os manômetros. Proposta pronta e **desligada** (`MANOMETRO_LEGIVEL=1`): mostrador 25 % maior e
    textos de 30 px fora do anel, com contorno.
- **Regressão corrigida (minha, da rodada 5):** a linha da lupa atravessava o manômetro e cortava "pres|são". Agora ela
  termina no topo do mostrador. A lupa e a sincronização não mudaram.
- **Risco a avaliar a olho** (eu não assisto): no fim do C2, a grade de arames (passo de ~12 px) anda 0–18 px na
  horizontal por quadro. Pode surgir **estroboscopia** (efeito roda-de-carroça) no celular. Só mudaria com câmera mais
  lenta ou desfoque de movimento, o que mexe num plano aprovado. Não mexi.

## 6. Som
- **Mixagem da rodada 5 preservada:** mesmos stems e ganhos. Só a montagem mudou (corte no último quadro + 50 ms de fade).
- **Fontes e licenças:** `relatorios/licencas_ep02.md` continua válido. Os mesmos 6 sons são Freesound CC0, e o chiado do
  capilar é síntese.
- **Originais do Freesound (em vez das prévias de 128 kb/s):** testei o acesso anônimo.
  - O download do original redireciona para o **login** (HTTP 302).
  - A API exige **OAuth** (HTTP 401).
  - Só uma conta Freesound gratuita resolve. Não criei conta nem usei credenciais.
  - **Opções:**
    - você baixa os 6 originais pelos ids do registro; eu troco e provo, por A/B, que só a qualidade mudou;
    - ou mantemos as prévias.
- **Narração:** licença **pendente**. O episódio **não** está liberado para uso comercial.

## 7. O que mudou e o que não mudou (medido no vídeo montado, V5 × V6)
- **Mudaram:**
  - **A4:** dif. média 1,09 (mão);
  - **J3:** 4,19 (faixa da porta);
  - **G3:** 0,66 (só a linha da lupa).
- **Os outros 36 planos:** nenhum render novo, quadros-fonte com data da rodada 5.
  - Diferença média de no máximo 0,70.
  - Nos vizinhos dos planos alterados (A3, B1, H1, H2, J4) a diferença vai até 1,11 e termina exatamente nos quadros-chave
    do codificador (4,9 / 11,1 / 114,7 / 147,93 s). É o x264 redistribuindo bits no mesmo grupo de quadros: ruído de
    codificação, não mudança de imagem.
- **Inalterados:**
  - roteiro, narração, palavras, legendas, cortes, duração;
  - corte seco de C2 e pulso;
  - modelo científico e verificação do G3 (`ciencia/verificar_g3.py` lê o exportado; o G3 não foi reexportado nesta
    rodada).

## 8. Problemas não resolvidos (decisão sua antes do definitivo)
1. **AO com corte (`aocorte`):** corrige a linha do G3 e o sombreado de todos os planos em corte, mas traz granulado leve
   nas tampas. Ligar ou manter como aprovado? Se ligar, recomendo um teste em 540 dos planos em corte antes.
2. **Manômetro legível:** ligar a proposta em todos os manômetros?
3. **C2:** possível estroboscopia da grade de arames no fim do movimento. Precisa de avaliação a olho.
4. **Originais do Freesound:** exigem conta (ver item 6).
5. **Licença da narração:** pendente.
6. **Detector:** os falsos positivos por textura animada e linhas finas em movimento continuam exigindo leitura humana.
   Eu meço, mas não assisto nem escuto como uma pessoa.

Os quadros em 1080 e as prévias ficam no contêiner temporário e se perdem no fim da sessão. Os trechos compostos, o código
e as medidas estão no git.
