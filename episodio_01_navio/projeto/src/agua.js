// Oceano estilizado em formato de "diorama": superfície com ondas, face de corte volumétrica,
// leito marinho e céu. Toda a água é mascarada pelo sólido do casco (GLSL_CASCO).
import * as THREE from 'three';
import { GLSL_CASCO } from './casco.js';

export const PROFUNDIDADE = 34;
export const CORES = {
  azul: new THREE.Color('#202B57'), branco: new THREE.Color('#F6F4EC'), amarelo: new THREE.Color('#F3B544'),
};

// Uniforms compartilhados por todos os shaders do mundo.
export const U = {
  uTempo: { value: 0 },
  uNavio: { value: new THREE.Vector3() },        // posição do navio (origem local = quilha a meia-nau)
  uCorte: { value: new THREE.Vector4(0, 0, 1, 3000) }, // plano (n.xyz, d): mantém pontos com dot(n,p) <= d
  uMascaraCasco: { value: 1 },                   // 1 = água não entra no casco
  uSol: { value: new THREE.Vector3(0.45, 0.62, 0.64).normalize() },
  uOndas: { value: 1 },
  uNeblina: { value: new THREE.Color('#c4dbe8') },
  uCeuTopo: { value: new THREE.Color('#3f74b5') },
  uCalado: { value: 8 },
  uVisSub: { value: 0 },                         // 1 = modo diagrama: água mais transparente
};

// Ondas: soma de senoides direcionais (mesma função em JS e GLSL).
const ONDAS = [
  // [amplitude, comprimento, direção (graus), fase]
  [0.55, 92, 20, 0.0], [0.35, 51, -35, 1.3], [0.22, 31, 70, 2.1], [0.12, 17, 5, 4.0], [0.07, 9.5, -60, 0.7],
];
const G = 9.81;
export function alturaOnda(x, z, t, escala = 1) {
  let h = 0;
  for (const [A, L, dg, f] of ONDAS) {
    const k = 2 * Math.PI / L, w = Math.sqrt(G * k), a = dg * Math.PI / 180;
    h += A * Math.sin(k * (Math.cos(a) * x + Math.sin(a) * z) - w * t + f);
  }
  return h * escala;
}
const GLSL_ONDAS = (() => {
  let s = 'vec3 ondaInfo(vec2 p, float t){ float h=0.0; vec2 d=vec2(0.0);\n';
  for (const [A, L, dg, f] of ONDAS) {
    const k = 2 * Math.PI / L, w = Math.sqrt(G * k), a = dg * Math.PI / 180;
    const dx = Math.cos(a), dz = Math.sin(a);
    s += ` { float ph=${k.toFixed(5)}*(${dx.toFixed(5)}*p.x+${dz.toFixed(5)}*p.y)-${w.toFixed(5)}*t+${f.toFixed(3)};` +
      ` h+=${A.toFixed(3)}*sin(ph); d+=${(A * k).toFixed(5)}*cos(ph)*vec2(${dx.toFixed(5)},${dz.toFixed(5)}); }\n`;
  }
  s += ' return vec3(h,d)*uOndas; }\n';
  return s;
})();

const GLSL_COMUM = /* glsl */`
uniform float uTempo; uniform vec3 uNavio; uniform vec4 uCorte; uniform float uMascaraCasco; uniform vec3 uSol;
uniform float uOndas; uniform vec3 uNeblina; uniform vec3 uCeuTopo; uniform float uCalado; uniform float uVisSub;
${GLSL_CASCO}
${GLSL_ONDAS}
float hash12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float ruido(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(hash12(i),hash12(i+vec2(1,0)),f.x),mix(hash12(i+vec2(0,1)),hash12(i+vec2(1,1)),f.x),f.y); }
float fbm(vec2 p){ float s=0.0,a=0.5; for(int i=0;i<4;i++){ s+=a*ruido(p); p*=2.03; a*=0.5;} return s; }
bool cortado(vec3 p){ return dot(uCorte.xyz,p)>uCorte.w; }
vec3 corCeu(vec3 d){
  float y=d.y;
  vec3 c=mix(uNeblina, uCeuTopo, smoothstep(0.0,0.55,y));
  c=mix(c, vec3(0.0144,0.0242,0.0953), smoothstep(0.0,-0.06,y));
  if(y>0.0){ vec2 uv=d.xz/(y+0.06)*0.55; float nv=fbm(uv*1.3+vec2(uTempo*0.012,0.0))*0.65+fbm(uv*3.1)*0.35;
    float cl=smoothstep(0.50,0.80,nv)*smoothstep(0.015,0.16,y); c=mix(c,mix(vec3(0.80,0.84,0.90),vec3(1.0,0.98,0.95),smoothstep(0.5,0.9,nv)),cl*0.85); }
  float s=max(dot(d,uSol),0.0); c+=vec3(1.0,0.92,0.75)*(pow(s,600.0)*4.0+pow(s,12.0)*0.18);
  return c;
}
float causticas(vec2 p, float t){
  vec2 q=p*0.11; float c=0.0;
  c+=sin(q.x*2.1+t*0.9+sin(q.y*1.7+t*0.6)*1.8);
  c+=sin(q.y*2.4-t*0.8+sin(q.x*1.3-t*0.5)*1.6);
  return pow(clamp(0.5+0.25*c,0.0,1.0),6.0);
}
`;

// ---------- Céu ----------
export function criarCeu() {
  const mat = new THREE.ShaderMaterial({
    uniforms: U, side: THREE.BackSide, depthWrite: false,
    vertexShader: `varying vec3 vDir; void main(){ vDir=normalize(position); vec4 p=projectionMatrix*modelViewMatrix*vec4(position,1.0); gl_Position=p.xyww; }`,
    fragmentShader: GLSL_COMUM + `varying vec3 vDir; void main(){ gl_FragColor=vec4(corCeu(normalize(vDir)),1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(6000, 48, 24), mat);
  m.frustumCulled = false; m.renderOrder = -10;
  return m;
}

// ---------- Superfície ----------
function gradeRadial(n, raio) {
  const g = new THREE.PlaneGeometry(2, 2, n, n); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i);
    const f = (u) => Math.sign(u) * (0.1 * Math.abs(u) + 0.9 * u * u);
    p.setXYZ(i, f(x) * raio, 0, f(z) * raio);
  }
  return g;
}
export function criarSuperficie() {
  const mat = new THREE.ShaderMaterial({
    uniforms: U, transparent: true, depthWrite: true, side: THREE.DoubleSide,
    vertexShader: GLSL_COMUM + /* glsl */`
      varying vec3 vW; varying float vDist;
      void main(){
        vec3 w=(modelMatrix*vec4(position,1.0)).xyz;
        float amort=1.0-0.75*smoothstep(500.0,1500.0,length(w.xz));
        w.y=ondaInfo(w.xz,uTempo).x*amort;
        vW=w; vec4 mv=viewMatrix*vec4(w,1.0); vDist=-mv.z; gl_Position=projectionMatrix*mv;
      }`,
    fragmentShader: GLSL_COMUM + /* glsl */`
      varying vec3 vW; varying float vDist;
      void main(){
        if(cortado(vW)) discard;
        vec3 l=vW-uNavio;
        if(uMascaraCasco>0.5 && dentroCasco(vec3(l.x,clamp(l.y,quilhaG(l.x)+0.02,PONTAL-0.02),l.z),0.0)) discard;
        if(!gl_FrontFacing){ float dd=clamp(length(cameraPosition-vW)/220.0,0.0,1.0);
          gl_FragColor=vec4(mix(vec3(0.30,0.70,0.82),vec3(0.05,0.20,0.32),dd),0.28);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
          return; }
        vec3 oi=ondaInfo(vW.xz,uTempo);
        // micro-ondulações
        vec2 q=vW.xz*0.35+vec2(uTempo*0.35,uTempo*0.2);
        float e=0.15; float r0=fbm(q); vec2 dr=vec2(fbm(q+vec2(e,0.0))-r0, fbm(q+vec2(0.0,e))-r0)/e;
        float perto=1.0-smoothstep(150.0,700.0,vDist); vec3 n=normalize(vec3(-oi.y-dr.x*0.10*perto, 1.0, -oi.z-dr.y*0.10*perto));
        vec3 v=normalize(cameraPosition-vW);
        float fres=0.02+0.98*pow(1.0-max(dot(n,v),0.0),5.0);
        vec3 refl=corCeu(reflect(-v,n));
        vec3 profundo=vec3(0.035,0.12,0.24), raso=vec3(0.07,0.36,0.50);
        vec3 corpo=mix(profundo,raso,0.35+0.45*clamp(oi.x*0.6+0.4,0.0,1.0))*(0.55+0.45*max(dot(n,uSol),0.0));
        vec3 c=mix(corpo,refl,clamp(fres,0.0,1.0)*0.85);
        vec3 hv=normalize(uSol+v); c+=vec3(1.0,0.95,0.85)*pow(max(dot(n,hv),0.0),420.0)*3.0;
        // espuma junto ao casco (linha d'água) e nas cristas
        float b=meiaBocaG(l.x,clamp(l.y,0.0,PONTAL));
        float dist=abs(l.z)-b; float naLinha=(l.x>POPA-3.0&&l.x<PROA+3.0)?1.0:0.0;
        float esp=naLinha*(1.0-smoothstep(0.0,3.2,dist))*smoothstep(0.35,0.75,fbm(vW.xz*0.6+uTempo*0.5)+0.25);
        esp+=smoothstep(0.62,0.95,oi.x)*smoothstep(0.55,0.8,fbm(vW.xz*0.25))*0.5;
        c=mix(c,vec3(0.93,0.96,0.97),clamp(esp,0.0,0.9));
        // brilho no limite do corte (aresta da fatia)
        float dc=uCorte.w-dot(uCorte.xyz,vW); c=mix(c,vec3(0.75,0.93,1.0),(1.0-smoothstep(0.0,0.8,dc))*0.6);
        float nevoa=smoothstep(900.0,2600.0,vDist)*0.85;
        c=mix(c,uNeblina*0.95,nevoa);
        gl_FragColor=vec4(c,1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const m = new THREE.Mesh(gradeRadial(360, 2200), mat);
  m.frustumCulled = false;
  return m;
}

// ---------- Face de corte (seção transversal da água) ----------
export function criarFaceCorte() {
  const g = new THREE.PlaneGeometry(1, 1, 500, 1);
  const mat = new THREE.ShaderMaterial({
    uniforms: U, transparent: true, depthWrite: false, side: THREE.DoubleSide,
    vertexShader: GLSL_COMUM + /* glsl */`
      varying vec3 vW;
      void main(){
        // posição ao longo da face: s em [-1,1] -> metros (mais densa no centro)
        float s=position.x*2.0; s=sign(s)*(0.15*abs(s)+0.85*s*s)*1400.0;
        vec3 n=normalize(vec3(uCorte.x,0.0,uCorte.z)); vec3 tg=vec3(-n.z,0.0,n.x);
        vec3 base=n*uCorte.w+tg*s;
        float topo=ondaInfo(base.xz,uTempo).x;
        float y=position.y>0.0? topo : -${PROFUNDIDADE.toFixed(1)};
        vW=vec3(base.x,y,base.z);
        gl_Position=projectionMatrix*viewMatrix*vec4(vW,1.0);
      }`,
    fragmentShader: GLSL_COMUM + /* glsl */`
      varying vec3 vW;
      void main(){
        vec3 l=vW-uNavio;
        if(uMascaraCasco>0.5 && dentroCasco(l,0.0)) discard;
        float topo=ondaInfo(vW.xz,uTempo).x;
        float prof=clamp((topo-vW.y)/${PROFUNDIDADE.toFixed(1)},0.0,1.0);
        vec3 raso=vec3(0.035,0.36,0.52), fundo=vec3(0.006,0.05,0.16);
        vec3 c=mix(raso,fundo,pow(prof,0.7));
        // raios de luz e cáusticas
        vec3 n=normalize(vec3(uCorte.x,0.0,uCorte.z)); float s=dot(vW,vec3(-n.z,0.0,n.x));
        float raios=pow(max(0.0,sin(s*0.09+uTempo*0.25+sin(s*0.023)*3.0)),6.0)*(1.0-prof)*0.35;
        c+=vec3(0.25,0.55,0.75)*raios;
        float a=mix(0.38,0.80,pow(prof,0.8))*(1.0-0.5*uVisSub);
        // menisco brilhante na superfície
        float m=1.0-smoothstep(0.0,0.45,topo-vW.y); c=mix(c,vec3(0.85,0.97,1.0),m*0.9); a=max(a,m*0.95);
        float lateral=smoothstep(900.0,1350.0,abs(s)); a*=1.0-lateral;
        gl_FragColor=vec4(c,a);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const m = new THREE.Mesh(g, mat);
  m.frustumCulled = false; m.renderOrder = 5;
  return m;
}

// ---------- Leito marinho + camada de solo na face ----------
export function criarLeito() {
  const grupo = new THREE.Group();
  const g = new THREE.PlaneGeometry(3000, 3000, 1, 1); g.rotateX(-Math.PI / 2); g.translate(0, -PROFUNDIDADE, 0);
  const mat = new THREE.MeshStandardMaterial({ color: '#c9b48a', roughness: 0.95 });
  aplicarSubaquatico(mat, { areia: true });
  const leito = new THREE.Mesh(g, mat); leito.receiveShadow = true; grupo.add(leito);
  // faixa de solo na face de corte
  const gs = new THREE.PlaneGeometry(1, 1, 200, 1);
  const ms = new THREE.ShaderMaterial({
    uniforms: U, side: THREE.DoubleSide,
    vertexShader: GLSL_COMUM + `varying vec3 vW; void main(){ float s=position.x*2.0; s=sign(s)*(0.15*abs(s)+0.85*s*s)*1400.0;
      vec3 n=normalize(vec3(uCorte.x,0.0,uCorte.z)); vec3 tg=vec3(-n.z,0.0,n.x); vec3 b=n*uCorte.w+tg*s;
      vW=vec3(b.x, position.y>0.0? -${PROFUNDIDADE.toFixed(1)} : -${(PROFUNDIDADE + 9).toFixed(1)}, b.z); gl_Position=projectionMatrix*viewMatrix*vec4(vW,1.0); }`,
    fragmentShader: GLSL_COMUM + `varying vec3 vW; void main(){ float d=-${PROFUNDIDADE.toFixed(1)}-vW.y; vec3 n=normalize(vec3(uCorte.x,0.0,uCorte.z));
      float s=dot(vW,vec3(-n.z,0.0,n.x)); float camadas=0.5+0.5*sin(d*2.2+fbm(vec2(s*0.05,d))*4.0);
      vec3 c=mix(vec3(0.20,0.15,0.09),vec3(0.07,0.05,0.04),smoothstep(0.0,9.0,d)); c*=0.85+0.15*camadas;
      c=mix(c,vec3(0.0144,0.0242,0.0953),smoothstep(5.0,9.0,d)*0.8);
      float lateral=smoothstep(900.0,1350.0,abs(s)); if(lateral>0.99) discard;
      gl_FragColor=vec4(mix(c,vec3(0.0144,0.0242,0.0953),lateral),1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
  });
  const solo = new THREE.Mesh(gs, ms); solo.frustumCulled = false; grupo.add(solo);
  return grupo;
}

// ---------- Tingimento subaquático para materiais padrão ----------
export function aplicarSubaquatico(mat, { areia = false, seco = false, tampa = null } = {}) {
  if (tampa) mat.side = THREE.DoubleSide;
  const tc = tampa ? new THREE.Color(tampa) : null;
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = 'varying vec3 vWS;\n' + sh.vertexShader.replace('#include <worldpos_vertex>', `#include <worldpos_vertex>
      { vec4 wp=vec4(transformed,1.0);
        #ifdef USE_INSTANCING
          wp=instanceMatrix*wp;
        #endif
        vWS=(modelMatrix*wp).xyz; }`);
    const capa = tc ? `if(!gl_FrontFacing && abs(dot(uCorte.xyz,vWS)-uCorte.w)<3.0){ gl_FragColor=linearToOutputTexel(vec4(${tc.r.toFixed(4)},${tc.g.toFixed(4)},${tc.b.toFixed(4)},1.0)); return; }` : '';
    sh.fragmentShader = 'varying vec3 vWS;\n' + GLSL_COMUM + sh.fragmentShader
      .replace('void main() {', `void main() {\n if(cortado(vWS)) discard;\n ${capa}`)
      .replace('#include <opaque_fragment>', `#include <opaque_fragment>
      {
        vec3 l=vWS-uNavio;
        float topo=ondaInfo(vWS.xz,uTempo).x;
        bool noPorao = ${seco ? 'true' : 'false'} || (uMascaraCasco>0.5 && dentroCasco(l,0.25));
        if(vWS.y<topo-0.05 && !noPorao){
          float prof=topo-vWS.y;
          float f=clamp(0.22+prof*0.016,0.0,0.72)*(1.0-0.45*uVisSub);
          vec3 agua=mix(vec3(0.045,0.20,0.30),vec3(0.02,0.045,0.12),clamp(prof/${PROFUNDIDADE.toFixed(1)},0.0,1.0));
          vec3 cor=gl_FragColor.rgb;
          cor+= vec3(0.45,0.75,0.9)*causticas(vWS.xz+vWS.y*0.3,uTempo)*${areia ? '0.45' : '0.2'}*(1.0-prof/${(PROFUNDIDADE + 6).toFixed(1)});
          gl_FragColor.rgb=mix(cor,agua,f);
        }
      }`);
  };
  mat.customProgramCacheKey = () => 'sub' + (areia ? 'A' : '') + (seco ? 'S' : '') + (tc ? tc.getHexString() : '');
  return mat;
}
