# Ep. 02 · R13: relatório final da montagem definitiva

**Arquivos:**
- `episodio/ep02_definitivo_r13_1080x1920.mp4`: o episódio completo, com legendas;
- `episodio/ep02_master_imagem_sem_legendas_r13_1080.mp4`: o master sem legendas.

No git, os dois estão em partes de 95 MB, em `episodio/definitivo_r13/`, com instruções e SHA-256.

**Situação:**
- **Aprovação técnica: passou.**
- **A aprovação final do vídeo completo é sua.** Eu meço, mas não assisto nem escuto como uma pessoa.
- **Nada foi publicado.** O Episódio 01 não foi alterado.

## 1. Decisões aplicadas (todas aprovadas por você)

| Item | O que entrou |
|---|---|
| Som | Mixagem R13C final (`som/audio_ep02_r13_r13c_final_r13_teste.wav`): mixagem B com Spice Intrigue, ruído contínuo removido, efeitos retirados em 0:14, 1:12 e 1:48, 0:33 **discreta**, passos de 1:55 e batida da porta de 0:29,6 pela perspectiva |
| E3 | Quadros `quadros_final_r13c2/E3`, da cena `E3_r13c_v2`: bobina com as faces de contato retiradas e bloco do cilindro com folga de 0,02 mm |
| Quadros repetidos | `ARRED_QUADROS=1` no A1, B7, H1 e I1 |
| Entrada do E3 | **A fusão atual foi mantida.** O corte seco não foi usado |
| Todo o resto | Igual à R12: geometria, câmera, legendas, narração, modelo científico, cortes e tempos |

A montagem está registrada em `episodio/montar_r13.sh`. Nenhuma cena intacta foi renderizada de novo.

## 2. Quadros repetidos: validação pedida antes de incorporar

Registro em `relatorios/testes_r13c/validacao_quadros_repetidos.json`.

| Plano | Índice antes (repetições / saltos de 2) | Índice depois |
|---|---|---|
| A1 | 17 / 17 | passo único: 0 repetições, 0 saltos, 0 retrocessos |
| B7 | 20 / 19 | passo único |
| H1 | 18 / 18 | passo único |
| I1 | 11 / 11 | passo único |

- **Nenhum congelamento:** nenhum par de quadros idêntico depois da correção.
- **Duração inalterada:** 4.537 quadros e 151,233 s. O deslocamento máximo é de 16,7 ms, meio quadro, e o primeiro quadro do vídeo não muda.
- **Sinais do detector, todos investigados:** são legendas aparecendo (A1, B7 e I1, iguais na versão aprovada) e a cozinha vazia e parada antes de o personagem entrar (I1). O render bruto também está parado ali, e os hashes são diferentes, então não há congelamento.
  - Evidência: `relatorios/testes_r13c/falsos_positivos_legendas.png`.

## 3. Validação técnica do definitivo

Registro em `relatorios/testes_r13c/validacao_final_r13.json`.

| Medida | Resultado |
|---|---|
| Fluxo | 1080 × 1920, 30 qps, **4.537 quadros**, 151,233 s, H.264 + AAC 48 kHz, título sem marca de revisão |
| Integridade | 4.537 quadros decodificados, 0 pretos; master com 4.537 quadros |
| R13 × R12, nos quadros esperados (282: E3 + empates) | Mudaram, como previsto |
| R13 × R12, nos outros 4.255 quadros | Diferença média de 0,07, p99 de 0,51, máximo de 0,57: só ruído do codificador. Nenhum acima de 1,5 |
| Continuidade temporal | **Nenhum salto novo.** O salto do A1 (q13) sumiu; os outros 6 já existiam no R12 |
| Quadros quase idênticos em sequência | 168 → 111, ou seja, −57, exatamente os que a correção removeu |
| Master × definitivo | Diferença só na faixa da legenda (linhas 309–371 de 480); fora dela, média de 0,30 |

**Entrada e saída do E3:** a curva da fusão é a mesma do R12.

| Trecho | R12 | R13 |
|---|---|---|
| Entrada da fusão, 78,07–78,23 s | 2,99 / 10,77 / 14,87 / 16,15 / 15,16 / 7,38 | 2,99 / 10,77 / 14,89 / 16,13 / 14,82 / 7,14 |
| Logo depois de entrar no E3 | 2,53 / 2,36 / 1,79 | 1,54 / 1,19 / 1,23 (sem a cintilação) |
| Saída para o E4, 82,90–83,03 s | 10,9–15,2 | 10,8–15,1 |
| Depois da saída | 0,3–0,4 | 0,3–0,4 |

**E3 corrigido:**
- 160 quadros, com manifesto e SHA-256 em `relatorios/testes_r13c/e3/manifesto_quadros_E3_r13c2.json`;
- cada quadro conferido contra o definitivo: semelhança mínima de 0,976 e diferença média máxima de 1,88;
- cintilação na bobina: de 11,07 para 1,32;
- cintilação na placa de válvulas: de 16,0 para 3,2. O que sobra é a palheta abrindo de verdade.

## 4. Áudio, medido no AAC do definitivo

| Medida | Resultado | Meta |
|---|---|---|
| Loudness | **−14,16 LUFS** | −14 |
| Pico verdadeiro | **−1,87 dBTP** | ≤ −1,5 |
| Voz − resto no celular (p5 / mediana) | **11,1 / 23,5 dB** | p5 ≥ 10 |
| Perda em mono | 0,00 dB | ~0 |
| Último 0,5 s | −71 dBFS | silêncio |

- O áudio do definitivo e o do master são **idênticos** ao arquivo de escuta que você aprovou: o MD5 do fluxo AAC é o mesmo, `fce2ed83…`.
- Os 22 eventos que ficaram passam no critério (registro em `relatorios/testes_r13c/verificacao_r13c_final.json`).

## 5. O que não mudou (preservado, com hash conferido)

Registro em `relatorios/testes_r13c/preservacao_r13_definitivo.json`.

- **R12:**
  - definitivo `53cb24f5…` e master `92a17870…`, em partes conferidas;
  - quadros do E3 da R12 (`quadros_final/E3`, 160 de 160 pelo manifesto);
  - cena `cenas/E3` (`f28eb3ab…`);
  - FLAC da R12 (`5c3b593e…`).
- **R13B:** mixagem, FLAC, stems de música e Mixkit e stem CC0, todos com SHA-256 conferido.
- **Narração:** a mesma, porque a mixagem usa o mesmo master da R13B (diferença ≤ −150 dBFS).
- **Geometria, câmera, legendas e modelo científico:** só mudaram as duas malhas do E3 (bobina e bloco), e só por dentro das junções.
- **Episódio 01:** intocado.

## 6. Reconstrução

| O quê | Como |
|---|---|
| Cena do E3 | `python3 episodio/bobina_r13c.py E3 _r13c_faces faces && python3 episodio/bloco_r13c.py E3_r13c_faces E3_r13c_v2` |
| Quadros do E3 | `CENA_R13C=E3_r13c_v2 PASTA_R13C=quadros_final_r13c2 python3 episodio/render_r13c_e3.py` |
| Montagem | `bash episodio/montar_r13.sh` (com `SEM_LEGENDAS=1` para o master) |
| Áudio | `som/preservado_r13c/audio_ep02_r13C_final.flac`, ou `som/som_r13.py` com as opções registradas em `som/preservado_r13c/preservado_r13c.json` |

**Aviso:** os quadros renderizados ficam fora do git, e este contêiner é temporário. O que garante a reconstrução são os scripts, as cenas regeneráveis, os manifestos com SHA-256 e os MP4 em partes.

## 7. Licenças

- **Narração:** plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória. Para monetizar, a voz precisa de outra licença antes da publicação.
- **Música:** "Spice Intrigue", de RomanSenykMusic, sob a Pixabay Content License. Continua pendente a sua conferência da página da faixa (Content ID).
- **Efeitos:** Freesound CC0 e Mixkit Sound Effects Free License; os arquivos isolados ficam fora do git. Detalhes em `relatorios/licencas_r13.md`.

**Nada foi publicado.**

---

# R13.1: avisos retirados (pedido depois da R13)

**Pedido:** tirar os avisos "Visão térmica", "Corte ilustrativo", "Tempo acelerado", "Fluxo desacelerado" e "Câmera lenta".

**Arquivos:**
- `episodio/ep02_definitivo_r13_1_1080x1920.mp4` (SHA-256 `1c7cdd5b…`);
- `episodio/ep02_master_imagem_sem_legendas_r13_1_1080.mp4` (`67eb850e…`);
- as partes estão em `episodio/definitivo_r13_1/`;
- antes × depois em `episodio/previas_r13c/12_avisos_antes_depois.png`.

**Como foi feito:** com a opção `AVISOS_OCULTOS` da montagem (`montar_r13_1.sh`), que só deixa de **desenhar** esses avisos.
- As posições de rótulos e cartões de pressão continuam calculadas como antes, então nada mais se mexe.
- Ficam "Canal ampliado (esquema)" (D4, F2) e o aviso da lupa (G3). Quando estava abaixo de um aviso retirado, o "Canal ampliado" sobe para o primeiro lugar.
- Sem render 3D.

**Prova, R13.1 × R13 quadro a quadro** (`relatorios/testes_r13c/validacao_r13_1.json` e `…_master.json`):

| Medida | Definitivo | Master |
|---|---|---|
| Quadros | 4.537 = 4.537 | 4.537 = 4.537 |
| Quadros que mudaram | **3.570**, exatamente os que tinham um aviso retirado | 3.570, idem |
| Quadros que mudaram sem aviso retirado | **0** | 0 |
| Região alterada | só o canto superior direito, onde ficam os avisos | idem |
| Fora dessa região | nenhum pixel acima de 25; p99,99 = 5 (ruído do codificador) | — |
| Áudio | **idêntico** (MD5 do AAC `fce2ed83…`) | idêntico |

As medidas de áudio da R13 valem sem mudança: −14,16 LUFS, −1,87 dBTP e voz − resto p5 de 11,1 dB.

**Observação:** o manual do projeto pedia avisos honestos quando a cena dramatiza. A retirada foi decisão sua e está registrada. A R13, com avisos, continua preservada em `episodio/definitivo_r13/`, caso queira voltar a ela.

**Nada foi publicado.**
