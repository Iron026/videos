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

const P = new URLSearchParams(location.search);
const CENA = P.get('cena') || '../cena2_q3/';
const ESCALA = parseFloat(P.get('escala') || '0.5');
const AO = P.get('ao') !== '0';
const AO_AMOSTRAS = parseInt(P.get('aoamostras') || '16');
const SOMBRA = P.get('sombra') || 'pcf';
const SMAP = parseInt(P.get('smap') || '4096');
const CACHE = P.get('cache') === '1';
const ENV = parseFloat(P.get('env') || '1');
const MSAA = parseInt(P.get('msaa') || '4');
const meta = await (await fetch(CENA + 'cena.json')).json();
const W = Math.round(meta.camera.largura * ESCALA), H = Math.round(meta.camera.altura * ESCALA);
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
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
scene.environment = pm.fromScene(cenaEnv, 0.02).texture; scene.environmentIntensity = ENV;

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
  if (t === 'aco') { mat.metalness = 1.0; mat.roughness = m.rug ?? 0.32; }
  if (t === 'vidro') { mat.color.setRGB(...[28, 40, 58].map(v => Math.pow(v / 255, 2.2))); mat.roughness = 0.08; mat.metalness = 0.4; }
  if (t === 'concreto') { mat.roughness = 0.88; }
  if (t === 'areia') { mat.roughness = 0.95; }
  if (t === 'conteiner') { mat.roughness = 0.55; }
  if (t === 'emissivo') { mat.emissive = cor.clone(); mat.emissiveIntensity = m.forca ?? 6; }
  const faixas = (m.faixas || []).slice(0, 6);
  const U = {
    uTipo: { value: ['pintura', 'aco', 'concreto', 'areia', 'conteiner', 'faixas_z', 'corte_ld', 'emissivo', 'vidro', 'generico'].indexOf(t) },
    uCorB: { value: cor }, uVar: { value: m.variacao ?? 0.06 }, uEsc: { value: m.escala_var ?? m.escala ?? 0.6 },
    uRugB: { value: m.rug ?? 0.5 }, uBump: { value: m.bump ?? 0 }, uEscov: { value: m.escovado ? 1 : 0 },
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
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec3 aLocal; attribute vec3 aGen; varying vec3 vW; varying vec3 vL; varying vec3 vNw;`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
      vW = (modelMatrix*vec4(position,1.0)).xyz; vL = aLocal; vNw = normalize(mat3(modelMatrix)*normal);`);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec3 vW; varying vec3 vL; varying vec3 vNw;
      uniform int uTipo, uNF; uniform vec3 uCorB; uniform float uVar, uEsc, uRugB, uBump, uEscov, uCaus, uEscCaus;
      uniform float uFZ[6]; uniform vec3 uFC[6]; uniform vec3 uAcima, uAbaixoC, uLinha; uniform float uZ0, uEsp;
      uniform float uSub, uSinSol; uniform vec3 uSigma, uAMin, uAMax;
      uniform float uCasca, uBc[64], uKc, uCalc, uTopoC, uEspC; uniform vec3 uCorC;
      ${RUIDO}
      float alturaRelevo(){
        if(uTipo==0 && uBump>0.0) return fbm(vL*18.0,6,0.5)*uBump*0.06;
        if(uTipo==1 && uEscov>0.5) return fbm(vec3(vL.x*12.0, vL.y*720.0, vL.z*720.0),3,0.5)*0.004;
        if(uTipo==2) return fbm(vW*9.0,6,0.5)*0.006;
        if(uTipo==3){ float d=fbm(vL*0.2,3,0.5)*6.0; return (0.5+0.5*sin(vL.x*0.9*6.2832+d))*0.035; }
        if(uTipo==4){ float w=fract(vL.x*3.6*20.0/6.2832); return abs(w*2.0-1.0)*0.02; }
        return 0.0; }
    `)
    .replace('#include <color_fragment>', `#include <color_fragment>
      { vec3 c = diffuseColor.rgb;
        if(uTipo==0 || uTipo==9){ float n=fbm(vL*uEsc,5,0.5); c*=mapear(n,0.0,1.0,1.0-uVar,1.0+uVar); }
        else if(uTipo==2){ float n=fbm(vW*uEsc,5,0.5); c=mix(uCorB*0.78,uCorB*1.08,mapear(n,0.3,0.75,0.0,1.0)); }
        else if(uTipo==3){ float n=fbm(vL*0.25,6,0.5); c=mix(uCorB*0.7,uCorB,n); }
        else if(uTipo==4){ float n=fbm(vL*1.5,6,0.5); c*=mapear(n,0.0,1.0,0.82,1.05); }
        else if(uTipo==5){ vec3 cf=uFC[uNF-1]; for(int i=uNF-2;i>=0;i--){ if(vL.z<uFZ[i]) cf=uFC[i]; }
                           c=cf*mapear(fbm(vL*0.08,6,0.5),0.0,1.0,0.9,1.06); }
        else if(uTipo==6){ c=(vW.z<uZ0)?uAbaixoC:uAcima; if(abs(vW.z-uZ0)<uEsp) c=uLinha;
          if(uCasca>0.5){ float zl=vW.z+uCalc; float f=clamp((zl-uKc)/(uTopoC-uKc),0.0,1.0)*63.0; int i0=int(floor(f)); int i1=min(i0+1,63);
            float bz=mix(uBc[i0],uBc[i1],fract(f)); float dcas=min(bz-abs(vW.y), zl-uKc);
            if(dcas<uEspC && zl<uTopoC-0.6) c=uCorC; } }
        diffuseColor.rgb=c; }`)
    .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
      if(uTipo==0) roughnessFactor=mapear(fbm(vL*uEsc,5,0.5),0.0,1.0,uRugB*0.8,min(1.0,uRugB*1.2));
      if(uTipo==1) roughnessFactor=mapear(fbm(vL*2.2,8,0.5),0.0,1.0,uRugB*0.65,uRugB*1.45);`)
    .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
      { float h=alturaRelevo()*exp(-length(vViewPosition)/45.0); if(h!=0.0){ vec3 sx=dFdx(-vViewPosition), sy=dFdy(-vViewPosition); vec3 r1=cross(sy,normal), r2=cross(normal,sx);
        float det=dot(sx,r1)*faceDirection; vec2 dh=vec2(dFdx(h),dFdy(h)); vec3 g=sign(det)*(dh.x*r1+dh.y*r2);
        normal=normalize(abs(det)*normal-g); } }`)
    .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
      if(uTipo==3 && uCaus>0.0 && vW.z<0.0 && vNw.z>0.4){ vec3 q=vW*vec3(1.0,1.0,0.3)*uEscCaus; q+=vec3(fbm(vW*1.6,2,0.5)-0.5)*0.45;
        float e=bordaVoronoi(q.xy+q.z*0.3); totalEmissiveRadiance+=vec3(1.0,0.98,0.9)*mapear(e,0.0,0.045,1.0,0.0)*uCaus*mapear(vNw.z,0.4,0.8,0.0,1.0); }`)
    .replace('#include <aomap_fragment>', `#include <aomap_fragment>
      // sob a água o céu só é visto por um cone estreito (e o casco o bloqueia): menos luz indireta
      if(uSub>0.5 && vW.z<0.0 && all(greaterThan(vW.xy,uAMin.xy+0.3)) && all(lessThan(vW.xy,uAMax.xy-0.3))){
        float k=mix(1.0,0.35,clamp(-vW.z/12.0,0.0,1.0)); reflectedLight.indirectDiffuse*=k; reflectedLight.indirectSpecular*=k; }`)
    .replace('#include <opaque_fragment>', `
      if(uSub>0.5 && vW.z<0.0 && all(greaterThan(vW.xy,uAMin.xy+0.3)) && all(lessThan(vW.xy,uAMax.xy-0.3))){ float d=-vW.z; outgoingLight*=exp(-uSigma*d*(1.0+1.0/max(uSinSol,0.2))*0.5); }
      #include <opaque_fragment>`);
  };
  mat.customProgramCacheKey = () => 'rt2_' + t + (coat > 0 ? 'c' : '');
  return mat;
}

function materialAgua(m) {
  return new THREE.ShaderMaterial({
    uniforms: Object.assign({ tCor: { value: null }, tProf: { value: null }, uRes: { value: new THREE.Vector2(W, H) },
      uNear: { value: 0.5 }, uFar: { value: 8000 }, uSigma: { value: sigma }, uSolDir: { value: dirSol.clone().negate() },
      uSolCor: { value: new THREE.Vector3(...s.cor).multiplyScalar(s.energia) }, uMarola: { value: m.marola ?? 0.3 }, uEscMar: { value: m.escala_marola ?? 0.3 }, uTempo, uNOndas: { value: ONDAS.length },
      uOndas: { value: [0, 1].map(k => ONDAS[k] ? new THREE.Vector3(ONDAS[k].x, ONDAS[k].y, ONDAS[k].t0) : new THREE.Vector3(0, 0, 1e9)) } }, uCeu),
    vertexShader: `varying vec3 vW; varying vec3 vN; varying float vZv; void main(){ vW=position; vN=normal; vec4 mv=viewMatrix*vec4(position,1.0); vZv=-mv.z; gl_Position=projectionMatrix*mv; }`,
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
        if(N.z<0.5) c=mix(c, vec3(0.003,0.016,0.040), smoothstep(4.0,95.0,prof)*0.88);   // face lateral do corte: mar profundo
        gl_FragColor=vec4(c,1.0);
      }` });
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
const matProfOcl = new THREE.MeshBasicMaterial({ colorWrite: false, side: THREE.DoubleSide });
let tris = 0; const caixa = new THREE.Box3(); const matsAgua = [], matsRaio = [];
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
  if (m.tipo === 'agua') { const mat = materialAgua(m); matsAgua.push(mat); const ma = new THREE.Mesh(g, mat); registrarAnim(ma, m); cenaTransp.add(ma); return; }
  if (m.tipo === 'raio_luz') { const mat = materialRaio(m); matsRaio.push(mat); const r = new THREE.Mesh(g, mat); r.renderOrder = 2; cenaTransp.add(r); return; }
  if (m.tipo === 'fantasma') { const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(...m.cor).multiplyScalar(m.brilho ?? 1), transparent: true, opacity: m.alfa ?? 0.35, depthWrite: false, side: THREE.DoubleSide }); const mf = new THREE.Mesh(g, mat); registrarAnim(mf, m); scene.add(mf); return; }
  if (m.tipo === 'oclusor') { const mo = new THREE.Mesh(g, matProfOcl); registrarAnim(mo, m); cenaOclusor.add(mo); return; }
  if (m.tipo === 'bolha') { const mat = new THREE.MeshPhysicalMaterial({ color: 0xf2fbff, transmission: 0, transparent: true, opacity: 0.55, roughness: 0.05, emissive: 0x9fd8ee, emissiveIntensity: 0.35 }); const mb = new THREE.Mesh(g, mat); mb.renderOrder = 3; registrarAnim(mb, m); cenaTransp.add(mb); return; }
  const mesh = new THREE.Mesh(g, criarMaterial(m)); registrarAnim(mesh, m);
  mesh.castShadow = m.tipo !== 'emissivo' && !/^(mar_longe|longe)/.test(m.chave || ''); mesh.receiveShadow = true; scene.add(mesh);
  g.computeBoundingBox(); if (!/^(mar_longe|longe|chao|ceu)/.test(m.chave || '')) caixa.union(g.boundingBox);
}));

// ------------------------------------------------------------------ câmera idêntica e ajuste do mapa de sombras ao que ela vê
const c = meta.camera;
const camera = new THREE.PerspectiveCamera(c.fov, W / H, 0.5, 8000); camera.up.set(...c.up);
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
