import './style.css';
import mqtt from 'mqtt';

// Simulation Data Handlers
const bpmElement = document.getElementById('bpm-value');
let simulatedBpm = 72;

setInterval(() => {
  // Simulate natural heartbeat variations
  if(bpmElement) {
      simulatedBpm = 70 + Math.floor(Math.random() * 8) - 4;
      bpmElement.innerHTML = `${simulatedBpm}<span class="text-3xl ml-1 font-medium opacity-80 text-white">BPM</span>`;
  }
}, 1200);

// In the real system, you would connect to the WebSockets MQTT address:
// const client = mqtt.connect('ws://localhost:9001');
// client.on('connect', () => { client.subscribe('pacemaker/telemetry'); });
// client.on('message', (topic, message) => {
//    const data = JSON.parse(message.toString());
//    // update UI...
// });

