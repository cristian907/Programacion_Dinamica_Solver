"""
Pestaña de Fundamento Teórico del Modelo.
Documenta rigurosamente el modelo de Programación Dinámica, la formulación matemática
y la justificación analítica del algoritmo de Bellman.
"""

import customtkinter as ctk


class TheoryTab(ctk.CTkScrollableFrame):
    """Pestaña con la documentación matemática y teórica del problema."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # 1. Título General
        header_card = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=10)
        header_card.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(
            header_card,
            text="📚 Marco Teórico: Modelo de Tamaño de la Fuerza de Trabajo",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3498db",
        ).pack(padx=15, pady=(12, 4), anchor="w")

        ctk.CTkLabel(
            header_card,
            text="Programación Dinámica Determinística — Basado en Investigación de Operaciones (Hamdy A. Taha)",
            font=ctk.CTkFont(size=12),
            text_color="#bdc3c7",
        ).pack(padx=15, pady=(0, 12), anchor="w")

        # 2. Tarjeta: Principio de Optimalidad de Bellman
        c1 = self._create_card("1. Principio de Optimalidad de Bellman")
        p1 = (
            "En 1957, Richard Bellman formuló el Principio de Optimalidad:\n"
            "«Una política óptima tiene la propiedad de que, cualesquiera que sean el estado y las decisiones\n"
            "iniciales, las decisiones restantes deben constituir una política óptima con respecto al estado\n"
            "resultante de la primera decisión».\n\n"
            "En este modelo de fuerza laboral, esto nos permite descomponer un problema complejo de 5 semanas\n"
            "en 5 subproblemas encadenados de 1 sola semana, resolviendo recursivamente de atrás hacia adelante."
        )
        self._add_content(c1, p1)

        # 3. Tarjeta: Elementos Formales del Modelo
        c2 = self._create_card("2. Definición Formal de Elementos del Modelo")
        p2 = (
            "• ETAPAS (i):\n"
            "  Representan cada una de las semanas del proyecto (i = 1, 2, 3, 4, 5).\n\n"
            "• VARIABLE DE ESTADO (x_{i-1}):\n"
            "  Cantidad de obreros disponibles al inicio de la semana i (heredados de la semana i-1).\n"
            "  Para la primera semana, se define la condición inicial x_0 = 0 trabajadores.\n\n"
            "• VARIABLE DE DECISIÓN (x_i):\n"
            "  Cantidad de obreros empleados y asignados durante la semana i.\n"
            "  Restricción esencial: x_i >= b_i (se debe satisfacer obligatoriamente la demanda b_i).\n"
            "  Cota superior práctica: x_i <= max_{k >= i} { b_k } = 8 trabajadores."
        )
        self._add_content(c2, p2)

        # 4. Tarjeta: Funciones de Costo y Ecuación Recursiva
        c3 = self._create_card("3. Funciones de Costo y Ecuación de Recurrencia")
        p3 = (
            "• Costo de Mano de Obra Excedente:\n"
            "  C_exceso(x_i) = C1 * (x_i - b_i)   [con C1 = $300 por trabajador/semana]\n\n"
            "• Costo de Nueva Contratación:\n"
            "  C_contr(x_{i-1}, x_i) = K + c * (x_i - x_{i-1})  si x_i > x_{i-1}\n"
            "  C_contr(x_{i-1}, x_i) = $0                        si x_i <= x_{i-1}\n"
            "  [con costo fijo K = $400 y costo marginal c = $200 por trabajador contratado]\n\n"
            "• Ecuación Recursiva Hacia Atrás (Backward Recursion):\n"
            "  f_i(x_{i-1}) = min { C_exceso(x_i) + C_contr(x_{i-1}, x_i) + f_{i+1}(x_i) }\n"
            "  con condición terminal: f_{6}(x_5) = 0."
        )
        self._add_content(c3, p3)

        # 5. Tarjeta: Análisis del Trade-Off Económico
        c4 = self._create_card("4. El Compromiso Económico (Trade-off) y Solución Óptima")
        p4 = (
            "¿Por qué la política óptima retiene obreros en vez de contratar estrictamente lo necesario?\n\n"
            "• En la Semana 2 (demanda 7), el contratista contrata 3 trabajadores para tener 8.\n"
            "  Esto incurre en un costo de excedente de $300 en la semana 2, pero evita incurrir\n"
            "  en el costo fijo de contratación de $400 en la semana 3 (demanda 8).\n"
            "  Ahorro neto: $400 - $300 = $100.\n\n"
            "• En la Semana 4 (demanda 4), el contratista despide/reduce hasta 6 obreros (no hasta 4).\n"
            "  Paga $600 por conservar 2 obreros ociosos durante la semana 4, pero evita tener que contratar\n"
            "  2 trabajadores en la Semana 5 (demanda 6), lo cual habría costado $400 + 2*$200 = $800.\n"
            "  Ahorro neto: $800 - $600 = $200.\n\n"
            "• Resultado Global Óptimo:\n"
            "  El costo total mínimo obtenido es de $3,300.00."
        )
        self._add_content(c4, p4)

    def _create_card(self, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=10)
        card.pack(fill="x", padx=10, pady=6)
        lbl = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71",
        )
        lbl.pack(padx=15, pady=(10, 4), anchor="w")
        return card

    def _add_content(self, card: ctk.CTkFrame, text: str) -> None:
        lbl = ctk.CTkLabel(
            card,
            text=text,
            font=ctk.CTkFont(size=11),
            text_color="#ecf0f1",
            justify="left",
        )
        lbl.pack(padx=15, pady=(0, 12), anchor="w")
