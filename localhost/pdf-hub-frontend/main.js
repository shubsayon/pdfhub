// 3D Scene Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ 
    antialias: true, 
    alpha: true 
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.getElementById('canvas-container').appendChild(renderer.domElement);

// Floating Particles
const particlesGeometry = new THREE.BufferGeometry();
const particleCount = 2000;
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount * 3; i++) {
    positions[i] = (Math.random() - 0.5) * 2000;
    colors[i] = Math.random();
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const particleMaterial = new THREE.PointsMaterial({
    size: 0.5,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending
});

const particles = new THREE.Points(particlesGeometry, particleMaterial);
scene.add(particles);

// Floating Geometric Shapes
function createFloatingShape(geometry, color, x, y, z) {
    const material = new THREE.MeshPhongMaterial({
        color: color,
        transparent: true,
        opacity: 0.3,
        wireframe: true
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, y, z);
    return mesh;
}

// Add floating shapes
const shapes = [];
const geometries = [
    new THREE.BoxGeometry(30, 30, 30),
    new THREE.SphereGeometry(20, 16, 16),
    new THREE.TorusGeometry(15, 5, 16, 100),
    new THREE.IcosahedronGeometry(20, 1)
];

const colors_hex = [0x667eea, 0x764ba2, 0xf093fb, 0xf5576c];

for (let i = 0; i < 8; i++) {
    const geo = geometries[i % geometries.length];
    const col = colors_hex[i % colors_hex.length];
    const shape = createFloatingShape(
        geo, 
        col, 
        (Math.random() - 0.5) * 400,
        (Math.random() - 0.5) * 200,
        (Math.random() - 0.5) * 400 - 200
    );
    scene.add(shape);
    shapes.push(shape);
}

// Lights
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(1, 1, 1);
scene.add(directionalLight);

const backLight = new THREE.DirectionalLight(0x667eea, 0.5);
backLight.position.set(-1, -1, -1);
scene.add(backLight);

// Camera position
camera.position.z = 300;
camera.position.y = 50;

// Mouse tracking for parallax
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
    mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
});

// Animation
function animate() {
    requestAnimationFrame(animate);

    // Rotate particles
    particles.rotation.x += 0.0001;
    particles.rotation.y += 0.0002;

    // Animate shapes
    shapes.forEach((shape, index) => {
        shape.rotation.x += 0.003 * (index % 3 + 1);
        shape.rotation.y += 0.005 * (index % 2 + 1);
        shape.position.x += Math.sin(Date.now() * 0.0005 + index) * 0.02;
        shape.position.y += Math.cos(Date.now() * 0.0007 + index) * 0.02;
    });

    // Follow mouse
    camera.position.x += (mouseX * 20 - camera.position.x) * 0.01;
    camera.position.y += (-mouseY * 20 - camera.position.y) * 0.01;
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
}

animate();

// Resize handler
window.addEventListener('resize', () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
});