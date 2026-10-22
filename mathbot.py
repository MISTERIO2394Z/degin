import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor
)
import os
import random

# MathBot - Asistente de Cálculo y Precálculo
# Requisitos: Python 3.10+, sympy, pillow, matplotlib

X = sp.symbols("x")
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

EJEMPLOS = [
    ("Resolver ecuación", "2*x + 5 = 17"),
    ("Factorizar", "x**2 - 5*x + 6"),
    ("Derivar", "x**3 - 6*x**2 + 9*x + 1"),
    ("Integrar", "3*x**2 + 2*x"),
    ("Límite", "sin(x)/x"),
    ("Simplificar", "(x**2 - 9)/(x - 3)"),
    ("Resolver cuadrática", "x**2 - 5*x + 6 = 0"),
    ("Graficar", "x**2 - 4"),
    ("Integral definida", "x**2"),
    ("Derivada trigonométrica", "sin(x) + cos(x)"),
]

def parse_math(text):
    text = text.strip().replace("π", "pi").replace("√", "sqrt")
    if not text:
        raise ValueError("Escribe una operación o función matemática.")
    local = {
        "x": X, "pi": sp.pi, "e": sp.E, "E": sp.E,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "sqrt": sp.sqrt, "log": sp.log, "ln": sp.log,
        "exp": sp.exp, "abs": sp.Abs,
    }
    return parse_expr(text, local_dict=local, transformations=TRANSFORMATIONS,
                      evaluate=True)

class MathBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MathBot | Asistente de Cálculo y Precálculo")
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)
        self.bg_original = None
        self.bg_photo = None
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        try:
            from PIL import Image, ImageTk
            path = os.path.join(os.path.dirname(__file__), "fondo_matematicas.png")
            self.bg_original = Image.open(path).convert("RGB")
            self.Image = Image
            self.ImageTk = ImageTk
        except Exception:
            self.bg_original = None

        self.panel = tk.Frame(self.canvas, bg="#ffffff", bd=0)
        self.panel_window = self.canvas.create_window(0, 0, anchor="nw", window=self.panel)
        self.canvas.bind("<Configure>", self.resize_background)
        self.build_ui()
        self.resize_background()

    def resize_background(self, event=None):
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        if self.bg_original is not None:
            image = self.bg_original.copy()
            scale = max(w / image.width, h / image.height)
            image = image.resize((int(image.width*scale), int(image.height*scale)), self.Image.Resampling.LANCZOS)
            left = (image.width - w) // 2
            top = (image.height - h) // 2
            image = image.crop((left, top, left+w, top+h))
            self.bg_photo = self.ImageTk.PhotoImage(image)
            self.canvas.delete("background")
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="background")
            self.canvas.tag_lower("background")
        self.canvas.coords(self.panel_window, max((w-900)//2, 15), 18)
        self.canvas.itemconfigure(self.panel_window, width=min(900, w-30), height=h-36)

    def build_ui(self):
        self.panel.configure(bg="#ffffff")
        header = tk.Frame(self.panel, bg="#17365d", padx=22, pady=15)
        header.pack(fill="x")
        tk.Label(header, text="MathBot", font=("Segoe UI", 25, "bold"),
                 fg="white", bg="#17365d").pack(anchor="w")
        tk.Label(header, text="Asistente virtual de cálculo y precálculo",
                 font=("Segoe UI", 11), fg="#e5efff", bg="#17365d").pack(anchor="w")

        body = tk.Frame(self.panel, bg="#ffffff", padx=22, pady=16)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="¿Qué ejercicio quieres resolver?", font=("Segoe UI", 15, "bold"),
                 bg="white", fg="#17365d").pack(anchor="w")
        tk.Label(body, text="Usa x como variable. Ejemplos: x^2 - 4, 2*x + 5 = 17, sin(x)/x",
                 font=("Segoe UI", 10), bg="white", fg="#444444").pack(anchor="w", pady=(3, 8))

        entry_row = tk.Frame(body, bg="white")
        entry_row.pack(fill="x")
        self.input_var = tk.StringVar()
        self.entry = ttk.Entry(entry_row, textvariable=self.input_var, font=("Consolas", 13))
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda e: self.solve())
        ttk.Button(entry_row, text="Resolver", command=self.solve).pack(side="left", padx=(8, 0), ipady=5)

        buttons = tk.Frame(body, bg="white")
        buttons.pack(fill="x", pady=10)
        actions = [
            ("Resolver ecuación", self.solve_equation),
            ("Factorizar", self.factor),
            ("Derivar", self.derivative),
            ("Integrar", self.integral),
            ("Límite", self.limit),
            ("Graficar", self.graph),
            ("Simplificar", self.simplify),
            ("Práctica", self.practice),
        ]
        for i, (label, cmd) in enumerate(actions):
            ttk.Button(buttons, text=label, command=cmd).grid(row=i//4, column=i%4, padx=4, pady=4, sticky="ew")
        for col in range(4):
            buttons.grid_columnconfigure(col, weight=1)

        tk.Label(body, text="Procedimiento y respuesta", font=("Segoe UI", 12, "bold"),
                 bg="white", fg="#17365d").pack(anchor="w", pady=(7, 5))
        output_frame = tk.Frame(body, bg="white")
        output_frame.pack(fill="both", expand=True)
        self.output = tk.Text(output_frame, wrap="word", font=("Segoe UI", 11),
                              bg="#f7faff", fg="#202020", relief="solid", bd=1,
                              padx=12, pady=10, height=14)
        scrollbar = ttk.Scrollbar(output_frame, command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.write("¡Hola! Soy MathBot.\n\nEscribe una función o elige una operación. Te mostraré el procedimiento disponible y la respuesta.\n\nPrueba: x^3 - 6*x^2 + 9*x + 1")
        tk.Label(body, text="Integrantes: ____________________ y ____________________    |    Asignatura: Cálculo y Precálculo",
                 bg="white", fg="#666666", font=("Segoe UI", 9)).pack(anchor="w", pady=(9, 0))

    def write(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="normal")

    def get_expr(self):
        return parse_math(self.input_var.get())

    def solve(self):
        text = self.input_var.get().strip()
        if "=" in text:
            self.solve_equation()
        else:
            self.simplify()

    def solve_equation(self):
        try:
            text = self.input_var.get().strip()
            if "=" not in text:
                expr = self.get_expr()
                answer = sp.solve(sp.Eq(expr, 0), X)
                self.write(f"OPERACIÓN: Resolver ecuación\n\n1. Interpretamos la expresión como:\n   {sp.pretty(expr)} = 0\n\n2. Buscamos los valores de x que hacen verdadera la igualdad.\n\nRESPUESTA:\n   x = {answer}")
                return
            left, right = text.split("=", 1)
            lhs, rhs = parse_math(left), parse_math(right)
            equation = sp.Eq(lhs, rhs)
            result = sp.solve(equation, X)
            self.write(f"OPERACIÓN: Resolver ecuación\n\n1. Ecuación original:\n   {sp.pretty(equation)}\n\n2. Pasamos todo al lado izquierdo:\n   {sp.pretty(lhs-rhs)} = 0\n\n3. Igualamos a cero y despejamos x.\n\nRESPUESTA:\n   x = {result}")
        except Exception as e:
            self.error(e)

    def factor(self):
        try:
            expr = self.get_expr()
            self.write(f"OPERACIÓN: Factorización\n\n1. Expresión original:\n   {sp.pretty(expr)}\n\n2. Buscamos factores cuyo producto sea la expresión original.\n\nRESPUESTA:\n   {sp.pretty(sp.factor(expr))}")
        except Exception as e: self.error(e)

    def derivative(self):
        try:
            expr = self.get_expr()
            result = sp.diff(expr, X)
            self.write(f"OPERACIÓN: Derivada\n\n1. Función original:\n   f(x) = {sp.pretty(expr)}\n\n2. Aplicamos las reglas de derivación término por término.\n\n3. Derivamos respecto de x.\n\nRESPUESTA:\n   f'(x) = {sp.pretty(result)}")
        except Exception as e: self.error(e)

    def integral(self):
        try:
            expr = self.get_expr()
            result = sp.integrate(expr, X)
            self.write(f"OPERACIÓN: Integral indefinida\n\n1. Función a integrar:\n   {sp.pretty(expr)}\n\n2. Buscamos una función cuya derivada sea la expresión original.\n\nRESPUESTA:\n   ∫ f(x) dx = {sp.pretty(result)} + C")
        except Exception as e: self.error(e)

    def limit(self):
        try:
            expr = self.get_expr()
            result = sp.limit(expr, X, 0)
            self.write(f"OPERACIÓN: Límite cuando x tiende a 0\n\n1. Función original:\n   {sp.pretty(expr)}\n\n2. Evaluamos el comportamiento de la función cuando x se acerca a 0.\n\nRESPUESTA:\n   lim(x→0) f(x) = {sp.pretty(result)}\n\nNota: esta herramienta calcula el límite en x = 0. Para otro punto, modifica la función o el código.")
        except Exception as e: self.error(e)

    def simplify(self):
        try:
            expr = self.get_expr()
            self.write(f"OPERACIÓN: Simplificación\n\n1. Expresión original:\n   {sp.pretty(expr)}\n\n2. Reducimos términos y simplificamos la expresión.\n\nRESPUESTA:\n   {sp.pretty(sp.simplify(expr))}")
        except Exception as e: self.error(e)

    def graph(self):
        try:
            expr = self.get_expr()
            import numpy as np
            import matplotlib.pyplot as plt
            f = sp.lambdify(X, expr, modules=["numpy"])
            xs = np.linspace(-10, 10, 600)
            with np.errstate(all="ignore"):
                ys = f(xs)
            if np.isscalar(ys):
                ys = np.full_like(xs, ys, dtype=float)
            ys = np.asarray(ys, dtype=float)
            ys[~np.isfinite(ys)] = np.nan
            plt.figure("MathBot - Gráfica")
            plt.clf()
            plt.plot(xs, ys, label=f"f(x) = {sp.sstr(expr)}")
            plt.axhline(0, linewidth=0.8)
            plt.axvline(0, linewidth=0.8)
            plt.grid(True)
            plt.xlabel("x")
            plt.ylabel("f(x)")
            plt.title("Gráfica de la función")
            plt.legend()
            plt.tight_layout()
            plt.show()
            self.write(f"OPERACIÓN: Representación gráfica\n\nFunción:\n   f(x) = {sp.pretty(expr)}\n\nSe abrió una ventana con la gráfica en el intervalo aproximado -10 ≤ x ≤ 10.\n\nObserva dónde corta los ejes, dónde crece o decrece y sus puntos importantes.")
        except Exception as e: self.error(e)

    def practice(self):
        problem = random.choice([
            ("derivada", "x**3 - 4*x", "3*x**2 - 4", "Deriva término por término: la derivada de x^n es n*x^(n-1)."),
            ("factorización", "x**2 - 7*x + 12", "(x - 3)*(x - 4)", "Busca dos números que multipliquen 12 y sumen -7."),
            ("ecuación", "2*x + 6 = 14", "[4]", "Resta 6 en ambos lados y luego divide entre 2."),
            ("integral", "2*x", "x**2", "La integral de x^n es x^(n+1)/(n+1), más la constante C."),
            ("simplificación", "(x**2 - 4)/(x - 2)", "x + 2", "Factoriza el numerador como diferencia de cuadrados."),
        ])
        kind, question, answer, hint = problem
        win = tk.Toplevel(self.root)
        win.title("Práctica MathBot")
        win.geometry("560x310")
        win.transient(self.root)
        win.configure(bg="white")
        tk.Label(win, text="PRÁCTICA RÁPIDA", font=("Segoe UI", 16, "bold"),
                 bg="white", fg="#17365d").pack(pady=(18, 8))
        tk.Label(win, text=f"Resuelve: {question}", font=("Consolas", 13),
                 bg="white").pack(pady=5)
        tk.Label(win, text="Escribe tu respuesta (puedes usar x, *, ^):",
                 bg="white").pack()
        ans = ttk.Entry(win, font=("Consolas", 12), width=42)
        ans.pack(pady=8)
        feedback = tk.Label(win, text="", bg="white", wraplength=500, justify="left")
        feedback.pack(pady=6)
        def check():
            user = ans.get().strip()
            try:
                if kind == "ecuación":
                    ok = sp.simplify(parse_math(user) - 4) == 0 or user.replace(" ", "") in ("4", "[4]", "x=4")
                elif kind == "factorización":
                    ok = sp.expand(parse_math(user) - parse_math(answer)) == 0
                elif kind == "simplificación":
                    ok = sp.simplify(parse_math(user) - parse_math(answer)) == 0
                else:
                    ok = sp.simplify(parse_math(user) - parse_math(answer)) == 0
                feedback.config(text=("¡Correcto! Muy bien. 🎉" if ok else f"Aún no. Pista: {hint}"),
                                fg=("#16803c" if ok else "#a33a22"))
            except Exception:
                feedback.config(text=f"No pude interpretar la respuesta. Pista: {hint}", fg="#a33a22")
        ttk.Button(win, text="Comprobar respuesta", command=check).pack(pady=4)

    def error(self, error):
        messagebox.showwarning("No se pudo resolver", f"Revisa la expresión e inténtalo de nuevo.\n\nDetalle: {error}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MathBotApp(root)
    root.mainloop()
