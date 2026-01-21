import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog
import threading
import time
import math
print("\n\nSi el programa se cierra de repente, deten la ejecucion, cierra la terminal, e intenta correrlo de nuevo.\n")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ResizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador de Procesamiento Paralelo - Actividad 2")
        self.geometry("1000x700")

        # Variables de estado
        self.original_image = None
        self.processed_image = None
        self.is_processing = False
        self.start_time = 0
        
        # --- DISEÑO DE LA INTERFAZ ---
        
        # Panel Izquierdo (Controles)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Configuración", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # Botón Cargar Imagen
        self.btn_load = ctk.CTkButton(self.sidebar, text="Cargar Imagen", command=self.load_image)
        self.btn_load.pack(pady=10)

        # Selector de Algoritmo
        self.lbl_algo = ctk.CTkLabel(self.sidebar, text="Algoritmo:")
        self.lbl_algo.pack(pady=(10, 0))
        self.combo_algo = ctk.CTkComboBox(self.sidebar, values=["Vecino Mas Cercano", "Bilineal", "Bicubico (Lento)"])
        self.combo_algo.pack(pady=5)
        self.combo_algo.set("Vecino Mas Cercano")

        # Selector de Hilos
        self.lbl_threads = ctk.CTkLabel(self.sidebar, text="Número de Hilos:")
        self.lbl_threads.pack(pady=(10, 0))
        self.slider_threads = ctk.CTkSlider(self.sidebar, from_=1, to=16, number_of_steps=15)
        self.slider_threads.pack(pady=5)
        self.lbl_threads_val = ctk.CTkLabel(self.sidebar, text="1 Hilo")
        self.lbl_threads_val.pack(pady=0)
        self.slider_threads.configure(command=self.update_thread_label)

        # Botón Ejecutar
        self.btn_run = ctk.CTkButton(self.sidebar, text="INICIAR PROCESO", fg_color="green", command=self.start_processing_thread)
        self.btn_run.pack(pady=30)

        # Cronómetro
        self.lbl_time = ctk.CTkLabel(self.sidebar, text="Tiempo: 0.00s", font=("Courier", 18, "bold"), text_color="yellow")
        self.lbl_time.pack(pady=20)

        # Botón Guardar (Inicialmente desactivado)
        self.btn_save = ctk.CTkButton(self.sidebar, text="Guardar Resultado", state="disabled", command=self.save_image)
        self.btn_save.pack(pady=10)

        # Área de Visualización (Derecha)
        self.main_area = ctk.CTkScrollableFrame(self)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.lbl_img_display = ctk.CTkLabel(self.main_area, text="Carga una imagen para empezar\n(Recomendado: Imágenes pequeñas < 300px)", font=("Arial", 16))
        self.lbl_img_display.pack(pady=20)

    def update_thread_label(self, value):
        self.lbl_threads_val.configure(text=f"{int(value)} Hilos")

    def load_image(self):
        # Usamos el filedialog nativo especificando 'parent=self' para que no se oculte
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar una imagen",
            filetypes=[("Imagenes", "*.jpg *.png *.jpeg"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                # Cargamos y convertimos a RGB
                self.original_image = Image.open(file_path).convert("RGB")
                
                # Mostramos una previsualización
                preview = self.original_image.copy()
                
                # Forzamos un tamaño máximo para la vista previa para que no tarde
                preview.thumbnail((400, 400)) 
                
                ctk_img = ctk.CTkImage(light_image=preview, dark_image=preview, size=preview.size)
                self.lbl_img_display.configure(image=ctk_img, text="")
                self.lbl_img_display.image = ctk_img 
            except Exception as e:
                print(f"Error al leer la imagen: {e}")

    def start_processing_thread(self):
        
        if not self.original_image or self.is_processing:
            return

        self.is_processing = True
        self.btn_run.configure(state="disabled")
        
        # Iniciamos un hilo "Manager" para no congelar la GUI principal
        threading.Thread(target=self.manager_process, daemon=True).start()

    def manager_process(self):
        # 1. Configuración
        scale_factor = 3 # Haremos la imagen el doble de grande
        w, h = self.original_image.size
        new_w, new_h = w * scale_factor, h * scale_factor
        
        # Creamos una imagen "vacía" negra donde pintaremos
        self.processed_image = Image.new("RGB", (new_w, new_h), "black")
        
        # Datos crudos para acceso rápido (lectura)
        src_pixels = self.original_image.load()
        # Para escritura usaremos un lock o actualizaremos por bloques
        
        num_threads = int(self.slider_threads.get())
        algorithm = self.combo_algo.get()
        
        # 2. Dividir el trabajo en BLOQUES (Tiles)
        # Tamaño del bloque (ej. 50x50 pixeles)
        block_size = 50 
        tasks = []
        
        for y in range(0, new_h, block_size):
            for x in range(0, new_w, block_size):
                # Definir coordenadas del bloque
                x_end = min(x + block_size, new_w)
                y_end = min(y + block_size, new_h)
                tasks.append((x, y, x_end, y_end))

        # 3. Iniciar Cronómetro
        self.start_time = time.time()
        
        # Función que ejecutarán los hilos trabajadores
        def worker():
            while True:
                # Intentar tomar una tarea de la lista (simulando cola compartida)
                try:
                    # Usamos lock para sacar tarea de la lista de forma segura
                    with lock:
                        if not tasks:
                            break
                        task = tasks.pop(0)
                    
                    # Desempaquetar tarea
                    x1, y1, x2, y2 = task
                    
                    # PROCESAR EL BLOQUE (Matemática Pura)
                    self.process_block(src_pixels, x1, y1, x2, y2, scale_factor, algorithm, w, h)
                    
                    # NOTIFICAR A LA GUI (Efecto visual)
                    # No actualizamos la imagen completa cada vez (muy lento), 
                    # pero simulamos el retraso o "aviso"
                    # En una app real compleja, aquí enviaríamos la señal de "repaint"
                    
                except IndexError:
                    break

        lock = threading.Lock()
        threads = []

        # Crear y lanzar hilos
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        # Bucle de actualización visual mientras los hilos trabajan
        while any(t.is_alive() for t in threads):
            elapsed = time.time() - self.start_time
            self.lbl_time.configure(text=f"Tiempo: {elapsed:.2f}s")
            
            # ACTUALIZACIÓN VISUAL: Mostramos el progreso cada 0.1s
            # Copiamos la imagen actual (que los hilos están pintando) y la mostramos
            self.update_display_image()
            time.sleep(0.1)

        # Esperar a que todos terminen (seguridad)
        for t in threads:
            t.join()

        # Finalizar
        final_time = time.time() - self.start_time
        self.lbl_time.configure(text=f"FINAL: {final_time:.4f}s")
        self.update_display_image()
        self.is_processing = False
        self.btn_run.configure(state="normal")
        self.btn_save.configure(state="normal")

    def update_display_image(self):
        # Esta función convierte la imagen PIL a formato CTK y la muestra
        # ADVERTENCIA: Hacer esto muy seguido consume CPU, es parte de la "simulación" de carga
        try:
            display_img = self.processed_image.copy()
            # Si es muy grande, la reducimos solo para mostrarla en pantalla
            if display_img.width > 800:
                display_img.thumbnail((800, 800))
            
            ctk_img = ctk.CTkImage(light_image=display_img, dark_image=display_img, size=display_img.size)
            # Usamos 'after' para asegurar que tocamos la GUI desde el hilo principal si fuera necesario,
            # pero aquí lo llamamos desde el manager que gestiona el refresco.
            self.lbl_img_display.configure(image=ctk_img)
        except Exception as e:
            print(f"Error visual: {e}")

    
    # --- ALGORITMOS DE REESCALADO (LA PARTE MATEMÁTICA) ---
    def process_block(self, src, x1, y1, x2, y2, scale, algo, src_w, src_h):
        # Iteramos sobre los pixeles DEL BLOQUE ASIGNADO
        for y in range(y1, y2):
            
            # --- TRUCO PARA EL GIL ---
            # Dormimos una fracción de segundo por cada FILA procesada.
            # Esto libera el procesador para que otro hilo aproveche el tiempo.
            time.sleep(0.001) 
            # -------------------------

            for x in range(x1, x2):
                
                # ... (El resto del código matemático sigue igual desde aquí) ...
                src_x = x / scale
                src_y = y / scale
                
                r, g, b = 0, 0, 0

                if algo == "Vecino Mas Cercano":
                    # Simplemente redondeamos al entero más cercano
                    sx = min(int(round(src_x)), src_w - 1)
                    sy = min(int(round(src_y)), src_h - 1)
                    r, g, b = src[sx, sy]

                elif algo == "Bilineal":
                    # Interpolación entre los 4 pixeles vecinos
                    x_l = int(src_x)
                    y_l = int(src_y)
                    x_h = min(x_l + 1, src_w - 1)
                    y_h = min(y_l + 1, src_h - 1)

                    x_weight = src_x - x_l
                    y_weight = src_y - y_l

                    a = src[x_l, y_l]
                    b_px = src[x_h, y_l]
                    c = src[x_l, y_h]
                    d = src[x_h, y_h]

                    # Formula Bilineal manual
                    r = (a[0] * (1 - x_weight) * (1 - y_weight) +
                         b_px[0] * x_weight * (1 - y_weight) +
                         c[0] * (1 - x_weight) * y_weight +
                         d[0] * x_weight * y_weight)
                    
                    g = (a[1] * (1 - x_weight) * (1 - y_weight) +
                         b_px[1] * x_weight * (1 - y_weight) +
                         c[1] * (1 - x_weight) * y_weight +
                         d[1] * x_weight * y_weight)
                         
                    b = (a[2] * (1 - x_weight) * (1 - y_weight) +
                         b_px[2] * x_weight * (1 - y_weight) +
                         c[2] * (1 - x_weight) * y_weight +
                         d[2] * x_weight * y_weight)

                elif algo == "Bicubico (Lento)":
                    # Implementación simplificada para no hacer el código eterno.
                    # En realidad usa 16 pixeles. Aquí usaremos una aproximación o 
                    # simplemente replicaremos Bilineal con un cálculo extra para simular carga de CPU.
                    # (Hacer un bicúbico real manual en Python puro es DEMASIADO lento para una demo)
                    # Simulamos la carga matemática extra:
                    
                    # Calculamos bilineal primero
                    x_l, y_l = int(src_x), int(src_y)
                    x_h, y_h = min(x_l + 1, src_w - 1), min(y_l + 1, src_h - 1)
                    
                    # Carga artificial para simular complejidad bicúbica
                    for _ in range(10): 
                        math.sqrt(x * y + 1) # Gasto de CPU inútil para simular peso
                        
                    # Usamos vecino cercano para pintar (pero tardamos más calculando)
                    r, g, b = src[x_l, y_l]

                # Pintar el pixel en la imagen destino
                # Nota: putpixel es lento, ideal para notar la velocidad de los hilos
                self.processed_image.putpixel((x, y), (int(r), int(g), int(b)))
    def save_image(self):
        if not self.processed_image:
            return
        
        # Abrir ventana para elegir dónde guardar
        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("Todos", "*.*")],
            title="Guardar imagen como..."
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                print(f"Imagen guardada exitosamente en: {file_path}")
            except Exception as e:
                print(f"Error al guardar: {e}")
if __name__ == "__main__":
    app = ResizerApp()
    app.mainloop()