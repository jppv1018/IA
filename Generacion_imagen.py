
# Algoritmo Genético - Generación de Imágenes
# Juan Pablo Paz Vasco
# IA - Grupo 02

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import random
from PIL import Image, ImageDraw, ImageTk
import numpy as np


ANCHO_DISPLAY = 250
ALTO_DISPLAY  = 250


# Cada círculo tiene 7 datos: dónde está, qué tan grande es y de qué color.
# Un color en pantalla se forma con 3 números: rojo + verde + azul (0 a 255).
# El alfa es la transparencia (40=casi transparente, 160=bastante sólido).

class Circulo:

    def __init__(self, ancho_imagen, alto_imagen):
        self.ancho_imagen = ancho_imagen
        self.alto_imagen  = alto_imagen
        self.x     = random.randint(0, ancho_imagen)  # posición horizontal
        self.y     = random.randint(0, alto_imagen)   # posición vertical
        self.radio = random.randint(5, 40)            # tamaño
        self.rojo  = random.randint(0, 255)           # componente rojo del color
        self.verde = random.randint(0, 255)           # componente verde del color
        self.azul  = random.randint(0, 255)           # componente azul del color
        self.alfa  = random.randint(40, 160)          # transparencia

    def mutar(self, tasa_mutacion=0.15):
        # Crea una copia de este círculo y cambia LEVEMENTE algunos valores.
        copia = Circulo(self.ancho_imagen, self.alto_imagen)
        copia.x, copia.y, copia.radio = self.x, self.y, self.radio
        copia.rojo, copia.verde, copia.azul, copia.alfa = \
            self.rojo, self.verde, self.azul, self.alfa

        if random.random() < tasa_mutacion:
            copia.x     = max(0, min(self.ancho_imagen, self.x     + random.randint(-20, 20)))
        if random.random() < tasa_mutacion:
            copia.y     = max(0, min(self.alto_imagen,  self.y     + random.randint(-20, 20)))
        if random.random() < tasa_mutacion:
            copia.radio = max(3, min(60,  self.radio + random.randint(-8,  8)))
        if random.random() < tasa_mutacion:
            copia.rojo  = max(0, min(255, self.rojo  + random.randint(-40, 40)))
        if random.random() < tasa_mutacion:
            copia.verde = max(0, min(255, self.verde + random.randint(-40, 40)))
        if random.random() < tasa_mutacion:
            copia.azul  = max(0, min(255, self.azul  + random.randint(-40, 40)))
        if random.random() < tasa_mutacion:
            copia.alfa  = max(20, min(180, self.alfa + random.randint(-20, 20)))
        return copia


# El Cromosoma es una imagen completa formada por varios círculos.
# La aptitud dice qué tan parecido es a la imagen objetivo (menor = mejor).

class Individuo:

    def __init__(self, ancho_imagen, alto_imagen, cantidad_circulos=40):
        self.ancho_imagen = ancho_imagen
        self.alto_imagen  = alto_imagen
        # el cromosoma: lista de círculos al azar
        self.circulos = [Circulo(ancho_imagen, alto_imagen)
                         for _ in range(cantidad_circulos)]
        self.aptitud  = float('inf')   # empieza muy malo, se calcula después

    def dibujar(self):
        # Pinta todos los círculos sobre un lienzo blanco y devuelve la imagen.
        imagen_base = Image.new("RGB",  (self.ancho_imagen, self.alto_imagen), (255, 255, 255))
        capa        = Image.new("RGBA", (self.ancho_imagen, self.alto_imagen), (0, 0, 0, 0))
        pincel      = ImageDraw.Draw(capa)
        for c in self.circulos:
            pincel.ellipse(
                [c.x - c.radio, c.y - c.radio, c.x + c.radio, c.y + c.radio],
                fill=(c.rojo, c.verde, c.azul, c.alfa)
            )
        imagen_base.paste(capa, mask=capa)
        return imagen_base

    def calcular_aptitud(self, arreglo_objetivo):
        # Función objetivo: compara píxel a píxel esta imagen con la objetivo.
        # Calcula el error promedio entre cada píxel de ambas imágenes.
        imagen_dibujada  = self.dibujar()
        arreglo_dibujado = np.array(imagen_dibujada, dtype=np.float32)
        diferencia       = arreglo_dibujado - arreglo_objetivo
        self.aptitud     = float(np.mean(diferencia ** 2))
        return self.aptitud

    def crear_hijo(self, tasa_mutacion):
        # El hijo hereda todos los círculos del padre pero ligeramente cambiados.
        hijo          = Individuo(self.ancho_imagen, self.alto_imagen, len(self.circulos))
        hijo.circulos = [c.mutar(tasa_mutacion) for c in self.circulos]
    
        if random.random() < 0.03:
            i = random.randint(0, len(hijo.circulos) - 1)
            hijo.circulos[i] = Circulo(self.ancho_imagen, self.alto_imagen)
        return hijo


class AlgoritmoGenetico:

    def __init__(self, imagen_objetivo, cantidad_circulos, tam_poblacion, tasa_mutacion):
        self.imagen_objetivo   = imagen_objetivo.convert("RGB")
        self.arreglo_objetivo  = np.array(self.imagen_objetivo, dtype=np.float32)
        self.ancho, self.alto  = self.imagen_objetivo.size
        self.cantidad_circulos = cantidad_circulos
        self.tam_poblacion     = tam_poblacion
        self.tasa_mutacion     = tasa_mutacion
        self.generacion        = 0
        self.mejor_aptitud     = float('inf')
        self.historial_aptitud = []

        # Se crean varias imágenes al azar (población inicial)
        self.poblacion = [
            Individuo(self.ancho, self.alto, cantidad_circulos)
            for _ in range(tam_poblacion)
        ]

        for individuo in self.poblacion:
            individuo.calcular_aptitud(self.arreglo_objetivo)
        # ordenar de mejor a peor (menor error = mejor)
        self.poblacion.sort(key=lambda ind: ind.aptitud)
        self.mejor_individuo = self.poblacion[0]
        self.mejor_aptitud   = self.mejor_individuo.aptitud

    def paso(self):

        nueva_poblacion = [self.poblacion[0]]

        while len(nueva_poblacion) < self.tam_poblacion:
            # solo los mejores pueden ser padres
            mitad  = max(1, self.tam_poblacion // 2)
            padre  = random.choice(self.poblacion[:mitad])
            # el hijo es una versión mutada del padre
            hijo   = padre.crear_hijo(self.tasa_mutacion)
            hijo.calcular_aptitud(self.arreglo_objetivo)
            nueva_poblacion.append(hijo)

        self.poblacion = sorted(nueva_poblacion, key=lambda ind: ind.aptitud)
        self.generacion += 1

        if self.poblacion[0].aptitud < self.mejor_aptitud:
            self.mejor_aptitud   = self.poblacion[0].aptitud
            self.mejor_individuo = self.poblacion[0]

        self.historial_aptitud.append(self.mejor_aptitud)

# INTERFAZ GRÁFICA

class Aplicacion(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AG - Generador de Imágenes con Círculos")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        self.ag         = None
        self.corriendo  = False
        self.imagen_pil = None

        self._construir_interfaz()

        self.update_idletasks()
        ancho_ventana  = self.winfo_reqwidth()
        alto_ventana   = self.winfo_reqheight()
        x = (self.winfo_screenwidth()  // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana  // 2)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    # ── construcción ──

    def _construir_interfaz(self):
        tk.Label(self, text="Algoritmo Genético — Generación de Imágenes",
                 font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=(12, 4))
        tk.Label(self, text="Aproxima una imagen usando círculos de colores",
                 font=("Arial", 9), fg="gray", bg="#f0f0f0").pack(pady=(0, 10))

        # zona de imágenes
        marco_imgs = tk.Frame(self, bg="#f0f0f0")
        marco_imgs.pack(padx=16)
        tk.Label(marco_imgs, text="Imagen objetivo", font=("Arial", 9, "bold"),
                 bg="#f0f0f0").grid(row=0, column=0, pady=(0, 4))
        tk.Label(marco_imgs, text="Mejor individuo", font=("Arial", 9, "bold"),
                 bg="#f0f0f0").grid(row=0, column=1, pady=(0, 4))
        self.canvas_objetivo  = tk.Canvas(marco_imgs, width=ANCHO_DISPLAY, height=ALTO_DISPLAY,
                                          bg="white", relief="solid", bd=1)
        self.canvas_objetivo.grid(row=1, column=0, padx=(0, 10))
        self.canvas_resultado = tk.Canvas(marco_imgs, width=ANCHO_DISPLAY, height=ALTO_DISPLAY,
                                          bg="white", relief="solid", bd=1)
        self.canvas_resultado.grid(row=1, column=1)

        # estadísticas
        marco_stats = tk.Frame(self, bg="#f0f0f0")
        marco_stats.pack(pady=8)
        self.var_generacion = tk.StringVar(value="Generación: —")
        self.var_aptitud    = tk.StringVar(value="Aptitud: —")
        tk.Label(marco_stats, textvariable=self.var_generacion,
                 font=("Arial", 10), bg="#f0f0f0", width=20).pack(side="left", padx=10)
        tk.Label(marco_stats, textvariable=self.var_aptitud,
                 font=("Arial", 10), bg="#f0f0f0", width=25).pack(side="left", padx=10)

        # parámetros: solo círculos y mutación
        marco_params = tk.LabelFrame(self, text="Parámetros", bg="#f0f0f0",
                                     font=("Arial", 9, "bold"), padx=10, pady=6)
        marco_params.pack(padx=16, fill="x", pady=(0, 8))
        self.var_circulos = tk.IntVar(value=40)
        self.var_mutacion = tk.IntVar(value=12)
        fila = tk.Frame(marco_params, bg="#f0f0f0")
        fila.pack()
        self._slider(fila, "Círculos:",     self.var_circulos, 10, 100)
        self._slider(fila, "Mutación (%):", self.var_mutacion,  1,  40)

        # botones
        marco_botones = tk.Frame(self, bg="#f0f0f0")
        marco_botones.pack(pady=8)
        tk.Button(marco_botones, text="Cargar imagen", command=self._cargar_imagen,
                  width=14, bg="#4a90d9", fg="white", relief="flat",
                  font=("Arial", 9, "bold")).pack(side="left", padx=5)
        self.boton_iniciar = tk.Button(marco_botones, text="▶ Iniciar",
                  command=self._iniciar, width=10, bg="#27ae60", fg="white",
                  relief="flat", font=("Arial", 9, "bold"))
        self.boton_iniciar.pack(side="left", padx=5)
        self.boton_detener = tk.Button(marco_botones, text="■ Detener",
                  command=self._detener, width=10, bg="#e74c3c", fg="white",
                  relief="flat", font=("Arial", 9, "bold"), state="disabled")
        self.boton_detener.pack(side="left", padx=5)
        tk.Button(marco_botones, text="↺ Reiniciar", command=self._reiniciar,
                  width=10, bg="#e67e22", fg="white", relief="flat",
                  font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Button(marco_botones, text="💾 Guardar", command=self._guardar,
                  width=10, bg="#8e44ad", fg="white", relief="flat",
                  font=("Arial", 9, "bold")).pack(side="left", padx=5)

        # estado
        self.var_estado = tk.StringVar(value="Carga una imagen para comenzar.")
        tk.Label(self, textvariable=self.var_estado, font=("Arial", 8),
                 fg="gray", bg="#f0f0f0").pack(pady=(0, 8))

    def _slider(self, padre, etiqueta, variable, minimo, maximo):
        marco = tk.Frame(padre, bg="#f0f0f0")
        marco.pack(side="left", padx=8)
        tk.Label(marco, text=etiqueta, font=("Arial", 8), bg="#f0f0f0").pack(side="left")
        tk.Scale(marco, from_=minimo, to=maximo, orient="horizontal",
                 variable=variable, bg="#f0f0f0", length=110,
                 font=("Arial", 8), showvalue=True).pack(side="left")

    # ── acciones ───

    def _cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            img = Image.open(ruta).convert("RGB")
            img.thumbnail((150, 150), Image.LANCZOS)
            self.imagen_pil = img
            self._mostrar_imagen(self.canvas_objetivo, img)
            self.var_estado.set(f"Imagen cargada: {img.size[0]}×{img.size[1]} px")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def _iniciar(self):
        if self.imagen_pil is None:
            messagebox.showwarning("Aviso", "Primero carga una imagen objetivo.")
            return
        if self.ag is None:
            self.ag = AlgoritmoGenetico(
                imagen_objetivo   = self.imagen_pil,
                cantidad_circulos = self.var_circulos.get(),
                tam_poblacion     = 6,
                tasa_mutacion     = self.var_mutacion.get() / 100,
            )
        self.corriendo = True
        self.boton_iniciar.configure(state="disabled")
        self.boton_detener.configure(state="normal")
        threading.Thread(target=self._bucle_evolucion, daemon=True).start()
        self._bucle_actualizacion()

    def _detener(self):
        self.corriendo = False
        self.boton_iniciar.configure(state="normal")
        self.boton_detener.configure(state="disabled")
        gen = self.ag.generacion if self.ag else 0
        self.var_estado.set(f"Pausado en generación {gen}.")

    def _reiniciar(self):
        self.corriendo = False
        self.ag = None
        self.boton_iniciar.configure(state="normal")
        self.boton_detener.configure(state="disabled")
        self.canvas_resultado.delete("all")
        self.var_generacion.set("Generación: —")
        self.var_aptitud.set("Aptitud: —")
        self.var_estado.set("Reiniciado. Listo para comenzar.")

    def _guardar(self):
        if self.ag is None:
            messagebox.showwarning("Aviso", "No hay resultado todavía.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png")])
        if ruta:
            self.ag.mejor_individuo.dibujar().save(ruta)
            messagebox.showinfo("Guardado", f"Imagen guardada en:\n{ruta}")

    def _bucle_evolucion(self):
        while self.corriendo and self.ag:
            self.ag.paso()

    def _bucle_actualizacion(self):
        if not self.corriendo:
            return
        if self.ag:
            gen     = self.ag.generacion
            aptitud = self.ag.mejor_aptitud
            self.var_generacion.set(f"Generación: {gen}")
            self.var_aptitud.set(f"Aptitud: {aptitud:.1f}")
            self.var_estado.set(
                f"Evolucionando... gen {gen} | aptitud {aptitud:.2f} | "
                f"{self.ag.cantidad_circulos} círculos")
            self._mostrar_imagen(self.canvas_resultado, self.ag.mejor_individuo.dibujar())
        self.after(300, self._bucle_actualizacion)


    def _mostrar_imagen(self, canvas, imagen_pil):
        img_display = imagen_pil.copy()
        img_display.thumbnail((ANCHO_DISPLAY - 4, ALTO_DISPLAY - 4), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img_display)
        canvas._foto = foto
        canvas.delete("all")
        canvas.create_image(ANCHO_DISPLAY // 2, ALTO_DISPLAY // 2, image=foto)


if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageTk
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw, ImageTk

    app = Aplicacion()
    app.mainloop()