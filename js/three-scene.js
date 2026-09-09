/**
 * Autogram 3D WebGL Holographic Nebula & Quantum Core
 * Powered by Three.js
 */

(function () {
  const canvas = document.getElementById('webgl-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 45;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // 1. Holographic Quantum Torus Knot
  const knotGeo = new THREE.TorusKnotGeometry(12, 3.2, 120, 16);
  const knotMat = new THREE.MeshBasicMaterial({
    color: 0x00F0FF,
    wireframe: true,
    transparent: true,
    opacity: 0.18
  });
  const coreKnot = new THREE.Mesh(knotGeo, knotMat);
  scene.add(coreKnot);

  // Outer Violet Ring
  const ringGeo = new THREE.TorusGeometry(18, 0.4, 16, 100);
  const ringMat = new THREE.MeshBasicMaterial({
    color: 0x8A2BE2,
    wireframe: true,
    transparent: true,
    opacity: 0.25
  });
  const outerRing = new THREE.Mesh(ringGeo, ringMat);
  outerRing.rotation.x = Math.PI / 3;
  scene.add(outerRing);

  // 2. Cyber Particle Nebula Field
  const particleCount = 1200;
  const particleGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  const colorCyan = new THREE.Color(0x00F0FF);
  const colorViolet = new THREE.Color(0x8A2BE2);

  for (let i = 0; i < particleCount; i++) {
    const idx = i * 3;
    positions[idx] = (Math.random() - 0.5) * 140;
    positions[idx + 1] = (Math.random() - 0.5) * 140;
    positions[idx + 2] = (Math.random() - 0.5) * 140;

    const mixed = Math.random() > 0.5 ? colorCyan : colorViolet;
    colors[idx] = mixed.r;
    colors[idx + 1] = mixed.g;
    colors[idx + 2] = mixed.b;
  }

  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particleMat = new THREE.PointsMaterial({
    size: 0.75,
    vertexColors: true,
    transparent: true,
    opacity: 0.65
  });

  const particleSystem = new THREE.Points(particleGeo, particleMat);
  scene.add(particleSystem);

  // Mouse Parallax
  let mouseX = 0;
  let mouseY = 0;
  let targetX = 0;
  let targetY = 0;

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.0008;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.0008;
  });

  // Responsive Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation Loop
  function animate() {
    requestAnimationFrame(animate);

    targetX += (mouseX - targetX) * 0.05;
    targetY += (mouseY - targetY) * 0.05;

    coreKnot.rotation.x += 0.004;
    coreKnot.rotation.y += 0.006;

    outerRing.rotation.z += 0.005;
    outerRing.rotation.y += 0.003;

    particleSystem.rotation.y += 0.0008;

    camera.position.x = targetX * 15;
    camera.position.y = -targetY * 15;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }

  animate();
})();
