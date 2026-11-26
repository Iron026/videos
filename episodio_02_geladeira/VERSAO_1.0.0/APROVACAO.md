# Ep. 02 · versão 1.0.0 — APROVADA E CONGELADA

**"Como a geladeira esfria sem produzir frio?"**

| Item | Registro |
|---|---|
| Versão | **1.0.0** (= R13.1) |
| Aprovação | integral, pelo usuário, em **26/11/2026** |
| Situação | **Concluído e aprovado.** Versão final de produção, congelada: sem mais alterações em imagem, animação, narração, música, efeitos ou composição |
| Publicação | **Não publicado.** Há pendências de licenciamento para uso comercial; ver abaixo |

## Entregáveis

| Arquivo | SHA-256 |
|---|---|
| `episodio/ep02_definitivo_r13_1_1080x1920.mp4` (1080 × 1920, 4.537 quadros, 151,233 s) | `1c7cdd5bd4300b4c035c3328f996c7aff1be8c0572c985552c556ee95349b7f5` |
| `episodio/ep02_master_imagem_sem_legendas_r13_1_1080.mp4` | `67eb850e73801555862146dfa86d08a4f4584804ea826ec5a77204fb63850cd3` |

No git, os dois estão em partes de 95 MB em `episodio/definitivo_r13_1/`.

## O que este diretório guarda

| Arquivo | Conteúdo |
|---|---|
| `manifesto_v1.0.0.json` | SHA-256 de entregáveis, partes, áudio, stems, cenas, motor e montagem |
| `cenas_definitivo_ep02.tar.xz` (13 MB) | As 46 cenas exportadas usadas pelo definitivo, cada uma com o MESMO hash dos manifestos de render. A exportação do Blender não é determinística na ordem dos triângulos; por isso as cenas ficam congeladas aqui, em vez de regeneradas |
| `manifestos_render_ep02.tar.xz` | Manifestos de quadro a quadro: configuração, hash da cena e do motor, SHA-256 de cada quadro |
| `verificar_recuperacao.py` | Prova de recuperação. Funciona num checkout limpo e também lendo direto de um ref remoto (`--git-ref`) |

**Fora do git, por limite de tamanho ou de licença** (com hashes registrados):
- os quadros renderizados (`episodio/quadros_*`): regeneráveis a partir das cenas congeladas e do motor registrado, com equivalência provada pela variação natural do render, não por hash;
- os stems isolados de música (Pixabay) e de efeitos Mixkit: a licença proíbe redistribuir o arquivo isolado;
- o WAV da mixagem: no git fica o FLAC equivalente, `som/preservado_r13c/audio_ep02_r13C_final.flac`.

**Versões anteriores, todas preservadas:**
- R11: `episodio/definitivo/`
- R12: `episodio/definitivo_r12/`
- R13: `episodio/definitivo_r13/`
- mixagens: `som/preservado_r12`, `som/preservado_r13` (R13B) e `som/preservado_r13c`

## Pendências de licenciamento (antes de publicação comercial)

1. **Narração:** gerada no plano gratuito da ElevenLabs, que **não permite uso comercial** e exige atribuição. Para monetizar, é preciso licença compatível (plano pago com direito comercial) ou nova gravação licenciada, antes da publicação.
2. **Música:** "Spice Intrigue", de RomanSenykMusic, sob a Pixabay Content License. Falta conferir na página da faixa a licença vigente e se ela está registrada em Content ID. A página recusa acesso automático; a conferência é sua.
3. **Efeitos:** Freesound CC0 e Mixkit Sound Effects Free License. Os dois permitem uso comercial sem atribuição. O Mixkit proíbe redistribuir o arquivo isolado, por isso esses arquivos estão fora do git. Sem pendência.
4. **Fontes tipográficas, personagem e modelos:** próprios do projeto ou Montserrat (SIL Open Font License). Sem pendência.
