# Ep. 02 · Relatório de encerramento

**"Como a geladeira esfria sem produzir frio?"**
- **Situação:** CONCLUÍDO E APROVADO.
- **Versão:** 1.0.0 (= R13.1), aprovada integralmente pelo usuário em **26/11/2026**.
- **Publicação:** nada foi publicado e nenhum serviço foi contratado. O Episódio 01 não foi modificado. O Episódio 03 não foi iniciado e aguarda autorização.

## 1. Arquivos definitivos

| Arquivo | SHA-256 |
|---|---|
| `episodio/ep02_definitivo_r13_1_1080x1920.mp4` (1080 × 1920, 30 qps, 4.537 quadros, 151,233 s, H.264 + AAC 48 kHz) | `1c7cdd5bd4300b4c035c3328f996c7aff1be8c0572c985552c556ee95349b7f5` |
| `episodio/ep02_master_imagem_sem_legendas_r13_1_1080.mp4` | `67eb850e73801555862146dfa86d08a4f4584804ea826ec5a77204fb63850cd3` |
| Fluxo AAC dos dois (MD5) | `fce2ed831aae9347b27b887825cd8df8` |
| `som/preservado_r13c/audio_ep02_r13C_final.flac` (mixagem final, FLAC 24 bits) | ver `VERSAO_1.0.0/manifesto_v1.0.0.json` |

**No git:** os dois MP4 estão em partes de 95 MB, com SHA-256 e LEIA-ME, em `episodio/definitivo_r13_1/`.

**Medidas finais:**

| Medida | Resultado |
|---|---|
| Loudness | −14,16 LUFS |
| Pico verdadeiro | −1,87 dBTP |
| Voz − resto no celular (p5 / mediana) | 11,1 / 23,5 dB |
| Perda em mono | 0 dB |
| Último 0,5 s | −71 dBFS |
| Quadros pretos | 0 |
| Saltos novos | 0 |
| Padrão de quadros repetidos | 0 |

## 2. Congelamento e recuperação

`VERSAO_1.0.0/` guarda:
- `APROVACAO.md`;
- `manifesto_v1.0.0.json`, com os hashes de entregáveis, partes, áudio, stems, cenas, motor e montagem;
- as **46 cenas** do definitivo (`cenas_definitivo_ep02.tar.xz`, 13 MB), com o mesmo hash dos manifestos de render;
- os manifestos de render;
- `verificar_recuperacao.py`.

**Prova de recuperação:** 55 de 55 itens conferidos, com zero falhas, de duas formas:
- na cópia de trabalho;
- **lendo só o ramo remoto** (`--git-ref origin/ccr-3e676310-v0rijq`).

O remoto estava no mesmo commit do local (`8b29aaa`).

**Etiqueta de versão:** `ep02-v1.0.0` foi criada localmente sobre `8b29aaa`. O envio da etiqueta foi recusado pelo canal de acesso ao GitHub desta sessão, que só aceita envio no ramo de trabalho. A identificação da versão está no ramo, em `VERSAO_1.0.0/`. Para ter a etiqueta no GitHub, basta criá-la a partir do commit `8b29aaa`.

**Versões anteriores, todas preservadas:**

| Versão | Onde |
|---|---|
| R11 | `episodio/definitivo/` |
| R12 | `episodio/definitivo_r12/` (`53cb24f5…` e `92a17870…`, conferidos) |
| R13, com avisos | `episodio/definitivo_r13/` |
| Mixagens | `som/preservado_r12`, `som/preservado_r13` (R13B) e `som/preservado_r13c` |

**Scripts, modelos, cenas e relatórios:** estão no git. As exceções, por tamanho ou licença, ficam listadas no manifesto, com hash e receita de reconstrução:
- quadros renderizados;
- stems isolados de música e Mixkit;
- WAV da mixagem (no git fica o FLAC).

## 3. Aprendizados consolidados

**`APRENDIZADOS_EP02.md`** cobre os 20 temas pedidos. Cada aprendizado traz problema, causa, solução validada, prevenção e testes:
1. Roteiro e ciência
2. Modelagem
3. Z-fighting e faces coplanares
4. Transparentes
5. Antisserrilhado e cintilação
6. Obturador
7. Luz, materiais e AO
8. Continuidade
9. Personagem
10. Transições
11. Legendas, rótulos e avisos
12. Quadros repetidos e sincronia
13. Sound design
14. Ruído e ambiência
15. Música e inteligibilidade
16. Efeitos
17. Regressão
18. Render e checkpoints
19. Preservação
20. Licenças

Além dos temas, o documento traz:
- a separação entre **requisitos técnicos obrigatórios** e **preferências criativas**;
- os erros que cometi e o que fazer diferente;
- no apêndice, todas as lições originais, rodada a rodada.

## 4. Padrões incorporados ao projeto

| Onde | O que entrou |
|---|---|
| **`MANUAL_DE_PRODUCAO.md`** (novo, na raiz) | Parte A: requisitos obrigatórios em checklist (ciência, modelagem, render, montagem, som, regressão, preservação, licenças). Parte B: preferências criativas a confirmar com o usuário. Parte C: checklist por etapa, da pauta à publicação |
| **`CLAUDE.md`** | Estado dos episódios (Ep. 02 aprovado e congelado; Ep. 03 só com autorização); seção "Padrões obrigatórios" com as verificações que rodam desde a 1ª versão; avisos de dramatização decididos com o usuário por episódio. As lições soltas por rodada foram para o apêndice de `APRENDIZADOS_EP02.md`, sem perda |
| **`ferramentas_producao/`** (novo) | Verificações genéricas, validadas no Ep. 02 (tabela abaixo) |

| Ferramenta | Resultado no Ep. 02 |
|---|---|
| `varrer_faces_coplanares.py` | No E3 original, acha os dois pares que causaram listras |
| `verificar_g0_meio_quadro.py` | Acha os 4 planos com quadros repetidos |
| `detectar_quadros_repetidos.py` | R12: 7 trechos com padrão alternado. R13.1: 0 |

Com isso, os três defeitos que mais custaram rodadas no Ep. 02 passam a ser pegos antes do primeiro render ou da primeira montagem:
- faces coplanares;
- arredondamento de empate;
- camadas de som esquecidas.

## 5. Pendências de licenciamento para publicação comercial

1. **Narração:** plano gratuito da ElevenLabs, **sem uso comercial**, com atribuição obrigatória. Antes de monetizar: licença comercial da voz, ou nova gravação licenciada.
2. **Música** ("Spice Intrigue", RomanSenykMusic, Pixabay Content License): falta conferir a página da faixa (licença vigente e Content ID). O acesso automático é recusado; a conferência é sua.
3. **Efeitos** (Freesound CC0, Mixkit SFX): ok para uso comercial, sem atribuição. Os arquivos Mixkit isolados continuam fora do git.

**Nada foi publicado.**
