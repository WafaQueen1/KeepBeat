import './style.css';
import { renderNavigation, renderHeader } from './navigation.js';

// Context Retrieval
const docId = localStorage.getItem('doctor_id');
if (!docId) {
    window.location.href = '/login.html'; // Require auth
}

// Role-based redirection logic
const role = localStorage.getItem('doctor_role') || 'doctor';
const path = window.location.pathname;
const isDashboard = path === '/' || path === '/index.html';

if (path === '/admin.html' && role !== 'admin') {
    window.location.href = '/index.html';
} else if (isDashboard && role === 'admin') {
    window.location.href = '/admin.html';
}

const patientId = localStorage.getItem('selectedPatientId');

// Render Layout
if (path === '/admin.html') {
    renderHeader('Admin Panel');
} else if (path === '/patients.html') {
    renderHeader('Patient Management');
} else {
    renderHeader(); 
}
renderNavigation();

// --- Real-Time ECG Animation Logic ---
class ECGAnimator {
    constructor() {
        this.pathBg = document.getElementById('ecg-path-bg');
        this.pathMain = document.getElementById('ecg-path-main');
        this.bpm = 72;
        this.isFlatline = false;
        this.points = [];
        this.maxPoints = 100;
        this.xScale = 1000 / this.maxPoints;
        this.counter = 0;
        
        if (this.pathMain) {
            this.init();
            this.animate();
        }
    }

    init() {
        // Initialize with a flat line
        for (let i = 0; i <= this.maxPoints; i++) {
            this.points.push(50);
        }
    }

    setBPM(newBPM) {
        this.bpm = Math.max(30, Math.min(220, newBPM));
    }

    setFlatline(isFlatline) {
        this.isFlatline = isFlatline;
    }

    generateECGPoint() {
        if (this.isFlatline) {
            // Flatline with subtle static noise
            return 50 + (Math.random() - 0.5) * 1.5;
        }

        // Frequency changes based on BPM
        const pulseWidth = Math.floor(6000 / this.bpm);
        const cyclePosition = this.counter % pulseWidth;

        let y = 50;
        
        // P Wave
        if (cyclePosition > 5 && cyclePosition < 15) {
            y -= 5 * Math.sin((cyclePosition - 5) * Math.PI / 10);
        }
        // QRS Complex
        else if (cyclePosition >= 18 && cyclePosition <= 20) { // Q
            y += 5;
        }
        else if (cyclePosition > 20 && cyclePosition < 24) { // R
            y -= 40;
        }
        else if (cyclePosition >= 24 && cyclePosition <= 26) { // S
            y += 10;
        }
        // T Wave
        else if (cyclePosition > 40 && cyclePosition < 60) {
            y -= 8 * Math.sin((cyclePosition - 40) * Math.PI / 20);
        }

        // Add some noise
        y += (Math.random() - 0.5) * 1.5;
        return y;
    }

    updatePath() {
        const nextY = this.generateECGPoint();
        this.points.push(nextY);
        this.points.shift();
        this.counter++;

        let d = `M 0 ${this.points[0]}`;
        for (let i = 1; i < this.points.length; i++) {
            d += ` L ${i * this.xScale} ${this.points[i]}`;
        }
        
        this.pathMain.setAttribute('d', d);
        this.pathBg.setAttribute('d', d);
    }

    animate() {
        this.updatePath();
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize animator if on dashboard
let ecg;
if (isDashboard) {
    ecg = new ECGAnimator();
}

// --- Telemetry Polling ---
const API_URL = `http://127.0.0.1:8000/api/v1/telemetry/${patientId || 'PT_001'}?limit=5`;
const bpmElement = document.getElementById('bpm-value');

async function fetchTelemetry() {
    if (!patientId && isDashboard) return;
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Network response not ok');
        
        const data = await response.json();
        const signalWarning = document.getElementById('no-signal-warning');

        if (data && data.length > 0) {
            const latestPacemaker = data.find(item => item.sensor_type === 'pacemaker');
            if (latestPacemaker) {
                const val = Math.round(latestPacemaker.value);
                if (bpmElement) {
                    bpmElement.innerHTML = `${val}<span class="text-[0.6em] ml-1 font-medium opacity-80 text-white font-['Plus_Jakarta_Sans']">BPM</span>`;
                }
                if (ecg) {
                    ecg.setBPM(val);
                    ecg.setFlatline(false);
                }
                if (signalWarning) signalWarning.classList.add('hidden');
                return;
            }
        }
        
        // No data found -> Flatline
        if (ecg) ecg.setFlatline(true);
        if (signalWarning) signalWarning.classList.remove('hidden');
    } catch (error) {
        console.warn('Telemetry offline. Using flatline.');
        const signalWarning = document.getElementById('no-signal-warning');
        if (ecg) ecg.setFlatline(true);
        if (signalWarning) signalWarning.classList.remove('hidden');
    }
}

if (isDashboard) {
    setInterval(fetchTelemetry, 3000);
    fetchTelemetry();
}
