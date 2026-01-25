import socket
import struct

def procesar_pixel_remoto(r, g, b):
    # Lógica simple para cambiar color y probar
    new_r = min(255, int(r * 1.2))
    new_g = min(255, int(g * 0.9))
    new_b = min(255, int(b + 50))
    return new_r, new_g, new_b

def iniciar_servidor():
    # IMPORTANTE: 0.0.0.0 para aceptar conexiones de fuera
    HOST = '0.0.0.0'
    PORT = 65432

    print(f"🚀 NODO WORKER ACTIVO en puerto {PORT}. Esperando al maestro...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita error de "puerto ocupado" al reiniciar
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"¡CONEXIÓN RECIBIDA! Cliente conectado desde: {addr}")
                pixels_procesados = 0
                
                while True:
                    data = conn.recv(3)
                    if not data:
                        print("Cliente desconectado.")
                        break
                    
                    try:
                        r, g, b = struct.unpack('BBB', data)
                        nr, ng, nb = procesar_pixel_remoto(r, g, b)
                        conn.sendall(struct.pack('BBB', nr, ng, nb))

                        # --- ESTO HACE QUE SE VEA ACTIVIDAD ---
                        pixels_procesados += 1
                        if pixels_procesados % 5000 == 0:
                            print(f"Procesando flujo de datos... {pixels_procesados} px completados", end='\r')
                            
                    except Exception as e:
                        print(f"Error procesando paquete: {e}")
                        break

if __name__ == "__main__":
    iniciar_servidor()