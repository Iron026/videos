"""Monta o animatic r2 (revisão de direção): mesmos recursos da v1 (montar_animatic.py), nova linha do tempo.
Animação principal 0–13,75 s; assinatura curta 13,75–16,85 s (voz em J-cut a partir de 13,30 s).
Uso: python3 animatic/montar_animatic_r2.py → animatic/animatic_ep01_r2.mp4
"""
import montar_animatic as M

M.DUR = 16.85
M.PLANOS = [('r2_p1', 0.00, 4.80), ('r2_p23', 4.60, 13.85), ('r2_p4', 13.75, 16.85)]
M.FUSOES = [(4.60, 4.80), (13.75, 13.85)]          # 7,00 e 10,25 s são cortes secos dentro de r2_p23
# legendas PROVISÓRIAS (texto do roteiro; ~145 pal/min, ritmo medido da amostra) — não são sincronia definitiva
M.LEGENDAS = [(0.15, 2.20, 'Se eu jogar este bloco'), (2.20, 3.85, 'de aço na água,'), (3.85, 4.70, 'ele afunda.'),
              (4.90, 7.35, 'Mas e se eu usar toneladas'), (7.35, 9.40, 'do mesmo aço para construir'), (9.40, 10.30, 'um navio?'),
              (10.60, 11.50, 'Parece impossível.'), (11.70, 13.15, 'Então vamos montar um.')]
M.T_TAG, M.TAG_TXT = 13.30, 'ANIMATIC r2 · narração definitiva pendente (texto)'
M.SAIDA, M.AUDIO, M.MONTAGEM = 'animatic_ep01_r2.mp4', 'audio_animatic_r2.wav', 'montagem_r2'

if __name__ == '__main__':
    M.montar()
