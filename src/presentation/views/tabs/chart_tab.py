"""
Pestaña de Gráficos Analíticos.
Incrusta la visualización de matplotlib en CustomTkinter para comparar demanda vs personal
y observar el desglose semanal de costos.
"""

import customtkinter as ctk
from typing import Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.domain.entities import OptimizationResult
from src.infrastructure.chart_service import ChartService


class ChartTab(ctk.CTkFrame):
    """Pestaña interactiva con gráficos de barras y curvas de costo acumulado."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._current_result: Optional[OptimizationResult] = None
        self._canvas: Optional[FigureCanvasTkAgg] = None
        self._toolbar: Optional[NavigationToolbar2Tk] = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Barra superior con descripción
        top_bar = ctk.CTkFrame(self, fg_color="#1e2124", corner_radius=8)
        top_bar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        lbl = ctk.CTkLabel(
            top_bar,
            text="📈 Visualización Gráfica: Demanda vs Asignación y Composición de Costos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
        )
        lbl.pack(padx=15, pady=8, anchor="w")

        # Contenedor para el Canvas
        self.chart_container = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=10)
        self.chart_container.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.chart_container.grid_columnconfigure(0, weight=1)
        self.chart_container.grid_rowconfigure(0, weight=1)

        self.placeholder_lbl = ctk.CTkLabel(
            self.chart_container,
            text="Haga clic en 'Resolver Modelo' en la primera pestaña para generar los gráficos interactivos.",
            font=ctk.CTkFont(size=13),
            text_color="#95a5a6",
        )
        self.placeholder_lbl.pack(expand=True)

    def display_result(self, result: OptimizationResult) -> None:
        """Genera e incrusta la nueva figura en el canvas."""
        self._current_result = result

        # Ocultar placeholder
        self.placeholder_lbl.pack_forget()

        # Limpiar canvas anterior si existía
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None

        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None

        # Crear nueva figura
        fig = ChartService.create_workforce_figure(result)

        # Incrustar en tkinter
        self._canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self._canvas.draw()
        canvas_widget = self._canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)
