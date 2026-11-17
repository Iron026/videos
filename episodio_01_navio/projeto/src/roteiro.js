// Linha do tempo do Episódio 01 (segundos). Tempos de fala vêm de narracao/frases.json;
// os eventos visuais abaixo foram ancorados a eles.
export const DURACAO = 75.0;
export const FPS = 30;

export const T = {
  quedaBloco: 3.25, fatiaInicio: 4.25, fatiaFim: 5.4,
  cena2: 8.0, corteNavio0: 8.25, corteNavio1: 10.2,
  cena3: 13.0, transicao3b: 19.75, cena3b: 20.0,
  transicao4: 27.75, entradaInicio: 27.95, entradaDescida: 28.45,
  cena5: 36.0, cena6: 47.0, transicao7: 55.75, cena7: 56.0,
  transicao8: 62.75, cena8: 62.75, cartaoFinal: 70.3,
};

// Contêineres: camadas 0–1 já a bordo; camadas 2–4 embarcadas na Cena 06.
export const CARGA = {
  baias: [-52, -39, -26, -13, 0, 13, 26, 39, 52],
  fileiras: 12,
  camadasIniciais: 2,
  camadasExtras: [ { camada: 2, t: 47.7 }, { camada: 3, t: 49.6 }, { camada: 4, t: 51.5 } ],
  duracaoCamada: 1.5, // espalhamento dos pousos dentro de uma camada
  extra: 9 * 12 * 3,
};

// Anteparas transversais e porões (x local, metros).
export const ANTEPARAS = [-58.5, -32.5, -6.5, 19.5, 45.5, 71.5, 86];
export const ALAGAMENTO = {
  inicio: 56.2,
  poroes: [
    { x0: -6.5, x1: 19.5, t0: 56.6, t1: 58.6 },   // pequena entrada de água: ainda flutua
    { x0: -32.5, x1: -6.5, t0: 59.0, t1: 61.3 },  // água em excesso
    { x0: 19.5, x1: 45.5, t0: 59.2, t1: 61.5 },
    { x0: -58.5, x1: -32.5, t0: 59.6, t1: 62.0 },
    { x0: 45.5, x1: 71.5, t0: 59.8, t1: 62.2 },
  ],
};

// Bloco de aço da Cena 01 (aresta em metros, posição x/z no mundo).
export const BLOCO = { aresta: 2.6, x: 136, z: -3.5 };
