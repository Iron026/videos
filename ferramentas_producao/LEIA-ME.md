# Ferramentas de verificação preventiva (todos os episódios)

São versões genéricas das verificações que, no Ep. 02, só apareceram depois de muitas rodadas. Rode-as desde a primeira versão de cada episódio. Mais contexto em `../MANUAL_DE_PRODUCAO.md`.

| Ferramenta | Quando | Validada no Ep. 02 |
|---|---|---|
| `varrer_faces_coplanares.py <pasta_cena> [prefixos]` | Antes de renderizar qualquer cena com corte ilustrativo | No E3 original, acha os pares bobina × estator e bloco × placa, os dois que causaram listras. No E3 corrigido, restam só pares escondidos da câmera |
| `verificar_g0_meio_quadro.py <pasta_cenas>` | Antes da 1ª montagem | Acha A1, B7, H1 e I1, os 4 planos com quadros repetidos |
| `detectar_quadros_repetidos.py <video.mp4>` | Em toda montagem | R12: 7 trechos com padrão alternado (A1 e B7). R13.1: 0 |

**Ferramentas específicas do Ep. 02, também reaproveitáveis,** em `episodio_02_geladeira/episodio/`:

| Ferramenta | O que faz |
|---|---|
| `compor_janela_r13c.py` | Hash dos quadros compostos numa janela |
| `validar_final_r13.py` | Vídeo × versão anterior, com quadros esperados |
| `validar_r13_1.py` | Prova de mudança restrita a uma região |
| `detectar_listras_r13c.py` | Listras de z-fighting |
| `varrer_ordem_transparentes.py` | Trocas de ordem de desenho entre transparentes |
| `medir_estrobo.py` | Estroboscopia de grades |
| `validar_arred_r13c.py` | Quadros repetidos por índice e por imagem |

Em `episodio_02_geladeira/som/`:

| Ferramenta | O que faz |
|---|---|
| `validar_audio.py` | Metas medidas no AAC |
| `verificar_r13c.py` | Eventos, nulo e passos |
