import socket
import struct

def procesar_pixel_remoto(r, g, b):
    # --- AQUÍ VA LA LÓGICA DE PROCESAMIENTO ---
    # Para demostrar que el cluster funciona, haremos algo visible:
    # Aumentar brillo y cambiar tono para que se note qué hizo el servidor.
    
    new_r = min(255, int(r * 1.2))      # Aumentar rojo
    new_g = min(255, int(g * 0.9))      # Disminuir verde
    new_b = min(255, int(b + 50))       # Aumentar azul (brillo)
    
    return new_r, new_g, new_b

def iniciar_servidor():
    # '0.0.0.0' permite que te conectes desde otra PC (servera/serverb)
    HOST = '0.0.0.0'
    PORT = 65432      

    print(f"🚀 NODO WORKER ACTIVO en puerto {PORT}...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            with conn:
                # print(f"Conectado por {addr}") # Comentado para no llenar la terminal
                while True:
                    # Recibimos 3 bytes (R, G, B)
                    data = conn.recv(3)
                    if not data:
                        break
                    
                    # Desempaquetamos
                    try:
                        r, g, b = struct.unpack('BBB', data)
                        
                        # Procesamos
                        nr, ng, nb = procesar_pixel_remoto(r, g, b)
                        
                        # Respondemos
                        conn.sendall(struct.pack('BBB', nr, ng, nb))
                    except:
                        break

if __name__ == "__main__":
    iniciar_servidor()