from flask import Flask, render_template, request, send_file, jsonify
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
        buffer.write(b";$FILEVERSION=1.1\n")
        buffer.write(b";$STARTTIME=0\n")
        buffer.write(b";   Message Number  Time(ms)   Type    ID     DLC  Data Bytes\n")
        
        msg_num = 1
        for _, row in df.iterrows():
            can_id = row['pgn_hex'].replace("0x", "") 
            payload = row['payload_hex']
            line = f"{msg_num:>6} {row['time_ms']:>10.1f} Rx {can_id:>8} 8 {payload}\n"
            buffer.write(line.encode('utf-8'))
            msg_num += 1
            
        mimetype = 'text/plain'
        fname = 'j1939_trace.trc'

    elif file_format == 'txt':
        for _, row in df.iterrows():
            header = f"{row['pgn_hex']}h\n"
            payload = f"{row['payload_hex']}\n"
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
