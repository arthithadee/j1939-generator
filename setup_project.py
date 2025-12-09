import os

# Define the project structure and file contents
project_name = "j1939_generator"

# --- File Contents ---

requirements_txt = """Flask==3.0.0
numpy==1.26.0
pandas==2.1.0
"""

j1939_db_py = """\"\"\"
J1939 Industrial Database
Extracted from VERC/SwiSys PGN/SPN Working List
\"\"\"

# PGN Definitions
PGNS = {
    61444: {
        "name": "Electronic Engine Controller 1 (EEC1)",
        "hex": "0x0CF00400",  # Priority 3, PGN F004, Source 00 (Engine)
        "cycle_time_ms": 20,
        "spns": [899, 4154, 512, 513, 190, 2432]
    },
    65265: {
        "name": "Cruise Control/Vehicle Speed (CCVS1)",
        "hex": "0x18FEF100",
        "cycle_time_ms": 100,
        "spns": [84] 
    },
    65266: {
        "name": "Fuel Economy (LFE)",
        "hex": "0x18FEF200",
        "cycle_time_ms": 100,
        "spns": [183, 184, 51]
    },
    65262: {
        "name": "Engine Temperature 1 (ET1)",
        "hex": "0x18FEEE00",
        "cycle_time_ms": 1000,
        "spns": [110, 175]
    },
    65263: {
        "name": "Engine Fluid Level/Pressure 1 (EFL/P1)",
        "hex": "0x18FEEF00",
        "cycle_time_ms": 500,
        "spns": [98, 100]
    }
}

# SPN Definitions (ID, Name, StartByte, BitLen, Res, Offset, Min, Max, Unit)
# StartByte is 0-indexed here for Python (Doc says 1-indexed)
SPNS = {
    # --- EEC1 ---
    899:  {"name": "Engine Torque Mode", "start_byte": 0, "start_bit": 0, "len": 4, "res": 1, "offset": 0, "min": 0, "max": 15, "unit": "mode"},
    4154: {"name": "Actual Eng % Torque High Res", "start_byte": 0, "start_bit": 4, "len": 4, "res": 0.125, "offset": 0, "min": 0, "max": 0.875, "unit": "%"},
    512:  {"name": "Driver Demand Eng % Torque", "start_byte": 1, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},
    513:  {"name": "Actual Eng % Torque", "start_byte": 2, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},
    190:  {"name": "Engine Speed", "start_byte": 3, "start_bit": 0, "len": 16, "res": 0.125, "offset": 0, "min": 0, "max": 8031.875, "unit": "rpm"},
    2432: {"name": "Engine Demand % Torque", "start_byte": 7, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},

    # --- CCVS1 ---
    84:   {"name": "Wheel-Based Vehicle Speed", "start_byte": 1, "start_bit": 0, "len": 16, "res": 0.00390625, "offset": 0, "min": 0, "max": 250.996, "unit": "km/h"},
    
    # --- LFE ---
    183:  {"name": "Engine Fuel Rate", "start_byte": 0, "start_bit": 0, "len": 16, "res": 0.05, "offset": 0, "min": 0, "max": 3212.75, "unit": "L/h"},
    184:  {"name": "Instantaneous Fuel Economy", "start_byte": 2, "start_bit": 0, "len": 16, "res": 0.001953125, "offset": 0, "min": 0, "max": 125.5, "unit": "km/L"},
    51:   {"name": "Engine Throttle Position", "start_byte": 6, "start_bit": 0, "len": 8, "res": 0.4, "offset": 0, "min": 0, "max": 100, "unit": "%"},

    # --- ET1 ---
    110:  {"name": "Engine Coolant Temperature", "start_byte": 0, "start_bit": 0, "len": 8, "res": 1, "offset": -40, "min": -40, "max": 210, "unit": "deg C"},
    175:  {"name": "Engine Oil Temperature", "start_byte": 2, "start_bit": 0, "len": 16, "res": 0.03125, "offset": -273, "min": -273, "max": 1735, "unit": "deg C"},

    # --- EFL/P1 ---
    98:   {"name": "Engine Oil Level", "start_byte": 2, "start_bit": 0, "len": 8, "res": 0.4, "offset": 0, "min": 0, "max": 100, "unit": "%"},
    100:  {"name": "Engine Oil Pressure", "start_byte": 3, "start_bit": 0, "len": 8, "res": 4, "offset": 0, "min": 0, "max": 1000, "unit": "kPa"},
}
"""

engine_py = """import numpy as np
import pandas as pd
import struct
from j1939_db import PGNS, SPNS

class J1939Engine:
    def __init__(self):
        pass

    def get_smart_pattern(self, spn_id, duration_sec, sample_rate_ms):
        \"\"\"
        Automatically selects the best pattern based on the SPN ID/Name.
        Returns a numpy array of values.
        \"\"\"
        spn = SPNS.get(spn_id)
        if not spn:
            return np.zeros(1)
            
        num_samples = int((duration_sec * 1000) / sample_rate_ms)
        # Handle case where duration is too short for rate
        if num_samples == 0: num_samples = 1
            
        t = np.linspace(0, duration_sec, num_samples)
        
        name = spn['name'].lower()
        
        # --- SMART LOGIC ---
        
        if "speed" in name and "engine" in name: 
            pattern = 600 + 1000 * np.sin(0.1 * t) + 200 * np.random.normal(0, 0.1, num_samples)
            pattern = np.clip(pattern, 600, 2500) 
            
        elif "vehicle speed" in name:
            pattern = 100 * (1 - np.exp(-0.1 * t)) 
            
        elif "throttle" in name or "demand" in name:
            pattern = 50 + 40 * np.sin(0.2 * t)
            pattern = np.clip(pattern, 0, 100)
            
        elif "temperature" in name:
            base_temp = 80 if "coolant" in name else 90
            pattern = base_temp + 10 * (1 - np.exp(-0.05 * t)) + np.random.normal(0, 0.2, num_samples)
            
        elif "pressure" in name:
            base_p = 300
            pattern = base_p + 100 * np.sin(0.1 * t)
            
        elif "level" in name:
            pattern = 100 - (0.5 * t) 
            
        else:
            mid = (spn['max'] - spn['min']) / 2
            amp = mid * 0.5
            pattern = mid + amp * np.sin(t)

        return np.clip(pattern, spn['min'], spn['max'])

    def pack_message(self, pgn_id, spn_values):
        \"\"\"
        Pack physical values into 8 bytes (64 bits) Little Endian
        \"\"\"
        data_int = 0
        
        target_spns = PGNS[pgn_id]['spns']
        
        for spn_id in target_spns:
            if spn_id not in spn_values:
                continue
                
            val = spn_values[spn_id]
            spec = SPNS[spn_id]
            
            # 1. Physical to Raw
            raw = int((val - spec['offset']) / spec['res'])
            
            # Mask to ensure it fits length
            mask = (1 << spec['len']) - 1
            raw = raw & mask
            
            # 2. Shift to position
            global_shift = (spec['start_byte'] * 8) + spec['start_bit']
            
            data_int |= (raw << global_shift)
            
        return data_int.to_bytes(8, byteorder='little')

    def generate_dataset(self, selected_pgns, duration_sec=10):
        messages = []
        
        for pgn_id in selected_pgns:
            pgn_def = PGNS[pgn_id]
            rate = pgn_def['cycle_time_ms']
            
            spn_data = {}
            for spn_id in pgn_def['spns']:
                spn_data[spn_id] = self.get_smart_pattern(spn_id, duration_sec, rate)
                
            num_samples = len(list(spn_data.values())[0])
            
            for i in range(num_samples):
                timestamp = i * rate
                
                current_values = {k: v[i] for k, v in spn_data.items()}
                
                payload_bytes = self.pack_message(pgn_id, current_values)
                payload_hex = " ".join([f"{b:02X}" for b in payload_bytes])
                
                msg = {
                    "time_ms": timestamp,
                    "pgn_dec": pgn_id,
                    "pgn_hex": pgn_def['hex'],
                    "dlc": 8,
                    "payload_hex": payload_hex,
                    "payload_bytes": payload_bytes
                }
                
                for spn_id, val in current_values.items():
                    msg[SPNS[spn_id]['name']] = val
                    
                messages.append(msg)
                
        df = pd.DataFrame(messages)
        if not df.empty:
            df = df.sort_values(by="time_ms")
        return df
"""

app_py = """from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import time
from engine import J1939Engine
from j1939_db import PGNS

app = Flask(__name__)
engine = J1939Engine()

@app.route('/')
def index():
    available_pgns = [{"id": k, "name": v['name']} for k, v in PGNS.items()]
    return render_template('index.html', pgns=available_pgns)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    selected_pgns = [int(x) for x in data.get('pgns', [])]
    file_format = data.get('format', 'csv')
    duration = int(data.get('duration', 10))

    if not selected_pgns:
        return jsonify({"error": "No PGN selected"}), 400

    df = engine.generate_dataset(selected_pgns, duration_sec=duration)
    
    if df.empty:
         return jsonify({"error": "No data generated"}), 400

    buffer = io.BytesIO()
    
    if file_format == 'csv':
        df.drop(columns=['payload_bytes'], inplace=True, errors='ignore')
        df.to_csv(buffer, index=False)
        mimetype = 'text/csv'
        fname = 'j1939_data.csv'

    elif file_format == 'trc':
        buffer.write(b";$FILEVERSION=1.1\\n")
        buffer.write(b";$STARTTIME=0\\n")
        buffer.write(b";   Message Number  Time(ms)   Type    ID     DLC  Data Bytes\\n")
        
        msg_num = 1
        for _, row in df.iterrows():
            can_id = row['pgn_hex'].replace("0x", "") 
            payload = row['payload_hex']
            line = f"{msg_num:>6} {row['time_ms']:>10.1f} Rx {can_id:>8} 8 {payload}\\n"
            buffer.write(line.encode('utf-8'))
            msg_num += 1
            
        mimetype = 'text/plain'
        fname = 'j1939_trace.trc'

    elif file_format == 'txt':
        for _, row in df.iterrows():
            header = f"{row['pgn_hex']}h\\n"
            payload = f"{row['payload_hex']}\\n"
            buffer.write(header.encode('utf-8'))
            buffer.write(payload.encode('utf-8'))
        
        mimetype = 'text/plain'
        fname = 'j1939_dump.txt'

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=fname,
        mimetype=mimetype
    )

if __name__ == '__main__':
    app.run(debug=True, port=3000)
"""

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J1939 Signal Generator</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .pgn-list { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; }
        .pgn-item { padding: 8px; border-bottom: 1px solid #eee; }
        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        select, input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { width: 100%; padding: 15px; background-color: #3498db; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
        button:hover { background-color: #2980b9; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ J1939 Signal Generator</h1>
        
        <label>Select PGNs (Signals are auto-included):</label>
        <div class="pgn-list">
            {% for pgn in pgns %}
            <div class="pgn-item">
                <input type="checkbox" id="pgn_{{ pgn.id }}" value="{{ pgn.id }}">
                <label for="pgn_{{ pgn.id }}" style="display:inline; font-weight:normal;">{{ pgn.name }} (PGN {{ pgn.id }})</label>
            </div>
            {% endfor %}
        </div>

        <div class="controls">
            <div>
                <label>Simulation Duration (seconds):</label>
                <input type="number" id="duration" value="10" min="1" max="600">
            </div>
            <div>
                <label>Export Format:</label>
                <select id="format">
                    <option value="csv">CSV (Excel Readable)</option>
                    <option value="trc">.TRC (Vector/Peak)</option>
                    <option value="txt">.TXT (Hex Dump)</option>
                </select>
            </div>
        </div>

        <button onclick="generateData()">🚀 Generate & Download</button>
    </div>

    <script src="/static/script.js"></script>
</body>
</html>
"""

script_js = """async function generateData() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const selectedPgns = Array.from(checkboxes).map(cb => cb.value);
    const format = document.getElementById('format').value;
    const duration = document.getElementById('duration').value;

    if (selectedPgns.length === 0) {
        alert("Please select at least one PGN!");
        return;
    }

    const button = document.querySelector('button');
    button.innerText = "Generating...";
    button.disabled = true;

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pgns: selectedPgns, format: format, duration: duration })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `j1939_dataset.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Generation failed. Server returned error.");
        }
    } catch (error) {
        console.error(error);
        alert("An error occurred while connecting to the server.");
    }

    button.innerText = "🚀 Generate & Download";
    button.disabled = false;
}
"""

# --- Creation Logic ---

# Create main directory
if not os.path.exists(project_name):
    os.makedirs(project_name)

# Create subdirectories
os.makedirs(os.path.join(project_name, "static"), exist_ok=True)
os.makedirs(os.path.join(project_name, "templates"), exist_ok=True)

# Function to write file
def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# Write all files
write_file(os.path.join(project_name, "requirements.txt"), requirements_txt)
write_file(os.path.join(project_name, "j1939_db.py"), j1939_db_py)
write_file(os.path.join(project_name, "engine.py"), engine_py)
write_file(os.path.join(project_name, "app.py"), app_py)
write_file(os.path.join(project_name, "templates", "index.html"), index_html)
write_file(os.path.join(project_name, "static", "script.js"), script_js)

print("\\n✅ Project successfully created!")
print(f"👉 To run: cd {project_name} && python app.py")