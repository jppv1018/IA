# Agente reactivo simple - Gestión automática de subtítulos
# Juan Pablo Paz Vasco
# IA - Grupo 02 


"""Acciones del agente:
  1. ACTIVAR_SUBTÍTULOS    — cuando el video inicia y subs están desactivados
  2. DESACTIVAR_SUBTÍTULOS — cuando el idioma del video = idioma nativo del usuario
  3. CAMBIAR_IDIOMA        — cuando se detecta un idioma diferente al activo en subs
  4. AJUSTAR_VELOCIDAD_SUBS— cuando la velocidad de reproducción supera 1.5×
  5. MODO_SOLO_AUDIO       — cuando la señal de video se pierde pero hay audio
"""

import tkinter as tk
import random
import time

C = {
    "bg":       "#F5F0E8",   
    "panel":    "#EDE8DC",   
    "borde":    "#C8BFA8",   
    "acento":   "#C0392B",   
    "acento2":  "#2471A3",   
    "verde":    "#1E8449",   
    "amarillo": "#B7770D",   
    "texto":    "#1C1C1C",  
    "subtexto": "#7A7060",   
    "card":     "#FDFAF4",   
    "linea":    "#D5CCBA",
}

FONT_TITULO  = ("Georgia", 16, "bold")
FONT_SUBTIT  = ("Georgia", 9, "italic")
FONT_LABEL   = ("Georgia", 9)
FONT_VALOR   = ("Georgia", 11, "bold")
FONT_BTN     = ("Georgia", 9, "bold")
FONT_LOG     = ("Georgia", 8)
FONT_SECCION = ("Georgia", 8, "bold")

IDIOMAS = ["EN", "ES", "FR", "PT", "DE", "JA"]


#  LÓGICA DEL AGENTE

REGLAS = [
    (
        lambda s: s["video_activo"] and not s["subs_activos"],
        "ACTIVAR_SUBTÍTULOS",
        "Video iniciado sin subtítulos → activarlos automáticamente",
    ),
    (
        lambda s: s["idioma_video"] == s["idioma_usuario"] and s["subs_activos"],
        "DESACTIVAR_SUBTÍTULOS",
        "Idioma del video igual al nativo → desactivar subtítulos",
    ),
    (
        lambda s: s["idioma_video"] != s["idioma_subs_actual"] and s["subs_activos"],
        "CAMBIAR_IDIOMA",
        "Idioma del video cambió → ajustar idioma de subtítulos",
    ),
    (
        lambda s: s["velocidad_reproduccion"] > 1.5 and s["subs_activos"] and not s["velocidad_subs_ajustada"],
        "AJUSTAR_VELOCIDAD_SUBS",
        "Velocidad alta detectada → reducir duración de los subtítulos",
    ),
    (
        lambda s: not s["video_activo"] and s["audio_activo"],
        "MODO_SOLO_AUDIO",
        "Sin señal de video pero audio presente → activar modo solo audio",
    ),
]


def percibir(estado):
    return [(a, d) for cond, a, d in REGLAS if cond(estado)]


def actuar(percepciones, estado):
    if not percepciones:
        return None, "Entorno estable — ninguna regla activada", estado
    accion, descripcion = percepciones[0]
    if accion == "ACTIVAR_SUBTÍTULOS":
        estado["subs_activos"] = True
        estado["idioma_subs_actual"] = estado["idioma_video"]
    elif accion == "DESACTIVAR_SUBTÍTULOS":
        estado["subs_activos"] = False
    elif accion == "CAMBIAR_IDIOMA":
        estado["idioma_subs_actual"] = estado["idioma_video"]
    elif accion == "AJUSTAR_VELOCIDAD_SUBS":
        estado["velocidad_subs_ajustada"] = True
    elif accion == "MODO_SOLO_AUDIO":
        estado["modo_solo_audio"] = True
    return accion, descripcion, estado


def ciclo_agente(estado):
    p = percibir(estado)
    return actuar(p, estado)


def estado_inicial():
    return {
        "video_activo": False,
        "audio_activo": False,
        "subs_activos": False,
        "idioma_video": "EN",
        "idioma_usuario": "ES",
        "idioma_subs_actual": "EN",
        "velocidad_reproduccion": 1.0,
        "velocidad_subs_ajustada": False,
        "modo_solo_audio": False,
    }


#  INTERFAZ


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente Reactivo — Subtítulos Automáticos")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)

        W, H = 800, 620
        self.root.geometry(f"{W}x{H}")
        # Centrar ventana
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - W) // 2
        y = (sh - H) // 2
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        self.estado = estado_inicial()
        self._build()
        self._refrescar()

    def _build(self):
        # ── Cabecera ──
        cab = tk.Frame(self.root, bg=C["bg"])
        cab.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(cab, text="🎙  Agente de Subtítulos Automáticos",
                 bg=C["bg"], fg=C["texto"], font=FONT_TITULO, anchor="w"
                 ).pack(side="left")

        tk.Frame(self.root, bg=C["linea"], height=1).pack(fill="x", padx=30, pady=(10, 14))

        # Cuerpo
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=30)

        izq = tk.Frame(body, bg=C["bg"], width=310)
        izq.pack(side="left", fill="y")
        izq.pack_propagate(False)

        der = tk.Frame(body, bg=C["bg"])
        der.pack(side="right", fill="both", expand=True, padx=(18, 0))

        self._panel_sensores(izq)
        self._panel_idiomas(izq)
        self._panel_velocidad(izq)
        self._panel_accion(izq)
        self._panel_log(der)
        self._panel_botones()

    def _tarjeta(self, parent, titulo):
        wrap = tk.Frame(parent, bg=C["card"],
                        highlightbackground=C["borde"], highlightthickness=1)
        wrap.pack(fill="x", pady=(0, 10))
        tk.Label(wrap, text=titulo.upper(), bg=C["card"],
                 fg=C["subtexto"], font=FONT_SECCION, anchor="w"
                 ).pack(fill="x", padx=12, pady=(8, 3))
        tk.Frame(wrap, bg=C["linea"], height=1).pack(fill="x", padx=12, pady=(0, 6))
        return wrap

    def _indicador(self, parent, etiqueta):
        f = tk.Frame(parent, bg=C["card"])
        f.pack(side="left", padx=(0, 18))
        dot = tk.Label(f, text="●", bg=C["card"],
                       fg=C["borde"], font=("Georgia", 14))
        dot.pack()
        tk.Label(f, text=etiqueta, bg=C["card"],
                 fg=C["subtexto"], font=("Georgia", 7)).pack()
        return dot

    def _panel_sensores(self, p):
        t = self._tarjeta(p, "Señales activas")
        row = tk.Frame(t, bg=C["card"])
        row.pack(fill="x", padx=12, pady=(0, 10))
        self.dot_video = self._indicador(row, "VIDEO")
        self.dot_audio = self._indicador(row, "AUDIO")
        self.dot_subs  = self._indicador(row, "SUBS")

    def _panel_idiomas(self, p):
        t = self._tarjeta(p, "Idiomas")
        g = tk.Frame(t, bg=C["card"])
        g.pack(fill="x", padx=12, pady=(0, 10))

        filas = [
            ("Video:",        "EN", C["acento"],  "lbl_iv"),
            ("Usuario:",      "ES", C["verde"],   "lbl_iu"),
            ("Subs activo:",  "EN", C["amarillo"],"lbl_is"),
        ]
        for i, (lbl, val, color, attr) in enumerate(filas):
            tk.Label(g, text=lbl, bg=C["card"], fg=C["subtexto"],
                     font=FONT_LABEL, width=12, anchor="w").grid(row=i, column=0, sticky="w")
            w = tk.Label(g, text=val, bg=C["card"], fg=color, font=FONT_VALOR, width=5)
            w.grid(row=i, column=1, sticky="w")
            setattr(self, attr, w)

    def _panel_velocidad(self, p):
        t = self._tarjeta(p, "Velocidad de reproducción")
        g = tk.Frame(t, bg=C["card"])
        g.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(g, text="Actual:", bg=C["card"], fg=C["subtexto"],
                 font=FONT_LABEL, anchor="w").grid(row=0, column=0, sticky="w")
        self.lbl_vel = tk.Label(g, text="1.0×", bg=C["card"],
                                fg=C["texto"], font=FONT_VALOR)
        self.lbl_vel.grid(row=0, column=1, sticky="w", padx=8)

    def _panel_accion(self, p):
        t = self._tarjeta(p, "Última acción del agente")
        self.lbl_accion = tk.Label(t, text="—  Sin acción",
                 bg=C["card"], fg=C["acento2"],
                 font=("Georgia", 10, "bold"), anchor="w",
                 wraplength=268, justify="left")
        self.lbl_accion.pack(fill="x", padx=12, pady=(0, 4))
        self.lbl_razon = tk.Label(t, text="",
                 bg=C["card"], fg=C["subtexto"],
                 font=("Georgia", 8, "italic"), anchor="w",
                 wraplength=268, justify="left")
        self.lbl_razon.pack(fill="x", padx=12, pady=(0, 10))

    def _panel_log(self, p):
        tk.Label(p, text="LOG DEL AGENTE", bg=C["bg"],
                 fg=C["subtexto"], font=FONT_SECCION).pack(anchor="w", pady=(0, 6))

        marco = tk.Frame(p, bg=C["card"],
                         highlightbackground=C["borde"], highlightthickness=1)
        marco.pack(fill="both", expand=True)

        self.log = tk.Text(marco, bg=C["card"], fg=C["texto"],
                           font=FONT_LOG, state="disabled",
                           relief="flat", bd=0, wrap="word",
                           selectbackground=C["panel"])
        sb = tk.Scrollbar(marco, command=self.log.yview, bg=C["panel"])
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

        self.log.tag_config("ts",      foreground=C["subtexto"])
        self.log.tag_config("accion",  foreground=C["acento"],  font=("Georgia", 8, "bold"))
        self.log.tag_config("estable", foreground=C["subtexto"], font=("Georgia", 8, "italic"))
        self.log.tag_config("desc",    foreground=C["texto"])

    def _panel_botones(self):
        tk.Frame(self.root, bg=C["linea"], height=1).pack(fill="x", padx=30, pady=(10, 10))


        bf = tk.Frame(self.root, bg=C["bg"])
        bf.pack(fill="x", padx=30, pady=(0, 18))

        botones = [
            ("▶  Iniciar video",    self._iniciar_video,  C["verde"]),
            ("⏹  Detener video",   self._detener_video,  C["acento"]),
            ("🌐  Cambiar idioma",  self._cambiar_idioma,  C["acento2"]),
            ("⚡  Velocidad 2×",    self._velocidad_alta,  C["amarillo"]),
            ("🔁  Reiniciar",       self._reset,           C["subtexto"]),
        ]

        for txt, cmd, color in botones:
            b = tk.Button(bf, text=txt, command=cmd,
                          bg=C["panel"], fg=color,
                          font=FONT_BTN, relief="flat", bd=0,
                          cursor="hand2", padx=10, pady=6,
                          activebackground=C["borde"],
                          activeforeground=color)
            b.pack(side="left", padx=(0, 8))

    # Acciones

    def _iniciar_video(self):
        self.estado["video_activo"] = True
        self.estado["audio_activo"] = True
        self.estado["modo_solo_audio"] = False
        self._ciclo()

    def _detener_video(self):
        self.estado["video_activo"] = False
        self.estado["audio_activo"] = True
        self._ciclo()

    def _cambiar_idioma(self):
        self.estado["idioma_video"] = random.choice(
            [i for i in IDIOMAS if i != self.estado["idioma_video"]])
        self._ciclo()

    def _velocidad_alta(self):
        self.estado["velocidad_reproduccion"] = 2.0
        self.estado["velocidad_subs_ajustada"] = False
        self._ciclo()

    def _reset(self):
        self.estado = estado_inicial()
        self._refrescar()
        self._log("── Sistema reiniciado ──\n", "estable")

    # Ciclo agente

    def _ciclo(self):
        accion, desc, self.estado = ciclo_agente(self.estado)
        self._refrescar()
        ts = time.strftime("%H:%M:%S")
        if accion:
            self.lbl_accion.config(text=f"▸  {accion}", fg=C["acento"])
            self.lbl_razon.config(text=desc)
            self._log(f"[{ts}]  ", "ts")
            self._log(f"{accion}\n", "accion")
            self._log(f"         {desc}\n\n", "desc")
        else:
            self.lbl_accion.config(text="✓  Entorno estable", fg=C["verde"])
            self.lbl_razon.config(text="Ninguna regla activada")
            self._log(f"[{ts}]  Entorno estable — sin acción\n", "estable")

    def _log(self, texto, tag="desc"):
        self.log.config(state="normal")
        self.log.insert("end", texto, tag)
        self.log.see("end")
        self.log.config(state="disabled")

    # Refresco visual

    def _refrescar(self):
        e = self.estado
        on, off = C["verde"], C["borde"]
        self.dot_video.config(fg=on if e["video_activo"] else off)
        self.dot_audio.config(fg=on if e["audio_activo"] else off)
        self.dot_subs.config( fg=on if e["subs_activos"]  else off)

        self.lbl_iv.config(text=e["idioma_video"])
        self.lbl_iu.config(text=e["idioma_usuario"])
        self.lbl_is.config(text=e["idioma_subs_actual"])

        vel = e["velocidad_reproduccion"]
        self.lbl_vel.config(text=f"{vel}×",
                            fg=C["acento"] if vel > 1.5 else C["texto"])


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()