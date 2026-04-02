import './style.css';

// Context Retrieval
const docId = localStorage.getItem('doctor_id');
if (!docId) {
    window.location.href = '/login.html'; // Require auth
}

const docName = localStorage.getItem('doctor_name');
if (docName) {
    const docDisplay = document.getElementById('doctor-name-display');
    if (docDisplay) docDisplay.innerText = docName;
}

const patientId = localStorage.getItem('selectedPatientId');
const patientName = localStorage.getItem('selectedPatientName');
const medicalId = localStorage.getItem('selectedPatientMedicalId');

if (!patientId && window.location.pathname !== '/patients.html' && window.location.pathname !== '/login.html') {
    window.location.href = '/patients.html'; // Force select patient
}

if (patientName && medicalId) {
    const ptDisplay = document.getElementById('patient-name-display');
    if (ptDisplay) {
        ptDisplay.innerHTML = `Patient: ${patientName} <span class="text-on-surface-variant font-medium text-sm ml-2">ID: ${medicalId}</span>`;
    }
}

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
