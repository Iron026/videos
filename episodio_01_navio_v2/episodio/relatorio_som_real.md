# Ep. 01 · Sound design com gravações reais + correção da água em 1:19

| Entrega | Arquivo |
|---|---|
| Demonstração alternada (cada trecho: som anterior → gravações reais) | `episodio/ep01_demo_som_AB.mp4` (196,6 s) |
| Só gravações reais (4 trechos) | `episodio/ep01_demo_som_real.mp4` (98,3 s) |
| Só som anterior, sintético (4 trechos) | `episodio/ep01_demo_som_sintetico.mp4` (98,3 s) |
| Água em 1:19, antes × depois (lado a lado) | `episodio/ep01_agua_1m19_antes_depois.mp4` (7 s) |
| Fontes e licenças de cada gravação | `episodio/som/fontes_efeitos_reais.md` (+ `.json`) |
| Medições | `som/mix_real.json` · `som/demos_medidas.json` · `som/demos_sincronia_ms.json` · `som/sincronia_eventos_real.json` |

**Trechos das demos:**
1. Abertura, 0–15 s.
2. Estaleiro e solda, 15–30 s.
3. Empuxo, retomada e experimento, 48–95 s.
4. Avaria, 134–155 s.

Nas duas versões são as mesmas imagens, a mesma narração, a mesma trilha e **o mesmo processo de mixagem** (reverberação por ambiente, ducking, master). Cada trecho foi igualado em **−16 LUFS** (±0,1), para comparar o som e não o volume.

## 1. Limitações (antes de tudo)

- **Referência (Desmontando o Mundo): não assisti nem escutei os vídeos citados.** Não tenho como reproduzir áudio, e não baixei nem extraí nada do canal. Nada neste relatório é análise auditiva da referência.
- **Não escuto as gravações.** Escolhi cada uma assim:
  - pelo **título e pelas categorias da biblioteca**;
  - por uma **análise técnica objetiva** (formato, pico, clipping, piso de ruído, faixa de frequências, posição do ataque);
  - por um **detector de voz humana** (Whisper com detecção de atividade de voz): nenhuma das 84 candidatas tem fala detectada.

  O julgamento de timbre (se o som "convence") depende da sua escuta.
- **Bibliotecas:**

  | Biblioteca | Situação |
  |---|---|
  | **Mixkit** | ✅ usada |
  | Freesound | o servidor recusa este ambiente em nuvem (HTTP 403 vazio, inclusive na API) |
  | Pixabay | exige o desafio anti-robô da Cloudflare; não contornei |
  | YouTube Audio Library | exige login no YouTube Studio |

## 2. Licenças

- Todas as **43 gravações** usadas (98 usos) são do **Mixkit**, sob a **Mixkit Sound Effects Free License**, conferida em 19/11/2026 em https://mixkit.co/license/#sfxFree.
  - **Permitido:** uso em vídeos do YouTube e projetos comerciais e monetizados. **Atribuição não exigida.**
  - **Proibido:** redistribuir o arquivo isolado e registrá-lo em serviço de gestão de direitos (Content ID).
- O registro completo está em `fontes_efeitos_reais.md`: ID, nome, URL original, URL do arquivo, licença, atribuição, arquivo local e onde cada uma foi usada. **Autor:** o Mixkit não identifica o artista dos efeitos; está registrado como "Mixkit (Envato)".
- Por causa da proibição de redistribuir, **os WAVs baixados não vão para o repositório**. `som/baixar_efeitos.py` os baixa de novo das URLs oficiais. Os stems com gravações reais também ficam fora do git e são regenerados por `som/som_real.py` em ~1,5 min.

## 3. Gravações usadas por trecho (substituindo a síntese)

| Trecho | Gravações reais (ID Mixkit) |
|---|---|
| **Abertura** | <ul><li>**Arrasto do aço no concreto:** tampa de bueiro de ferro, 2927.</li><li>**Baque grave na borda:** 752.</li><li>**Queda:** 1461.</li><li>**Impacto na água em câmera lenta:** duas gravações de mergulho em camadas, 1304 + 1180, levemente mais graves (tom 0,72–0,8, só porque a cena está a 0,35×), + baque 752.</li><li>**Bolhas e afundamento debaixo d'água:** 1178, 1321.</li><li>**Leito e sedimento:** 2498, 753.</li><li>**Cais:** pedras do porto 1208, mar distante 1191.</li><li>**Mar aberto:** 1189, vento 1200.</li><li>**Máquinas do navio:** 3077.</li><li>**Casco passando:** 3078.</li><li>**Onda de proa:** 2461.</li><li>**Espuma e esteira:** 1195.</li></ul> |
| **Estaleiro e solda** | <ul><li>**Ambiente de estaleiro naval:** 3074; máquinas ao fundo 803.</li><li>**Motor do carro do pórtico:** 1619 (motor de escada mecânica), com volume seguindo a velocidade real do carro, **sem alterar a altura**.</li><li>**Rodas no trilho:** 1534.</li><li>**Rangidos de cabo/estrutura** nas arrancadas e freadas: 3076.</li><li>**Encaixe da chapa:** porta de aço pesada 201 + batida metálica 2980.</li><li>**Solda:** gravação real de arco e faíscas 2603, só nos cordões, com o brilho do shader como envelope suave (±4 dB); solda ao fundo 812, 814.</li><li>**Chapas chegando:** **5 contatos selecionados** (2754, 3158, 2980, 201), e não 39.</li></ul> |
| **Empuxo** | <ul><li>**Entrada da câmera na água:** 2923, bolhas 1321.</li><li>**Ambiente subaquático:** 1312 + 1205.</li><li>**Casco sob pressão:** rangido grave e discreto, 3076.</li><li>**Água deslocada enchendo o volume:** 1877.</li><li>**Síntese mantida só na formação gráfica** (laterais se anulam, convergência, empuxo), em nível baixo.</li></ul> |
| **Retomada** | <ul><li>**O mesmo arrasto** (outro trecho de 2927).</li><li>**Borda:** 752.</li><li>**Impacto na água:** variação 2923 + 1304 + 752.</li><li>**Passagem para a câmera lenta:** 1167.</li><li>**Bolhas lentas:** 1178 (tom 0,8).</li><li>**Leito:** 2498, sedimento 753.</li></ul> |
| **Experimento** | <ul><li>**Bloco:** respingo curto e denso 1304 + baque 752, depois afunda borbulhando, abafado (1178).</li><li>**Casco:** mergulho largo 1180, água espirrando ao longo do costado 1198, onda de deslocamento 1195, e 4 batidas de água a cada balanço até parar (1208, cada vez mais fracas).</li><li>Os dois ficam em lados opostos do estéreo.</li></ul> |
| **Avaria** | <ul><li>**Ruptura:** batida metálica 2980 + aço raspando 200.</li><li>**Bolhas sugadas:** 1877, 1321.</li><li>**Água sob pressão:** cascata forte 3029 + jorro 3140, que diminuem quando o rombo é coberto.</li><li>**Turbulência do porão enchendo:** 2461 + gorgolejo 1877.</li><li>**5 golpes de água nas anteparas:** 1198, 3216, 1311.</li><li>**6 rangidos do casco sob carga:** 3076.</li><li>**Tensão grave crescente** (cama industrial real 2509), que **alivia** após as divisórias.</li><li>**Divisórias:** batida firme, 201.</li><li>Tudo com reverberação de compartimento de aço.</li></ul> |

**Edição de cada gravação:**
- Recorte no **ataque real do evento**.
- Fusões curtas nas pontas.
- Normalização de nível.
- Equalização por ambiente: grave abafado debaixo d'água, corte de agudos no que está distante.
- Camadas só nos impactos (no máximo 3 gravações).
- **Altura:** só ligeiramente mais grave nos impactos em câmera lenta. Nenhuma gravação foi acelerada.
- **Camas contínuas** feitas com emendas por fusão, sem mudar a altura.

## 4. Correção da água em 1:19

- **Causa:** no plano 35 (78,6–81,5 s) a câmera ficava do **lado de fora** do volume de água do diorama e se aproximava da face de corte até 0,1 m. O motor recorta tudo o que está a menos de 0,5 m da câmera (plano próximo). A partir de **79,8 s** a face da água era recortada e aparecia o fundo: céu e guindaste.
- **Não era:** troca de plano de água, oclusor, transição entre cenas nem shader.
- **Primeira tentativa (descartada):** câmera dentro da água. Deu outro problema: a superfície vista por baixo mostrava o céu.
- **Correção adotada:** a câmera continua fora, como no plano aprovado, mas **fica sempre a 0,9 m da face** (lente 28,5 mm, mesmo enquadramento).
- Foram re-renderizados **87 quadros (78,6–81,5 s)**. O resto do segmento não mudou.

## 5. Mixagem e validação

| Verificação | Som anterior (sintético) | Gravações reais |
|---|---|---|
| Loudness integrado (mix) | −14,0 LUFS | −14,0 LUFS |
| Pico verdadeiro | −1,8 dBTP | −1,8 dBTP |
| Limitador (máx.) | 2,8 dB | 2,8 dB, só no impacto da abertura |
| Mono × estéreo | −14,06 / −14,03 | −14,04 / −14,01 (sem perda) |
| **Voz no celular** (simulação mono 350 Hz–7 kHz): mediana | 22,7 dB | **24,2 dB** |
| Voz no celular: fala plena com voz ≥ 10 dB acima do fundo | 95,4% | **97,1%** |
| Demos: loudness por trecho | −16,0 a −16,1 LUFS | −16,0 a −16,1 LUFS |
| Demos: pico por trecho | −3,6 a −4,4 dBTP | −3,5 a −4,3 dBTP |
| Narração nas demos | +8 ms em todos os trechos | +8 ms em todos os trechos (< 1 quadro) |

**Sincronia dos impactos** (ataque medido × evento da animação):

| Evento | Desvio |
|---|---|
| Borda | −16 ms |
| Água | −20 ms |
| Leito | +17 ms |
| Encaixe | −21 ms |
| Retomada | −21 ms |
| Leito na retomada | +19 ms |
| Experimento | −11 ms |
| Ruptura | −33 ms |
| Divisórias | −8 ms (medido na gravação isolada, porque o jato encobre a medição no mix) |

Os impactos entram ~20 ms antes de propósito, para o contato soar no quadro do toque.

## 6. O que falta e como melhorar

1. **O Mixkit não tem gravações específicas de guindaste portuário, guincho, corrente e contêiner.** Usei substitutos reais e próximos:
   - motor de escada mecânica de caminhão de bombeiro para o motor do pórtico;
   - portas de aço pesadas e batidas industriais para os contatos e encaixes;
   - tampa de bueiro de ferro para o aço arrastando no concreto.

   Se quiser sons exatos, você pode baixar no Freesound (CC0) ou no Pixabay os específicos e colocá-los em `som/bib/manual/` com a licença. Eu os encaixo nos mesmos instantes.
2. **Carregamento e conclusão** não estão nas demos, como pedido. Só serão refeitos depois da sua aprovação, com o mesmo método.
3. **Escuta:** a escolha final do timbre depende de você. Se alguma gravação soar errada, basta indicar o trecho e eu a troco por outra candidata. Há 84 baixadas e analisadas, 41 ainda não usadas.

**Nada foi publicado, nada foi contratado e o render em 1080 × 1920 não foi iniciado.**
