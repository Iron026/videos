# Relatório de produção — Episódio 01 · “Como um navio de milhares de toneladas consegue flutuar?”

Canal **De Olho no Invisível** · @deolhonoinvisivel · “O invisível ganha forma.”

## Entregáveis
| Arquivo | Conteúdo |
|---|---|
| `entrega/episodio_01_navio_final.mp4` | Vídeo final (narração, legendas queimadas, efeitos e trilha) |
| `entrega/episodio_01_legendas.srt` | Legendas (34 blocos, texto idêntico ao roteiro, tempos palavra a palavra) |
| `entrega/validacao.json` | Resultado completo da validação automática |
| Projeto-fonte | Toda a pasta `episodio_01_navio/` (ver `README.md` para reprodução e reaproveitamento) |

## Especificações técnicas (medidas no arquivo final com ffprobe)
| Item | Valor |
|---|---|
| Duração | **75,00 s** (vídeo e áudio) |
| Resolução | **1080 × 1920** (9:16 vertical) |
| Taxa de quadros | **30 fps** constantes, 2250 quadros |
| Formato | MP4 (faststart) · H.264 High, yuv420p, CRF 15 (≈ 8,2 Mb/s) · AAC 192 kb/s, 48 kHz, estéreo |
| Tamanho | 77,0 MB |
| Áudio | −14,1 LUFS integrado · pico real −1,4 dBTP · LRA 2,3 LU |
| Metadados | título do episódio e nome do canal |

## Testes realizados
| Teste | Resultado |
|---|---|
| Prévia de baixa resolução antes do render final (folhas de contato de toda a sequência) | ✅ aprovada, sem deformações ou objetos inconsistentes |
| Quadros pretos (`blackdetect`) | ✅ nenhum |
| Congelamentos > 1,5 s (`freezedetect`) | ✅ nenhum |
| Loudness (`ebur128`) | ✅ −14,1 LUFS / −1,4 dBTP (padrão de plataformas de vídeo curto) |
| Legendas SRT: ordem, sobreposição e limites | ✅ 34 blocos, sem problemas, de 0,25 s a 74,47 s |
| Texto das legendas idêntico ao roteiro aprovado | ✅ sim |
| Transcrição automática (Whisper) do áudio **final mixado** comparada ao roteiro | ✅ WER 5,0 %, só variações de grafia do ASR (“por que”/“porque”, “contêineres”/“containers”, “afunda”/“a funda”) e três artigos “a” inseridos; nenhuma palavra do roteiro faltando |
| Sincronia narração × legendas queimadas × eventos | ✅ todos derivados da mesma linha do tempo (`palavras.json` / `frases.json`), conferido visualmente |
| Física | ✅ setas iguais em repouso; calado de 8,0 m → maior com a carga e abaixo da linha de carga máxima; 1 porão alagado → ainda flutua; alagamento excessivo → afunda |
| Área segura do Shorts | ✅ textos entre y≈140 e y≈1340 px, fora da faixa inferior de botões e descrição |

## Storyboard × resultado
| Tempo | Cena pedida | O que o vídeo mostra |
|---|---|---|
| 0–8 s | Gancho: navio flutua × aço afunda | Navio porta-contêineres em mar aberto; um bloco de aço cai na água e afunda; o oceano é “fatiado” para mostrar o casco submerso e o bloco no fundo |
| 8–13 s | Segredo no formato do casco | A câmera atravessa o casco em corte: porões, anteparas e duplo fundo — “Formato do casco” |
| 13–28 s | Maciço × oco | Bloco de 1 m³ de aço ao lado de 1 m³ de água + painel de densidade (aço ≈ 7,85 t, água do mar ≈ 1,03 t). Depois, seção a meia-nau: casco de aço envolvendo “muito espaço sem água” |
| 28–36 s | Entrada no mar e volume deslocado | O navio desce até o calado de equilíbrio; o volume deslocado (fantasma ciano) tem exatamente a forma da parte submersa do casco, delimitado pela linha-d’água amarela |
| 36–47 s | Empuxo = peso da água deslocada | Setas de empuxo e de peso; no repouso as duas têm o mesmo comprimento — “Empuxo = Peso · O navio flutua” |
| 47–56 s | Mais contêineres | 324 contêineres extras (30 t cada) chegam em 3 camadas; o calado aumenta a cada camada e se estabiliza abaixo da “Linha de carga máxima” |
| 56–63 s | Água em excesso | Corte longitudinal: um porão alaga e o navio ainda flutua (mais fundo); com vários porões alagados não há mais equilíbrio, o peso supera o empuxo e o navio afunda |
| 63–71 s | Conclusão | Navio carregado em equilíbrio; “É o volume de água que o casco desloca” |
| 71–75 s | Assinatura | Olho estilizado nas cores da marca, título do canal, slogan e @deolhonoinvisivel |

### Coerência científica (regras do briefing)
- Nunca se afirma que “o ar empurra”: o texto e os rótulos tratam o espaço sem água como volume que desloca água.
- O empuxo é sempre derivado do volume submerso real do casco: uma única função de forma alimenta malha, hidrostática e volume fantasma.
- Em repouso, as setas de peso e empuxo são iguais; só ficam desiguais durante o movimento (oscilação amortecida) e no naufrágio.
- Mais carga → mais calado (simulação física; o navio só para quando desloca a água necessária).
- Um pequeno alagamento não afunda o navio; só o alagamento excessivo elimina o equilíbrio.

## Ferramentas (todas gratuitas e locais, sem créditos e sem marcas-d’água)
Three.js r170 (MIT) renderizado em Chromium headless · FFmpeg / libx264 · Kokoro-82M (Apache-2.0, voz `pm_alex`, pt-BR) para a narração ·
faster-whisper small (MIT), usado só para alinhar legendas e validar · Montserrat (SIL OFL) · Python/NumPy/SciPy para efeitos sonoros e trilha.
**Música e efeitos sonoros:** síntese original deste projeto, sem material de terceiros e sem restrição de licença.

## Impedimentos e decisões
1. **Mascote:** o repositório não tinha os arquivos de referência aprovados do personagem. Seguindo a instrução “Não invente uma nova versão do personagem”, ele **não foi usado**. Enviando as referências, ele pode entrar numa nova versão (por exemplo, na assinatura).
2. **Logotipo oficial:** também não foi encontrado. A assinatura usa um olho estilizado genérico nas cores da marca; basta substituir em `sobreposicao.js → assinatura()`.
3. **Sem GPU e sem Blender no ambiente:** a cena 3D foi feita em Three.js (WebGL por software, SwiftShader). Cada quadro 1080×1920 levou ≈ 2,8 s; a renderização foi dividida em segmentos de 2 s retomáveis, após um reinício do contêiner interromper a primeira tentativa.
4. **HuggingFace bloqueado na rede:** os pesos do Kokoro e do Whisper foram obtidos por pacotes npm públicos que os redistribuem (detalhes no `README.md`).
5. **Pronúncia:** o fonemizador gerava “lh” como [lj] em “Olho”, e o reconhecimento automático entendia “De óleo”. Foi aplicada uma correção de fonema ([ʎ], o som correto) só nessa palavra. A transcrição automática do arquivo final passou a reconhecer “De olho no invisível”.
6. **Duração:** a narração coube nos 75 s sem cortes de conteúdo; só os alvos de início de cada frase foram ajustados ao storyboard.

## Como refazer
```bash
./montar.sh --previa   # prévia em baixa resolução
./montar.sh            # final 1080×1920 (retoma segmentos já prontos)
python3 ferramentas/validar.py entrega/episodio_01_navio_final.mp4 entrega/episodio_01_legendas.srt $WHISPER_MODELO
```
Nada foi publicado no YouTube ou em qualquer outra plataforma.
