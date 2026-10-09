"""
Pestaña de Entrada y Configuración de Parámetros.
Permite ingresar o ajustar las demandas semanales, costos unitarios y mano de obra inicial.
"""

import customtkinter as ctk
from typing import Callable, List


class InputTab(ctk.CTkFrame):
    """Pestaña para parametrizar el modelo de programación dinámica."""

    def __init__(
        self,
        master: ctk.CTkFrame,
        on_solve_callback: Callable[[], None],
        on_reset_callback: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_solve = on_solve_callback
        self.on_reset = on_reset_callback

        self._build_ui()

    def _build_ui(self) -> None:
        # Contenedor con scroll si fuera necesario
        self.grid_columnconfigure((0, 1), weight=1, uniform="group")
        self.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo: Formularios de entrada
        left_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#23272a")
        left_card.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="nsew")
        left_card.grid_columnconfigure((0, 1), weight=1)

        # Título
        title_lbl = ctk.CTkLabel(
            left_card,
            text="⚙️ Parámetros del Modelo",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3498db",
        )
        title_lbl.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")

        # Demandas semanales (b_1 a b_5)
        demands_lbl = ctk.CTkLabel(
            left_card,
            text="Demandas Semanales Requeridas (b_i):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff",
        )
        demands_lbl.grid(row=1, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self.demand_entries: List[ctk.CTkEntry] = []
        demands_frame = ctk.CTkFrame(left_card, fg_color="#1e2124", corner_radius=8)
        demands_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=5, sticky="ew")

        default_b = [5, 7, 8, 4, 6]
        for i in range(5):
            demands_frame.grid_columnconfigure(i, weight=1)
            lbl = ctk.CTkLabel(
                demands_frame,
                text=f"Sem {i+1} (b_{i+1})",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#95a5a6",
            )
            lbl.grid(row=0, column=i, padx=4, pady=(6, 2))

            entry = ctk.CTkEntry(
                demands_frame,
                width=55,
                justify="center",
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            entry.insert(0, str(default_b[i]))
            entry.grid(row=1, column=i, padx=4, pady=(2, 8))
            self.demand_entries.append(entry)

        # Costos Unitarios
        cost_lbl = ctk.CTkLabel(
            left_card,
            text="Estructura de Costos del Problema:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff",
        )
        cost_lbl.grid(row=3, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        # Costo Excedente C1
        c1_lbl = ctk.CTkLabel(left_card, text="Costo Mano de Obra Excedente ($/trab/sem):", font=ctk.CTkFont(size=12))
        c1_lbl.grid(row=4, column=0, padx=15, pady=6, sticky="w")
        self.c1_entry = ctk.CTkEntry(left_card, width=120)
        self.c1_entry.insert(0, "300")
        self.c1_entry.grid(row=4, column=1, padx=15, pady=6, sticky="e")

        # Costo Fijo Contratación K
        k_lbl = ctk.CTkLabel(left_card, text="Costo Fijo de Contratación K ($/evento):", font=ctk.CTkFont(size=12))
        k_lbl.grid(row=5, column=0, padx=15, pady=6, sticky="w")
        self.k_entry = ctk.CTkEntry(left_card, width=120)
        self.k_entry.insert(0, "400")
        self.k_entry.grid(row=5, column=1, padx=15, pady=6, sticky="e")

        # Costo Variable Contratación c
        c_lbl = ctk.CTkLabel(left_card, text="Costo Variable Contratación c ($/trab):", font=ctk.CTkFont(size=12))
        c_lbl.grid(row=6, column=0, padx=15, pady=6, sticky="w")
        self.c_entry = ctk.CTkEntry(left_card, width=120)
        self.c_entry.insert(0, "200")
        self.c_entry.grid(row=6, column=1, padx=15, pady=6, sticky="e")

        # Fuerza Inicial x0
        x0_lbl = ctk.CTkLabel(left_card, text="Fuerza de Trabajo Inicial (x0):", font=ctk.CTkFont(size=12))
        x0_lbl.grid(row=7, column=0, padx=15, pady=6, sticky="w")
        self.x0_entry = ctk.CTkEntry(left_card, width=120)
        self.x0_entry.insert(0, "0")
        self.x0_entry.grid(row=7, column=1, padx=15, pady=6, sticky="e")

        # Botones de Acción
        btn_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, padx=15, pady=(20, 15), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.reset_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Restablecer UJAP",
            command=self.on_reset,
            fg_color="#34495e",
            hover_color="#2c3e50",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.reset_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.solve_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Resolver Modelo",
            command=self.on_solve,
            fg_color="#27ae60",
            hover_color="#229954",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.solve_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Panel Derecho: Tarjeta Informativa del Problema
        right_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#23272a")
        right_card.grid(row=0, column=1, padx=(10, 10), pady=10, sticky="nsew")
        right_card.grid_columnconfigure(0, weight=1)

        info_title = ctk.CTkLabel(
            right_card,
            text="📋 Enunciado Oficial (UJAP - 3 ptos)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2ecc71",
        )
        info_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        info_text = (
            "Un contratista estima que el tamaño de la fuerza de trabajo necesaria\n"
            "durante las siguientes 5 semanas es de:\n"
            "  • Semana 1:  b₁ = 5 trabajadores\n"
            "  • Semana 2:  b₂ = 7 trabajadores\n"
            "  • Semana 3:  b₃ = 8 trabajadores\n"
            "  • Semana 4:  b₄ = 4 trabajadores\n"
            "  • Semana 5:  b₅ = 6 trabajadores\n\n"
            "Costos Incurridos:\n"
            "  • Mano de obra excedente conservada: $300 por trabajador por semana.\n"
            "  • Nueva contratación en cualquier semana: costo fijo de $400 más\n"
            "    $200 por trabajador contratado.\n\n"
            "Objetivo de Optimización:\n"
            "Determinar el plan de contratación y tamaño de personal x_i para cada semana\n"
            "que minimice el costo total acumulado mediante Programación Dinámica."
        )

        info_box = ctk.CTkLabel(
            right_card,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            text_color="#ecf0f1",
        )
        info_box.grid(row=1, column=0, padx=15, pady=5, sticky="nw")

        # Nota de Clean Architecture
        arch_card = ctk.CTkFrame(right_card, fg_color="#1e2124", corner_radius=8)
        arch_card.grid(row=2, column=0, padx=15, pady=(15, 15), sticky="ew")

        arch_lbl = ctk.CTkLabel(
            arch_card,
            text=(
                "🏛️ Arquitectura Limpia Implementada:\n"
                "• Dominio: Entidades y reglas de negocio puras (WorkforceParameters)\n"
                "• Aplicación: Casos de uso desacoplados (SolveWorkforceModel)\n"
                "• Infraestructura: Algoritmo de Bellman y exportador TXT\n"
                "• Presentación: CustomTkinter GUI + CLI en Python POO"
            ),
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color="#bdc3c7",
        )
        arch_lbl.pack(padx=10, pady=10, anchor="w")

    def get_inputs(self) -> dict:
        """Obtiene y retorna los valores actuales de los campos de entrada."""
        demands = [int(entry.get().strip()) for entry in self.demand_entries]
        return {
            "demands": demands,
            "excess_cost": float(self.c1_entry.get().strip()),
            "hiring_fixed": float(self.k_entry.get().strip()),
            "hiring_var": float(self.c_entry.get().strip()),
            "initial_workforce": int(self.x0_entry.get().strip()),
        }

    def set_inputs(
        self,
        demands: List[int],
        excess_cost: float,
        hiring_fixed: float,
        hiring_var: float,
        initial_workforce: int,
    ) -> None:
        """Rellena los campos con los valores especificados."""
        for i, val in enumerate(demands):
            if i < len(self.demand_entries):
                self.demand_entries[i].delete(0, "end")
                self.demand_entries[i].insert(0, str(val))

        self.c1_entry.delete(0, "end")
        self.c1_entry.insert(0, str(int(excess_cost) if excess_cost.is_integer() else excess_cost))

        self.k_entry.delete(0, "end")
        self.k_entry.insert(0, str(int(hiring_fixed) if hiring_fixed.is_integer() else hiring_fixed))

        self.c_entry.delete(0, "end")
        self.c_entry.insert(0, str(int(hiring_var) if hiring_var.is_integer() else hiring_var))

        self.x0_entry.delete(0, "end")
        self.x0_entry.insert(0, str(initial_workforce))
