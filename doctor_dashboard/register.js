import * as THREE from 'three';

// Mount on the specific left container
const container = document.getElementById('canvas-bg');
if (!container) throw new Error("Canvas container not found!");

const scene = new THREE.Scene();

let width = container.clientWidth;
let height = container.clientHeight;

const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
camera.position.set(0, 0, 32); // Pull back

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.insertBefore(renderer.domElement, container.firstChild);

// Heart Math - Volumetric Heart (Increased particle count + depth)
const particleCount = 10000;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);
const originalPositions = new Float32Array(particleCount * 3);
const sizes = new Float32Array(particleCount);

let idx = 0;
while (idx < particleCount) {
    const x = (Math.random() - 0.5) * 3;
    const y = (Math.random() - 0.5) * 3;
    const z = (Math.random() - 0.5) * 3;
    
    // Heart equation
    const xx = x*x, yy = y*y, zz = z*z;
    const a = (xx + 2.25 * zz + yy - 1.0);
    const val = (a * a * a) - (xx * yy * y) - (0.1125 * zz * yy * y);
    
    if (val <= 0.0) {
        // Shift up/scale
        const px = x * 8; 
        const py = (y * 8) + 2; 
        const pz = z * 8;

        positions[idx * 3] = px;
        positions[idx * 3 + 1] = py;
        positions[idx * 3 + 2] = pz;

        originalPositions[idx * 3] = px;
        originalPositions[idx * 3 + 1] = py;
        originalPositions[idx * 3 + 2] = pz;

        // Depth-based color for 3D feel
        const normalizedZ = (pz + 8) / 16.0; // 0 (back) to 1 (front)
        
        // Deep medical red with intense glowing core
        const backColor = new THREE.Color(0x3a0005); // Very dark red
        const midColor = new THREE.Color(0xb6171e); // Primary red
        const coreColor = new THREE.Color(0xff4a53); // Bright red-pink

        let mix;
        if(normalizedZ < 0.5) {
            mix = backColor.clone().lerp(midColor, normalizedZ * 2.0);
        } else {
            mix = midColor.clone().lerp(coreColor, (normalizedZ - 0.5) * 2.0);
        }

        colors[idx * 3] = mix.r;
        colors[idx * 3 + 1] = mix.g;
        colors[idx * 3 + 2] = mix.b;
        
        // Particles closer to front or center are slightly larger for volume
        sizes[idx] = (Math.random() * 0.4 + 0.1) * (0.5 + normalizedZ);

        idx++;
    }
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

// Custom standard material
const material = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.12,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
});

const heartParticles = new THREE.Points(geometry, material);
scene.add(heartParticles);

// Advanced glowing core
const coreGeo = new THREE.SphereGeometry(4, 32, 32);
const coreMat = new THREE.MeshBasicMaterial({
    color: 0xda3433,
    transparent: true,
    opacity: 0.1,
    blending: THREE.AdditiveBlending,
    depthWrite: false
});
const coreMesh = new THREE.Mesh(coreGeo, coreMat);
coreMesh.position.y = 2;
scene.add(coreMesh);

// Ambient data particles to symbolize AI
const bgGeo = new THREE.BufferGeometry();
const bgVerts = [];
for(let i=0; i<1500; i++) {
    bgVerts.push(
        (Math.random() - 0.5) * 160,       // Much wider X to cross onto the right side
        (Math.random() - 0.5) * 100,
        (Math.random() - 0.5) * 60 - 30
    );
}
bgGeo.setAttribute('position', new THREE.Float32BufferAttribute(bgVerts, 3));
// Slight blue AI tech feel
const bgMat = new THREE.PointsMaterial({ color: 0x4aa6ff, size: 0.12, transparent: true, opacity: 0.4, blending: THREE.AdditiveBlending }); 
const bgPoints = new THREE.Points(bgGeo, bgMat);
scene.add(bgPoints);

// Triple ECG Lines for deeper medical feel
const ecgLines = [];
const numEcgPoints = 350;
const createEcgLine = (yOffset, zOffset, colorHex, opacity, speedOffset) => {
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(numEcgPoints * 3);
    for(let i = 0; i < numEcgPoints; i++) pos[i*3] = (i / numEcgPoints) * 160 - 80; 
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: opacity, blending: THREE.AdditiveBlending });
    const line = new THREE.Line(geo, mat);
    scene.add(line);
    ecgLines.push({ geo, attr: geo.attributes.position, yOff: yOffset, zOff: zOffset, speedScale: speedOffset });
    return line;
};

createEcgLine(-10, -15, 0xda3433, 0.4, 1.0); // Primary red
createEcgLine(-14, -20, 0xb6171e, 0.2, 0.8); // Background slow red
createEcgLine(-6, -25, 0x4aa6ff, 0.15, 1.2); // Cyan AI tech line

scene.fog = new THREE.FogExp2(0x020202, 0.025);

// Handle Resize
window.addEventListener('resize', () => {
    if(!container) return;
    width = container.clientWidth; // We will handle full window resize in CSS
    height = window.innerHeight; // The canvas container is 100vh
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});

// Position the camera to the Right so the Heart appears on the Left of the widened screen
camera.position.set(13, 0, 32); 

// Animation Loop
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    
    const time = clock.getElapsedTime();
    
    // Slow cinematic rotation
    heartParticles.rotation.y = Math.sin(time * 0.1) * 0.2 + 0.2; // Keep it slightly angled
    heartParticles.rotation.x = Math.sin(time * 0.15) * 0.1;
    
    coreMesh.rotation.y = heartParticles.rotation.y;
    coreMesh.rotation.x = heartParticles.rotation.x;

    // Advanced Beating using layered sines
    const speed = 1.6;
    const beat1 = Math.pow(Math.max(0, Math.sin(time * speed)), 16);
    const beat2 = Math.pow(Math.max(0, Math.sin(time * speed - 0.3)), 10);
    const combined = beat1 * 0.2 + beat2 * 0.12;
    
    // Dynamic Scale
    const baseScale = 1.0;
    const pulseScale = baseScale + combined;
    heartParticles.scale.set(pulseScale, pulseScale, pulseScale);
    coreMesh.scale.set(pulseScale + combined * 2.0, pulseScale + combined * 2.0, pulseScale + combined * 2.0); // Core expands faster

    // Particle displacement (Volumetric Jitter)
    const posAttr = heartParticles.geometry.attributes.position;
    for (let i = 0; i < particleCount; i++) {
        const ox = originalPositions[i * 3];
        const oy = originalPositions[i * 3 + 1];
        const oz = originalPositions[i * 3 + 2];
        const len = Math.sqrt(ox*ox + oy*oy + oz*oz);
        if(len > 0) {
            // Complex wave moving through volume
            const wave = Math.sin(oy * 0.8 + oz * 0.5 + time * 3) * 0.15; 
            const displacement = (combined * 3.0) + wave;
            
            posAttr.array[i * 3] = ox + (ox / len) * displacement;
            posAttr.array[i * 3 + 1] = oy + (oy / len) * displacement;
            posAttr.array[i * 3 + 2] = oz + (oz / len) * displacement;
        }
    }
    posAttr.needsUpdate = true;

    // Dust streaming
    bgPoints.position.y = (time * 0.5) % 10;
    bgPoints.rotation.y = time * 0.02;

    // Update ECG lines (Expanded to 160 width)
    ecgLines.forEach(line => {
        const arr = line.attr.array;
        for(let i=0; i<numEcgPoints; i++) {
            const x = (i / numEcgPoints) * 160 - 80; 
            const cursor = ((time * 20 * line.speedScale) % 160) - 80; 
            const dist = x - cursor;
            
            let y = line.yOff;
            if (Math.abs(dist) < 1.0) {
                if (dist > -0.2 && dist < 0.2) y += 5.0; // R peak
                else if (dist > -0.5 && dist <= -0.2) y -= 1.5; // Q
                else if (dist >= 0.2 && dist < 0.5) y -= 2.0; // S
            } else if (Math.abs(dist + 2.5) < 1.0) {
                y += Math.sin((dist + 2.5) * Math.PI) * 1.2; // T
            } else if (Math.abs(dist - 2.0) < 0.6) {
                y += Math.sin((dist - 2.0) * Math.PI / 0.6) * 0.8; // P
            }
            
            arr[i*3+1] = y;
        }
        line.attr.needsUpdate = true;
    });

    renderer.render(scene, camera);
}

animate();
