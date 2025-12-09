import numpy as np
import pandas as pd
import struct
from j1939_db import PGNS, SPNS

class J1939Engine:
    def __init__(self):
        pass

    def get_smart_pattern(self, spn_id, duration_sec, sample_rate_ms):
        """
        Automatically selects the best pattern based on the SPN ID/Name.
        Returns a numpy array of values.
        """
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
        """
        Pack physical values into 8 bytes (64 bits) Little Endian
        """
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
