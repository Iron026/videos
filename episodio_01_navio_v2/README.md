# Episódio 01 — reformulação (v2)

Pasta nova; a v1 (`../episodio_01_navio/`) foi preservada sem alterações.
Estado (19/11/2026): **Ep. 01 em validação final** — revisão de 168 s aprovada visualmente (`episodio/ep01_revisao_polimento.mp4`),
som híbrido aguardando escuta, render definitivo de 1080 × 1920 **não autorizado** ainda. Validação: `episodio/validacao_final_audio_atual.md`.

> ⚠️ **Licença:** a narração (`voz/narracao_ep01/Narração ep 1.mp3`, ElevenLabs · Will - Deep) foi gerada no **plano gratuito**:
> uso **não comercial** e atribuição obrigatória ("elevenlabs.io" ou "11.ai" no título). **O episódio não está licenciado para
> exploração comercial.** Detalhes: `voz/LICENCA_NARRACAO.md`.

Histórico: a tabela abaixo descreve as Etapas A e B (iniciais).

| Caminho | Conteúdo |
|---|---|
| `etapa_b/relatorio_etapas_A_B.md` | Auditoria da v1, proposta de direção de arte, limitações e próximos passos |
| `etapa_b/quadros/quadro1..5.png` | Quadros de referência 1080×1920 renderizados no Blender 5.1 · Cycles |
| `etapa_b/quadros/quadro6_assinatura.png` | Assinatura com a imagem oficial do mascote |
| `etapa_b/comparacao_v1_v2.jpg` | v1 rejeitada × v2, lado a lado (gerada por `etapa_b/comparar.py`) |
| `etapa_b/v1/` | Quadros equivalentes extraídos do MP4 da v1 |
| `etapa_b/web/` | Página de revisão (HTML) |
| `blender/lib.py` | Cena, materiais (aço, pinturas, concreto, areia, água volumétrica, cáusticas, raios de luz), geometria e utilitários |
| `blender/navio.py` | Casco (mesma forma e hidrostática da v1), bulbo, leme, hélice, superestrutura, convés, carga, estrutura em construção, marcas de calado, Plimsoll |
| `blender/cenario.py` | Cais, cabeços, defensas, chapas, operários, pórtico de estaleiro, portêiner (STS), galpões, peixes |
| `blender/quadros.py` | Os cinco quadros (`python3 quadros.py <n> [pct] [amostras] [saida]`) |
| `blender/render_quadros.sh` | Renderiza os quadros em sequência |
| `assinatura/` | HTML e captura da assinatura (fonte Montserrat da v1) |
| `referencias/` | Imagem oficial do mascote e recorte circular |
| `voz/teste_voz.py` | Teste da voz ElevenLabs Will - Deep (não executado: falta a chave). A chave nunca vai para o repositório |

## Reproduzir
```bash
pip install --target /caminho/bpy bpy==5.1.2          # Blender como módulo Python (Python 3.13)
export BPY_SITE=/caminho/bpy
cd blender && ./render_quadros.sh 160                  # 1080×1920; prévia: python3 quadros.py 1 30 48
python3 ../etapa_b/comparar.py
```
Num computador com GPU, os mesmos scripts rodam com `scene.cycles.device = 'GPU'` (de 10 a 30 vezes mais rápido).
