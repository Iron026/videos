# Ep. 01 · Render definitivo 1080 × 1920: relatório de renderização e validação

## Entregas

| # | Entrega | Arquivo |
|---|---|---|
| 1 | **MP4 definitivo** (1080 × 1920, 30 fps, 168,000 s, 5.040 quadros, 141,8 MB) | `episodio/ep01_definitivo_1080x1920.mp4`; no git, em partes: `episodio/definitivo/` (remontagem em `LEIA-ME.md`) |
| 2 | Este relatório | `episodio/relatorio_render_definitivo.md` |
| 3 | Registro de configuração e integridade | `episodio/registro_final_ep01.md` / `.json` · manifesto completo `manifesto_render_final.json` · histórico `progresso_render_final.log` |
| 4 | Problemas encontrados e corrigidos | seção 4 |
| + | Master de imagem sem legendas 1080 (para trocar o áudio) | `episodio/ep01_master_imagem_sem_legendas_1080.mp4` (em partes em `definitivo/`) |
| + | Quadros-chave do arquivo final | `episodio/ep01_definitivo_amostras.jpg` |
| + | Validações em números | `validacao_final_1080.json` · `validacao_cintilacao_final.json` · `validacao_janoff_1080.json` |

**SHA-256:**
- MP4 definitivo: `5640980a5627f9bec4bc8c9125645501aa94b53681e1fad5d628e3394e8e2491`
- Master sem legendas: `a5d0dd2e14bf3918512184201919f4fce3029a398fec7c332eb1fd4c62eae188`

Nada foi publicado. A autorização foi usada só para finalizar o arquivo.

> Não consigo assistir nem escutar como você. A validação é por métricas, por comparação quadro a quadro com a revisão aprovada e por inspeção de quadros e recortes. Recomendo assistir ao arquivo final antes de publicar.

## 1. Configuração definitiva

| Item | Valor |
|---|---|
| Resolução / taxa / duração | 1080 × 1920 · 30 fps reais · 168,000 s · 5.040 quadros (5.148 renderizados, incluindo as fusões entre segmentos) |
| Oclusão ambiente | GTAO, 16 amostras |
| Antisserrilhado | MSAA 4× |
| Bloom | 0,22 |
| Correção de cor | a aprovada (`grade_ep01.py` e o nivelamento por segmento da revisão) |
| Correção de profundidade da água | oclusor a 0,994 (padrão do `render2.js`) |
| Janelas | `janoff=1` (aprovado) |
| Correção local | s08a: `fantoff=1` (seção 4) |
| Consulta | `escala=1&aoamostras=16&msaa=4&bloom=0.22&janoff=1` · configuração `9c03e3e543938e4c` (s08a: `def6e201ffdfcdce`) |
| Selo "VERSÃO DE REVISÃO" | **removido no perfil final**; continua só nas versões internas de revisão |
| Codificação | H.264, CRF 17, yuv420p; AAC 192 kbps, 48 kHz |
| Título (metadados) | "De Olho no Invisível · Ep. 01 · Como um navio de aço consegue flutuar?" |

A configuração antiga (`render_segmentos.sh final`, com AO 8 e sem bloom) **não** foi usada.

## 2. Execução

**Regras do render:**
- `render_final.py`: **um processo por vez**, nada em paralelo, em blocos de 60 quadros.
- **Checkpoint e retomada:** cada quadro fica no manifesto com configuração, hash da cena e do renderizador e SHA-256 do arquivo. Na retomada, um quadro só é reaproveitado se tudo isso bater e o arquivo decodificar inteiro. O resto vai para `quadros_final_descartados/`; nada foi apagado.

**Cada quadro novo foi verificado:**
- decodificação completa;
- 1080 × 1920;
- não preto;
- semelhança com o quadro da revisão aprovada no mesmo índice, em escala grosseira: SSIM ≥ 0,93 e diferença média ≤ 6.
- Se falhar, o quadro é renderizado de novo, isoladamente. Persistindo a falha, o render **para** para investigação.

**Números do render:**
- Tempo: cerca de 12 h de calendário, incluindo as paradas e a investigação.
- Velocidade: 4,5–12 s por quadro, conforme o segmento.
- Resultado: **5.148/5.148 quadros**, nenhum corrompido, nenhum re-render por defeito no resultado final.
- Semelhança grosseira mínima por segmento com a revisão aprovada: 0,947 a 0,998 (tabela em `registro_final_ep01.md`).

**Paradas:**

| Quando | O que aconteceu | Causa | Ação |
|---|---|---|---|
| s02 q129 (8,7 s) | parada automática | **falso positivo**: textura fina dos contêineres (serrilhada em 540, resolvida em 1080) | critério passou a comparar em escala grosseira (calibrado: quadro deslocado 10 posições = 0,902; plano errado = 0,53) |
| s08a (≈77,6 s) | **interrompido manualmente** | **defeito real, já existente na revisão aprovada** (seção 4) | correção local, s08a renderizado de novo |
| s12 q0 (137,0 s) | parada automática | **falso positivo**: moiré dos contêineres na revisão 540 (SSIM grosso 0,947, diferença 2,0) | limite 0,95 → 0,93 |

**Migração verificada:**
- O código do renderizador mudou (parâmetro novo, desligado por padrão), então os segmentos já prontos só foram reaproveitados com prova.
- Para cada segmento, renderizei de novo 3 quadros de amostra: todos ficaram dentro da variação normal entre duas renderizações idênticas.
- No s03, a variação natural entre duas renderizações do mesmo código já é 0,57, igual à diferença medida.
- A evidência está no manifesto (chave `migracoes`).

## 3. Validação do arquivo definitivo

Comparação contra `ep01_revisao_s08b_corrigido.mp4`, a referência aprovada.

| Verificação | Resultado |
|---|---|
| Formato | H.264 1080 × 1920 yuv420p 30/1 · AAC 48 kHz estéreo |
| Duração | vídeo 168,000 s · áudio 168,000 s · **5.040 quadros** |
| Quadros pretos / congelamentos / erros de decodificação | **0 / 0 / 0** |
| Selo de revisão | **ausente em 100 % dos quadros** (região do selo difere do aprovado em todos os 5.040) |
| Rótulos científicos, avisos, legendas | presentes, nas mesmas posições e tempos (ver `ep01_definitivo_amostras.jpg`) |
| Encerramento | natural, sem mascote, vinheta ou assinatura |
| Semelhança com o aprovado | SSIM médio 0,968 (reduzido a 540 × 960, sem a região do selo). Os menores valores (0,865, em 7,7–9,0 s) são o plano próximo dos contêineres: mesmo conteúdo, só sem o moiré do 540 |
| Continuidade temporal | correlação 0,9989 entre a variação quadro a quadro do final e a do aprovado. Cortes e fusões nos mesmos instantes. Os 29 "saltos" que só o final acusou têm a mesma intensidade nas duas versões (razão 0,99–1,04): só efeito de limiar |
| Cintilação e defeitos de profundidade | detector absoluto (pixels que vão e voltam entre quadros) nos 15 segmentos: final igual ou melhor que o aprovado. s12 80 → 32 quadros (janelas), s08a 99 → 84 (cubo), s13 166 → 155. Os casos restantes são reflexos do sol na água, faíscas, cortes de cena e linhas finas; nenhum conflito de profundidade (`validacao_cintilacao_final.json`) |
| Experimento (s08b) | sem vazamento do mar, sem piscadas novas |
| Avaria (s12) | sem os pontos do mar sobre o porão; jato, espuma e linha d'água iguais ao aprovado |
| Janelas da superestrutura (146,5–148,3 s) | cintilação 18,75 (aprovado) → **5,03**; vidro escuro sólido |
| Áudio | **idêntico, amostra por amostra, ao da revisão aprovada** (resíduo −240 dB; deslocamento 0 ms) |
| Sincronia da narração | +3 ms, constante nas 21 janelas |
| Sincronia de efeitos e buzinas | inalterada (mesmo áudio, mesmo deslocamento 0) |
| Loudness / pico verdadeiro (AAC final) | **−14,1 LUFS / −2,0 dBTP**; 0 amostras saturadas |

**Uma métrica que não serve aqui:** a "cintilação local relativa", que compara blocos de 20 px entre o final e o aprovado, acusou 2.106 ocorrências. Ela é dominada pela diferença de resolução: água, raios de luz e texturas ficam mais detalhados em 1080 e variam mais entre quadros. Por isso o critério de defeito foi o detector absoluto acima. Ele foi calibrado num defeito real: 11 de 23 quadros piscando antes da correção, 0 depois.

## 4. Problemas encontrados e corrigidos

1. **Janelas da superestrutura** (aprovado): `janoff=1`.
   - Conflito de profundidade entre a faixa de janelas e a parede.
   - Na área das janelas, a cintilação caiu 77 % e os pontos isolados de 8.263 para 2.103. Fora delas, nada mudou.
2. **Cubo ciano da água deslocada × bloco de aço** (s08a, ≈77,6–83,8 s): **defeito encontrado durante o render**.
   - O cubo tem exatamente o tamanho do bloco: as faces coincidem.
   - A fronteira azul/cinza saltava de lugar a cada quadro. O mesmo defeito estava na revisão aprovada.
   - Correção: `fantoff=1`, uma pequena prioridade de profundidade aplicada **só no s08a**. Nos outros segmentos com volumes semelhantes, o teste não mostrou mudança visível.
   - Resultado: cubo uniforme e estável, como pretendido. Detector de cintilação: até 101 blocos piscando antes, 0 depois.
3. **Vazamento do mar** (avaria e experimento): a correção da rodada anterior foi confirmada em 1080.
4. **Dois falsos positivos do verificador** (contêineres): critério recalibrado, sem efeito sobre a imagem.
5. **Nivelamento de cor do s0607b:** no perfil final, a média de cor vem dos quadros 1080. Foi conferido: o fator de brilho é 0,9947 contra 0,9934 da revisão (0,13 %), uma diferença desprezível.

## 5. Áudio definitivo

- Exatamente a mixagem aprovada: `audio_ep01_refinado_buzina.wav`, SHA-256 `5bb652cb…`.
- Inclui:
  - narração original *Will - Deep*;
  - mixagem refinada, com menos água;
  - efeitos interativos;
  - buzina inicial com o aumento aprovado;
  - transição do estaleiro em 0:30;
  - cinco brilhos nas linhas luminosas;
  - buzina final logo após "navio.";
  - música, legendas e sincronização.
- Nenhuma voz gerada; o sound design não foi alterado.

**Trocar o áudio depois:**
- **Pelo master:** `python3 episodio/trocar_audio.py <mixagem.wav> <saida.mp4> episodio/ep01_master_imagem_sem_legendas_1080.mp4`. O master é detectado como 1080 e são aplicadas as legendas do perfil final, CRF 17 e o controle de loudness e pico.
- **Sem perda de geração, enquanto os quadros `quadros_final/` existirem:** `AUDIO_EP01=<mixagem.wav> python3 episodio/montar_ep01.py final <saida.mp4>`.

> ⚠️ A narração continua do plano gratuito da ElevenLabs: o episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).

## 6. Guarda dos arquivos

- **No git:** o GitHub limita arquivos a 100 MB. O MP4 definitivo e o master estão em `episodio/definitivo/`, em partes de 95 MB, com SHA-256 de cada parte e do arquivo remontado (já conferidos).
- **Fora do git (só neste contêiner temporário):** os 5.148 quadros 1080 (`quadros_final/`, 1,2 GB). Eles só são necessários para remontar sem perda de geração.

Não foi feita nenhuma publicação, nenhuma nova narração e nenhuma mudança de física, roteiro ou animação.
