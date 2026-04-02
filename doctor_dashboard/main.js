import './style.css';
import { renderNavigation, renderHeader } from './navigation.js';

// Context Retrieval
const docId = localStorage.getItem('doctor_id');
if (!docId) {
    window.location.href = '/login.html'; // Require auth
}

// Check role globally to prevent unauthorized admin access
const role = localStorage.getItem('doctor_role') || 'doctor';
if (window.location.pathname === '/admin.html' && role !== 'admin') {
    window.location.href = '/index.html';
} else if ((window.location.pathname === '/' || window.location.pathname === '/index.html') && role === 'admin') {
    window.location.href = '/admin.html';
}

const patientId = localStorage.getItem('selectedPatientId');

// Disappearing content fixes:
// Render navigation and header for current page
const isPatientRequired = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '/correlations.html' || window.location.pathname === '/ai-diagnostics.html';

if (isPatientRequired && !patientId) {
    window.location.href = '/patients.html'; // Force select patient
}

if (window.location.pathname === '/admin.html' || window.location.pathname === '/patients.html') {
    renderHeader(window.location.pathname === '/admin.html' ? 'Admin Panel' : 'Patient Management');
} else {
    renderHeader(); // Auto-generates based on current selected patient
}
renderNavigation();

// KeepBeat API Endpoint dynamically mapped

const API_URL = `http://127.0.0.1:8000/api/v1/telemetry/${patientId || 'PT_001'}?limit=10`;

const bpmElement = document.getElementById('bpm-value');
let latestBpm = 72;

// Function to fetch telemetry from the Cloud
async function fetchTelemetry() {
  if (!patientId) return; // Prevent raw query
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    
    if (data && data.length > 0) {
      // Find the most recent pacemaker reading
      const latestPacemaker = data.find(item => item.sensor_type === 'pacemaker');
      if (latestPacemaker) {
        latestBpm = Math.round(latestPacemaker.value);
        if (bpmElement) {
          bpmElement.innerHTML = `${latestBpm}<span class="text-[0.6em] ml-1 font-medium opacity-80 text-white">BPM</span>`;
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch telemetry, falling back to cached value.', error);
  }
}

// Poll every 3 seconds for updates
setInterval(fetchTelemetry, 3000);
fetchTelemetry(); // Initial fetch
