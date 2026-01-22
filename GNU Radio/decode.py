import socket
import binascii
from Crypto.Cipher import AES

def lora_decrypt(appskey, payload, devaddr, fcnt, direction=0):
    k = int((len(payload) - 1) / 16) + 1
    s_block = b""
    cipher = AES.new(appskey, AES.MODE_ECB)
    for i in range(1, k + 1):
        # Construction of Ai block (devaddr and fcnt are in Little Endian)
        a_i = bytes([0x01, 0x00, 0x00, 0x00, 0x00, direction]) + \
              devaddr + \
              fcnt.to_bytes(4, byteorder='little') + \
              bytes([0x00, i])
        s_block += cipher.encrypt(a_i)
    return bytes([payload[i] ^ s_block[i] for i in range(len(payload))])

# --- DATA FROM THE IMAGE ---
# ChirpStack AppSKey (MSB)
APPSKEY = binascii.unhexlify("09b21596973f2cd8a0f8a5169be47784")

# ChirpStack Device Address (018a36d6 in MSB) -> AES requires Little Endian
DEVADDR = binascii.unhexlify("018a36d6")[::-1] 

UDP_PORT = 40868
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', UDP_PORT))

print(f"Listening on port {UDP_PORT} with new OTAA keys...")

while True:
    data, addr = sock.recvfrom(1024)
    start_idx = data.find(b'\x40')
    if start_idx == -1: 
        continue
    
    clean_data = data[start_idx:].rstrip(b'\x00')
    fcnt = int.from_bytes(clean_data[6:8], byteorder='little')
    payload = clean_data[9:-4]
    
    if len(payload) > 0:
        decrypted = lora_decrypt(APPSKEY, payload, DEVADDR, fcnt)
        print(f"\n[FCnt: {fcnt}]")
        try:
            print(f"DECODED: {decrypted.decode('ascii')}")
        except:
            print(f"HEX: {decrypted.hex()}")
