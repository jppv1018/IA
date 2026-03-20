
#Algoritmo Genético - Recorrer ciudades
# Juan Pablo Paz Vasco
# IA - Grupo 02

import tkinter as tk
from tkinter import messagebox
import threading
import random
import math


CIUDADES = {
    "Bogotá"       : (300, 420),
    "Medellín"     : (210, 310),
    "Cali"         : (180, 430),
    "Barranquilla" : (280, 100),
    "Cartagena"    : (220, 110),
    "Bucaramanga"  : (320, 240),
    "Pereira"      : (210, 370),
    "Manizales"    : (230, 350),
    "Cúcuta"       : (380, 200),
    "Ibagué"       : (265, 400),
    "Santa Marta"  : (320, 90),
    "Pasto"        : (180, 510),
}

ANCHO_MAPA  = 560
ALTO_MAPA   = 600
RADIO_CIUDAD = 7


# Cada ciudad tiene un número (índice): Bogotá=0, Medellín=1, Cali=2, etc.
nombres_ciudades = list(CIUDADES.keys())
posiciones       = list(CIUDADES.values())
num_ciudades     = len(nombres_ciudades)


# Funcion objetivo
# Recibe los índices de dos ciudades (ej. 0 y 3) y devuelve la distancia.

def calcular_distancia(ciudad_a, ciudad_b):
    x1, y1 = posiciones[ciudad_a]
    x2, y2 = posiciones[ciudad_b]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# - Función objetivo
# 
# Suma todas las distancias entre ciudades consecutivas de la ruta.
# Al final también suma la distancia de regreso a la ciudad inicial.
# Resultado: mientras más BAJO el número, mejor es la ruta.
#
# Ejemplo con 3 ciudades [0, 2, 5]:
#   distancia(0→2) + distancia(2→5) + distancia(5→0)  ← cierra el ciclo

def calcular_distancia_total(ruta):
    distancia_total = 0
    for i in range(len(ruta)):
        ciudad_actual    = ruta[i]
        ciudad_siguiente = ruta[(i + 1) % len(ruta)]  # % cierra el ciclo al llegar al final
        distancia_total += calcular_distancia(ciudad_actual, ciudad_siguiente)
    return distancia_total



# El cromosoma representa una ruta completa: el orden en que el
# vendedor visita las 12 ciudades.
#
# El GEN aquí no es una sola ciudad, sino el ORDEN COMPLETO de visita.
# Ejemplo: [3, 0, 7, 1, 9, 2, 5, 11, 4, 8, 6, 10]
#   → visita primero Barranquilla (3), luego Bogotá (0), luego Cúcuta (7)...
#
# Cada ciudad aparece exactamente una vez en la lista.
# No se puede visitar la misma ciudad dos veces ni saltarse ninguna.

class Individuo:

    def __init__(self, ruta=None):
        if ruta is None:
            # ruta inicial: mezcla los 12 índices al azar
            self.ruta = list(range(num_ciudades))
            random.shuffle(self.ruta)
        else:
            self.ruta = ruta[:]

        # calcular la distancia total de esta ruta (función objetivo)
        self.distancia = calcular_distancia_total(self.ruta)

    def mutar(self, tasa_mutacion=0.15):
        # Se muta por intercambio:
        # Recorre la ruta y con cierta probabilidad intercambia dos ciudades de lugar.
        
        nueva_ruta = self.ruta[:]
        for i in range(num_ciudades):
            if random.random() < tasa_mutacion:
                j = random.randint(0, num_ciudades - 1)
                nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]
        return Individuo(nueva_ruta)

    def cruzar(self, otro):
        # CRUCE por orden:
        # Combina dos rutas padre para crear una ruta hijo.
    
        inicio   = random.randint(0, num_ciudades - 2)
        fin      = random.randint(inicio + 1, num_ciudades - 1)
        segmento = self.ruta[inicio:fin]
        resto    = [c for c in otro.ruta if c not in segmento]
        nueva_ruta = resto[:inicio] + segmento + resto[inicio:]
        return Individuo(nueva_ruta)

class AlgoritmoGenetico:

    def __init__(self, tam_poblacion=80, tasa_mutacion=0.15):
        self.tam_poblacion   = tam_poblacion
        self.tasa_mutacion   = tasa_mutacion
        self.generacion      = 0
        self.mejor_distancia = float('inf')
        self.historial       = []

        # Se crean varias rutas al azar
        self.poblacion = [Individuo() for _ in range(tam_poblacion)]
        # ordenar de mejor a peor (menor distancia = mejor)
        self.poblacion.sort(key=lambda ind: ind.distancia)
        self.mejor_individuo = self.poblacion[0]
        self.mejor_distancia = self.mejor_individuo.distancia

    def paso(self):
        # Se ejecuta una generación completa

        nueva_poblacion = [self.poblacion[0]]

        # Se crean nuevos hijos hasta completar la población
        while len(nueva_poblacion) < self.tam_poblacion:
        
            mitad  = max(2, self.tam_poblacion // 3)
            padre1 = random.choice(self.poblacion[:mitad])
            padre2 = random.choice(self.poblacion[:mitad])

            # el hijo combina las rutas de dos padres y luego muta levemente
            hijo = padre1.cruzar(padre2)
            hijo = hijo.mutar(self.tasa_mutacion)
            nueva_poblacion.append(hijo)

        
        self.poblacion = sorted(nueva_poblacion, key=lambda ind: ind.distancia)
        self.generacion += 1

       
        if self.poblacion[0].distancia < self.mejor_distancia:
            self.mejor_distancia = self.poblacion[0].distancia
            self.mejor_individuo = self.poblacion[0]

        self.historial.append(self.mejor_distancia)


#  INTERFAZ GRÁFICA

COLOR_FONDO_MAPA   = "#1a2035"
COLOR_RUTA         = "#00bcd4"
COLOR_CIUDAD       = "#ff5722"
COLOR_CIUDAD_BORDE = "#ffffff"
COLOR_NOMBRE       = "#ffffff"
COLOR_INICIO       = "#ffeb3b"


class Aplicacion(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AG - Turista (Recorrer ciudades)")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        self.ag        = None
        self.corriendo = False

        self._construir_interfaz()

        self.update_idletasks()
        ancho_ventana  = self.winfo_reqwidth()
        alto_ventana   = self.winfo_reqheight()
        x = (self.winfo_screenwidth()  // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana  // 2)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        self._dibujar_ciudades()

    # ── construcción ──────────────────────────────────────────────────────────

    def _construir_interfaz(self):
        tk.Label(self, text="AG — Turista (Recorrer ciudades)",
                 font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(8, 2))
        tk.Label(self, text="Ruta más corta para visitar todas las ciudades",
                 font=("Arial", 8), fg="gray", bg="#f0f0f0").pack(pady=(0, 6))

        # mapa
        self.canvas_mapa = tk.Canvas(self, width=440, height=420,
                                     bg=COLOR_FONDO_MAPA, relief="solid", bd=1)
        self.canvas_mapa.pack(padx=14)

        # estadísticas
        marco_stats = tk.Frame(self, bg="#f0f0f0")
        marco_stats.pack(pady=(8, 4))
        self.var_generacion = tk.StringVar(value="Generación: —")
        self.var_distancia  = tk.StringVar(value="Distancia: —")
        for var in [self.var_generacion, self.var_distancia]:
            tk.Label(marco_stats, textvariable=var, font=("Arial", 9),
                     bg="#f0f0f0", width=18).pack(side="left", padx=4)

        # parámetros: mutación y generaciones máximas
        marco_params = tk.Frame(self, bg="#f0f0f0")
        marco_params.pack(pady=(0, 6))
        self.var_mutacion = tk.IntVar(value=15)
        self.var_max_gen  = tk.IntVar(value=300)
        self._slider(marco_params, "Mutación (%):",      self.var_mutacion, 1,   50)
        self._slider(marco_params, "Generaciones máx:", self.var_max_gen,  50, 1000)

        # botones
        marco_botones = tk.Frame(self, bg="#f0f0f0")
        marco_botones.pack(pady=(0, 6))
        tk.Button(marco_botones, text="▶ Iniciar", command=self._iniciar,
                  bg="#27ae60", fg="white", relief="flat", width=12,
                  font=("Arial", 9, "bold")).pack(side="left", padx=5)
        self.boton_detener = tk.Button(marco_botones, text="■ Detener",
                  command=self._detener, bg="#e74c3c", fg="white",
                  relief="flat", width=12, state="disabled",
                  font=("Arial", 9, "bold"))
        self.boton_detener.pack(side="left", padx=5)
        tk.Button(marco_botones, text="↺ Reiniciar", command=self._reiniciar,
                  bg="#e67e22", fg="white", relief="flat", width=12,
                  font=("Arial", 9, "bold")).pack(side="left", padx=5)

        # estado
        self.var_estado = tk.StringVar(value="Presiona Iniciar para comenzar.")
        tk.Label(self, textvariable=self.var_estado, font=("Arial", 8),
                 fg="gray", bg="#f0f0f0").pack(pady=(0, 8))

    def _slider(self, padre, etiqueta, variable, minimo, maximo):
        marco = tk.Frame(padre, bg="#f0f0f0")
        marco.pack(side="left", padx=8)
        tk.Label(marco, text=etiqueta, font=("Arial", 8),
                 bg="#f0f0f0").pack(side="left")
        tk.Scale(marco, from_=minimo, to=maximo, orient="horizontal",
                 variable=variable, bg="#f0f0f0", length=110,
                 font=("Arial", 7), showvalue=True).pack(side="left")

    # ── Mapa 

    def _dibujar_ciudades(self):
        self.canvas_mapa.delete("all")
        for i, (nombre, (x, y)) in enumerate(CIUDADES.items()):
            px = int(x * 440 / 560)
            py = int(y * 420 / 600)
            self.canvas_mapa.create_oval(
                px - RADIO_CIUDAD, py - RADIO_CIUDAD,
                px + RADIO_CIUDAD, py + RADIO_CIUDAD,
                fill=COLOR_CIUDAD, outline=COLOR_CIUDAD_BORDE, width=1)
            self.canvas_mapa.create_text(
                px + 10, py - 10, text=nombre,
                fill=COLOR_NOMBRE, font=("Arial", 7), anchor="w")

    def _dibujar_ruta(self, individuo: Individuo):
        self.canvas_mapa.delete("all")
        ruta = individuo.ruta

        def escalar(idx):
            x, y = posiciones[idx]
            return int(x * 440 / 560), int(y * 420 / 600)

        for i in range(len(ruta)):
            x1, y1 = escalar(ruta[i])
            x2, y2 = escalar(ruta[(i + 1) % len(ruta)])
            self.canvas_mapa.create_line(x1, y1, x2, y2, fill=COLOR_RUTA, width=2)

        for i, (nombre, _) in enumerate(CIUDADES.items()):
            px, py = escalar(i)
            color  = COLOR_INICIO if ruta[0] == i else COLOR_CIUDAD
            self.canvas_mapa.create_oval(
                px - RADIO_CIUDAD, py - RADIO_CIUDAD,
                px + RADIO_CIUDAD, py + RADIO_CIUDAD,
                fill=color, outline=COLOR_CIUDAD_BORDE, width=1)
            self.canvas_mapa.create_text(
                px + 10, py - 10, text=nombre,
                fill=COLOR_NOMBRE, font=("Arial", 7), anchor="w")

        for orden, idx in enumerate(ruta):
            px, py = escalar(idx)
            self.canvas_mapa.create_text(px, py, text=str(orden + 1),
                                         fill="white", font=("Arial", 6, "bold"))

    # Funciones botones

    def _iniciar(self):
        if self.ag is None:
            self.ag = AlgoritmoGenetico(
                tam_poblacion = 80,
                tasa_mutacion = self.var_mutacion.get() / 100,
            )
        self.corriendo = True
        self.boton_detener.configure(state="normal")
        threading.Thread(target=self._bucle_evolucion, daemon=True).start()
        self._bucle_actualizacion()

    def _detener(self):
        self.corriendo = False
        self.boton_detener.configure(state="disabled")
        gen = self.ag.generacion if self.ag else 0
        self.var_estado.set(f"Pausado en generación {gen}.")

    def _reiniciar(self):
        self.corriendo = False
        self.ag = None
        self.boton_detener.configure(state="disabled")
        self.var_generacion.set("Generación: —")
        self.var_distancia.set("Distancia: —")
        self._dibujar_ciudades()
        self.var_estado.set("Reiniciado. Presiona Iniciar para comenzar.")



    def _bucle_evolucion(self):
        max_gen = self.var_max_gen.get()
        while self.corriendo and self.ag:
            if self.ag.generacion >= max_gen:
                self.corriendo = False
                break
            self.ag.paso()

    def _bucle_actualizacion(self):
        if self.ag:
            gen       = self.ag.generacion
            distancia = self.ag.mejor_distancia
            historial = self.ag.historial
            max_gen   = self.var_max_gen.get()

            if len(historial) > 1:
                pass
            self.var_generacion.set(f"Generación: {gen}/{max_gen}")
            self.var_distancia.set(f"Distancia: {distancia:.1f} px")
            self._dibujar_ruta(self.ag.mejor_individuo)

            if not self.corriendo and gen >= max_gen:
                self.boton_detener.configure(state="disabled")
                self.var_estado.set(
                    f"✅ Finalizado en gen {gen} | Mejor distancia: {distancia:.1f} px")
                return

            if self.corriendo:
                self.var_estado.set(
                    f"Evolucionando... gen {gen}/{max_gen} | distancia {distancia:.1f} px")

        if self.corriendo:
            self.after(200, self._bucle_actualizacion)


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()

