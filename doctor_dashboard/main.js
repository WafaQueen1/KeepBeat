import './style.css';

// KeepBeat API Endpoint
const API_URL = 'http://127.0.0.1:8000/api/v1/telemetry/PT_001?limit=10';

const bpmElement = document.getElementById('bpm-value');
let latestBpm = 72;

// Function to fetch telemetry from the Cloud
async function fetchTelemetry() {
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
