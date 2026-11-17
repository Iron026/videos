// Renderizador em tempo real (Three.js r170) da mesma cena exportada do Blender.
// Mesma câmera, geometria, cores, sol e céu. Técnicas: sombras suaves (PCF), IBL do céu (PMREM),
// oclusão de ambiente (GTAO), MSAA 4x e mapeamento Khronos PBR Neutral.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const P = new URLSearchParams(location.search);
const CENA = P.get('cena') || '../cena_q2/';
const ESCALA = parseFloat(P.get('escala') || '0.5');
const AO = P.get('ao') !== '0';
const meta = await (await fetch(CENA + 'cena.json')).json();
const W = Math.round(meta.camera.largura * ESCALA), H = Math.round(meta.camera.altura * ESCALA);

const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

// --- céu: mesmo degradê do Blender (rampa por z da direção de visão)
const ceu = meta.ceu.slice().sort((a, b) => a.pos - b.pos);
const N = 8; const pos = new Float32Array(N), cores = [];
for (let i = 0; i < N; i++) { const e = ceu[Math.min(i, ceu.length - 1)]; pos[i] = i < ceu.length ? e.pos : 2.0; cores.push(new THREE.Vector3(...e.cor)); }
const matCeu = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false,
  uniforms: { uPos: { value: pos }, uCor: { value: cores }, uN: { value: ceu.length }, uForca: { value: meta.ceu_forca } },
  vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); gl_Position.z = gl_Position.w; }`,
  fragmentShader: `uniform float uPos[8]; uniform vec3 uCor[8]; uniform int uN; uniform float uForca; varying vec3 vDir;
    void main(){ float t = clamp(vDir.z*0.5+0.5, 0.0, 1.0); vec3 c = uCor[0];
      for(int i=1;i<8;i++){ if(i>=uN) break; float a=uPos[i-1], b=uPos[i]; if(t>=a){ c = mix(uCor[i-1], uCor[i], clamp((t-a)/max(b-a,1e-4),0.0,1.0)); } }
      gl_FragColor = vec4(c*uForca, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
const esferaCeu = new THREE.Mesh(new THREE.SphereGeometry(5000, 48, 24), matCeu); scene.add(esferaCeu);
// IBL a partir do mesmo céu
const pm = new THREE.PMREMGenerator(renderer);
const cenaCeu = new THREE.Scene(); const matCeuEnv = matCeu.clone(); matCeuEnv.fragmentShader = matCeu.fragmentShader.replace('#include <tonemapping_fragment>', '').replace('#include <colorspace_fragment>', '');
cenaCeu.add(new THREE.Mesh(new THREE.SphereGeometry(100, 48, 24), matCeuEnv));
scene.environment = pm.fromScene(cenaCeu, 0.02).texture;

// --- sol
const s = meta.sol; const dir = new THREE.Vector3(...s.dir).normalize();
const sol = new THREE.DirectionalLight(new THREE.Color(...s.cor), s.energia);
const alvoSol = new THREE.Vector3(60, 0, 10);
sol.position.copy(alvoSol).addScaledVector(dir, -400); sol.target.position.copy(alvoSol);
sol.castShadow = true; sol.shadow.mapSize.set(4096, 4096);
Object.assign(sol.shadow.camera, { left: -170, right: 170, top: 170, bottom: -170, near: 10, far: 900 });
sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.6; sol.shadow.radius = 3;
scene.add(sol, sol.target);
for (const l of meta.luzes) if (l.tipo === 'POINT') { const p = new THREE.PointLight(new THREE.Color(...l.cor), l.energia / (4 * Math.PI), 0, 2); p.position.set(...l.pos); scene.add(p); }

// --- geometria por material
let tris = 0;
await Promise.all(meta.materiais.map(async (m) => {
  const buf = new Float32Array(await (await fetch(CENA + m.arquivo)).arrayBuffer());
  const n = buf.length / 6; const p = new Float32Array(n * 3), nn = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { p.set(buf.subarray(i * 6, i * 6 + 3), i * 3); nn.set(buf.subarray(i * 6 + 3, i * 6 + 6), i * 3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nn, 3));
  tris += n / 3;
  const emis = m.emis_forca > 0;
  const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(...m.cor), roughness: m.rug, metalness: m.metal,
    emissive: emis ? new THREE.Color(...m.emis) : 0x000000, emissiveIntensity: emis ? m.emis_forca : 0, side: THREE.DoubleSide });
  if (m.transm > 0.5) { mat.transparent = true; mat.opacity = 0.35; }
  const mesh = new THREE.Mesh(g, mat); mesh.castShadow = !emis; mesh.receiveShadow = true; scene.add(mesh);
}));

// --- câmera idêntica
const c = meta.camera;
const camera = new THREE.PerspectiveCamera(c.fov, W / H, 0.5, 8000);
camera.up.set(...c.up);
const base = new THREE.Vector3(...c.pos), fwd = new THREE.Vector3(...c.dir);
function posicionar(i) {   // mesmo deslocamento usado no benchmark do Cycles
  camera.position.copy(base).add(new THREE.Vector3(-0.8 * i, 0.5 * i, 0.1 * i));
  camera.lookAt(camera.position.clone().add(fwd)); camera.updateProjectionMatrix();
}
posicionar(0);

const rt = new THREE.WebGLRenderTarget(W, H, { samples: 4, type: THREE.HalfFloatType });
const composer = new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene, camera));
if (AO) { const ao = new GTAOPass(scene, camera, W, H); ao.updateGtaoMaterial({ radius: 2.5, distanceExponent: 1.5, thickness: 2.0, scale: 1.0, samples: 16 }); ao.blendIntensity = 0.9; composer.addPass(ao); }
composer.addPass(new OutputPass());
const gl = renderer.getContext(); const px = new Uint8Array(4);

window.quadro = (i) => {   // renderiza o quadro i e mede o tempo até a GPU terminar (readPixels força a sincronização)
  posicionar(i); const t0 = performance.now(); composer.render(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return performance.now() - t0;
};
window.info = { W, H, tris, materiais: meta.materiais.length, ao: AO };
window.quadro(0);
window.pronto = true;
