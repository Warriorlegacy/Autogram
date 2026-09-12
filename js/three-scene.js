/**
 * Autogram 3D WebGL Holographic Nebula & Quantum Core
 * Powered by Three.js — Theme-Reactive & Multi-Tier Spatial Depth
 */

(function () {
  const canvas = document.getElementById('webgl-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 46;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true, powerPreference: 'high-performance' });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // ── Theme Palette Mapping ─────────────────────────────────────────────
  const PALETTES = {
    'dark':        { primary: 0x00F0FF, secondary: 0x8A2BE2, tertiary: 0x00FFA3, opacity: 0.22 },
    'cyberpunk':   { primary: 0x00E5FF, secondary: 0xFFB300, tertiary: 0xFF0055, opacity: 0.28 },
    'neumorphic':  { primary: 0x6366F1, secondary: 0x38BDF8, tertiary: 0x818CF8, opacity: 0.20 },
    'swiss-light': { primary: 0x0050FF, secondary: 0x1E293B, tertiary: 0x0284C7, opacity: 0.16 },
    'bento-grid':  { primary: 0x6366F1, secondary: 0x10B981, tertiary: 0x8B5CF6, opacity: 0.22 },
    'light':       { primary: 0x0E6F77, secondary: 0x4338CA, tertiary: 0x059669, opacity: 0.18 }
  };

  function getActivePalette() {
    const curTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    return PALETTES[curTheme] || PALETTES['dark'];
  }

  let curPalette = getActivePalette();

  // ── 1. Outer Gyro Ring (Spatial Depth) ─────────────────────────────────
  const gyroGeo = new THREE.TorusGeometry(22, 0.25, 16, 120);
  const gyroMat = new THREE.MeshBasicMaterial({
    color: curPalette.secondary,
    wireframe: true,
    transparent: true,
    opacity: curPalette.opacity * 0.7
  });
  const gyroRing = new THREE.Mesh(gyroGeo, gyroMat);
  gyroRing.rotation.x = Math.PI / 4;
  scene.add(gyroRing);

  // ── 2. Holographic Quantum Torus Knot ──────────────────────────────────
  const knotGeo = new THREE.TorusKnotGeometry(12, 2.8, 128, 16);
  const knotMat = new THREE.MeshBasicMaterial({
    color: curPalette.primary,
    wireframe: true,
    transparent: true,
    opacity: curPalette.opacity
  });
  const coreKnot = new THREE.Mesh(knotGeo, knotMat);
  scene.add(coreKnot);

  // ── 3. Inner Quantum Nucleus (Nested Icosahedron) ──────────────────────
  const icoGeo = new THREE.IcosahedronGeometry(6, 1);
  const icoMat = new THREE.MeshBasicMaterial({
    color: curPalette.tertiary,
    wireframe: true,
    transparent: true,
    opacity: curPalette.opacity * 0.9
  });
  const innerNucleus = new THREE.Mesh(icoGeo, icoMat);
  scene.add(innerNucleus);

  // ── 4. Cyber Particle Nebula Field ────────────────────────────────────
  const isMobile = window.innerWidth < 768;
  const particleCount = isMobile ? 650 : 1400;
  const particleGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  const colPri = new THREE.Color(curPalette.primary);
  const colSec = new THREE.Color(curPalette.secondary);

  for (let i = 0; i < particleCount; i++) {
    const idx = i * 3;
    positions[idx] = (Math.random() - 0.5) * 150;
    positions[idx + 1] = (Math.random() - 0.5) * 150;
    positions[idx + 2] = (Math.random() - 0.5) * 150;

    const mixed = Math.random() > 0.4 ? colPri : colSec;
    colors[idx] = mixed.r;
    colors[idx + 1] = mixed.g;
    colors[idx + 2] = mixed.b;
  }

  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particleMat = new THREE.PointsMaterial({
    size: isMobile ? 0.9 : 0.8,
    vertexColors: true,
    transparent: true,
    opacity: 0.65
  });

  const particleSystem = new THREE.Points(particleGeo, particleMat);
  scene.add(particleSystem);

  // ── Dynamic Theme Mutation Observer ───────────────────────────────────
  function updateThemeColors() {
    curPalette = getActivePalette();
    const cP = new THREE.Color(curPalette.primary);
    const cS = new THREE.Color(curPalette.secondary);
    const cT = new THREE.Color(curPalette.tertiary);

    knotMat.color = cP;
    knotMat.opacity = curPalette.opacity;

    gyroMat.color = cS;
    gyroMat.opacity = curPalette.opacity * 0.7;

    icoMat.color = cT;
    icoMat.opacity = curPalette.opacity * 0.9;

    const colAttr = particleGeo.getAttribute('color');
    for (let i = 0; i < particleCount; i++) {
      const idx = i * 3;
      const m = Math.random() > 0.4 ? cP : cS;
      colAttr.array[idx] = m.r;
      colAttr.array[idx + 1] = m.g;
      colAttr.array[idx + 2] = m.b;
    }
    colAttr.needsUpdate = true;
  }

  const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach((m) => {
      if (m.attributeName === 'data-theme') {
        updateThemeColors();
      }
    });
  });
  themeObserver.observe(document.documentElement, { attributes: true });

  window.addEventListener('storage', (e) => {
    if (e.key === 'autogram_theme') updateThemeColors();
  });

  // ── Mouse Parallax with Damped Spring Interpolation ────────────────────
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.0006;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.0006;
  }, { passive: true });

  // Responsive Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }, { passive: true });

  // ── Animation Loop ────────────────────────────────────────────────────
  let clock = 0;
  function animate() {
    requestAnimationFrame(animate);
    clock += 0.015;

    targetX += (mouseX - targetX) * 0.05;
    targetY += (mouseY - targetY) * 0.05;

    // Torus knot rotation
    coreKnot.rotation.x += 0.0035;
    coreKnot.rotation.y += 0.005;

    // Inner nucleus counter-rotation with gentle breath scale
    innerNucleus.rotation.x -= 0.006;
    innerNucleus.rotation.z += 0.004;
    const pulse = 1 + Math.sin(clock * 1.5) * 0.05;
    innerNucleus.scale.set(pulse, pulse, pulse);

    // Outer gyro ring
    gyroRing.rotation.z += 0.003;
    gyroRing.rotation.y -= 0.002;

    // Nebula rotation
    particleSystem.rotation.y += 0.0006;
    particleSystem.rotation.x += 0.0002;

    // Camera damped parallax
    camera.position.x = targetX * 18;
    camera.position.y = -targetY * 18;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }

  animate();
})();

