# Ep. 01 · Polimento audiovisual (revisão 540 × 960, 30 fps)

| Entrega | Arquivo |
|---|---|
| **Episódio completo, nova revisão** (som híbrido + polimento visual) | `episodio/ep01_revisao_polimento.mp4` · 168,0 s · 5.040 quadros |
| Comparativo de **som** antes × depois (6 trechos, cada versão a −16 LUFS) | `episodio/ep01_comparativo_som_polimento.mp4` · 193 s |
| Comparativo **visual** antes × depois (lado a lado, 6 trechos) | `episodio/ep01_comparativo_visual_polimento.mp4` · 27 s |
| Fontes, licenças e usos de cada gravação | `episodio/som/fontes_efeitos_hibrido.md` (+ `.json`) |
| Medições | `som/mix_hibrido.json` · `som/sincronia_hibrido.json` · `som/comparativo_hibrido_medidas.json` · `som/reservas_hibrido.json` |

**Como os quadros foram gerados:**
- Todos a **30 fps reais**, renderizados de verdade.
  - Nenhum quadro da prévia de 10 fps foi duplicado.
  - Nenhum render em 1080 × 1920.
- Re-renderizei só o que o polimento mudou: **2.668 quadros** (s02, s0607, s08b, s10, s12x, s12, s13), mais **141 quadros** de proa e **53 quadros** do fim de s11.
- O resto da montagem reutiliza os quadros existentes.

## 1. Limitações (antes de tudo)

- **Canal de referência (Desmontando o Mundo): não assisti nem escutei nenhum vídeo.**
  - **O que bloqueou:** o YouTube exige login ("confirme que você não é um robô"). Não baixei nem extraí áudio do canal.
  - **O que consegui verificar:** só os metadados públicos do feed RSS — títulos, datas e visualizações dos 15 vídeos mais recentes. Exemplos:
    - "Como uma grua levanta cargas e cresce junto com o prédio?" — 2,5 mi de visualizações;
    - "Como uma barragem segura tanta água sem cair?" — 5,1 mi;
    - "Como se constrói um estádio de futebol?" — 10,2 mi.
  - **Nenhuma observação sobre som, ritmo ou visual do canal** neste relatório vem de assistir ou escutar. Nada do canal foi copiado.
- **Não escuto o resultado.**
  - Tudo o que segue sobre som são **medições objetivas**: níveis, picos, sincronia, inteligibilidade simulada no celular. Elas **não substituem a sua escuta**.
  - O timbre ("convence ou não") só você pode julgar.
- **Wikimedia Commons bloqueado para download.**
  - Encontrei e registrei (licença, autor, URL) gravações reais e muito específicas da série *Work With Sounds*, todas **CC BY 4.0**:
    - guindaste de estaleiro;
    - portêiner carregando navio porta-contêineres;
    - terminal de contêineres;
    - dique flutuante;
    - solda em navio;
    - ondas no casco;
    - praça de máquinas.
  - A página e a licença ficam acessíveis, mas o servidor **de arquivos** do Wikimedia recusou este IP de nuvem compartilhado com HTTP 429. A mensagem do servidor: *"Too many requests — please contact noc@wikimedia.org…"*.
  - Tentei com pausa de 10 min entre tentativas, durante **1 h 20 min**, sem sucesso. Só 1 arquivo chegou, no início (corrente de caçambas). Não o usei porque o detector de voz não estava disponível para checá-lo (próximo item).
  - Não tentei contornar o bloqueio.
  - **Por isso, onde planejei Commons, usei a melhor reserva do Mixkit e marquei cada caso** como `[RESERVA Mixkit: WWS … não pôde ser baixado]` no registro (11 casos, lista em `som/reservas_hibrido.json`).
- **Detector de voz (Whisper) indisponível nesta sessão:** o modelo saiu do cache e o servidor de modelos está bloqueado. As gravações do Mixkit usadas já tinham passado por essa checagem na rodada anterior, sem fala detectada.

## 2. Pendências visuais

| Item | Situação | O que foi feito |
|---|---|---|
| **Água em 1:19 (77–82 s)** | ✅ confirmado na montagem completa | Água contínua de 76,5 a 82,5 s, sem céu vazando (`comparativo visual`, trecho 4). |
| **Espuma e onda de proa** | ✅ resolvido | <ul><li>Material novo no motor: espuma procedural que escorre para ré na velocidade do navio.</li><li>Onda de proa em V aberta pela forma do casco.</li><li>Faixa de espuma ao longo do costado e esteira.</li><li>Crista subindo na roda de proa com **topo irregular**: a primeira versão tinha borda reta e um "retângulo" saindo da roda de proa; corrigido e re-renderizado.</li><li>Antes havia um triângulo branco chapado.</li></ul> |
| **Faces de água do diorama** | ✅ melhorado (efeito **sutil**) | <ul><li>A face de corte ganhou turbidez de baixa frequência e raios de luz suaves, que somem com a profundidade.</li><li>Mais visível na conclusão (s13) e na avaria (s12).</li><li>No empuxo (s0607), a diferença é discreta.</li></ul> |
| **Solda** | ✅ conferida | <ul><li>Arco, faíscas e som começam e terminam juntos: os cordões do som usam os mesmos instantes do shader (23,75–24,55 e 24,68–25,25 s).</li><li>O brilho modula o som em ±4 dB.</li></ul> |
| **Salto da superestrutura (30,3 s)** | ✅ resolvido na montagem | <ul><li>Fusão de **0,9 s** (antes 0,2 s), com aviso honesto **"Meses depois"** no mesmo estilo dos avisos "Câmera lenta" e "Tempo acelerado".</li><li>Sopro suave de transição no som.</li><li>Combina com a narração ("O casco vai tomando forma. E aqui está…").</li></ul> |
| **Leitura da inclinação (avaria)** | ✅ resolvido, sem exagerar | <ul><li>Dois planos novos: **proa** e **popa**, cada um com a **linha d'água antes** (amarela tracejada) e o **nível do mar** (branca).</li><li>Na proa as linhas se separam: "Proa: +2,6 m". Na popa coincidem: "Popa: +0,0 m".</li><li>Matemática inalterada: trim 0,707°, GM₁ 0,735 m.</li><li>Corrigida uma sobreposição de rótulos em 143,8 s.</li></ul> |
| **Verificação geral** (céu, luz, água, texturas, interseções, enquadramento, legibilidade, transições, pop-ins) | ✅ | <ul><li>Folha de contato do episódio a cada 4 s, mais comparação quadro a quadro dos segmentos re-renderizados.</li><li>**Problema real encontrado e corrigido:** câmera **parada por 1,2 s** em 132,7 s (fim das marcas de calado, já existia antes). Agora há uma aproximação lenta até o corte.</li><li>Detector de quadros parados e pretos: **0 ocorrências** na nova montagem. Na anterior havia 3 trechos parados.</li></ul> |

## 3. Som híbrido

**Base: gravações reais. Síntese só como complemento.** São **48 gravações reais** em **153 usos**, mais **20 complementos sintéticos** discretos:
- reforço grave sob 12 impactos (peso e escala);
- 2 transições sutis;
- formações gráficas do empuxo;
- brilho das células e das marcas;
- volume deslocado e "peso = empuxo" na conclusão.

Nenhum som eletrônico ou "de videogame". A síntese fica sempre abaixo do timbre real.

### Substitutos inadequados

| Antes | Agora | Situação |
|---|---|---|
| **Motor de escada de caminhão de bombeiro (1619)** para o pórtico | Zumbido de máquina industrial elétrica (2504) + carro rolando (1534), com volume seguindo a velocidade real do carro | ⚠️ **Ainda é substituto.** A gravação real do guindaste (Commons) não pôde ser baixada. |
| **Porta de prisão (201)** no encaixe da chapa | Impacto metálico pesado (783) + batida de fábrica com eco real de galpão (2983) + contato agudo (2980) + reforço grave | ✅ Trocado. Também nas chapas chegando e nas **divisórias estanques**. |
| **Tampa de bueiro (2927)** no arrasto do aço | Porta pesada de correr, corpo grave (1523) + raspagem metálica, grão (809) + grave sintético discreto da massa | ✅ Trocado (abertura e retomada). |

### Trechos completados

**Corte do casco e dique (30–48 s):**
- proa se separando: aço deslizando, rangido, peso;
- interior vazio: zumbido industrial distante;
- comporta: impacto metálico grave;
- jatos: cascata real;
- enchimento: água correndo e fluxo;
- picadeiros: rangido leve.

**Carregamento (94–134 s):**
- ambiente de porto, empilhadeiras ao fundo e água no cais;
- portêiner principal com volume = movimento do carro + spreader; guindastes vizinhos mais distantes;
- **3 pousos** no instante exato, com batida de caixa metálica + peso e cabos tensionando;
- no **tempo acelerado, sem som para cada contêiner**: o ambiente fica mais presente, com só 3 contatos distantes;
- água batendo no casco conforme o calado aumenta;
- marcas de calado: **um único** brilho sutil para as 5 linhas.

> ⚠️ O ambiente portuário e os guindastes usam reservas: obra urbana (819), caminhão (1621), máquina de obra (802). **Não são gravações de porto.** As específicas estão bloqueadas no Commons (seção 1).

**Conclusão (154–168 s):**
- bloco de 17 m: queda, impacto enorme em camadas (mais grave pela escala), respingo, água caindo e reforço grave;
- afundamento e bolhas, abafados;
- ambiente submerso;
- volume deslocado e "peso = empuxo" sutis;
- saída para o aéreo final: mar aberto, água no casco, vento;
- a trilha resolve no acorde final, como antes;
- sem mascote e sem vinheta.

### Mixagem (4 stems: narração, efeitos, ambiências, música) com ducking MODERADO

| | Antes (demo real) | **Agora** |
|---|---|---|
| Redução máxima do fundo sob a voz | 24 dB | **18 dB** |
| Redução máxima das **ambiências** sob a voz | 24 dB | **9 dB** (o ambiente não some) |
| Graves durante a fala | −6 dB | **−3 dB** |

Testei 4 calibrações e escolhi a que mantém o ambiente presente e a voz clara:

| Calibração | Fala plena ≥ 10 dB acima do fundo (celular) |
|---|---|
| A | 80% |
| B | 86% |
| C | 90% |
| **Escolhida** | **93,5%** |

## 4. Verificações

| Verificação | Resultado |
|---|---|
| **Duração** | **168,000 s** · 5.040 quadros · 30 fps · 540 × 960 |
| **Integridade da imagem** | Decodificação completa sem erros · **0** quadros pretos · **0** trechos parados (≥ 0,6 s) |
| **Loudness integrado** (AAC final) | **−14,0 LUFS** · LRA 2,2 LU |
| **Pico verdadeiro** (AAC final) | **−2,4 dBTP** |
| Correção de pico | <ul><li>Na 1ª montagem o AAC chegou a −0,9 dBTP: a codificação cria picos entre amostras.</li><li>A montagem agora mede o pico **no arquivo codificado** e baixa o teto do limitador até cumprir a meta.</li></ul> |
| **Mix WAV** | −14,06 LUFS · −1,8 dBTP · limitador sem reduções acima de 1,5 dB (janelas de 100 ms) |
| **Mono × estéreo** | −14,10 × −14,06 LUFS (sem perda em mono) · correlação L/R 0,955 |
| **Voz no celular** (simulação mono 350 Hz–7 kHz) | Mediana 20,0 dB acima do fundo · fala plena ≥ 10 dB em **93,5%** (antes 97,1%, com ducking bem mais forte) |
| **Sincronia da narração no MP4** | +3 ms, constante em 10, 60, 110 e 160 s (< 1/10 de quadro) |

**Sincronia dos impactos** (ataque medido × evento da animação):

| Evento | Desvio |
|---|---|
| Borda | −8 ms |
| Água (abertura) | −19 ms |
| Leito | +21 ms |
| Encaixe | −10 ms |
| Comporta | −23 ms |
| Retomada | −15 ms |
| Experimento | +2 ms |
| Pousos 1/2/3 | 0/0/0 ms |
| Ruptura | −3 ms |
| Divisórias | +12 ms |
| Conclusão | −5 ms |

Todos abaixo de 1 quadro (33 ms). Os pousos estavam +125 ms atrasados no 1º teste: a gravação tem um rangido antes da batida real, então a recortei direto na batida. O mesmo ajuste foi aplicado às chapas chegando.

**Narração original:** o MP3 aprovado está intacto (SHA-256 79e1e8f2…). A fala de assinatura é removida só na cópia de montagem.

## 5. Fontes e licenças

- Todas as gravações efetivamente usadas são do **Mixkit**, sob a Mixkit Sound Effects Free License:
  - YouTube, uso comercial e monetizado permitidos;
  - atribuição não exigida;
  - proibido redistribuir o arquivo isolado e registrá-lo em Content ID.
- Por isso os WAVs e os stems ficam fora do git: `som/baixar_efeitos.py` e `som/som_hibrido.py` os regeneram.
- Registro completo em `fontes_efeitos_hibrido.md`: ID, nome, autor, URL, licença, crédito, arquivo local e cada uso com instante.
- As gravações do Commons pesquisadas e não baixadas estão em `som/fontes_commons.json`, com página, autor e licença. **Nenhuma está no vídeo.**
- **Nenhum** arquivo CC BY-NC, CC BY-SA, de procedência duvidosa ou extraído do YouTube foi usado.
- `som/creditos_descricao.txt` gera os créditos da descrição. Hoje só o Mixkit, que nem exige.

## 6. O que ainda bloquearia o render definitivo em 1080 × 1920

1. **A sua escuta** do som híbrido, principalmente do pórtico, do porto e dos guindastes, que ainda são reservas.
   - **Para usar as gravações reais do Commons:** baixe os `.ogg` das páginas listadas em `som/fontes_commons.json` no seu navegador e coloque em `episodio/som/bib/commons/`. São 11 arquivos, os marcados como RESERVA no registro: Containershipgantrycrane, Shipyardcrane, ContainerTerminalatthePortofDortmund, Mobileharbourcrane, Containerreachstackers, Adjustingadrydock, Waterintakepumpingstation, Weldingonshipinfloatingdrydock, Smallwaves, Crane, IcebreakerKunashipsengine.
   - `python3 som/som_hibrido.py` passa a usá-los **automaticamente**, nos mesmos instantes, e o registro gera o crédito CC BY 4.0 exigido para a descrição.
2. **A sua aprovação visual** de três pontos:
   - espuma de proa;
   - planos novos da inclinação;
   - aviso "Meses depois".
3. **Nenhum bloqueio técnico conhecido.** Duração, sincronia, loudness, picos e integridade estão dentro das metas. O perfil `final` da montagem já usa a mesma cadeia, incluindo a nova medição de pico no AAC.

**Nada foi publicado, nada foi contratado e o render em 1080 × 1920 não foi iniciado.**
