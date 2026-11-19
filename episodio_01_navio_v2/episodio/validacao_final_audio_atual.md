# Ep. 01 · Validação final com o áudio atual

> ⚠️ **Licença:** a narração foi gerada no **plano gratuito** da ElevenLabs.
> - Uso **não comercial**.
> - Atribuição **"elevenlabs.io" ou "11.ai" no título** obrigatória ao publicar.
> - **Este episódio NÃO está licenciado para exploração comercial.** Detalhes em `voz/LICENCA_NARRACAO.md`.
>
> Render definitivo de 1080 × 1920: **não iniciado, aguardando autorização.** Nada foi publicado.

**Versão em validação:** `episodio/ep01_revisao_polimento.mp4` (540 × 960, 30 fps). É a montagem de 168 s aprovada.

Nesta etapa **nada foi alterado** em imagem, som, narração, legendas ou sincronia. Todas as medições abaixo foram feitas só lendo os arquivos existentes.

## 1. Arquivos da versão validada (SHA-256)

| Arquivo | SHA-256 | No git? |
|---|---|---|
| `voz/narracao_ep01/Narração ep 1.mp3` (original, intacto) | `79e1e8f21f30c4d00a5ec4fd4e6443b734e41ac249cdd5b170a99c7224949ba0` | sim |
| `voz/narracao_ep01/trabalho/narracao_48k.wav` (cópia de trabalho) | `26f5f7f93aabccdb3040c076a1edf9b863e4b0d10b7cecc40f518d5fff23b5e2` | não (regenerável por `voz/preparar_narracao.py`) |
| `episodio/audio_ep01_hibrido.wav` (mixagem) | `d92d12e365ef89078f2dc7889cc9f0e09de94fa2803feae3c3575b6c27571e93` | não (Mixkit; regenerável por `som/som_hibrido.py`) |
| `episodio/stems/ep01_narracao_hibrido.wav` | `9df3bf34f007ab6313d1dc7cc3a0899520f42b1f3b4cf7fc3bf28cf58220fbe3` | não |
| `episodio/stems/ep01_efeitos_hibrido.wav` | `34b40182b42a7883b0f2283813ad966235438226ca10e7b99be8f653e3cdbcca` | não |
| `episodio/stems/ep01_ambiencias_hibrido.wav` | `08e20ede0e109323784dbecd31830f3e53cbe67a78887cdba61acd7457087063` | não |
| `episodio/stems/ep01_musica_hibrido.wav` | `ba15b4143ea3c0bc05ca9be70cb42b700c787a15fea41bddea2b55616ec035df` | não |
| `episodio/ep01_revisao_polimento.mp4` (revisão) | `7c86fb9c93273cbbb50dfddae5e69d3558b5c7b600d323c5a0affee7a99e7b7b` | sim |
| `episodio/ep01_master_imagem_sem_legendas.mp4` (master) | `307c299de9e1de74a519527e869476642ff588f5d31a3648bdbc91c94fe46879` | sim |

Os WAVs e stems não vão para o git porque contêm gravações do Mixkit, que não podem ser redistribuídas isoladas. Os scripts versionados os regeneram de forma determinística: nas rodadas anteriores, o mesmo SHA-256 saiu a cada execução.

## 2. Verificações técnicas

| Verificação | Resultado | Meta |
|---|---|---|
| Duração | **168,000 s** · 5.040 quadros · 30 fps | 168 s ✅ |
| Decodificação completa | 0 erros | ✅ |
| Quadros pretos / trechos parados (≥ 0,6 s) | 0 / 0 | ✅ |
| Loudness integrado (AAC final) | **−14,0 LUFS** | ≈ −14 ✅ |
| Pico verdadeiro (AAC final) | **−2,4 dBTP** | ≤ −1,5 ✅ |
| Faixa dinâmica (LRA) | 2,2 LU | típico de narração contínua |
| Mono | sem perda: a soma L+R dá a mesma intensidade (−14,1 LUFS no mesmo método do mix); correlação L/R 0,955 | ✅ |
| Narração no MP4 × narração de trabalho | **+3 ms constante** (medido em 5, 40, 80, 120 e 160 s) | < 1 quadro ✅ |
| Voz no celular (simulação mono 350 Hz–7 kHz) | fala plena ≥ 10 dB acima do fundo em **93,5%** · mediana 20,0 dB | voz clara ✅ |
| Legendas | <ul><li>115 blocos, 0 sobreposições, máx. 26 caracteres.</li><li>Começam em 0,0 s e terminam em 166,37 s, com a última frase científica (sem a fala de assinatura).</li></ul> | ✅ |
| Texto das legendas | as 384 palavras do roteiro oficial | ✅ |
| Sincronia dos impactos (ataque medido × evento da animação) | <ul><li>De −23 a +21 ms, todos abaixo de 1 quadro.</li><li>Borda −8, água −19, leito +21, encaixe −10, comporta −23, retomada −15, experimento +2, pousos 0/0/0, ruptura −3, divisórias +12, conclusão −5.</li></ul> | ✅ |

## 3. Lista de escuta (sua avaliação auditiva)

**Como escutar:**
- Ouça em **fones** e no **alto-falante do celular**.
- Para isolar um grupo, use os stems em `episodio/stems/grupos/`.
- Os itens marcados **(reserva)** usam gravações do Mixkit no lugar das específicas do Commons, que não puderam ser baixadas.

| ✔ | Instante | O que ouvir | Grupo / observação |
|---|---|---|---|
| ☐ | 0,5–1,4 s | Bloco arrastado no concreto e tombando na borda | abertura |
| ☐ | 2,6–4,0 s | Impacto na água em câmera lenta, bolhas, leito | abertura |
| ☐ | 4,4–15 s | Mar aberto, máquinas distantes, onda de proa, espuma | abertura |
| ☐ | 15–30 s | Motor do pórtico seguindo o movimento, rodas no trilho | **guindastes (reserva: zumbido industrial)** |
| ☐ | 23,6 s | Encaixe da chapa: peso + batida com eco de galpão | estaleiro |
| ☐ | 23,75–25,4 s | Solda: arco e faíscas junto do brilho | estaleiro |
| ☐ | 26–28,7 s | Chapas chegando (5 contatos, não um por chapa) | estaleiro |
| ☐ | 29,75–30,6 s | Passagem de tempo "Meses depois" (sopro suave) | estaleiro |
| ☐ | 33,2 s | Proa se separando no corte do casco | estaleiro |
| ☐ | 41,7–48 s | Comporta, jatos, enchimento, casco saindo dos picadeiros | **dique (reservas no ambiente e na tubulação)** |
| ☐ | 49–75 s | Mergulho, ambiente submerso, formações gráficas do empuxo (síntese discreta) | empuxo |
| ☐ | 74,9–82 s | Retomada: arrasto, queda, câmera lenta, leito | retomada |
| ☐ | 86,2 s | Bloco × casco caindo juntos: compacto × largo, balanço até parar | experimento |
| ☐ | 94,5–117 s | Ambiente de porto, portêineres, empilhadeiras | **porto/guindastes (reservas: obra urbana, caminhão, máquina de obra)** |
| ☐ | 101,6 · 102,95 · 104,45 s | Pousos dos 3 contêineres | porto |
| ☐ | 105–117 s | Tempo acelerado: sem som por contêiner, só ambiente e 3 contatos distantes | porto |
| ☐ | 117–134 s | Água no casco, calado, marcas (um único brilho sutil) | porto |
| ☐ | 134,9 s | Ruptura do costado | inundação |
| ☐ | 136,9–147,8 s | Jato sob pressão, porão enchendo, golpes nas anteparas, rangidos | inundação |
| ☐ | 151,05 s | Divisórias estanques: batida firme, tensão aliviando | inundação |
| ☐ | 155,8 s | Bloco de 17 m entrando na água (escala) | conclusão |
| ☐ | 156,4–164,3 s | Afundamento, ambiente submerso, "peso = empuxo" | conclusão |
| ☐ | 164,4–168 s | Mar no plano final; trilha resolve; fim natural | conclusão |
| ☐ | geral | Voz sempre clara; ambiente presente sob a voz (ducking moderado); nada "eletrônico" | mix |

**Se algo soar errado:**
1. Anote o instante.
2. Consulte o ID da gravação em `som/mapa_substituicao.md`.
3. Para trocar só aquele som: arquivo em `som/bib/manual/` + registro em `som/substituicoes.json`. Mais nada muda.

## 4. Licenças do episódio

| Componente | Licença | Uso comercial |
|---|---|---|
| Imagem (motor e cenas próprios) | código do projeto | sem restrição de terceiros |
| Música (síntese original) | código do projeto | sem restrição de terceiros |
| Efeitos sonoros (48 gravações Mixkit) | Mixkit Sound Effects Free License | permitido; não redistribuir arquivos isolados nem registrar em Content ID |
| **Narração (ElevenLabs, plano gratuito)** | **termos do plano gratuito** | **não permitido; atribuição "elevenlabs.io"/"11.ai" no título ao publicar** |
| **Episódio completo** | — | **não licenciado para exploração comercial** |

Créditos prontos: `som/creditos_descricao.txt`.

## 5. O que falta decidir

1. **Sua escuta** (lista acima).
2. **Autorização** do render definitivo em 1080 × 1920. Nada será renderizado antes dela.
3. A **pendência de licença comercial da narração** continua registrada. Não bloqueia o render técnico, mas limita o uso do episódio.
