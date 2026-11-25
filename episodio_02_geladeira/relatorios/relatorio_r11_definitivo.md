# Ep. 02 · Render definitivo e entrega (rodada 11)

"Como a geladeira esfria sem produzir frio?" — 1080 × 1920, 30 fps, 4.537 quadros, 151,233 s.

Tudo aqui é **medida**. Eu meço, mas não assisto nem escuto como uma pessoa, então a aprovação estética e auditiva final é sua. **Nada foi publicado.** O Episódio 01 não foi alterado: o último commit nele é de 21/11.

## 1. Arquivos finais

| Arquivo | Onde | Tamanho | SHA-256 |
|---|---|---|---|
| Episódio definitivo | `episodio/definitivo/ep02_definitivo_1080x1920.mp4.parte00-01` | 159.996.421 B | `32baf7334a461e2b00525ea0c5f27f46a06a5fcb77dd5bd28fc8fe6846efd4fa` |
| Master sem legendas | `episodio/definitivo/ep02_master_imagem_sem_legendas_1080.mp4.parte00-01` | 161.044.951 B | `50cd04cfd2c9c26b3d50b0eab98e160353310f0001943d3b77e9df8d07ff21a0` |
| Revisão 540 de referência | `episodio/ep02_v11_revisao_referencia.mp4` | 33.969.223 B | `f87a45aa695af9178c997f0124c9a3ea74df1c9af8ce73adb7d8005e56c29609` |
| Mixagem final, FLAC sem perdas | `som/preservado_r11/audio_ep02_r11_final.flac` | — | ver `som/preservado_r11/preservado_r11.json` |

- A remontagem e a troca de áudio estão em `episodio/definitivo/LEIA-ME.md`.
- O registro de versões, hashes e comandos está em `relatorios/manifesto_producao_r11.json`, chave `entrega_definitiva`.

Decisões preservadas, sem nenhuma alteração criativa nesta etapa:
- garrafa no B5;
- transição C (empurrão de 0,3 s aos 5,737 s);
- trilha Spice Intrigue;
- pop aprovado nas cinco apresentações;
- pouso da garrafa;
- obturador de 180° no C2 e no C4.

## 2. Testes e resultados

### Render e integridade dos quadros

| Teste | Resultado |
|---|---|
| Planos completos | 42 de 42 (A1 … J4) |
| Quadros renderizados em 1080 | 5.638 |
| Conferência de cada quadro (manifesto, SHA-256, decodificação, 1080 × 1920, não-preto) | **5.638 ok, 0 problemas** |
| Arquivos fora do manifesto | 0 |
| Paradas do verificador de saltos durante o render | 0. Os saltos aceitos têm justificativa registrada no log, como o mesmo salto na versão aprovada |
| Simulação de retomada (`--simular`) | 5.638 reaproveitados, **0 a renderizar** |

### Vídeo montado

| Teste | Resultado |
|---|---|
| Fluxo | H.264 yuv420p 1080 × 1920, 30/1, **4.537 quadros** decodificados, AAC 48 kHz em estéreo, 151,233 s |
| Marcações de revisão | Sem selo (conferido na imagem). O título dos metadados não tem "revisão", "animatic" nem "não publicar" |
| Quadros pretos | 0 (menor brilho médio: 28,5) |
| Final 1080 × revisão 540 com as mesmas decisões, quadro a quadro (faixa do selo excluída) | Correlação mínima 0,973, mediana 0,9975, diferença máxima 5,6. **0 quadros abaixo do limiar** (0,93 / 6) |
| Saltos entre quadros vizinhos fora dos cortes | 285. **278** aparecem iguais na revisão 540 aprovada (movimento e efeitos da cena). Os outros 7 ficam no limite do critério nas duas versões. Exemplo: final 0,926 / 12,0 contra 0,931 / 11,5 na revisão, e o mesmo quadro final × revisão ≥ 0,98. Nenhum salto novo |
| Master × definitivo | Diferenças só na faixa de 64 % a 78 % da altura, onde ficam as legendas. 373 quadros sem legenda são idênticos |
| Transição C no material final | Mesmos números do teste 1080 aprovado; o arquivo de medidas não mudou. Fora da janela, a imagem é idêntica ao corte seco. Rastro / deslocamento = 0,49–0,50 (obturador de 180°) |
| Cintilação, detector absoluto em todos os quadros 1080 reduzidos a 540, × revisão 540 | Igual por plano, com variação de poucos quadros. B5 (6 quadros) é a garrafa e dá o mesmo resultado na revisão 540 atual. D3 (129 × 74 quadros, pior com 10 blocos) são as linhas finas da prateleira e da luz no alto do quadro em câmera móvel: mesmo lugar na versão aprovada, com menos pixels por quadro no 1080 (mediana 1.496 × 2.030). Não é regressão |

### Áudio, medido no AAC final de cada arquivo

| Medida | Definitivo | Master sem legendas | Meta |
|---|---|---|---|
| Loudness | **−14,1 LUFS** | −14,1 LUFS | −14 |
| Pico verdadeiro | **−1,68 dBTP** | −1,68 dBTP | ≤ −1,5 |
| Voz − resto no celular simulado (p5 / mediana) | **12,2 / 25,8 dB** | 12,2 dB | ≥ 10 |
| Perda em mono | −0,01 dB | — | ~0 |
| Último 0,5 s | −45,6 dBFS | — | silêncio |
| Áudio decodificado | `87d457ac…` | idêntico | igual à revisão 540 aprovada (idêntico) |

Inteligibilidade nos instantes dos pops, no AAC definitivo. A janela vai de t − 0,02 a t + 0,20 s, na faixa do celular:

| Evento | t (s) | Alvo em relação à voz | Voz − resto no evento | Voz − resto em ±0,5 s | AAC × WAV |
|---|---|---|---|---|---|
| Garrafa pousa (B5) | 20,84 | −12 dB | 12,0 dB | 18,7 dB | corr. 0,9999 / −0,02 dB |
| Fluido refrigerante (C3) | 41,57 | −9 dB | 8,9 dB | 10,8 dB | 0,9998 / −0,04 dB |
| Evaporador (D1) | 49,69 | −9 dB | 9,0 dB | 14,9 dB | 0,9999 / −0,01 dB |
| Compressor (E2) | 75,563 | −9 dB | 8,9 dB | 16,1 dB | 0,9999 / −0,01 dB |
| Condensador (F1) | 88,343 | −9 dB | 9,0 dB | 15,4 dB | 0,9999 / −0,03 dB |
| Capilar (G2) | 101,23 | −9 dB | 8,6 dB | 12,4 dB | 0,9999 / −0,02 dB |

A voz continua dominante em todos (≥ 6 dB por critério), e o AAC reproduz cada evento. O atraso entre AAC e WAV é de 0 amostra.

## 3. Preservação e armazenamento

- **Versões anteriores:** V8, V9, V9a e as revisões V10 continuam no git, sem alteração. Também estão lá os A/B e as mixagens antigas (`som/audio_ep02*.flac`, `som/stems/ep02_*.flac`).
- **Narração original:** o MP3 está intacto, SHA-256 `fdedd877…05726ee`, igual ao do git.
- **Mixagem final e stems da validação:** em FLAC 24 bits, em `som/preservado_r11/`:
  - a mixagem e os stems da R10 são idênticos amostra a amostra;
  - os quatro stems em ponto flutuante foram gravados × 0,5, porque têm pico acima de 0 dBFS. Restaurar × 2; o erro é de 1,2·10⁻⁷ (−138 dBFS).
- **Stem de música:** não entra isolado no git, por causa da licença da Mixkit. Ele está dentro da mixagem.
- **Manifestos:** os manifestos de render por plano ficam em `quadros_final/*/_manifesto_quadros.json`, que não estão no git, porque a pasta inteira é ignorada. O log, as validações e o manifesto de produção estão no git.
- **Persistência provada:** depois do push, fiz um clone novo e parcial das pastas de entrega. A conferência de `partes.sha256` passou, a remontagem foi feita e o SHA-256 dos dois MP4 bateu com a tabela (detalhes no fim da seção 5).

## 4. Problemas encontrados

1. **O contêiner reiniciou durante o render** (C4, bloco 60–119).
   - Os quadros gravados sobreviveram. A retomada reaproveitou 1.906 quadros por manifesto + SHA-256 e refez só o bloco que estava em andamento.
   - Nenhum plano concluído foi reiniciado.
2. **O validador final reprovou por saltos fora dos cortes.**
   - O critério automático não sabe o que é movimento da cena. Todos os 285 saltos foram conferidos na revisão aprovada e explicados (seção 2).
   - Não houve correção, porque não há defeito.
3. **O registro antigo de cintilação da revisão 540 era anterior à garrafa no B5.**
   - Refiz a medida na revisão 540 atual antes de comparar.

## 5. Pendências e avisos

- **Aprovação final:** assistir e escutar o `ep02_definitivo_1080x1920.mp4` no celular. Isso é seu.
- **Licença da narração:** a narração vem do plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória. Para monetizar, a voz precisa de licença compatível antes da publicação.
- **Contêiner temporário:** os quadros 1080 (`quadros_final/`, 1,6 GB, com os manifestos de render) **se perdem quando a sessão acabar**. Os MP4 definitivos, o master e o áudio estão salvos no git; os quadros não. Refazer o episódio com outra legenda exigiria renderizar tudo de novo, cerca de 31 h, que foi a soma dos blocos deste render. Trocar só o áudio usa o master e não precisa de render.
- **Publicação:** título, miniatura, descrição e créditos não foram preparados nesta etapa. Nada foi publicado.

### Prova de recuperação

Feita em 25/11/2026 a partir do commit `f5c7d4e`, numa pasta nova, com clone parcial (`--filter=blob:none --sparse --depth 1`) só das pastas de entrega:

- `sha256sum -c partes.sha256`: as 4 partes **OK**;
- remontagem com `cat`:
  - definitivo `32baf7334a46…6efd4fa`, **igual**;
  - master `50cd04cfd2c9…07ff21a0`, **igual**;
  - 4.537 quadros decodificados;
- os 7 FLAC de `som/preservado_r11/` têm SHA-256 igual ao registrado;
- a revisão 540 de referência tem SHA-256 `f87a45aa…`, **igual**.
