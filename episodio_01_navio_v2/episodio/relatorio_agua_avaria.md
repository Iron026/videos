# Ep. 01 · Água dentro do navio na avaria (134,6–155 s)

**Comparativo:** `episodio/ep01_comparativo_agua_avaria.mp4` (20,4 s)
- Lado a lado: **ANTES** (revisão aprovada) × **DEPOIS**.
- Mesmos instantes, mesma narração e mesmo som. Muda só a imagem da água.

## O que mudou

| | Antes | Depois |
|---|---|---|
| **Água no porão** | volume azul chapado e liso ("fantasma" translúcido, sem luz) | <ul><li>Água do mar com **profundidade**: mais clara e esverdeada perto da superfície, mais escura no fundo, com leve turbidez.</li><li>**Superfície** com ondulação, reflexo do céu e brilho do sol.</li><li>**Linha do nível** sempre legível, inclusive nos planos gerais.</li></ul> |
| **Jato pelo rombo** | faixa clara reta que atravessava a água | <ul><li>**Fluxo aerado** ao longo da trajetória física: sai do rombo a ~6 m/s e cai sob a gravidade.</li><li>Abre-se e fica mais branco ao cair; as estrias correm no sentido do fluxo.</li><li>Nasce transparente na boca do rombo.</li><li>**Termina na superfície da água**, e fica mais curto à medida que o nível sobe.</li></ul> |
| **Impacto** | nada | **espuma** fragmentada onde o jato bate (densa na base, rala no alto), **bolhas** subindo junto ao jato e espuma espalhada na superfície |
| **Evolução** | constante | <ul><li>A agitação, a espuma e as bolhas seguem a intensidade do jato.</li><li>Fortes no início; perdem força a partir de 143,5 s, quando o rombo fica coberto; somem até 146,2 s.</li><li>Mesmos instantes do som da inundação.</li></ul> |

**Planos gerais:** a primeira versão deixava a água escura demais, quase da cor do mar, e o compartimento alagado se destacava menos. Ela foi clareada, e a linha do nível reforçada, para a leitura da explicação continuar clara.

**Correções técnicas no caminho:**
- A água fica em duas caixas, abaixo e acima do tanque lateral. Quando a de baixo enche, o topo dela não é mais desenhado, para não haver faces sobrepostas dentro da água.
- A face junto ao costado coincidia com o chapeamento curvo e cintilava; ela não é desenhada.

## O que não mudou

- **Física:** nível da água, trim de 0,71°, calado e tempos são exatamente os mesmos. O nível é calculado no motor pela mesma fórmula da cena.
- **Enquadramentos, rótulos, legendas e narração:** os mesmos.
- **Hipótese "sem divisórias":** os compartimentos vermelhos continuam como antes, porque são um recurso gráfico.
- **Resto do episódio:** idêntico. O master sem legendas é igual quadro a quadro de 0 a 133,9 s e quase idêntico depois de 155 s (PSNR 56 dB, só a fusão de 0,2 s com o plano anterior).

## Execução

- Re-renderizados os **529 quadros** do segmento da avaria (s12), em 540 × 960, a 30 fps reais.
- Quadros anteriores guardados em `quadros_revisao_antes5/s12`.
- Master de imagem sem legendas atualizado (`ep01_master_imagem_sem_legendas.mp4`): a troca de áudio futura (`trocar_audio.py`) já usa a água nova.
- Nenhum render de 1080 × 1920. Nada publicado.

**Código:**
- `motores/tempo_real_v2/render2.js`: materiais `alagado` e `jato`.
- `blender/lib.py`: `mat_alagado`, `mat_jato`.
- `blender/ep01_cenas.py`, `seg12`: tubo do jato na trajetória balística e âncora do respingo.
