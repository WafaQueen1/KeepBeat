import * as THREE from 'three';

// Mount on the specific left container
const container = document.getElementById('canvas-bg');
if (!container) throw new Error("Canvas container not found!");

const scene = new THREE.Scene();

let width = container.clientWidth;
let height = container.clientHeight;

const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
camera.position.set(0, 0, 35); // Pull back to see the whole heart

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.insertBefore(renderer.domElement, container.firstChild);

// Heart Math - Rejection sampling for perfect 3D volume Heart
const particleCount = 4000;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);
const originalPositions = new Float32Array(particleCount * 3);

let idx = 0;
while (idx < particleCount) {
    const x = (Math.random() - 0.5) * 3;
    const y = (Math.random() - 0.5) * 3;
    const z = (Math.random() - 0.5) * 3;
    
    // Heart equation: (x^2 + 2.25*z^2 + y^2 - 1)^3 - x^2*y^3 - 0.1125*z^2*y^3 <= 0
    const xx = x*x, yy = y*y, zz = z*z;
    const a = (xx + 2.25 * zz + yy - 1.0);
    const val = (a * a * a) - (xx * yy * y) - (0.1125 * zz * yy * y);
    
    if (val <= 0.0) {
        // Valid point inside the heart volume! Scale it up.
        // Also shifting slightly down so it centers visually better
        const px = x * 8; 
        const py = (y * 8) + 2; 
        const pz = z * 8;

        positions[idx * 3] = px;
        positions[idx * 3 + 1] = py;
        positions[idx * 3 + 2] = pz;

        originalPositions[idx * 3] = px;
        originalPositions[idx * 3 + 1] = py;
        originalPositions[idx * 3 + 2] = pz;

        // Colors
        // Let's create a gradient from deep red to bright pink/purple
        // Based on the position
        const colorRatio = (y + 1.5) / 3.0; // normalize
        const c1 = new THREE.Color(0xb6171e); // deep primary red
        const c2 = new THREE.Color(0xda3433); // brighter red
        const c3 = new THREE.Color(0xffb3ac); // light pink
        
        let mix;
        if(colorRatio < 0.5) {
            mix = c1.clone().lerp(c2, colorRatio * 2);
        } else {
            mix = c2.clone().lerp(c3, (colorRatio - 0.5) * 2);
        }

        colors[idx * 3] = mix.r;
        colors[idx * 3 + 1] = mix.g;
        colors[idx * 3 + 2] = mix.b;

        idx++;
    }
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

// Custom glowing points material
const material = new THREE.PointsMaterial({
    size: 0.25,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
});

const heartParticles = new THREE.Points(geometry, material);
// Rotate slightly so it faces the user dynamically
heartParticles.rotation.x = 0;
scene.add(heartParticles);

// Inner Core Glow to make the heart feel alive
const coreGeo = new THREE.IcosahedronGeometry(6, 2);
const coreMat = new THREE.MeshBasicMaterial({
    color: 0xff0000,
    wireframe: true,
    transparent: true,
    opacity: 0.05,
    blending: THREE.AdditiveBlending
});
const coreMesh = new THREE.Mesh(coreGeo, coreMat);
coreMesh.position.y = 2;
scene.add(coreMesh);


// Background ambient particles (dust)
const bgGeo = new THREE.BufferGeometry();
const bgVerts = [];
for(let i=0; i<500; i++) {
    bgVerts.push(
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 40 - 20
    );
}
bgGeo.setAttribute('position', new THREE.Float32BufferAttribute(bgVerts, 3));
const bgMat = new THREE.PointsMaterial({ color: 0xffb3ac, size: 0.1, transparent: true, opacity: 0.3 });
const bgPoints = new THREE.Points(bgGeo, bgMat);
scene.add(bgPoints);

// Subtle ECG Line Background
const numEcgPoints = 200;
const ecgGeo = new THREE.BufferGeometry();
const ecgPos = new Float32Array(numEcgPoints * 3);
for(let i = 0; i < numEcgPoints; i++) {
    ecgPos[i*3] = (i / numEcgPoints) * 80 - 40; // Spanning X
    ecgPos[i*3+1] = -12; // Lower Y
    ecgPos[i*3+2] = -10; // Z depth
}
ecgGeo.setAttribute('position', new THREE.BufferAttribute(ecgPos, 3));
const ecgMat = new THREE.LineBasicMaterial({ color: 0xda3433, transparent: true, opacity: 0.4 });
const ecgLine = new THREE.Line(ecgGeo, ecgMat);
scene.add(ecgLine);

// Add some fog for depth fading to almost black
scene.fog = new THREE.FogExp2(0x050505, 0.02);

// Handle Resize
window.addEventListener('resize', () => {
    if(!container) return;
    width = container.clientWidth;
    height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});

// Mouse Interaction
let mouseX = 0;
let mouseY = 0;
let targetRotX = 0;
let targetRotY = 0;

document.addEventListener('mousemove', (event) => {
    mouseX = (event.clientX - window.innerWidth / 2);
    mouseY = (event.clientY - window.innerHeight / 2);
});

// Animation Loop
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    
    const time = clock.getElapsedTime();
    
    // Parallax mouse effect -> smooth dampening towards mouse target
    targetRotX = mouseY * 0.0005;
    targetRotY = mouseX * 0.0005;
    
    heartParticles.rotation.x += 0.05 * (targetRotX - heartParticles.rotation.x);
    heartParticles.rotation.y += 0.05 * ((targetRotY + 0.1) - heartParticles.rotation.y); // slight offset so heart is angled
    
    coreMesh.rotation.x = heartParticles.rotation.x;
    coreMesh.rotation.y = heartParticles.rotation.y;

    // Smooth continuous beating (approx 90 BPM)
    // Using mathematical exponentials creates perfectly smooth, organic pulses without any rigid stops
    const speed = 1.8;
    const beat1 = Math.pow(Math.max(0, Math.sin(time * speed)), 10);
    const beat2 = Math.pow(Math.max(0, Math.sin(time * speed - 0.4)), 8);
    const combined = beat1 * 0.15 + beat2 * 0.1;
    
    const pulseScale = 1.0 + combined;
    const pointDisplacement = combined * 2.0;
    
    // Apply scale to heart
    heartParticles.scale.set(pulseScale, pulseScale, pulseScale);
    coreMesh.scale.set(pulseScale, pulseScale, pulseScale);

    // Make the particles jitter slightly when beating to simulate pumping energy
    const posAttr = heartParticles.geometry.attributes.position;
    for (let i = 0; i < particleCount; i++) {
        const ox = originalPositions[i * 3];
        const oy = originalPositions[i * 3 + 1];
        const oz = originalPositions[i * 3 + 2];
        
        // Push particles slightly outward along their normal vector from center
        const len = Math.sqrt(ox*ox + oy*oy + oz*oz);
        if(len > 0) {
            // Organic wave running vertically
            const wave = Math.sin(oy * 0.5 + time * 3) * 0.1;
            const displacement = pointDisplacement + wave;
            
            posAttr.array[i * 3] = ox + (ox / len) * displacement;
            posAttr.array[i * 3 + 1] = oy + (oy / len) * displacement;
            posAttr.array[i * 3 + 2] = oz + (oz / len) * displacement;
        }
    }
    posAttr.needsUpdate = true;

    // Undulate the background dust slightly
    bgPoints.rotation.y = (time * 0.05);

    // Animate the ECG scanning line
    const ecgAttr = ecgLine.geometry.attributes.position;
    for(let i=0; i<numEcgPoints; i++) {
        const x = (i / numEcgPoints) * 80 - 40; // -40 to 40
        // Travel across wave
        const cursor = ((time * 25) % 80) - 40; 
        const dist = x - cursor;
        
        let y = -12; // Base line
        if (Math.abs(dist) < 1.0) {
            // QRS spike
            if (dist > -0.2 && dist < 0.2) y += 6.0; // R peak
            else if (dist > -0.5 && dist <= -0.2) y -= 2.0; // Q
            else if (dist >= 0.2 && dist < 0.5) y -= 2.5; // S
        } else if (Math.abs(dist + 2.5) < 1.0) {
            // T wave
            y += Math.sin((dist + 2.5) * Math.PI) * 1.5;
        } else if (Math.abs(dist - 2.0) < 0.6) {
            // P wave
            y += Math.sin((dist - 2.0) * Math.PI / 0.6) * 1.0;
        }
        
        ecgAttr.array[i*3+1] = y;
    }
    ecgAttr.needsUpdate = true;

    renderer.render(scene, camera);
}

animate();
