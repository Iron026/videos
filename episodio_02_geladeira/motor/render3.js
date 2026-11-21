// [Ep. 02 · fork de episodio_01_navio_v2/motores/tempo_real_v2/render2.js — ver PROCEDENCIA.md]
// Acréscimos do Ep. 02: visão térmica (paleta centrada na temperatura da cozinha, varredura), fluido no circuito
// (cor = temperatura, aparência = fase, padrão no sentido do fluxo, antisserrilhado), feixes de calor (âmbar, contínuos),
// pulsos de trabalho (violeta), corte ilustrativo com tampa colorida e curvas de animação para uniformes.
// Motor em tempo real v2 (Three.js r170) — mesma cena exportada do Blender (exportar_rt2.py).
// Melhorias sobre a v1:
//  • materiais: ruído de cor/rugosidade e relevo procedurais iguais aos do Blender (pintura, aço escovado,
//    concreto, areia ondulada, corrugação dos contêineres, faixas do casco, face de corte com linha d'água);
//  • luz: sol + céu (IBL) + rebatimento do chão simulado + oclusão de ambiente (GTAO);
//  • sombras: mapa ajustado ao que a câmera vê (PCF suave) ou VSM; cache opcional (cena estática);
//  • água: espessura real por pixel (profundidade da cena − profundidade da água) → absorção Beer-Lambert com
//    os mesmos coeficientes do volume do Cycles, refração, Fresnel com reflexo do céu e brilho do sol;
//    luz que chega ao fundo atenuada pela coluna d'água; raios de luz aditivos.
// Parâmetros na URL: cena, escala, ao(0/1), aoamostras, sombra(pcf|vsm), smap, cache(0/1), msaa
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Pass, FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { CopyShader } from 'three/addons/shaders/CopyShader.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const P = new URLSearchParams(location.search);
const CENA = P.get('cena') || '../cena2_q3/';
const ESCALA = parseFloat(P.get('escala') || '0.5');
const AO = P.get('ao') !== '0';
const AO_AMOSTRAS = parseInt(P.get('aoamostras') || '16');
const SOMBRA = P.get('sombra') || 'pcf';
const SMAP = parseInt(P.get('smap') || '4096');
const CACHE = P.get('cache') === '1';
const ENV0 = P.get('env');
const MSAA = parseInt(P.get('msaa') || '4');
const FANT_OFF = parseFloat(P.get('fantoff') || '0');   // prioridade de profundidade dos volumes fantasmas (coincidentes com sólidos); 0 = desligado
const JAN_OFF = parseFloat(P.get('janoff') || '0');   // teste: prioridade de profundidade das janelas (polygon offset); 0 = como aprovado
const OCL_K = parseFloat(P.get('ocl') || '0.994');   // fator de aproximação do oclusor (1 = comportamento antigo, só diagnóstico)
const OCULTAR = new Set((P.get('ocultar') || '').split(',').filter(Boolean));   // diagnóstico: não carrega estes materiais (nome ou tipo)
const BLOOM = parseFloat(P.get('bloom') || '0');      // brilho suave só nas luzes fortes (solda, reflexo do sol, linhas luminosas)
const meta = await (await fetch(CENA + 'cena.json')).json();
const W = Math.round(meta.camera.largura * ESCALA), H = Math.round(meta.camera.altura * ESCALA);
// ---- Ep. 02: uniformes globais animados por curvas [[t, v], ...] (tempo global do episódio)
const UG = { uTermico: { value: 0 }, uVarre: { value: 1 }, uRevela: { value: 0 }, uPulso: { value: -1 }, uFluxo: { value: 1.0 },
  uTrab: { value: 0 }, uTrabVel: { value: 1 }, uResY: { value: H }, uAmb: { value: meta.fluido ? meta.fluido.T_ambiente : 25 },
  uFase: { value: 1 }, uCorteD: { value: 99 } };
const CURVAS = meta.curvas || {};
function curva(k, t) { if (!k || !k.length) return null; if (t <= k[0][0]) return k[0][1];
  for (let i = 0; i < k.length - 1; i++) if (t <= k[i + 1][0]) { const u = (t - k[i][0]) / Math.max(k[i + 1][0] - k[i][0], 1e-6), e = u * u * (3 - 2 * u); return k[i][1] + (k[i + 1][1] - k[i][1]) * e; }
  return k[k.length - 1][1]; }
const matsCurvas = [];   // { U, curvas } por material (temperatura animada, janela dos feixes…)
let tLUT = null;
if (meta.fluido) { const n = meta.fluido.n, d = new Float32Array(n * 4);
  for (let i = 0; i < n; i++) { d[4 * i] = meta.fluido.T[i]; d[4 * i + 1] = meta.fluido.x[i]; d[4 * i + 2] = meta.fluido.lado[i]; d[4 * i + 3] = 1; }
  const hf = new Uint16Array(n * 4); for (let i = 0; i < n * 4; i++) hf[i] = THREE.DataUtils.toHalfFloat(d[i]);
  tLUT = new THREE.DataTexture(hf, n, 1, THREE.RGBAFormat, THREE.HalfFloatType); tLUT.minFilter = tLUT.magFilter = THREE.LinearFilter;
  tLUT.wrapS = THREE.RepeatWrapping; tLUT.needsUpdate = true; }
const planoCorte = new THREE.Plane(new THREE.Vector3(...((meta.corte && meta.corte.n) || [1, 0, 0])), 99);
// paleta de temperatura (sRGB → linear no shader): azul = mais frio que a cozinha, cinza-claro = igual, laranja/vermelho = mais quente
const PALETA = /* glsl */`
vec3 paletaT(float T, float amb){ float d=T-amb; vec3 c;
  if(d<=-45.0) c=vec3(0.106,0.212,0.682);
  else if(d<-30.0) c=mix(vec3(0.106,0.212,0.682),vec3(0.165,0.400,0.878),(d+45.0)/15.0);
  else if(d<-15.0) c=mix(vec3(0.165,0.400,0.878),vec3(0.420,0.660,0.950),(d+30.0)/15.0);
  else if(d<0.0)  c=mix(vec3(0.420,0.660,0.950),vec3(0.880,0.880,0.865),(d+15.0)/15.0);
  else if(d<12.0) c=mix(vec3(0.880,0.880,0.865),vec3(0.965,0.700,0.400),d/12.0);
  else if(d<28.0) c=mix(vec3(0.965,0.700,0.400),vec3(0.930,0.470,0.200),(d-12.0)/16.0);
  else if(d<50.0) c=mix(vec3(0.930,0.470,0.200),vec3(0.820,0.180,0.150),(d-28.0)/22.0);
  else c=vec3(0.820,0.180,0.150);
  return pow(c,vec3(2.2)); }`;
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1); renderer.localClippingEnabled = true;
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = SOMBRA !== 'nao';   // 'nao': diagnóstico sem sombras
renderer.shadowMap.type = SOMBRA === 'vsm' ? THREE.VSMShadowMap : THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();          // opacos
const cenaTransp = new THREE.Scene();     // água, raios de luz, bolhas (passo próprio)

// ------------------------------------------------------------------ GLSL comum
const RUIDO = /* glsl */`
vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;} vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
vec4 permute(vec4 x){return mod289(((x*34.0)+10.0)*x);} vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){ const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
  vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx); vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g;
  vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy); vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy;
  i=mod289(i); vec4 p=permute(permute(permute(i.z+vec4(0.0,i1.z,i2.z,1.0))+i.y+vec4(0.0,i1.y,i2.y,1.0))+i.x+vec4(0.0,i1.x,i2.x,1.0));
  float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx; vec4 j=p-49.0*floor(p*ns.z*ns.z); vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_);
  vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y); vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0)); vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3))); p0*=norm.x; p1*=norm.y; p2*=norm.z; p3*=norm.w;
  vec4 m=max(0.5-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
  return 105.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3))); }
// fBm no estilo do Noise Texture do Blender: saída ~[0,1] centrada em 0.5
float fbm(vec3 p, int oct, float rug){ float a=1.0, s=0.0, n=0.0;
  for(int i=0;i<8;i++){ if(i>=oct) break; s+=a*snoise(p); n+=a; p*=2.0; a*=rug; } return 0.5+0.5*clamp(s/n*1.35,-1.0,1.0); }
float mapear(float v,float a,float b,float c,float d){ return c+(d-c)*clamp((v-a)/(b-a),0.0,1.0); }
// cáusticas: rede celular (distância à borda de Voronoi) com distorção, como no material do Blender
vec2 h22(vec2 p){ p=vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))); return fract(sin(p)*43758.5453); }
float bordaVoronoi(vec2 x){ vec2 n=floor(x), f=fract(x), mg, mr; float md=8.0;
  for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){ vec2 g=vec2(i,j); vec2 o=h22(n+g); vec2 r=g+o-f; float d=dot(r,r); if(d<md){md=d; mr=r; mg=g;} }
  md=8.0; for(int j=-2;j<=2;j++) for(int i=-2;i<=2;i++){ vec2 g=mg+vec2(i,j); vec2 o=h22(n+g); vec2 r=g+o-f;
    if(dot(mr-r,mr-r)>0.00001) md=min(md,dot(0.5*(mr+r),normalize(r-mr))); } return md; }
`;

// céu (mesmos parâmetros do ceu_estilizado do Blender)
const C = meta.ceu;
const COR_CEU = /* glsl */`
uniform vec3 uZen, uMeio, uHor, uAbaixo; uniform float uNuvens, uForcaCeu;
vec3 corCeu(vec3 d){ float t=clamp(d.z*0.5+0.5,0.0,1.0); vec3 c;
  if(t<0.495) c=mix(uAbaixo,uHor,t/0.495); else if(t<0.505) c=uHor; else if(t<0.62) c=mix(uHor,uMeio,(t-0.505)/0.115); else c=mix(uMeio,uZen,(t-0.62)/0.38);
  if(uNuvens>0.0){ vec3 g=d*0.5+0.5; float n=fbm(vec3(g.x,g.y,g.z*4.0)*2.2,6,0.55);
    float k=mapear(n,0.52,0.72,0.0,1.0)*mapear(d.z,0.02,0.10,0.0,1.0)*mapear(d.z,0.55,0.2,0.0,1.0)*uNuvens;
    c=mix(c,vec3(0.965,0.93,0.86),k); }
  return c*uForcaCeu; }
`;
const uCeu = { uZen: { value: new THREE.Vector3(...C.zenite) }, uMeio: { value: new THREE.Vector3(...C.meio) },
  uHor: { value: new THREE.Vector3(...C.horizonte) }, uAbaixo: { value: new THREE.Vector3(...C.abaixo) },
  uNuvens: { value: C.nuvens ?? 0.35 }, uForcaCeu: { value: C.forca ?? 1.0 } };
function materialCeu(comToneMap) {
  return new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: uCeu,
    vertexShader: `varying vec3 vDir; void main(){ vDir=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); gl_Position.z=gl_Position.w; }`,
    fragmentShader: RUIDO + COR_CEU + `varying vec3 vDir; void main(){ gl_FragColor=vec4(corCeu(normalize(vDir)),1.0); ${comToneMap ? '#include <tonemapping_fragment>\n#include <colorspace_fragment>' : ''} }` });
}
const ceu = new THREE.Mesh(new THREE.SphereGeometry(6000, 64, 32), materialCeu(false)); ceu.renderOrder = -1; scene.add(ceu);
const pm = new THREE.PMREMGenerator(renderer); const cenaEnv = new THREE.Scene();
cenaEnv.add(new THREE.Mesh(new THREE.SphereGeometry(100, 64, 32), materialCeu(false)));
scene.environment = pm.fromScene(cenaEnv, 0.02).texture; scene.environmentIntensity = ENV0 !== null ? parseFloat(ENV0) : (meta.env ?? 1);

// ------------------------------------------------------------------ luzes
const s = meta.sol; const dirSol = new THREE.Vector3(...s.dir).normalize();   // direção em que a luz viaja
const elevSol = Math.asin(Math.max(0.05, -dirSol.z));
const sol = new THREE.DirectionalLight(new THREE.Color(...s.cor), s.energia);
sol.castShadow = true; sol.shadow.mapSize.set(SMAP, SMAP);
sol.shadow.bias = SOMBRA === 'vsm' ? -0.0002 : -0.00025; sol.shadow.normalBias = SOMBRA === 'vsm' ? 0.05 : 0.35;
sol.shadow.radius = SOMBRA === 'vsm' ? 6 : 1; sol.shadow.blurSamples = 12;
scene.add(sol, sol.target);
// rebatimento do chão (o Cycles calcula; aqui é simulado): luz difusa vinda de baixo, cor do chão iluminado
const temAgua = meta.materiais.some(m => m.tipo === 'agua');
const albedoChao = temAgua ? new THREE.Color(0.05, 0.12, 0.14) : new THREE.Color(0.33, 0.31, 0.27);
const rebate = new THREE.DirectionalLight(albedoChao.clone().multiply(new THREE.Color(...s.cor)), s.energia * Math.sin(elevSol) * 0.55);
rebate.position.set(0.3 * dirSol.x, 0.3 * dirSol.y, -1).multiplyScalar(100);   // vem de baixo (luz refletida pelo chão)
scene.add(rebate);
for (const l of meta.luzes) {
  if (l.tipo === 'POINT') { const p = new THREE.PointLight(new THREE.Color(...l.cor), l.energia / (4 * Math.PI * Math.PI), 0, 2); p.position.set(...l.pos); scene.add(p); }
  if (l.tipo === 'AREA') { const p = new THREE.SpotLight(new THREE.Color(...l.cor), l.energia / (4 * Math.PI), 0, Math.PI / 2.2, 1, 2); p.position.set(...l.pos); p.target.position.set(...l.alvo); scene.add(p, p.target); }
}

// ------------------------------------------------------------------ materiais
const SUBMERSOS = /^(areia|rocha|peixe|alga|concha|seixo|casco|antiincrustante)/;   // recebem luz atenuada pela coluna d'água
let aguaMeta = meta.materiais.find(m => m.tipo === 'agua');
const caixaAgua = new THREE.Box3(new THREE.Vector3(1e9,1e9,1e9), new THREE.Vector3(-1e9,-1e9,-1e9));
const sigma = aguaMeta ? new THREE.Vector3(...aguaMeta.absorcao.map(c => aguaMeta.densidade * (1 - c))) : new THREE.Vector3();

function criarMaterial(m) {
  const t = m.tipo;
  const cor = new THREE.Color(...(m.cor || [0.7, 0.7, 0.7]));
  const coat = m.coat || (t === 'vidro' ? 0.6 : t === 'faixas_z' ? 0.15 : 0);
  const Base = coat > 0 ? THREE.MeshPhysicalMaterial : THREE.MeshStandardMaterial;
  const mat = new Base({ color: t === 'faixas_z' || t === 'corte_ld' ? 0xffffff : cor, roughness: m.rug ?? 0.5, metalness: m.metal ?? 0, side: THREE.DoubleSide });
  if (coat > 0) { mat.clearcoat = coat; mat.clearcoatRoughness = 0.15; }
  if (t === 'aco') { mat.metalness = m.macico ? 0.9 : 1.0; mat.roughness = m.rug ?? 0.32; }
  if (t === 'vidro') { mat.color.setRGB(...[28, 40, 58].map(v => Math.pow(v / 255, 2.2))); mat.roughness = 0.08; mat.metalness = 0.4; }
  if (t === 'vidro' && JAN_OFF > 0) { mat.polygonOffset = true; mat.polygonOffsetFactor = -JAN_OFF; mat.polygonOffsetUnits = -4 * JAN_OFF; }
  if (t === 'concreto') { mat.roughness = 0.88; }
  if (t === 'areia') { mat.roughness = 0.95; }
  if (t === 'conteiner') { mat.roughness = 0.55; }
  if (t === 'emissivo') { mat.emissive = cor.clone(); mat.emissiveIntensity = m.forca ?? 6; }
  if (m.fade) mat.transparent = true;   // pode desbotar por opacidade ao surgir/sumir (setas, mapa de pressão)
  if ((m.alfa ?? 1) < 1) { mat.transparent = true; mat.opacity = m.alfa; mat.depthWrite = false; }
  if (m.corte) mat.clippingPlanes = [planoCorte];
  const faixas = (m.faixas || []).slice(0, 6);
  const U = {
    uTipo: { value: ['pintura', 'aco', 'concreto', 'areia', 'conteiner', 'faixas_z', 'corte_ld', 'emissivo', 'vidro', 'generico', 'circuito', 'trabalho'].indexOf(t) },
    uTempMat: { value: m.temp ?? (meta.fluido ? meta.fluido.T_ambiente : 25) }, tLUT: { value: tLUT }, uCap: { value: new THREE.Vector3(...(m.cap || [0.91, 0.77, 0.42].map(v => Math.pow(v, 2.2)))) },
    uOnda: { value: m.onda ?? 10 }, uVelT: { value: m.vel ?? 1.2 },
    uCorB: { value: cor }, uVar: { value: m.variacao ?? 0.06 }, uEsc: { value: m.escala_var ?? m.escala ?? 0.6 },
    uRugB: { value: m.rug ?? 0.5 }, uBump: { value: m.bump ?? 0 }, uEscov: { value: m.escovado ? 1 : 0 },
    uMacico: { value: m.macico ? 1 : 0 }, uManchas: { value: m.manchas ?? 0 },
    uCaus: { value: m.causticas ?? 0 }, uEscCaus: { value: m.escala_caustica ?? 0.9 },
    uNF: { value: faixas.length }, uFZ: { value: [...faixas.map(f => f[0]), ...Array(6 - faixas.length).fill(1e9)] },
    uFC: { value: [...faixas.map(f => new THREE.Vector3(...f[1])), ...Array(6 - faixas.length).fill(new THREE.Vector3())] },
    uAcima: { value: new THREE.Vector3(...(m.acima || [1, 1, 1])) }, uAbaixoC: { value: new THREE.Vector3(...(m.abaixo || [1, 1, 1])) },
    uLinha: { value: new THREE.Vector3(...(m.linha || [0, 0, 0])) }, uZ0: { value: m.z0 ?? 0 }, uEsp: { value: m.esp ?? 0.2 },
    uCasca: { value: m.casca ? 1 : 0 }, uBc: { value: m.casca ? m.casca.b : Array(64).fill(0) }, uKc: { value: m.casca ? m.casca.k : 0 },
    uCalc: { value: m.casca ? m.casca.cal : 0 }, uTopoC: { value: m.casca ? m.casca.topo : 18 }, uEspC: { value: m.casca ? m.casca.esp : 0.38 },
    uCorC: { value: new THREE.Vector3(...(m.casca ? m.casca.cor : [1, 1, 1])) },
    uSub: { value: SUBMERSOS.test(m.chave || '') && aguaMeta ? 1 : 0 }, uSigma: { value: sigma }, uSinSol: { value: Math.sin(elevSol) },
    uAMin: { value: caixaAgua.min }, uAMax: { value: caixaAgua.max },
  };
  Object.assign(U, UG, { uTempo });
  if (m.curvas) matsCurvas.push({ U, curvas: m.curvas });
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec3 aLocal; attribute vec3 aGen; varying vec3 vW; varying vec3 vL; varying vec3 vNw; varying vec3 vGn;`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
      vW = (modelMatrix*vec4(position,1.0)).xyz; vL = aLocal; vNw = normalize(mat3(modelMatrix)*normal); vGn = aGen;`);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec3 vW; varying vec3 vL; varying vec3 vNw; varying vec3 vGn;
      uniform float uTermico, uVarre, uRevela, uPulso, uFluxo, uTrab, uTrabVel, uResY, uAmb, uTempMat, uTempo, uFase, uOnda, uVelT;
      uniform sampler2D tLUT; uniform vec3 uCap;
      ${PALETA}
      uniform int uTipo, uNF; uniform vec3 uCorB; uniform float uVar, uEsc, uRugB, uBump, uEscov, uCaus, uEscCaus, uMacico, uManchas;
      uniform float uFZ[6]; uniform vec3 uFC[6]; uniform vec3 uAcima, uAbaixoC, uLinha; uniform float uZ0, uEsp;
      uniform float uSub, uSinSol; uniform vec3 uSigma, uAMin, uAMax;
      uniform float uCasca, uBc[64], uKc, uCalc, uTopoC, uEspC; uniform vec3 uCorC;
      ${RUIDO}
      // fluido no circuito: s = vGn.x (posição global), u = vGn.z (coordenada de fluxo), ângulo = vGn.y
      vec4 lut(float s){ return texture2D(tLUT, vec2(s,0.5)); }
      vec3 fluido(out float brilho){ vec4 L=lut(vGn.x); float T=L.r, x=L.g; vec3 col=paletaT(T,uAmb);
        float ph=vGn.z-uTempo*uFluxo; float f=fract(ph); float aa=clamp(1.0-fwidth(ph)*1.6,0.0,1.0);   // sem detalhe abaixo do pixel
        float liq = x<0.002 ? 1.0 : 0.0, vap = x>0.998 ? 1.0 : 0.0, mis = 1.0-liq-vap;
        float pl = 0.82+0.18*smoothstep(0.35,0.5,f)*(1.0-smoothstep(0.85,1.0,f));                   // líquido: contínuo, ondulação leve
        float pv = 0.16+0.84*smoothstep(0.70,0.78,f)*(1.0-smoothstep(0.90,0.97,f));                // vapor: traços curtos e ralos
        float cel = fbm(vec3(ph*2.2, vGn.y*6.0, 1.3),2,0.5);                                       // bolhas na mistura (densidade ∝ título)
        float bol = smoothstep(0.62-0.22*x, 0.70-0.22*x, cel);
        float pm = mix(0.70, 0.30, x)+0.7*bol;
        float p = liq*pl + vap*pv + mis*pm; float pmed = liq*0.88 + vap*0.30 + mis*(mix(0.70,0.30,x)+0.25*x);
        p = mix(pmed, p, aa*uFase);
        brilho = p; vec3 c = mix(col, mix(col, vec3(1.0), 0.55), mis*bol*aa*uFase);
        if(uPulso>=0.0){ float d=abs(fract(vGn.x-uPulso+0.5)-0.5); brilho += 2.2*exp(-d*d/0.00018); c=mix(c, vec3(1.0,0.96,0.85), clamp(2.0*exp(-d*d/0.00018),0.0,1.0)); }
        return c; }
      float alturaRelevo(){
        if(uTipo==0 && uBump>0.0) return fbm(vL*18.0,6,0.5)*uBump*0.06;
        // aço maciço: grão fino muito sutil, atenuado quando fica menor que o pixel (sem cintilação)
        if(uTipo==1 && uMacico>0.5){ vec3 q=vL*55.0; float aa=1.0-smoothstep(0.25,0.9,length(fwidth(q))); return fbm(q,2,0.5)*0.0010*aa; }
        if(uTipo==1 && uEscov>0.5) return fbm(vec3(vL.x*12.0, vL.y*720.0, vL.z*720.0),3,0.5)*0.004;
        if(uTipo==2) return fbm(vW*9.0,6,0.5)*0.006;
        if(uTipo==3){ float d=fbm(vL*0.2,3,0.5)*6.0; return (0.5+0.5*sin(vL.x*0.9*6.2832+d))*0.035; }
        if(uTipo==4){ float w=fract(vL.x*3.6*20.0/6.2832); return abs(w*2.0-1.0)*0.02; }
        return 0.0; }
    `)
    .replace('#include <color_fragment>', `#include <color_fragment>
      { vec3 c = diffuseColor.rgb;
        if(uTipo==0 || uTipo==9){ float n=fbm(vL*uEsc,5,0.5); c*=mapear(n,0.0,1.0,1.0-uVar,1.0+uVar); }
        else if(uTipo==1 && uMacico>0.5){ float n=fbm(vL*uEsc,3,0.5), n2=fbm(vL*uEsc*3.1+7.0,2,0.5);   // manchas de laminação, largas e suaves
          c*=mapear(n,0.0,1.0,1.0-uManchas,1.0+uManchas)*mapear(n2,0.0,1.0,0.975,1.025); }
        else if(uTipo==2){ float n=fbm(vW*uEsc,5,0.5); c=mix(uCorB*0.78,uCorB*1.08,mapear(n,0.3,0.75,0.0,1.0)); }
        else if(uTipo==3){ float n=fbm(vL*0.25,6,0.5); c=mix(uCorB*0.7,uCorB,n); }
        else if(uTipo==4){ float n=fbm(vL*1.5,6,0.5); c*=mapear(n,0.0,1.0,0.82,1.05); }
        else if(uTipo==5){ vec3 cf=uFC[uNF-1]; for(int i=uNF-2;i>=0;i--){ if(vL.z<uFZ[i]) cf=uFC[i]; }
                           c=cf*mapear(fbm(vL*0.08,6,0.5),0.0,1.0,0.9,1.06); }
        else if(uTipo==6){ c=(vW.z<uZ0)?uAbaixoC:uAcima; if(abs(vW.z-uZ0)<uEsp) c=uLinha;
          if(uCasca>0.5){ float zl=vW.z+uCalc; float f=clamp((zl-uKc)/(uTopoC-uKc),0.0,1.0)*63.0; int i0=int(floor(f)); int i1=min(i0+1,63);
            float bz=mix(uBc[i0],uBc[i1],fract(f)); float dcas=min(bz-abs(vW.y), zl-uKc);
            if(dcas<uEspC && zl<uTopoC-0.6) c=uCorC; } }
        if(uTipo==10 && uRevela>0.0){ float b; vec3 fc=fluido(b); c=mix(c, fc*0.35, uRevela); }
        diffuseColor.rgb=c; }`)
    .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
      if(uTipo==0) roughnessFactor=mapear(fbm(vL*uEsc,5,0.5),0.0,1.0,uRugB*0.8,min(1.0,uRugB*1.2));
      if(uTipo==1) roughnessFactor = uMacico>0.5 ? mapear(fbm(vL*uEsc*1.3,3,0.5),0.0,1.0,uRugB*0.82,uRugB*1.22)
                                                : mapear(fbm(vL*2.2,8,0.5),0.0,1.0,uRugB*0.65,uRugB*1.45);`)
    .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
      { float h=alturaRelevo()*exp(-length(vViewPosition)/45.0); if(h!=0.0){ vec3 sx=dFdx(-vViewPosition), sy=dFdy(-vViewPosition); vec3 r1=cross(sy,normal), r2=cross(normal,sx);
        float det=dot(sx,r1)*faceDirection; vec2 dh=vec2(dFdx(h),dFdy(h)); vec3 g=sign(det)*(dh.x*r1+dh.y*r2);
        normal=normalize(abs(det)*normal-g); } }`)
    .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
      if(uTipo==10 && uRevela>0.0){ float b; vec3 fc=fluido(b); totalEmissiveRadiance += fc*b*1.15*uRevela; }
      if(uTipo==11 && uTrab>0.0){ float ph=vGn.x*uOnda-uTempo*uVelT*uTrabVel; float aa=clamp(1.0-fwidth(ph)*1.6,0.0,1.0);
        float pu=mix(0.35, smoothstep(0.55,0.75,fract(ph))*(1.0-smoothstep(0.85,1.0,fract(ph))), aa);
        totalEmissiveRadiance += pow(vec3(0.604,0.420,1.0),vec3(2.2))*(0.25+1.8*pu)*uTrab; }
      if(uTipo==3 && uCaus>0.0 && vW.z<0.0 && vNw.z>0.4){ vec3 q=vW*vec3(1.0,1.0,0.3)*uEscCaus; q+=vec3(fbm(vW*1.6,2,0.5)-0.5)*0.45;
        float e=bordaVoronoi(q.xy+q.z*0.3); totalEmissiveRadiance+=vec3(1.0,0.98,0.9)*mapear(e,0.0,0.045,1.0,0.0)*uCaus*mapear(vNw.z,0.4,0.8,0.0,1.0); }`)
    .replace('#include <aomap_fragment>', `#include <aomap_fragment>
      // sob a água o céu só é visto por um cone estreito (e o casco o bloqueia): menos luz indireta
      if(uSub>0.5 && vW.z<0.0 && all(greaterThan(vW.xy,uAMin.xy+0.3)) && all(lessThan(vW.xy,uAMax.xy-0.3))){
        float k=mix(1.0,0.35,clamp(-vW.z/12.0,0.0,1.0)); reflectedLight.indirectDiffuse*=k; reflectedLight.indirectSpecular*=k; }`)
    .replace('#include <opaque_fragment>', `
      if(uTermico>0.0){ float yy=1.0-gl_FragCoord.y/uResY; float f=uTermico*(1.0-smoothstep(uVarre-0.003,uVarre+0.003,yy));
        if(f>0.0){ float Tl = uTipo==10 ? lut(vGn.x).r : uTempMat; vec3 tc=paletaT(Tl,uAmb);
          float sh=0.60+0.40*abs(dot(normalize(vNw),normalize(cameraPosition-vW)));
          outgoingLight=mix(outgoingLight, tc*sh*0.95, f); } }
      if(!gl_FrontFacing && ${m.corte ? 'true' : 'false'}){ outgoingLight = uCap*(0.55+0.45*abs(dot(normalize(vNw),vec3(0.3,-0.5,0.8)))); }
      if(uSub>0.5 && vW.z<0.0 && all(greaterThan(vW.xy,uAMin.xy+0.3)) && all(lessThan(vW.xy,uAMax.xy-0.3))){ float d=-vW.z; outgoingLight*=exp(-uSigma*d*(1.0+1.0/max(uSinSol,0.2))*0.5); }
      #include <opaque_fragment>`);
  };
  mat.customProgramCacheKey = () => 'rt3_' + t + (coat > 0 ? 'c' : '') + (m.corte ? 'k' : '');
  return mat;
}

function materialAgua(m) {
  return new THREE.ShaderMaterial({
    uniforms: Object.assign({ tCor: { value: null }, tProf: { value: null }, uRes: { value: new THREE.Vector2(W, H) },
      uNear: { value: 0.5 }, uFar: { value: 8000 }, uSigma: { value: sigma }, uSolDir: { value: dirSol.clone().negate() },
      uSolCor: { value: new THREE.Vector3(...s.cor).multiplyScalar(s.energia) }, uMarola: { value: m.marola ?? 0.3 }, uEscMar: { value: m.escala_marola ?? 0.3 }, uTempo, uNOndas: { value: ONDAS.length },
      uOndas: { value: [0, 1].map(k => ONDAS[k] ? new THREE.Vector3(ONDAS[k].x, ONDAS[k].y, ONDAS[k].t0) : new THREE.Vector3(0, 0, 1e9)) } }, uCeu),
    vertexShader: `varying vec3 vW; varying vec3 vN; varying float vZv; void main(){ vW=(modelMatrix*vec4(position,1.0)).xyz; vN=normalize(mat3(modelMatrix)*normal); vec4 mv=viewMatrix*vec4(vW,1.0); vZv=-mv.z; gl_Position=projectionMatrix*mv; }`,   // modelMatrix: água animada (dique inundando); identidade na água estática
    fragmentShader: RUIDO + COR_CEU + /* glsl */`
      uniform sampler2D tCor, tProf; uniform vec2 uRes; uniform float uNear, uFar, uMarola, uEscMar; uniform vec3 uSigma, uSolDir, uSolCor;
      uniform float uTempo; uniform int uNOndas; uniform vec3 uOndas[2];
      float ondaImpacto(vec2 p){ float h=0.0; for(int k=0;k<2;k++){ if(k>=uNOndas) break; float dt=uTempo-uOndas[k].z; if(dt<=0.0) continue;
          float r=length(p-uOndas[k].xy); float frente=1.9*dt;
          for(int j=0;j<3;j++){ float rr=r-(frente-float(j)*0.9); h+=0.10*exp(-rr*rr/0.18)*cos(rr*7.0)*exp(-dt/1.4)/(1.0+0.35*r); } } return h; }
      varying vec3 vW; varying vec3 vN; varying float vZv;
      float linear(float d){ float z=d*2.0-1.0; return 2.0*uNear*uFar/(uFar+uNear-z*(uFar-uNear)); }
      void main(){
        vec2 uv=gl_FragCoord.xy/uRes; float zc=linear(texture2D(tProf,uv).x);
        if(zc < vZv-0.05) discard;                                  // atrás de um objeto opaco
        vec3 V=normalize(cameraPosition-vW); vec3 N=normalize(vN);
        if(N.z>0.5){ float e=0.25; vec3 p=vW*uEscMar; float h0=fbm(p,3,0.5);
          float hx=fbm(p+vec3(e,0,0),3,0.5); float hy=fbm(p+vec3(0,e,0),3,0.5);
          float fade=exp(-vZv/120.0);                                  // sem relevo fino ao longe (evita serrilhado)
          N=normalize(N-vec3(hx-h0,hy-h0,0.0)/e*uMarola*0.25*fade);
          if(uNOndas>0){ float o0=ondaImpacto(vW.xy), ox=ondaImpacto(vW.xy+vec2(0.08,0.0)), oy=ondaImpacto(vW.xy+vec2(0.0,0.08));
            N=normalize(N-vec3(ox-o0,oy-o0,0.0)/0.08); } }
        float cosv=dot(V,vec3(0,0,1))>0.0 ? dot(V,N) : abs(dot(V,N));
        // espessura percorrida dentro da água até o fundo/objeto (convertida de Δz de visão para distância no raio)
        vec3 Rv=normalize(vW-cameraPosition); vec3 fwd=normalize(-vec3(viewMatrix[0][2],viewMatrix[1][2],viewMatrix[2][2]));
        float dist=max(zc-vZv,0.0)/max(dot(Rv,fwd),0.2);
        vec2 off=N.xy*0.02*clamp(dist/12.0,0.0,1.0)*(N.z>0.5?1.0:0.3); vec2 uv2=uv+off;
        if(linear(texture2D(tProf,uv2).x)<vZv) uv2=uv;
        vec3 fundo=texture2D(tCor,uv2).rgb; float distTot=min(dist,400.0);
        vec3 T=exp(-uSigma*distTot);
        float F=0.02+0.98*pow(1.0-clamp(cosv,0.0,1.0),5.0);
        vec3 R=reflect(-V,N); vec3 refl=corCeu(normalize(vec3(R.xy,abs(R.z))));
        float spec=pow(max(dot(R,uSolDir),0.0),300.0)*12.0*exp(-vZv/300.0);
        float prof=max(-vW.z,0.0);
        vec3 inscat=vec3(0.020,0.120,0.150)*(uSolCor.x/4.4)*exp(-prof/38.0);           // luz espalhada na coluna d'água
        vec3 c=(fundo*T+inscat*(vec3(1.0)-T))*(1.0-F)+refl*F+uSolCor*spec*F;
        if(N.z<0.5){                                                       // face lateral do corte: mar profundo, mas não liso
          float hz=vW.x+vW.y;                                              // coordenada horizontal ao longo da face
          float turb=fbm(vec3(hz*0.022, prof*0.03, uTempo*0.025),3,0.5);   // turbidez em grande escala (manchas lentas)
          float r=fbm(vec3(hz*0.07, prof*0.008+uTempo*0.03, 3.7),3,0.5);   // feixes de luz quase verticais vindos da superfície
          float raios=smoothstep(0.56,0.82,r)*exp(-prof/16.0);
          c*=0.86+0.28*turb;
          c+=vec3(0.05,0.15,0.16)*raios*0.8*(uSolCor.x/4.4);
          c=mix(c, vec3(0.003,0.016,0.040), smoothstep(4.0,95.0,prof)*0.88); }
        gl_FragColor=vec4(c,1.0);
      }` });
}

// brilho aditivo localizado (arco de solda e luz refletida nas chapas): queda radial a partir da origem do objeto
// e tremulação irregular por quadro (30 Hz), sem luzes dinâmicas no motor
function materialBrilho(m) {
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, depthTest: true, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uCor: { value: new THREE.Vector3(...(m.cor || [1, 0.85, 0.6])) }, uForca: { value: m.forca ?? 1.5 }, uRaio: { value: m.raio ?? 1 },
      uQueda: { value: m.queda ?? 2 }, uTremor: { value: m.tremor ?? 0.3 }, uSemente: { value: m.semente ?? 0 }, uOp: { value: 1 }, uT: uTempo },
    vertexShader: `attribute vec3 aLocal; varying vec3 vL; void main(){ vL=aLocal; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 uCor; uniform float uForca,uRaio,uQueda,uTremor,uSemente,uOp,uT; varying vec3 vL;
      float h(float n){ return fract(sin(n*12.9898+uSemente*78.233)*43758.5453); }
      void main(){ float r=clamp(length(vL)/uRaio,0.0,1.0); float a=pow(1.0-r,uQueda);
        float q=floor(uT*30.0+0.5); float fl=1.0-uTremor+uTremor*(0.6*h(q)+0.4*h(q*0.5+3.1));
        gl_FragColor=vec4(uCor*a*uForca*fl*uOp,1.0); }` });
  Object.defineProperty(mat, 'opacity', { get() { return mat.uniforms.uOp.value; }, set(v) { if (mat.uniforms) mat.uniforms.uOp.value = v; }, configurable: true });
  return mat;
}

// espuma de proa/costado/esteira: desenhada DEPOIS da água (teste de profundidade manual contra a cena opaca), com ruído
// que escorre para trás na velocidade do navio e máscaras procedurais (vL = coordenadas do navio). uForma:
// 0 = onda de proa (V que abre a partir da roda de proa), 1 = esteira (V de Kelvin + turbulência central), 2 = faixa ao longo
// do costado, 3 = crista vertical encostada na roda de proa (altura decai para ré)
function materialEspuma(m) {
  return new THREE.ShaderMaterial({ transparent: true, depthWrite: false, depthTest: false, side: THREE.DoubleSide,
    uniforms: { tProf: { value: null }, uRes: { value: new THREE.Vector2(W, H) }, uNear: { value: 0.5 }, uFar: { value: 8000 }, uT: uTempo,
      uForma: { value: m.forma ?? 0 }, uX0: { value: m.x0 ?? 0 }, uVel: { value: m.vel ?? 6 }, uDecai: { value: m.decai ?? 20 }, uLarg: { value: m.larg ?? 2 },
      uAbre: { value: m.abre ?? 0.35 }, uZ0: { value: m.z0 ?? 0 }, uAlt: { value: m.alt ?? 1.5 }, uDens: { value: m.dens ?? 0.9 }, uEsc: { value: m.escala ?? 0.5 },
      uCor: { value: new THREE.Vector3(...(m.cor || [0.92, 0.96, 0.98])) } },
    vertexShader: `attribute vec3 aLocal; varying vec3 vL; varying float vZv; void main(){ vL=aLocal; vec4 mv=modelViewMatrix*vec4(position,1.0); vZv=-mv.z; gl_Position=projectionMatrix*mv; }`,
    fragmentShader: RUIDO + `uniform sampler2D tProf; uniform vec2 uRes; uniform float uNear,uFar,uT,uX0,uVel,uDecai,uLarg,uAbre,uZ0,uAlt,uDens,uEsc; uniform int uForma; uniform vec3 uCor;
      varying vec3 vL; varying float vZv;
      float linear(float d){ float z=d*2.0-1.0; return 2.0*uNear*uFar/(uFar+uNear-z*(uFar-uNear)); }
      void main(){
        if(linear(texture2D(tProf,gl_FragCoord.xy/uRes).x)<vZv-0.05) discard;          // atrás do casco
        float d = uForma==1 ? (uX0-vL.x) : (uX0-vL.x);                                  // distância para ré (da roda de proa ou do espelho de popa)
        if(d<-0.5) discard;
        float ay=abs(vL.y); float m=0.0;
        vec3 q=vec3((vL.x+uT*uVel)*uEsc, vL.y*uEsc*1.6, vL.z*uEsc*1.6);
        float n=fbm(q,3,0.5), n2=fbm(q*2.3+7.0,2,0.5);                                  // poucas oitavas: manchas de alguns metros, sem granulado
        if(uForma==0){ float b=max(0.0,uLarg*(1.0-exp(-(d-2.5)/uAbre)));                  // meia-boca do casco na linha d'água (ajuste)
          float e=b+1.6+0.44*d;                                                             // borda externa da onda (abre para ré)
          m=exp(-d/uDecai)*smoothstep(b-0.4,b+0.25,ay)*(1.0-smoothstep(e-1.6,e,ay))*(1.0-0.5*smoothstep(b,e,ay)); }
        else if(uForma==1){ float c=exp(-d/uDecai)*(1.0-smoothstep(uLarg+0.12*d-2.0,uLarg+0.12*d,ay));
          float k=abs(ay-0.36*d); float braco=exp(-d/(uDecai*1.6))*(1.0-smoothstep(0.6,2.2+0.02*d,k)); m=max(c,0.7*braco); }
        else if(uForma==2){ m=exp(-max(ay-uLarg,0.0)/1.3)*smoothstep(0.0,6.0,d)*exp(-max(d-uDecai,0.0)/30.0); }
        else { float h=uAlt*exp(-d/uDecai)*(0.55+0.7*n2); float z=vL.z-uZ0;                // crista: topo irregular (ruído), sem borda reta
          m=(1.0-smoothstep(h*0.25,h,z))*smoothstep(-0.6,0.0,z)*exp(-d/(uDecai*1.5))*smoothstep(-0.5,2.0,d)*0.85; }
        float a=clamp(m*1.4,0.0,1.0)*uDens*smoothstep(0.34-0.3*m,0.58-0.25*m,n*0.75+n2*0.35);
        if(a<0.01) discard;
        gl_FragColor=vec4(uCor*(0.95+0.1*n2),clamp(a,0.0,0.97)); }` });
}


// ------------------------------------------------------------------ água do alagamento (avaria) e jato pelo rombo
// Nível da água no porão (coordenadas do navio), igual ao da cena: lv(g) = 2,2 + (T(g) + xcm·tg θ(g) − 2,2)·suave((g−137)/7,6)
const NIVEL_GLSL = `
  float suave(float t){ t=clamp(t,0.0,1.0); return t*t*(3.0-2.0*t); }
  float nivelPorao(float g, vec4 P){ float f=suave((g-137.2)/8.6); float T=P.x+(P.y-P.x)*f; float th=P.z*f;
    float nl=T+P.w*tan(th); return g<137.0 ? 2.2 : 2.2+(nl-2.2)*suave((g-137.0)/7.6); }
  float intensJato(float g, vec3 J){ return smoothstep(J.x, J.x+0.3, g)*(1.0-smoothstep(J.y, J.z, g)); }`;
function materialAlagado(m) {
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uT: uTempo, uG0: { value: m.g0 ?? 0 }, uOp: { value: 1 }, uImp: { value: new THREE.Vector2(...(m.imp || [0, 0])) },
      uRaso: { value: new THREE.Vector3(...(m.raso || [0.10, 0.42, 0.52])) }, uFundo: { value: new THREE.Vector3(...(m.fundo || [0.02, 0.14, 0.24])) },
      uSol: { value: dirSol.clone().negate().normalize() }, uLv: { value: new THREE.Vector4(...(m.nivel || [9, 10, 0, 0])) },
      uJato: { value: new THREE.Vector3(...(m.jato || [1e9, 1e9, 1e9])) }, uRombo: { value: new THREE.Vector4(...(m.rombo || [0, 0, 7.4, 6.3])) }, uZmax: { value: m.zmax ?? 1e9 } },
    vertexShader: `attribute vec3 aGen; varying vec3 vP; varying vec3 vW; varying vec3 vNw; varying vec3 vG; varying float vH;
      void main(){ vP=position; vG=aGen; vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; vNw=normalize(mat3(modelMatrix)*normal);
        vH=length(modelMatrix[2].xyz); gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader: RUIDO + NIVEL_GLSL + `uniform float uT,uG0,uOp,uZmax; uniform vec2 uImp; uniform vec3 uRaso,uFundo,uSol,uJato; uniform vec4 uLv,uRombo;
      varying vec3 vP; varying vec3 vW; varying vec3 vNw; varying vec3 vG; varying float vH;
      void main(){
        float g=uT+uG0; float J=intensJato(g,uJato); float L=nivelPorao(g,uLv);
        bool cheia=L>uZmax-0.03;                                            // caixa de baixo cheia: a superfície é a da caixa de cima
        if(vNw.z<-0.6 || (cheia && vNw.z>0.6)) discard;                     // fundo (nunca visto) e topo interno não são desenhados
        if(vNw.y>0.6) discard;                                              // face junto ao costado: coincide com o chapeamento (sem cintilação)
        float tq=sqrt(max(2.0*(uRombo.z-L),0.0)/9.81); vec2 imp=vec2(uImp.x, uRombo.y-uRombo.w*tq);   // onde o jato toca a superfície
        float prof=max(0.0,(1.0-vP.z)*vH); vec3 V=normalize(cameraPosition-vW); float d=length(vP.xy-imp);
        float agit=0.25+0.75*J;
        float n=fbm(vec3(vP.x*0.45, vP.y*0.45, g*0.9),3,0.5), n2=fbm(vec3(vP.x*1.3+g*0.4, vP.y*1.3, g*1.7),2,0.5);
        float n3=fbm(vec3(vP.x*2.4+g*0.3, vP.y*2.4, g*2.2),3,0.5), n4=fbm(vec3(vP.x*0.9, vP.y*3.2-g*0.8, g*0.7),3,0.5);   // espuma fina, em estrias
        float esp=J*exp(-d/1.7)*smoothstep(0.42,0.80,n3*0.7+n*0.3+0.15) + J*0.35*exp(-d/5.0)*smoothstep(0.58,0.86,n4);
        vec3 c; float a;
        if(vNw.z>0.6){                                                     // SUPERFÍCIE: ondulação, reflexo do céu, brilho, espuma
          float fr=pow(1.0-max(V.z,0.0),3.0);
          vec3 base=mix(uRaso*1.5, uRaso*0.9, 0.5+0.5*n*agit);
          c=mix(base, vec3(0.42,0.58,0.66), 0.10+0.32*fr);
          vec3 Ns=normalize(vec3(n2*0.25*agit, n*0.25*agit, 1.0));
          c+=vec3(1.0,0.98,0.92)*pow(max(dot(reflect(-uSol,Ns),V),0.0),60.0)*0.35;
          float borda=1.0-smoothstep(0.0,0.02,min(min(vG.x,1.0-vG.x),min(vG.y,1.0-vG.y)));
          esp+=borda*0.25*agit; a=0.9;
        } else {                                                           // CORPO: profundidade, turbidez, bolhas, linha d'água
          float k=1.0-exp(-prof/4.0); c=mix(uRaso, uFundo, k);
          float turb=fbm(vec3(vP.x*0.2, prof*0.25-g*0.10, vP.y*0.2+3.0),3,0.5); c*=0.84+0.32*turb;
          float col=exp(-abs(vP.x-imp.x)/1.6)*exp(-abs(vP.y-imp.y)/4.0);
          float bol=smoothstep(0.66,0.90,fbm(vec3(vP.x*2.6+vP.y*1.3, prof*2.2+g*2.0, 5.0),3,0.5));   // bolhas finas subindo junto ao jato
          c+=vec3(0.45,0.66,0.72)*bol*col*J*0.5;
          float linha=cheia ? 0.0 : 1.0-smoothstep(0.0,0.10+0.006*distance(cameraPosition,vW),prof); c=mix(c, vec3(0.62,0.88,0.94), linha*0.8);   // nível legível também de longe
          a=mix(0.80,0.96,k);
        }
        c=mix(c, vec3(0.93,0.97,1.0), clamp(esp,0.0,1.0)); a=max(a, clamp(esp,0.0,1.0)*0.95);
        gl_FragColor=vec4(c, a*uOp); }` });
  Object.defineProperty(mat, 'opacity', { get() { return mat.uniforms.uOp.value; }, set(v) { if (mat.uniforms) mat.uniforms.uOp.value = v; }, configurable: true });
  return mat;
}
function materialJato(m) {
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uT: uTempo, uG0: { value: m.g0 ?? 0 }, uOp: { value: 1 }, uModo: { value: m.modo ?? 0 }, uLv: { value: new THREE.Vector4(...(m.nivel || [9, 10, 0, 0])) },
      uJato: { value: new THREE.Vector3(...(m.jato || [1e9, 1e9, 1e9])) }, uRombo: { value: new THREE.Vector4(...(m.rombo || [0, 0, 7.4, 6.3])) } },
    vertexShader: `varying vec3 vP; varying vec3 vW; varying vec3 vNw; void main(){ vP=position; vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz;
      vNw=normalize(mat3(modelMatrix)*normal); gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader: RUIDO + NIVEL_GLSL + `uniform float uT,uG0,uOp; uniform int uModo; uniform vec3 uJato; uniform vec4 uLv,uRombo;
      varying vec3 vP; varying vec3 vW; varying vec3 vNw;
      void main(){
        float g=uT+uG0; float J=intensJato(g,uJato); vec3 V=normalize(cameraPosition-vW); float face=abs(dot(normalize(vNw),V));
        if(uModo==0){                                                      // JATO: estrias correndo no sentido do fluxo, aerado
          float L=nivelPorao(g,uLv); if(vP.z<L-0.03) discard;              // termina na superfície da água (que sobe)
          float s=max(uRombo.y-vP.y,0.0);                                   // distância percorrida desde o rombo
          float n=fbm(vec3(vP.x*1.8, s*0.45-g*4.5, vP.z*0.3),3,0.5), n2=fbm(vec3(vP.x*3.2, s*1.6-g*8.0, 1.7),2,0.5);   // estrias longas no sentido do fluxo
          float aer=smoothstep(0.3,4.5,s);
          vec3 c=mix(vec3(0.16,0.40,0.47), vec3(0.93,0.97,1.0), clamp(0.12+0.62*aer+0.35*n2,0.0,1.0))*(0.86+0.28*n);
          float a=(0.28+0.55*smoothstep(0.30,0.72,n+0.35*n2))*(0.30+0.70*sqrt(face))*smoothstep(L-0.03,L+0.30,vP.z)*(0.35+0.65*J)
                  *smoothstep(0.0,0.9,s);                                                                  // nasce transparente na boca do rombo
          gl_FragColor=vec4(c, a*uOp);
        } else {                                                           // RESPINGO: espuma branca agitada onde o jato bate
          float n=fbm(vec3(vP.x*2.6, vP.y*2.6, vP.z*2.2-g*4.5),3,0.5), n2=fbm(vec3(vP.x*5.0+g, vP.y*5.0, vP.z*4.0-g*7.0),2,0.5);
          float alt=clamp(vP.z/1.1,0.0,1.0);                                                               // densa na base, rala no topo
          float a=J*smoothstep(0.50+0.25*alt,0.85,n*0.7+n2*0.45)*(0.35+0.65*face)*(1.0-0.7*alt)*0.85;
          if(a<0.02) discard;
          gl_FragColor=vec4(vec3(0.93,0.97,1.0)*(0.9+0.15*n), clamp(a,0.0,0.92)*uOp);
        } }` });
  Object.defineProperty(mat, 'opacity', { get() { return mat.uniforms.uOp.value; }, set(v) { if (mat.uniforms) mat.uniforms.uOp.value = v; }, configurable: true });
  return mat;
}

// Ep. 02 · feixe de CALOR (energia transferida): tubo luminoso âmbar com ondas em V que andam do quente para o frio.
// Visível só entre p0 e p1 (fração do percurso), animados por curvas; borda suave pela incidência (sem contorno duro).
function materialCalor(m) {
  const U = { uCor: { value: new THREE.Vector3(...(m.cor || [1.0, 0.54, 0.07])) }, uOnda: { value: m.onda ?? 6 }, uVel: { value: m.vel ?? 0.6 },
    uForca: { value: m.forca ?? 1 }, uP0: { value: 0 }, uP1: { value: 1 }, uT: uTempo, uOp: { value: 1 } };
  if (m.curvas) matsCurvas.push({ U, curvas: m.curvas });
  return new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, uniforms: U,
    vertexShader: `attribute vec3 aGen; varying vec3 vG; varying vec3 vN; varying vec3 vV;
      void main(){ vG=aGen; vec4 w=modelMatrix*vec4(position,1.0); vN=normalize(mat3(modelMatrix)*normal); vV=normalize(cameraPosition-w.xyz); gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader: `uniform vec3 uCor; uniform float uOnda,uVel,uForca,uP0,uP1,uT,uOp; varying vec3 vG; varying vec3 vN; varying vec3 vV;
      void main(){ float s=vG.x; if(s<uP0 || s>uP1 || uForca<=0.001) discard;
        float bord=smoothstep(0.0,0.06,s-uP0)*smoothstep(0.0,0.04,uP1-s);
        float fac=abs(dot(normalize(vN),normalize(vV))); float trans=pow(fac,0.9);
        float ph=s*uOnda-uT*uVel-(1.0-fac)*0.45; float aa=clamp(1.0-fwidth(ph)*1.6,0.0,1.0);
        float f=fract(ph); float onda=mix(0.5, smoothstep(0.0,0.22,f)*(1.0-smoothstep(0.45,0.75,f)), aa);
        float a=bord*trans*(0.38+0.62*onda)*uForca*uOp; if(a<0.01) discard;
        gl_FragColor=vec4(uCor*(1.35+0.9*onda), clamp(a,0.0,0.92)); }` });
}

function materialRaio(m) {
  return new THREE.ShaderMaterial({ transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { tProf: { value: null }, uRes: { value: new THREE.Vector2(W, H) }, uNear: { value: 0.5 }, uFar: { value: 8000 },
      uForca: { value: m.forca ?? 0.3 }, uCor: { value: new THREE.Vector3(...(m.cor || [0.85, 0.97, 1.0])) }, uSigma: { value: sigma } },
    vertexShader: `attribute vec3 aGen; varying vec3 vG; varying float vZv; varying vec3 vW; void main(){ vG=aGen; vW=position; vec4 mv=viewMatrix*vec4(position,1.0); vZv=-mv.z; gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `uniform sampler2D tProf; uniform vec2 uRes; uniform float uNear,uFar,uForca; uniform vec3 uCor,uSigma; varying vec3 vG; varying float vZv; varying vec3 vW;
      float linear(float d){ float z=d*2.0-1.0; return 2.0*uNear*uFar/(uFar+uNear-z*(uFar-uNear)); }
      void main(){ if(linear(texture2D(tProf,gl_FragCoord.xy/uRes).x)<vZv) discard;
        float a=pow(vG.z,1.8)*pow(max(1.0-abs(vG.x*2.0-1.0),0.0),1.5)*uForca;
        gl_FragColor=vec4(uCor*a*exp(-uSigma*max(-vW.z,0.0)*0.6),1.0); }` });
}

// ------------------------------------------------------------------ geometria
// Oclusor (só profundidade) do corte ilustrativo: fica no MESMO plano da face lateral do mar cortado. Coplanar + textura de
// profundidade de precisão limitada = decisão pixel a pixel instável no teste 'zc < vZv − 0,05' da água → pontos em grade do mar
// sobre o interior do navio. Correção: o oclusor é desenhado 0,6 % mais perto da câmera (o vértice é aproximado ao longo do próprio
// raio de visão: a posição na tela não muda, só a profundidade), com folga que cresce com a distância como a precisão.
const matProfOcl = new THREE.ShaderMaterial({ colorWrite: false, side: THREE.DoubleSide,
  vertexShader: `void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); mv.xyz*=${OCL_K.toFixed(4)}; gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `void main(){ gl_FragColor=vec4(0.0); }` });
let tris = 0; const caixa = new THREE.Box3(); const matsAgua = [], matsRaio = [];
const SEM_SOMBRA = new Set(meta.sem_sombra || []);   // interiores fechados (porão): sem sol direto atravessando o corte ilustrativo
const ANIM = meta.animacao; const animados = {}; const SURG = meta.surgir || {}; const surgem = [];
const cenaOclusor = new THREE.Scene();   // só profundidade: impede a água de aparecer dentro do casco em cortes
function registrarAnim(mesh, m) {
  if (!m.objeto) return; mesh.matrixAutoUpdate = false;
  if (SURG[m.objeto]) { const sv = SURG[m.objeto]; surgem.push({ mesh, sv, Mrel: new THREE.Matrix4().fromArray(sv.M), op: mesh.material.opacity }); mesh.visible = false; }
  else (animados[m.objeto] ||= []).push(mesh);
}
const ONDAS = (meta.ondas || []).slice(0, 2); const uTempo = { value: 0 };
for (const m of meta.materiais.filter(m => m.tipo === 'agua')) {
  const b = new Float32Array(await (await fetch(CENA + m.arquivo)).arrayBuffer());
  for (let i = 0; i < b.length; i += 12) caixaAgua.expandByPoint(new THREE.Vector3(b[i], b[i + 1], b[i + 2]));
}
await Promise.all(meta.materiais.map(async (m) => {
  const buf = new Float32Array(await (await fetch(CENA + m.arquivo)).arrayBuffer());
  const n = buf.length / 12; const ib = new THREE.InterleavedBuffer(buf, 12);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.InterleavedBufferAttribute(ib, 3, 0)); g.setAttribute('normal', new THREE.InterleavedBufferAttribute(ib, 3, 3));
  g.setAttribute('aLocal', new THREE.InterleavedBufferAttribute(ib, 3, 6)); g.setAttribute('aGen', new THREE.InterleavedBufferAttribute(ib, 3, 9));
  tris += n / 3;
  if (OCULTAR.has(m.nome) || OCULTAR.has(m.tipo)) return;
  if (m.tipo === 'agua') { const mat = materialAgua(m); matsAgua.push(mat); const ma = new THREE.Mesh(g, mat); registrarAnim(ma, m); cenaTransp.add(ma); return; }
  if (m.tipo === 'espuma') { const mat = materialEspuma(m); matsRaio.push(mat); const e = new THREE.Mesh(g, mat); e.renderOrder = 4; registrarAnim(e, m); cenaTransp.add(e); return; }
  if (m.tipo === 'calor') { const mc = new THREE.Mesh(g, materialCalor(m)); mc.renderOrder = 8; registrarAnim(mc, m); scene.add(mc); return; }
  if (m.tipo === 'raio_luz') { const mat = materialRaio(m); matsRaio.push(mat); const r = new THREE.Mesh(g, mat); r.renderOrder = 2; cenaTransp.add(r); return; }
  if (m.tipo === 'alagado') { const ma = new THREE.Mesh(g, materialAlagado(m)); ma.renderOrder = 6; registrarAnim(ma, m); scene.add(ma); return; }
  if (m.tipo === 'jato') { const mj = new THREE.Mesh(g, materialJato(m)); mj.renderOrder = 7; registrarAnim(mj, m); scene.add(mj); return; }
  if (m.tipo === 'fantasma') { const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(...m.cor).multiplyScalar(m.brilho ?? 1), transparent: true, opacity: m.alfa ?? 0.35, depthWrite: false, side: THREE.DoubleSide }); if (FANT_OFF > 0) { mat.polygonOffset = true; mat.polygonOffsetFactor = -FANT_OFF; mat.polygonOffsetUnits = -4 * FANT_OFF; } const mf = new THREE.Mesh(g, mat); registrarAnim(mf, m); scene.add(mf); return; }
  if (m.tipo === 'brilho') { const mb = new THREE.Mesh(g, materialBrilho(m)); mb.renderOrder = 5; registrarAnim(mb, m); scene.add(mb); return; }
  if (m.tipo === 'oclusor') { const mo = new THREE.Mesh(g, matProfOcl); registrarAnim(mo, m); cenaOclusor.add(mo); return; }
  if (m.tipo === 'bolha') { const mat = new THREE.MeshPhysicalMaterial({ color: 0xf2fbff, transmission: 0, transparent: true, opacity: 0.55, roughness: 0.05, emissive: 0x9fd8ee, emissiveIntensity: 0.35 }); const mb = new THREE.Mesh(g, mat); mb.renderOrder = 3; registrarAnim(mb, m); cenaTransp.add(mb); return; }
  const mesh = new THREE.Mesh(g, criarMaterial(m)); registrarAnim(mesh, m);
  mesh.castShadow = m.tipo !== 'emissivo' && !/^(mar_longe|longe)/.test(m.chave || ''); mesh.receiveShadow = !SEM_SOMBRA.has(m.nome); scene.add(mesh);
  g.computeBoundingBox(); if (!/^(mar_longe|longe|chao|ceu)/.test(m.chave || '')) caixa.union(g.boundingBox);
}));

// ------------------------------------------------------------------ câmera idêntica e ajuste do mapa de sombras ao que ela vê
const c = meta.camera;
const camera = new THREE.PerspectiveCamera(c.fov, W / H, meta.perto ?? 0.5, meta.longe ?? 8000);   // Ep. 02: planos macro (perto = 1 cm) camera.up.set(...c.up);
const base = new THREE.Vector3(...c.pos), fwd = new THREE.Vector3(...c.dir);
function ajustarSombra() {
  // pontos do tronco de visão até 260 m, recortados pela caixa da cena; envolve-os em espaço de luz
  const pts = []; const inv = camera.projectionMatrixInverse, mw = camera.matrixWorld;
  for (const x of [-1, 1]) for (const y of [-1, 1]) for (const zf of [0.5, 260]) {
    const v = new THREE.Vector3(x, y, -1).applyMatrix4(inv).normalize(); const p = v.multiplyScalar(zf / Math.abs(v.z)).applyMatrix4(mw);
    pts.push(p.clamp(caixa.min.clone().addScalar(-20), caixa.max.clone().addScalar(20)));
  }
  const centro = new THREE.Vector3(); pts.forEach(p => centro.add(p)); centro.divideScalar(pts.length);
  sol.position.copy(centro).addScalar(0).addScaledVector(dirSol, -600); sol.target.position.copy(centro); sol.updateMatrixWorld(); sol.target.updateMatrixWorld();
  const cs = sol.shadow.camera;   // usa a MESMA matriz de vista que o three usa para a câmera de sombra
  cs.position.copy(sol.position); cs.lookAt(centro); cs.updateMatrixWorld();
  const vm = cs.matrixWorldInverse;
  const b = new THREE.Box3(); pts.forEach(p => b.expandByPoint(p.clone().applyMatrix4(vm)));
  const m = 8;
  cs.left = b.min.x - m; cs.right = b.max.x + m; cs.top = b.max.y + m; cs.bottom = b.min.y - m; cs.near = 1; cs.far = 1400; cs.updateProjectionMatrix();
}
function posicionar(i) {   // animação: câmera e objetos do quadro i; benchmark: deslocamento fixo por quadro
  if (ANIM) {
    const q = ANIM.quadros[Math.min(i, ANIM.quadros.length - 1)];
    camera.position.set(...q.camera.pos); camera.up.set(...q.camera.up); camera.fov = q.camera.fov;
    camera.lookAt(camera.position.clone().add(new THREE.Vector3(...q.camera.dir)));
    for (const [nome, arr] of Object.entries(q.objetos)) for (const ms of (animados[nome] || [])) { ms.matrix.fromArray(arr); ms.matrixWorldNeedsUpdate = true; }
    uTempo.value = q.t ?? i / ANIM.fps;   // tempo de cena exportado (câmera lenta) ou tempo do quadro
    for (const [k, arr] of Object.entries(CURVAS)) { if (UG[k]) UG[k].value = curva(arr, uTempo.value); }
    if (CURVAS.corte) planoCorte.constant = curva(CURVAS.corte, uTempo.value);
    for (const mc of matsCurvas) for (const [k, arr] of Object.entries(mc.curvas)) {
      const nome = { temp: 'uTempMat', p0: 'uP0', p1: 'uP1', forca: 'uForca' }[k] || k; if (mc.U[nome]) mc.U[nome].value = curva(arr, uTempo.value); }
    const t = uTempo.value, ease = (x) => { x = Math.min(Math.max(x, 0), 1); return x * x * (3 - 2 * x); };
    for (const s of surgem) {   // objetos que surgem/somem: deslocamento d·(1−k), escala k, opacidade dos fantasmas
      const sv = s.sv, k = ease((t - sv.t0) / (sv.dur || 0.4)), k1 = sv.t1 != null ? 1 - ease((t - sv.t1) / (sv.dur1 || 0.4)) : 1;
      s.mesh.visible = t >= sv.t0 && k1 > 0.001;
      if (!s.mesh.visible) continue;
      const M = new THREE.Matrix4(); if (sv.pai && q.objetos[sv.pai]) M.fromArray(q.objetos[sv.pai]);
      const d = sv.d || [0, 0, 0]; M.multiply(new THREE.Matrix4().makeTranslation(d[0] * (1 - k), d[1] * (1 - k), d[2] * (1 - k))).multiply(s.Mrel);
      if (sv.escala) { const e = Math.max(1e-3, sv.escala === 'z' ? 1 : Math.min(k, k1)); M.multiply(new THREE.Matrix4().makeScale(sv.escala === 'z' ? 1 : e, sv.escala === 'z' ? 1 : e, sv.escala === 'z' ? Math.max(1e-3, Math.min(k, k1)) : e)); }
      s.mesh.matrix.copy(M); s.mesh.matrixWorldNeedsUpdate = true;
      if (s.mesh.material.transparent) s.mesh.material.opacity = s.op * Math.min(k, k1);
    }
  } else {
    camera.position.copy(base).add(new THREE.Vector3(-0.8 * i, 0.5 * i, 0.1 * i));
    camera.lookAt(camera.position.clone().add(fwd));
  }
  camera.updateMatrixWorld(); camera.updateProjectionMatrix();
  if (!CACHE || i === 0 || ANIM) { ajustarSombra(); renderer.shadowMap.needsUpdate = true; }
}

// ------------------------------------------------------------------ passes
const rtProf = new THREE.WebGLRenderTarget(W, H, { depthTexture: new THREE.DepthTexture(W, H, THREE.UnsignedIntType) });
const matProf = new THREE.MeshBasicMaterial({ colorWrite: false });
class PassoTransp extends Pass {
  constructor() { super(); this.copia = new FullScreenQuad(new THREE.ShaderMaterial(CopyShader)); this.needsSwap = true; }
  render(r, escrita, leitura) {
    this.copia.material.uniforms.tDiffuse.value = leitura.texture;
    r.setRenderTarget(this.renderToScreen ? null : escrita); r.clear(); this.copia.render(r);
    for (const m of matsAgua) { m.uniforms.tCor.value = leitura.texture; m.uniforms.tProf.value = rtProf.depthTexture; }
    for (const m of matsRaio) m.uniforms.tProf.value = rtProf.depthTexture;
    const ac = r.autoClear; r.autoClear = false; r.clearDepth(); r.render(cenaTransp, camera); r.autoClear = ac;
  }
}
const rt = new THREE.WebGLRenderTarget(W, H, { samples: MSAA, type: THREE.HalfFloatType });
const composer = new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene, camera));
if (AO) { const ao = new GTAOPass(scene, camera, W, H); ao.updateGtaoMaterial({ radius: 2.5, distanceExponent: 1.5, thickness: 2.0, scale: 1.0, samples: AO_AMOSTRAS }); ao.blendIntensity = 0.9; composer.addPass(ao); }
if (cenaTransp.children.length) composer.addPass(new PassoTransp());
if (BLOOM > 0) composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), BLOOM, 0.4, 1.6));
composer.addPass(new OutputPass());
if (CACHE) renderer.shadowMap.autoUpdate = false;
const gl = renderer.getContext(); const px = new Uint8Array(4);

window.quadro = (i) => {
  posicionar(i); const t0 = performance.now();
  if (cenaTransp.children.length) { scene.overrideMaterial = matProf; const vis = ceu.visible; ceu.visible = false;
    renderer.setRenderTarget(rtProf); renderer.clear(); renderer.render(scene, camera); scene.overrideMaterial = null; ceu.visible = vis;
    if (cenaOclusor.children.length) { const ac = renderer.autoClear; renderer.autoClear = false; renderer.render(cenaOclusor, camera); renderer.autoClear = ac; } }
  composer.render(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return performance.now() - t0;
};
const ROT = meta.rotulos || [];
if (ROT.length) {
  await document.fonts.load('800 30px Montserrat');
  posicionar(0);   // a câmera precisa estar no lugar antes de projetar as âncoras
  const sv = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); sv.setAttribute('width', W); sv.setAttribute('height', H);
  Object.assign(sv.style, { position: 'fixed', left: 0, top: 0, pointerEvents: 'none' }); document.body.appendChild(sv);
  const fs = Math.round(40 * ESCALA), pad = Math.round(16 * ESCALA);
  for (const r of ROT) {
    const v = new THREE.Vector3(...r.ancora).project(camera); const ax = (v.x + 1) / 2 * W, ay = (1 - v.y) / 2 * H;
    const bx = ax + r.dx * W, by = ay + r.dy * H;
    const el = document.createElement('div'); el.textContent = r.texto;
    Object.assign(el.style, { position: 'fixed', font: `800 ${fs}px Montserrat, sans-serif`, color: '#F6F4EC', background: 'rgba(32,43,87,0.94)',
      padding: `${pad * 0.55}px ${pad}px`, borderRadius: `${fs}px`, whiteSpace: 'nowrap', borderBottom: `${Math.max(3, Math.round(5 * ESCALA))}px solid #F3B544`,
      boxShadow: '0 4px 14px rgba(0,0,0,0.35)', letterSpacing: '-0.2px' });
    document.body.appendChild(el);
    const w = el.offsetWidth, h = el.offsetHeight;
    let lx = r.dx >= 0 ? bx : bx - w; lx = Math.min(Math.max(lx, 0.04 * W), 0.96 * W - w);
    const ly = Math.min(Math.max(by - h / 2, 0.10 * H), 0.74 * H - h);
    el.style.left = lx + 'px'; el.style.top = ly + 'px';
    const ex = Math.min(Math.max(ax, lx), lx + w), ey = ly + h / 2;
    sv.insertAdjacentHTML('beforeend', `<line x1="${ax}" y1="${ay}" x2="${ex}" y2="${ey}" stroke="#F6F4EC" stroke-width="${Math.max(2, 4 * ESCALA)}" stroke-linecap="round"/>` +
      `<circle cx="${ax}" cy="${ay}" r="${9 * ESCALA}" fill="#F3B544" stroke="#202B57" stroke-width="${3 * ESCALA}"/>`);
  }
}
window.info = { W, H, tris, materiais: meta.materiais.length, ao: AO, aoAmostras: AO_AMOSTRAS, sombra: SOMBRA, smap: SMAP, cache: CACHE, msaa: MSAA };
window.nQuadros = () => (ANIM ? ANIM.quadros.length : 1);
window.quadro(0);
window.pronto = true;
