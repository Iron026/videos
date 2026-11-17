// De Olho no Invisível — Ep. 01: "Como um navio de milhares de toneladas consegue flutuar?"
// Cena 3D determinística: window.quadro(t) posiciona tudo para o instante t e renderiza.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { solidoCasco, placaHorizontal, antepara, contornoNaAltura, meiaBoca, centroCarena, PONTAL } from './casco.js';
import { U, criarCeu, criarSuperficie, criarFaceCorte, criarLeito, aplicarSubaquatico, alturaOnda, PROFUNDIDADE } from './agua.js';
import { T, CARGA, ANTEPARAS, ALAGAMENTO, BLOCO, DURACAO } from './roteiro.js';
import { simular, HID, M_BASE, CALADO_MAX, PORAO_FOLGA } from './fisica.js';
import { estadoCamera } from './camera.js';
import { Sobreposicao, janela } from './sobreposicao.js';

const params = new URLSearchParams(location.search);
const LARG = +(params.get('w') || 1080), ALT = +(params.get('h') || 1920);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const suave = (a, b, t) => { const x = clamp((t - a) / (b - a), 0, 1); return x * x * (3 - 2 * x); };
const lerp = (a, b, f) => a + (b - a) * f;
function rnd(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ---------- Renderizador ----------
const canvas = document.getElementById('gl');
canvas.width = LARG; canvas.height = ALT;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(LARG, ALT, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const cena = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
cena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
cena.environmentIntensity = 0.55;
const camera = new THREE.PerspectiveCamera(45, LARG / ALT, 1.5, 9000);

// ---------- Luz ----------
cena.add(new THREE.HemisphereLight('#cfe3f2', '#33405f', 1.15));
const sol = new THREE.DirectionalLight('#fff0d8', 2.7);
sol.castShadow = true; sol.shadow.mapSize.set(2048, 2048);
Object.assign(sol.shadow.camera, { left: -150, right: 150, top: 150, bottom: -150, near: 10, far: 700 });
sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.6;
cena.add(sol, sol.target);

// ---------- Ambiente ----------
cena.add(criarCeu());
const superficie = criarSuperficie(); cena.add(superficie);
const faceCorte = criarFaceCorte(); cena.add(faceCorte);
cena.add(criarLeito());

// ---------- Navio ----------
const navio = new THREE.Group(); cena.add(navio);
const AMARELO = '#F3B544', AZUL = '#202B57', BRANCO = '#F6F4EC';
function matPadrao(cor, opts = {}, sub = {}) {
  const m = new THREE.MeshStandardMaterial({ color: cor, roughness: 0.6, metalness: 0.05, ...opts });
  return aplicarSubaquatico(m, sub);
}
function malha(geo, mat, sombra = true) { const m = new THREE.Mesh(geo, mat); m.castShadow = sombra; m.receiveShadow = true; return m; }

// Casco externo com pintura por altura (fundo antiincrustante, faixa branca, costado azul).
const gCasco = solidoCasco({ tampaTopo: false });
{
  const p = gCasco.attributes.position, cores = new Float32Array(p.count * 3), c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i);
    c.set(y < 10.85 ? '#8f3a2f' : y < 11.35 ? '#ece8dc' : AZUL);
    cores.set([c.r, c.g, c.b], i * 3);
  }
  gCasco.setAttribute('color', new THREE.BufferAttribute(cores, 3));
}
const matCasco = matPadrao('#ffffff', { vertexColors: true, roughness: 0.5, metalness: 0.15 }, { tampa: AMARELO });
navio.add(malha(gCasco, matCasco));
const matInterno = matPadrao('#b9c4d2', { roughness: 0.75 }, { tampa: AMARELO });
navio.add(malha(solidoCasco({ folga: 0.7, inverter: true, tampaTopo: false, x1: 86 }), matInterno, false));
const matConves = matPadrao('#5f6e6a', { roughness: 0.8 }, { tampa: AMARELO });
navio.add(malha(placaHorizontal(PONTAL, 0.5, 0), matConves));
navio.add(malha(placaHorizontal(2.4, 0.45, 0.7, -58.5, 86), matPadrao('#8d99a8', { roughness: 0.8 }, { tampa: AMARELO })));
const matAntepara = matPadrao('#a7b3c2', { roughness: 0.75 }, { tampa: AMARELO });
for (const x of ANTEPARAS) navio.add(malha(antepara(x, 0.5, 0.7), matAntepara, false));
// tampas de escotilha
const matEscotilha = matPadrao('#2c3a58', { roughness: 0.7 }, { tampa: '#c79a3a' });
for (const bx of CARGA.baias) {
  const w = 2 * meiaBoca(bx, PONTAL) - 3;
  const m = malha(new THREE.BoxGeometry(12.6, 1.4, Math.min(w, 29.6)), matEscotilha); m.position.set(bx, PONTAL + 1.2, 0); navio.add(m);
}
// marca de linha de carga (disco de Plimsoll) a meia-nau, nos dois bordos
const matMarca = new THREE.MeshStandardMaterial({ color: '#ffffff', emissive: '#ffffff', emissiveIntensity: 0.35 });
aplicarSubaquatico(matMarca);
for (const s of [1, -1]) {
  const z = s * (meiaBoca(0, CALADO_MAX) + 0.08);
  const anel = malha(new THREE.TorusGeometry(1.5, 0.16, 8, 40), matMarca, false); anel.position.set(0, CALADO_MAX, z); navio.add(anel);
  const barra = malha(new THREE.BoxGeometry(4.6, 0.3, 0.1), matMarca, false); barra.position.set(0, CALADO_MAX, z); navio.add(barra);
  const linha = malha(new THREE.BoxGeometry(6, 0.3, 0.1), matMarca, false); linha.position.set(0, PONTAL - 0.4, z); navio.add(linha);
}
// superestrutura (acomodações, passadiço, chaminé)
const matSuper = matPadrao(BRANCO, { roughness: 0.55 }, { tampa: '#bdb8ab' });
const matJanela = matPadrao('#1b2440', { roughness: 0.2, metalness: 0.4 }, { tampa: '#1b2440' });
const sup = new THREE.Group(); navio.add(sup);
const caixa = (w, h, d, x, y, z, mat) => { const m = malha(new RoundedBoxGeometry(w, h, d, 2, 0.35), mat); m.position.set(x, y, z); sup.add(m); return m; };
caixa(12, 15, 26, -79, PONTAL + 7.5, 0, matSuper);
caixa(10, 3.4, 36, -78.5, PONTAL + 16.7, 0, matSuper);
for (let i = 0; i < 5; i++) caixa(0.3, 1.0, 22, -72.9, PONTAL + 2.6 + i * 2.8, 0, matJanela);
caixa(0.3, 1.4, 33, -73.4, PONTAL + 17.0, 0, matJanela);
caixa(7, 13, 8, -90, PONTAL + 6.5, 0, matPadrao(AMARELO, {}, { tampa: '#c79a3a' }));
caixa(7.2, 2.2, 8.2, -90, PONTAL + 12.4, 0, matPadrao(AZUL, {}, { tampa: '#c79a3a' }));
caixa(1.2, 9, 1.2, -78, PONTAL + 22, 0, matPadrao('#d7d3c8', {}, { tampa: '#bdb8ab' }));
caixa(1.0, 10, 1.0, 92, PONTAL + 5, 0, matPadrao(AMARELO, {}, { tampa: '#c79a3a' }));
for (const s of [1, -1]) {
  const bote = malha(new THREE.CapsuleGeometry(1.5, 6, 6, 12), matPadrao('#e8742a', {}, { tampa: '#b85b20' }));
  bote.rotation.z = Math.PI / 2; bote.position.set(-82, PONTAL + 6, s * 14.2); sup.add(bote);
}

// ---------- Contêineres (instanciados) ----------
function texturaConteiner() {
  const c = document.createElement('canvas'); c.width = 256; c.height = 64; const g = c.getContext('2d');
  g.fillStyle = '#fff'; g.fillRect(0, 0, 256, 64);
  for (let x = 0; x < 256; x += 8) { g.fillStyle = 'rgba(0,0,0,0.16)'; g.fillRect(x, 0, 3, 64); g.fillStyle = 'rgba(255,255,255,0.5)'; g.fillRect(x + 4, 0, 1, 64); }
  g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, 0, 256, 4); g.fillRect(0, 60, 256, 4); g.fillRect(0, 0, 4, 64); g.fillRect(252, 0, 4, 64);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
const PALETA = ['#2f6db3', '#F3B544', '#d9d4c6', '#b54a3a', '#2a9d8f', '#5d6d7e', '#e07b39', '#355c7d', '#F6F4EC', '#7a3e65', '#3f8f5a', '#202B57'];
const conteineres = [];
{
  const r = rnd(7);
  for (let camada = 0; camada < 5; camada++) for (let bi = 0; bi < CARGA.baias.length; bi++) for (let f = 0; f < CARGA.fileiras; f++) {
    const extra = CARGA.camadasExtras.find(e => e.camada === camada);
    const c = {
      x: CARGA.baias[bi], y: PONTAL + 1.9 + 1.3 + camada * 2.62, z: (f - (CARGA.fileiras - 1) / 2) * 2.48,
      cor: PALETA[Math.floor(r() * PALETA.length)], camada,
    };
    if (extra) { const ordem = (bi * CARGA.fileiras + f) / (CARGA.baias.length * CARGA.fileiras); c.pouso = extra.t + 0.55 + ordem * CARGA.duracaoCamada + r() * 0.12; }
    conteineres.push(c);
  }
}
const matConteiner = new THREE.MeshStandardMaterial({ map: texturaConteiner(), roughness: 0.62, metalness: 0.2 });
aplicarSubaquatico(matConteiner, { tampa: '#3a3f4a' });
const instConteiner = new THREE.InstancedMesh(new THREE.BoxGeometry(12.19, 2.59, 2.44), matConteiner, conteineres.length);
instConteiner.castShadow = true; instConteiner.receiveShadow = true;
conteineres.forEach((c, i) => instConteiner.setColorAt(i, new THREE.Color(c.cor)));
navio.add(instConteiner);
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3();
function atualizarConteineres(t) {
  conteineres.forEach((c, i) => {
    let y = c.y, esc = 1;
    if (c.pouso !== undefined) {
      const ini = c.pouso - 0.55;
      if (t < ini) esc = 0;
      else if (t < c.pouso) { const f = (t - ini) / 0.55; y = c.y + 22 * (1 - f * f); }
      else { const d = t - c.pouso; y = c.y + 0.35 * Math.exp(-d * 9) * Math.abs(Math.sin(d * 18)); }
    }
    _p.set(c.x, y, c.z); _s.setScalar(esc ? 1 : 0.0001); _m.compose(_p, _q, _s); instConteiner.setMatrixAt(i, _m);
  });
  instConteiner.instanceMatrix.needsUpdate = true;
}

// ---------- Simulação física (calado ao longo do tempo) ----------
const FIS = simular(conteineres);
window.FIS = FIS;

// ---------- Volume deslocado (fantasma) ----------
const matFantasma = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, side: THREE.DoubleSide,
  uniforms: { uA: { value: 0 }, uCor: { value: new THREE.Color('#3cc6ff') }, uTempo: U.uTempo, uBrilho: { value: 0 } },
  vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vL; void main(){ vL=position; vec4 w=modelMatrix*vec4(position,1.0); vN=normalize(mat3(modelMatrix)*normal); vV=normalize(cameraPosition-w.xyz); gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform float uA; uniform vec3 uCor; uniform float uTempo; uniform float uBrilho; varying vec3 vN; varying vec3 vV; varying vec3 vL;
    void main(){ float f=pow(1.0-abs(dot(normalize(vN),vV)),2.0); float faixas=0.5+0.5*sin(vL.y*3.0-uTempo*3.0);
      float a=uA*(0.5+0.4*f+0.06*faixas+0.2*uBrilho); vec3 c=uCor*(0.55+0.3*f+0.35*uBrilho)+vec3(0.03)*faixas;
      gl_FragColor=vec4(c,a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
});
const fantasma = new THREE.Mesh(new THREE.BufferGeometry(), matFantasma); fantasma.renderOrder = 8; navio.add(fantasma);
const matLinhaAgua = new THREE.MeshBasicMaterial({ color: AMARELO, transparent: true, depthTest: false });
const linhaAgua = new THREE.Mesh(new THREE.BufferGeometry(), matLinhaAgua); linhaAgua.renderOrder = 9; navio.add(linhaAgua);
let caladoFantasma = -1;
function atualizarFantasma(calado) {
  if (Math.abs(calado - caladoFantasma) < 0.015) return;
  caladoFantasma = calado;
  fantasma.geometry.dispose(); linhaAgua.geometry.dispose();
  if (calado <= 0.05) { fantasma.geometry = new THREE.BufferGeometry(); linhaAgua.geometry = new THREE.BufferGeometry(); return; }
  fantasma.geometry = solidoCasco({ topo: Math.min(calado, PONTAL), folga: -0.15, nx: 120, ny: 18 });
  const pts = contornoNaAltura(Math.min(calado, PONTAL - 0.01), -0.2, 160);
  linhaAgua.geometry = pts.length > 3 ? new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 300, 0.32, 6, true) : new THREE.BufferGeometry();
}

// Espaço interno (Cena 03b)
const matInternoVol = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, side: THREE.DoubleSide, uniforms: { uA: { value: 0 } },
  vertexShader: `varying vec3 vN; varying vec3 vV; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vN=normalize(mat3(modelMatrix)*normal); vV=normalize(cameraPosition-w.xyz); gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform float uA; varying vec3 vN; varying vec3 vV; void main(){ float f=pow(1.0-abs(dot(normalize(vN),vV)),1.5);
    gl_FragColor=vec4(vec3(1.0,0.93,0.72)*(1.0+f),uA*(0.16+0.5*f));
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`,
});
const volInterno = new THREE.Mesh(solidoCasco({ x0: -6.25, x1: 10.0, topo: PONTAL - 0.1, folga: 0.95, nx: 30, ny: 18 }), matInternoVol);
volInterno.renderOrder = 7; navio.add(volInterno);
{ const gi = volInterno.geometry; const pos = gi.attributes.position; for (let i = 0; i < pos.count; i++) if (pos.getY(i) < 2.85) pos.setY(i, 2.85); gi.computeVertexNormals(); }

// ---------- Setas de força ----------
function geoSeta(raio = 1.4, cabeca = 3.4, compCabeca = 6.5) {
  const haste = new THREE.CylinderGeometry(raio, raio, 1, 20); haste.translate(0, 0.5, 0);
  const ponta = new THREE.ConeGeometry(cabeca, compCabeca, 24); ponta.translate(0, compCabeca / 2, 0);
  return { haste, ponta, compCabeca };
}
class Seta {
  constructor(cor) {
    const g = geoSeta();
    this.grupo = new THREE.Group(); this.grupo.renderOrder = 30;
    const mat = new THREE.MeshBasicMaterial({ color: cor, depthTest: false, transparent: true });
    const borda = new THREE.MeshBasicMaterial({ color: '#0f1633', depthTest: false, transparent: true, side: THREE.BackSide });
    this.haste = new THREE.Mesh(g.haste, mat); this.ponta = new THREE.Mesh(g.ponta, mat);
    this.hasteB = new THREE.Mesh(g.haste, borda); this.pontaB = new THREE.Mesh(g.ponta, borda);
    this.hasteB.scale.set(1.45, 1, 1.45); this.pontaB.scale.set(1.18, 1.1, 1.18);
    for (const m of [this.hasteB, this.pontaB]) { m.renderOrder = 30; this.grupo.add(m); }
    for (const m of [this.haste, this.ponta]) { m.renderOrder = 31; this.grupo.add(m); }
    this.compCabeca = g.compCabeca; this.mats = [mat, borda];
    cena.add(this.grupo);
  }
  // origem (cauda), direção (+1 para cima, -1 para baixo), comprimento total, opacidade
  definir(origem, sentido, comp, a) {
    this.grupo.visible = a > 0.001 && comp > 0.5;
    if (!this.grupo.visible) return;
    this.grupo.position.copy(origem); this.grupo.rotation.set(sentido > 0 ? 0 : Math.PI, 0, 0);
    const h = Math.max(0.01, comp - this.compCabeca);
    this.haste.scale.set(1, h, 1); this.hasteB.scale.set(1.45, h, 1.45);
    this.ponta.position.y = h; this.pontaB.position.y = h - 0.3;
    this.mats.forEach(m => m.opacity = a);
  }
}
const setaEmpuxo = new Seta('#6FD6F7'), setaPeso = new Seta(AMARELO);
const setaEmpuxoBloco = new Seta('#6FD6F7'), setaPesoBloco = new Seta(AMARELO);
for (const s of [setaEmpuxoBloco, setaPesoBloco]) s.grupo.scale.setScalar(0.32);

// Setas de pressão (Cena 04): perpendiculares ao casco, comprimento ∝ profundidade.
const PONTOS_PRESSAO = [];
for (let x = -60; x <= 60; x += 12) {
  for (const y of [1.2, 3.4, 5.6]) PONTOS_PRESSAO.push({ x, y, lado: 1 });
  for (const z of [-9, -3, 3, 9]) PONTOS_PRESSAO.push({ x, y: 0, z, fundo: true });
}
const gPressao = (() => { const g = geoSeta(0.32, 0.9, 1.6); const m = mergeGeometries([g.haste, g.ponta]); return m; })();
const matPressao = new THREE.MeshBasicMaterial({ color: '#8fe3ff', transparent: true, depthTest: true });
const instPressao = new THREE.InstancedMesh(gPressao, matPressao, PONTOS_PRESSAO.length); instPressao.renderOrder = 12; navio.add(instPressao);
function atualizarPressao(calado, a) {
  instPressao.visible = a > 0.001; if (!instPressao.visible) return;
  matPressao.opacity = a;
  PONTOS_PRESSAO.forEach((p, i) => {
    const prof = Math.max(0, calado - p.y), L = 0.62 * prof * a;
    if (p.fundo) { _p.set(p.x, p.y - L - 0.3, p.z); _q.identity(); }
    else { const z = meiaBoca(p.x, p.y) + L + 0.3; _p.set(p.x, p.y, z); _q.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2); }
    // a geometria tem comprimento-base ~1 (haste) + 1.6 (ponta): escala no eixo da seta
    _s.set(1, prof > 0.2 ? Math.max(0.05, (L - 1.6)) : 0.0001, 1);
    _m.compose(_p, _q, _s); instPressao.setMatrixAt(i, _m);
  });
  instPressao.instanceMatrix.needsUpdate = true;
}

// ---------- Água dentro dos porões (Cena 07) ----------
const matAlag = new THREE.MeshStandardMaterial({ color: '#2a8fc0', transparent: true, opacity: 0.82, roughness: 0.15, metalness: 0.0, side: THREE.DoubleSide, depthWrite: false });
aplicarSubaquatico(matAlag, { seco: true });
const alagados = ALAGAMENTO.poroes.map(() => { const m = new THREE.Mesh(new THREE.BufferGeometry(), matAlag); m.renderOrder = 6; m.userData.nivel = -1; navio.add(m); return m; });
function atualizarAlagamento(t) {
  ALAGAMENTO.poroes.forEach((p, k) => {
    const nivel = (t >= ALAGAMENTO.inicio && t < T.cena8) ? FIS.nivel(k, t) : 0;
    const m = alagados[k];
    m.visible = nivel > PORAO_FOLGA + 0.15;
    if (!m.visible || Math.abs(nivel - m.userData.nivel) < 0.02) return;
    m.userData.nivel = nivel; m.geometry.dispose();
    m.geometry = solidoCasco({ x0: p.x0 + 0.3, x1: p.x1 - 0.3, topo: Math.min(nivel, PONTAL), folga: PORAO_FOLGA + 0.05, nx: 26, ny: 14 });
  });
}

// ---------- Bloco de aço ----------
const bloco = malha(new RoundedBoxGeometry(BLOCO.aresta, BLOCO.aresta, BLOCO.aresta, 3, 0.12),
  aplicarSubaquatico(new THREE.MeshStandardMaterial({ color: '#a9b2bc', metalness: 0.85, roughness: 0.32 })));
cena.add(bloco);
const cuboAgua = new THREE.Mesh(new THREE.BoxGeometry(BLOCO.aresta, BLOCO.aresta, BLOCO.aresta),
  new THREE.MeshBasicMaterial({ color: '#6FD6F7', transparent: true, opacity: 0.3, depthWrite: false }));
const cuboAguaArestas = new THREE.LineSegments(new THREE.EdgesGeometry(cuboAgua.geometry), new THREE.LineBasicMaterial({ color: '#c9f1ff', transparent: true }));
cuboAgua.add(cuboAguaArestas); cena.add(cuboAgua);
const FUNDO_BLOCO = -PROFUNDIDADE + BLOCO.aresta / 2;
// trajetória: queda no ar, impacto, desaceleração até velocidade terminal, pouso no leito
function trajetoriaBloco(t) {
  const t0 = T.quedaBloco, y0 = 26, v0 = 14, g = 9.81 * 2.2;
  const tImp = t0 + (-v0 + Math.sqrt(v0 * v0 + 2 * g * y0)) / g;
  if (t < t0) return { y: 999, fase: 'antes', tImp };
  if (t < tImp) { const d = t - t0; return { y: y0 - v0 * d - 0.5 * g * d * d, fase: 'ar', tImp }; }
  const vI = v0 + g * (tImp - t0), vt = 9.5, tau = 0.35, d = t - tImp;
  const y = -(vt * d + (vI - vt) * tau * (1 - Math.exp(-d / tau)));
  const yf = Math.max(y, FUNDO_BLOCO);
  return { y: yf, fase: y <= FUNDO_BLOCO ? 'fundo' : 'agua', tImp, rot: Math.min(d, 2.5) };
}
// instante do pouso (busca numérica)
const T_POUSO = (() => { for (let t = T.quedaBloco; t < 20; t += 0.005) if (trajetoriaBloco(t).fase === 'fundo') return t; return 20; })();

// ---------- Partículas ----------
function texturaGota() {
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.7)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64); const t = new THREE.CanvasTexture(c); return t;
}
const TEX_GOTA = texturaGota();
class Particulas {
  constructor(n, cor, tamanho, ordem = 15) {
    this.n = n; this.geo = new THREE.BufferGeometry();
    this.pos = new Float32Array(n * 3); this.alfa = new Float32Array(n); this.tam = new Float32Array(n);
    this.geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    this.geo.setAttribute('alfa', new THREE.BufferAttribute(this.alfa, 1));
    this.geo.setAttribute('tam', new THREE.BufferAttribute(this.tam, 1));
    this.mat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, uniforms: { uMapa: { value: TEX_GOTA }, uCor: { value: new THREE.Color(cor) }, uEsc: { value: ALT * tamanho } },
      vertexShader: `attribute float alfa; attribute float tam; varying float vA; uniform float uEsc; void main(){ vA=alfa; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_PointSize=tam*uEsc/(-mv.z); gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `uniform sampler2D uMapa; uniform vec3 uCor; varying float vA; void main(){ vec4 t=texture2D(uMapa,gl_PointCoord); gl_FragColor=vec4(uCor,t.a*vA);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
    });
    this.obj = new THREE.Points(this.geo, this.mat); this.obj.frustumCulled = false; this.obj.renderOrder = ordem; cena.add(this.obj);
  }
  atualizar() { this.geo.attributes.position.needsUpdate = true; this.geo.attributes.alfa.needsUpdate = true; this.geo.attributes.tam.needsUpdate = true; }
}
// respingo + bolhas do bloco
const respingo = new Particulas(420, '#f4fbff', 0.0016);
const SEM_RESP = (() => { const r = rnd(11); return Array.from({ length: 420 }, () => ({ a: r() * Math.PI * 2, v: 4 + r() * 13, vy: 6 + r() * 16, s: 0.5 + r() * 1.3, atraso: r() * 0.12 })); })();
const bolhas = new Particulas(260, '#d8f6ff', 0.0011, 16);
const SEM_BOLHA = (() => { const r = rnd(23); return Array.from({ length: 260 }, () => ({ te: r(), dx: (r() - 0.5) * 2.4, dz: (r() - 0.5) * 2.4, vs: 1.6 + r() * 2.2, f: r() * 6, s: 0.25 + r() * 0.6 })); })();
const poeira = new Particulas(160, '#d8c7a0', 0.0026, 14);
const SEM_POEIRA = (() => { const r = rnd(31); return Array.from({ length: 160 }, () => ({ a: r() * Math.PI * 2, v: 1 + r() * 4, vy: 0.4 + r() * 1.8, s: 1 + r() * 2 })); })();
const jatos = new Particulas(600, '#bfeaff', 0.0018, 16);
const SEM_JATO = (() => { const r = rnd(41); return Array.from({ length: 600 }, () => ({ k: Math.floor(r() * 5), te: r(), dy: (r() - 0.5) * 1.6, dx: (r() - 0.5) * 2.0, v: 9 + r() * 6, s: 0.4 + r() * 0.7 })); })();
const anelImpacto = new THREE.Mesh(new THREE.RingGeometry(0.8, 1, 64), new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, depthWrite: false }));
anelImpacto.rotation.x = -Math.PI / 2; cena.add(anelImpacto);

function atualizarParticulas(t, traj, calado) {
  // respingo
  const dImp = t - traj.tImp;
  for (let i = 0; i < respingo.n; i++) {
    const s = SEM_RESP[i], d = dImp - s.atraso;
    if (d > 0 && d < 1.8) {
      const x = BLOCO.x + Math.cos(s.a) * (1.2 + s.v * d), z = BLOCO.z + Math.sin(s.a) * (1.2 + s.v * d);
      const y = s.vy * d - 0.5 * 9.81 * 1.3 * d * d;
      respingo.pos.set([x, Math.max(y, -0.2), z], i * 3); respingo.alfa[i] = y > -0.1 ? Math.min(1, (1.8 - d) * 1.2) : 0; respingo.tam[i] = s.s;
    } else respingo.alfa[i] = 0;
  }
  respingo.atualizar();
  anelImpacto.visible = dImp > 0 && dImp < 3.2;
  if (anelImpacto.visible) { const r = 2 + dImp * 7; anelImpacto.scale.setScalar(r); anelImpacto.position.set(BLOCO.x, alturaOnda(BLOCO.x, BLOCO.z, t) + 0.15, BLOCO.z); anelImpacto.material.opacity = 0.7 * (1 - dImp / 3.2); }
  // bolhas: emitidas ao longo da descida, sobem até a superfície
  for (let i = 0; i < bolhas.n; i++) {
    const s = SEM_BOLHA[i];
    const te = traj.tImp + s.te * Math.max(0.1, T_POUSO - traj.tImp + 1.0);
    const d = t - te;
    const yEm = trajetoriaBloco(te).y;
    if (d > 0 && te < T.transicao3b && yEm < 0) {
      const y = yEm + s.vs * d * (1 + d * 0.3);
      bolhas.pos.set([BLOCO.x + s.dx + Math.sin(d * 3 + s.f) * 0.4, y, BLOCO.z + s.dz + Math.cos(d * 2.5 + s.f) * 0.4], i * 3);
      bolhas.alfa[i] = y < -0.3 ? Math.min(1, d * 4) * 0.8 : 0; bolhas.tam[i] = s.s;
    } else bolhas.alfa[i] = 0;
  }
  bolhas.atualizar();
  // poeira no pouso
  const dp = t - T_POUSO;
  for (let i = 0; i < poeira.n; i++) {
    const s = SEM_POEIRA[i];
    if (dp > 0 && dp < 4) {
      const r = s.v * (1 - Math.exp(-dp * 1.5)) + 1.4;
      poeira.pos.set([BLOCO.x + Math.cos(s.a) * r, -PROFUNDIDADE + 0.3 + s.vy * (1 - Math.exp(-dp * 2)), BLOCO.z + Math.sin(s.a) * r], i * 3);
      poeira.alfa[i] = 0.55 * (1 - dp / 4); poeira.tam[i] = s.s;
    } else poeira.alfa[i] = 0;
  }
  poeira.atualizar();
  // jatos de água entrando pelos rombos (Cena 07): do costado de bombordo (z<0) para dentro
  for (let i = 0; i < jatos.n; i++) {
    const s = SEM_JATO[i], p = ALAGAMENTO.poroes[s.k];
    const ativo = t > p.t0 - 0.2 && t < p.t1 && t < T.cena8;
    if (ativo) {
      const per = 0.8, d = ((t * 1.0 + s.te * per) % per);
      const xc = (p.x0 + p.x1) / 2, yl = Math.max(1.5, calado - 3.0);
      const z0 = -(meiaBoca(xc, yl) - 0.7);
      const x = xc + s.dx, y = yl + s.dy + 1.5 * d - 4.9 * d * d, z = z0 + s.v * d;
      jatos.pos.set([x, y - calado, z], i * 3); jatos.alfa[i] = 0.85 * Math.min(1, (p.t1 - t) * 2) * (1 - d / per); jatos.tam[i] = s.s;
    } else jatos.alfa[i] = 0;
  }
  jatos.atualizar();
}

// ---------- Sobreposição 2D ----------
const ov = document.getElementById('ov'); ov.width = LARG; ov.height = ALT;
const LEGENDAS = await (await fetch('../narracao/legendas.json')).json();
const sob = new Sobreposicao(ov, LEGENDAS);
const _v = new THREE.Vector3();
function projetar(x, y, z) {
  _v.set(x, y, z).project(camera);
  return { x: (_v.x * 0.5 + 0.5) * 1080, y: (-_v.y * 0.5 + 0.5) * 1920, visivel: _v.z < 1 && _v.z > -1 };
}

// ---------- Estado por cena ----------
function corteNoInstante(t) {
  // [nx, nz, d]: mantém dot(n,p) <= d
  if (t < T.fatiaInicio) return [0, 1, 3000];
  if (t < T.cena2) { const f = suave(T.fatiaInicio, T.fatiaFim, t); return [0, 1, lerp(700, 40, Math.pow(f, 0.8))]; }
  if (t < T.cena3) { const f = suave(T.corteNavio0, T.corteNavio1, t); return [0, 1, lerp(40, 0, f)]; }
  if (t < T.transicao3b) return [0, 1, 0];
  if (t < T.transicao4) return [1, 0, 10];
  if (t < T.transicao7) return [0, 1, 40];
  if (t < T.transicao8) return [0, 1, 0];
  return [0, 1, 40];
}
function ondasNoInstante(t) {
  if (t < T.cena2) return 1.0;
  if (t < T.transicao3b) return lerp(1.0, 0.55, suave(T.cena2, T.cena3, t));
  if (t < T.transicao4) return 0.45;
  if (t < T.transicao8) return 0.32;
  return lerp(0.32, 0.9, suave(T.cena8, T.cena8 + 3, t));
}

const MARCOS = { // instantes de fala (narracao/frases.json) usados para sincronizar
  segredo: 8.2, formato: 10.91, bloco: 13.3, navio3: 20.6, envolve: 22.59, semAgua: 24.43,
  entra: 28.3, empuxo: 31.9, chamadaEmpuxo: 33.61, arquimedes: 36.3, iguala: 41.6, flutua: 44.21,
  conteineres: 47.3, carga: 52.75, excesso: 56.4, perder: 59.97, portanto: 63.4, volume: 66.07,
};

function quadro(t) {
  U.uTempo.value = t;
  const [nx, nz, d] = corteNoInstante(t); U.uCorte.value.set(nx, 0, nz, d);
  U.uOndas.value = ondasNoInstante(t);
  U.uVisSub.value = t < T.fatiaInicio ? 0 : t < T.transicao4 ? 0.5 : t < T.transicao7 ? 1 : t < T.transicao8 ? 0.6 : 1;
  const calado = FIS.calado(t);
  U.uCalado.value = calado;
  // balanço suave somente em plano aberto (sem cortes técnicos)
  const bal = (t < T.cena2 ? 1 - suave(T.cena2 - 0.8, T.cena2, t) : 0) + (t > T.cena8 ? suave(T.cena8 + 0.5, T.cena8 + 3, t) : 0);
  const afund = t > ALAGAMENTO.inicio && t < T.cena8 ? suave(60.6, 62.75, t) : 0;
  navio.position.set(0, -calado, 0);
  navio.rotation.set(0.006 * Math.sin(t * 0.7) * bal, 0, 0.004 * Math.sin(t * 0.55 + 1) * bal + 0.025 * afund * afund);
  U.uNavio.value.copy(navio.position);
  atualizarConteineres(t);

  // câmera
  const cam = estadoCamera(t);
  camera.position.set(...cam.pos); camera.lookAt(...cam.alvo); camera.fov = cam.fov; camera.updateProjectionMatrix();
  sol.position.set(U.uSol.value.x * 400, U.uSol.value.y * 400, U.uSol.value.z * 400); sol.target.position.set(0, 0, 0);

  // bloco
  const traj = trajetoriaBloco(t);
  bloco.visible = traj.fase !== 'antes';
  bloco.position.set(BLOCO.x, traj.y, BLOCO.z);
  bloco.rotation.set(0.25 * Math.min(1, (traj.rot || 0)) , 0.4 + 0.3 * Math.min(1, (traj.rot || 0)), 0.12);
  if (traj.fase === 'fundo') bloco.rotation.set(0, 0.7, 0);
  const aCubo = janela(t, 15.0, T.transicao3b - 0.2, 0.6, 0.4);
  cuboAgua.visible = aCubo > 0.01; cuboAgua.material.opacity = 0.28 * aCubo; cuboAguaArestas.material.opacity = aCubo;
  cuboAgua.position.set(BLOCO.x + BLOCO.aresta + 2.2, FUNDO_BLOCO + 0.02, BLOCO.z); cuboAgua.rotation.set(0, 0.7, 0);
  atualizarParticulas(t, traj, calado);

  // volume deslocado
  const aFant = Math.max(
    t >= T.entradaInicio && t < T.transicao7 ? suave(MARCOS.entra + 0.3, MARCOS.entra + 1.2, t) : 0,
    t >= T.cena8 ? janela(t, MARCOS.portanto + 0.5, T.cartaoFinal + 0.3, 1.0, 0.4) : 0);
  fantasma.visible = linhaAgua.visible = aFant > 0.001;
  if (fantasma.visible) { atualizarFantasma(calado); matFantasma.uniforms.uA.value = aFant; matLinhaAgua.opacity = aFant; }
  matFantasma.uniforms.uBrilho.value = t >= T.cena8 ? janela(t, MARCOS.volume, T.cartaoFinal, 0.4, 0.5) : (t > MARCOS.arquimedes && t < MARCOS.iguala ? janela(t, MARCOS.arquimedes + 1.8, MARCOS.iguala, 0.4, 0.5) : 0);
  matInternoVol.uniforms.uA.value = t >= T.cena3b && t < T.transicao4 ? janela(t, MARCOS.envolve, T.transicao4 - 0.1, 0.6, 0.2) : 0;
  volInterno.visible = matInternoVol.uniforms.uA.value > 0.001;

  // pressões (Cena 04)
  atualizarPressao(calado, t >= T.entradaInicio && t < T.cena5 ? janela(t, MARCOS.empuxo + 0.2, MARCOS.chamadaEmpuxo + 0.9, 0.5, 0.6) : 0);

  // forças no navio
  const B = centroCarenaCache(calado);
  const escala = 22 / M_BASE;
  const wx = B.x;
  let aEmp = 0, aPeso = 0;
  if (t >= T.entradaInicio && t < T.transicao7) { aEmp = suave(MARCOS.chamadaEmpuxo + 0.2, MARCOS.chamadaEmpuxo + 0.7, t); aPeso = suave(MARCOS.iguala, MARCOS.iguala + 0.6, t); }
  if (t >= T.cena7 && t < T.transicao8) { aEmp = aPeso = janela(t, MARCOS.perder - 0.3, T.transicao8, 0.4, 0.2); }
  if (t >= T.cena8) { aEmp = aPeso = janela(t, MARCOS.volume + 0.4, T.cartaoFinal, 0.5, 0.4); }
  const Lemp = FIS.empuxo(t) * escala, Lpeso = FIS.peso(t) * escala;
  const yB = B.y - calado;
  setaEmpuxo.definir(new THREE.Vector3(wx + 4, yB - Lemp, 0), 1, Lemp, aEmp);
  const yG = 10.5 - calado;
  setaPeso.definir(new THREE.Vector3(wx - 4, yG, 0), -1, Lpeso, aPeso);
  setaEmpuxoBloco.definir(new THREE.Vector3(), 1, 0, 0); setaPesoBloco.definir(new THREE.Vector3(), -1, 0, 0);
  atualizarAlagamento(t);

  // ---------- render 3D ----------
  renderer.render(cena, camera);

  // ---------- sobreposição ----------
  sob.iniciar(t);
  const P = (x, y, z) => projetar(x, y, z);
  // Cena 01
  sob.rotulo({ texto: 'Navio: flutua', ancora: P(40, PONTAL - calado - 4, 14), dx: -60, dy: -230, a: janela(t, 5.7, 7.9, 0.3, 0.25) });
  if (traj.fase !== 'antes') sob.rotulo({ texto: 'Aço: afunda', ancora: P(BLOCO.x, traj.y, BLOCO.z), dx: 120, dy: 170, a: janela(t, 5.7, 7.9, 0.3, 0.25) });
  // Cena 02
  sob.rotulo({ texto: 'Formato do casco', ancora: P(-30, 0.6 - calado, 0), dx: 40, dy: 280, a: janela(t, MARCOS.formato, T.cena3 - 0.2, 0.3, 0.3) });
  // Cena 03a
  sob.rotulo({ texto: 'Bloco maciço\nde aço', ancora: P(BLOCO.x, FUNDO_BLOCO + 1, BLOCO.z), dx: -170, dy: 260, a: janela(t, 14.55, 18.3, 0.3, 0.3) });
  sob.rotulo({ texto: 'mesmo volume\nde água', ancora: P(BLOCO.x + BLOCO.aresta + 2.2, FUNDO_BLOCO + 1, BLOCO.z), dx: 170, dy: 260, cor: '#6FD6F7', a: janela(t, 15.4, 18.3, 0.3, 0.3) });
  sob.painelDensidade(janela(t, 14.9, 18.45, 0.4, 0.35), suave(15.1, 16.2, t));
  // Cena 03b
  sob.rotulo({ texto: 'Casco de aço', ancora: P(10, 9 - calado, -meiaBoca(10, 9)), dx: 0, dy: -300, a: janela(t, MARCOS.navio3 + 0.6, T.transicao4 - 0.15, 0.3, 0.2) });
  sob.rotulo({ texto: 'Muito espaço\nsem água', ancora: P(10, 4 - calado, 0), dx: 0, dy: 330, a: janela(t, MARCOS.semAgua - 1.6, T.transicao4 - 0.15, 0.3, 0.2) });
  sob.rotulo({ texto: 'Água', ancora: P(10, -14, -32), dx: -30, dy: 200, cor: '#6FD6F7', a: janela(t, MARCOS.semAgua, T.transicao4 - 0.15, 0.3, 0.2) });
  // Cena 04
  sob.rotulo({ texto: 'Volume submerso =\nágua deslocada', ancora: P(40, -calado * 0.55, 10), dx: 40, dy: 330, cor: '#6FD6F7', a: janela(t, MARCOS.entra + 1.6, MARCOS.empuxo - 0.1, 0.35, 0.3) });
  sob.rotulo({ texto: 'Pressão da água', ancora: P(36, 1.2 - calado, meiaBoca(36, 1.2) + 2), dx: 30, dy: 300, cor: '#8fe3ff', a: janela(t, MARCOS.empuxo + 0.5, MARCOS.chamadaEmpuxo + 0.6, 0.3, 0.3) });
  const pontaEmp = P(wx + 4, yB, 0), pontaPeso = P(wx - 4, yG - Lpeso, 0);
  sob.rotulo({ texto: 'Empuxo', ancora: P(wx + 4, yB - Lemp * 0.55, 0), dx: 230, dy: 40, cor: '#6FD6F7', a: aEmp * (t < T.cena7 ? 1 : 0) * (t < T.cena6 ? 1 : 0) });
  sob.rotulo({ texto: 'Peso', ancora: P(wx - 4, yG - Lpeso * 0.3, 0), dx: -230, dy: -60, cor: '#F3B544', a: aPeso * (t < T.cena6 ? 1 : 0) });
  // Cena 05
  sob.cartao({ texto: 'Empuxo = *peso da água*\n*deslocada*', a: janela(t, MARCOS.arquimedes + 0.4, MARCOS.iguala - 0.15, 0.35, 0.3) });
  sob.cartao({ texto: '*Empuxo* = *Peso*\nO navio flutua', a: janela(t, MARCOS.iguala + 0.4, T.cena6 + 0.3, 0.35, 0.35) });
  // Cena 06
  sob.cartao({ texto: '+ carga → + água deslocada', tam: 46, a: janela(t, MARCOS.conteineres + 0.3, T.transicao7 - 0.2, 0.35, 0.3) });
  sob.rotulo({ texto: 'Linha de carga\nmáxima', ancora: P(0, CALADO_MAX - calado, meiaBoca(0, CALADO_MAX)), dx: 150, dy: 300, a: janela(t, MARCOS.carga - 0.4, T.transicao7 - 0.2, 0.3, 0.3) });
  // Cena 07
  sob.rotulo({ texto: 'Pouca água:\nainda flutua', ancora: P(6.5, Math.max(1, FIS.nivel(0, t)) - calado, -8), dx: 120, dy: -330, cor: '#6FD6F7', a: janela(t, 57.6, 59.4, 0.3, 0.3) });
  sob.cartao({ texto: 'Água em *excesso*', a: janela(t, 59.2, T.transicao8 - 0.05, 0.3, 0.2) });
  sob.rotulo({ texto: 'Peso > Empuxo', ancora: P(wx - 4, yG - Lpeso * 0.5, 0), dx: -150, dy: 260, a: janela(t, 61.0, T.transicao8 - 0.05, 0.3, 0.2) });
  // Cena 08
  sob.cartao({ texto: 'Não é a leveza do aço', a: janela(t, MARCOS.portanto + 0.1, MARCOS.volume - 0.15, 0.35, 0.3) });
  sob.cartao({ texto: 'É o *volume de água*\nque o casco desloca', a: janela(t, MARCOS.volume + 0.1, T.cartaoFinal + 0.2, 0.35, 0.3) });
  // legendas (ocultas na assinatura)
  if (t < T.cartaoFinal + 0.2) sob.legenda(t);
  // transições na cor da marca
  let mg = 0;
  for (const tc of [T.transicao3b, T.transicao4, T.transicao7, T.transicao8]) mg = Math.max(mg, 1 - Math.abs(t - tc) / 0.28);
  sob.mergulho(clamp(mg * 1.25, 0, 1));
  sob.assinatura(t, T.cartaoFinal);
  if (t < 0.35) sob.mergulho(1 - t / 0.35);
}
const _cacheB = new Map();
function centroCarenaCache(calado) {
  const k = Math.round(Math.max(0.2, Math.min(PONTAL, calado)) * 20) / 20;
  if (!_cacheB.has(k)) _cacheB.set(k, centroCarena(k));
  return _cacheB.get(k);
}

window.quadro = (t) => { quadro(t); return true; };
window.DURACAO = DURACAO;
window.DBG = { cena, superficie, faceCorte, navio, fantasma, U };
window.pronto = true;
document.title = 'pronto';
