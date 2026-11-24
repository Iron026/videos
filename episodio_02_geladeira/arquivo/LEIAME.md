# Arquivo de versões do Ep. 02

- `cenas_v8.tgz`: TODAS as cenas exportadas usadas na V8 (`episodio/cenas/`, 46 pastas: cena.json, malhas .bin,
  rotulos2d.json, manometros2d.json), guardadas antes de qualquer mudança da rodada 9. Com elas e o motor do commit
  1fc440f, a V8 é re-renderizável e remontável.
  Restaurar: `cd episodio_02_geladeira/episodio && tar xzf ../arquivo/cenas_v8.tgz` (confira `sha256sum -c cenas_v8.tgz.sha256`).
- A V8 montada: `episodio/ep02_v8_revisao.mp4`; mixagem: `som/audio_ep02_v8.flac`; V6 aprovada: `episodio/ep02_animatic.mp4` + `som/audio_ep02_v6.flac`.

## Rodada 11 — B5 antes da garrafa

`cenas_r11_B5.tgz` (fora do git, como os demais .tgz; SHA-256 em `cenas_r11_B5.tgz.sha256`) guarda a cena do B5 aprovada
na V10 (`B5_v10_aprovada`) e as variantes de prévia da garrafa. A cena aprovada da V10 também se regenera idêntica (provado
149/149 quadros) com `CENA_R9=1 python3 blender/episodio02.py B5` (sem `GARRAFA_B5`). A cena atual (`cenas/B5`) é a da
garrafa entrando sozinha, aprovada pelo usuário em 24/11: `CENA_R9=1 GARRAFA_B5=1 python3 blender/episodio02.py B5`.
