"""
Pestaña del Plan Óptimo de Fuerza Laboral y Análisis de Costos.
Presenta la trayectoria óptima reconstruida (forward traceback), tarjetas de métricas
y el desglose analítico de las decisiones gerenciales.
"""

import customtkinter as ctk
from typing import Optional
from src.domain.entities import OptimizationResult
from ..components.table_view import ModernTableView


class OptimalPlanTab(ctk.CTkFrame):
    """Pestaña con la política óptima global y las métricas finales."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._current_result: Optional[OptimizationResult] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Fila de Tarjetas de Métricas (KPI Cards)
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        # Card 1: Costo Total Mínimo
        self.kpi_cost = self._create_kpi_card(cards_frame, 0, "💰 Costo Total Mínimo", "$0.00", "#2ecc71")
        # Card 2: Contrataciones Totales
        self.kpi_hires = self._create_kpi_card(cards_frame, 1, "👥 Total Contratados", "0 trab.", "#3498db")
        # Card 3: Excedente Total
        self.kpi_excess = self._create_kpi_card(cards_frame, 2, "⏱️ Excedente Retenido", "0 trab/sem", "#f39c12")
        # Card 4: Semanas Planificadas
        self.kpi_weeks = self._create_kpi_card(cards_frame, 3, "📅 Horizonte Planificado", "5 semanas", "#9b59b6")

        # 2. Título de la Tabla
        table_title_card = ctk.CTkFrame(self, fg_color="#1e2124", corner_radius=8)
        table_title_card.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        table_title_lbl = ctk.CTkLabel(
            table_title_card,
            text="📊 Cronograma Semanal y Desglose de Costos de la Política Óptima",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
        )
        table_title_lbl.pack(padx=15, pady=8, anchor="w")

        # 3. Tabla Moderna con la Política Óptima
        plan_columns = [
            ("week", "Semana", 80),
            ("demand", "Demanda (b_i)", 100),
            ("start", "Disponible (x_{i-1})", 130),
            ("assigned", "Asignado (x_i*)", 120),
            ("hired", "Contratados", 100),
            ("excess", "Excedente", 90),
            ("cost_hire", "Costo Contr. ($)", 120),
            ("cost_excess", "Costo Exced. ($)", 120),
            ("cost_week", "Costo Semanal ($)", 130),
            ("cost_acc", "Costo Acumulado ($)", 140),
        ]
        self.plan_table = ModernTableView(self, columns=plan_columns)
        self.plan_table.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # 4. Panel Inferior de Análisis Gerencial
        analysis_card = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=10)
        analysis_card.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        analysis_card.grid_columnconfigure(0, weight=1)

        analysis_title = ctk.CTkLabel(
            analysis_card,
            text="💡 Justificación Económica de las Decisiones (Trade-offs)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3498db",
        )
        analysis_title.pack(padx=15, pady=(8, 2), anchor="w")

        self.analysis_body = ctk.CTkLabel(
            analysis_card,
            text="Ejecute la optimización para visualizar el análisis estratégico del plan.",
            font=ctk.CTkFont(size=11),
            text_color="#ecf0f1",
            justify="left",
        )
        self.analysis_body.pack(padx=15, pady=(0, 10), anchor="w")

    def _create_kpi_card(self, parent: ctk.CTkFrame, col: int, title: str, default_val: str, accent_color: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color="#23272a", corner_radius=10)
        card.grid(row=0, column=col, padx=4, pady=2, sticky="ew")

        t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#bdc3c7")
        t_lbl.pack(padx=10, pady=(8, 0))

        v_lbl = ctk.CTkLabel(
            card,
            text=default_val,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=accent_color,
        )
        v_lbl.pack(padx=10, pady=(0, 8))
        return v_lbl

    def display_result(self, result: OptimizationResult) -> None:
        """Actualiza la vista con el plan óptimo."""
        self._current_result = result
        policy = result.optimal_policy

        total_hires = sum(p.hired_count for p in policy)
        total_excess = sum(p.excess_count for p in policy)

        # Actualizar KPIs
        self.kpi_cost.configure(text=f"${result.total_minimal_cost:,.2f}")
        self.kpi_hires.configure(text=f"{total_hires} trab.")
        self.kpi_excess.configure(text=f"{total_excess} trab/sem")
        self.kpi_weeks.configure(text=f"{len(policy)} semanas")

        # Rellenar tabla
        rows = []
        is_opt = []
        for step in policy:
            rows.append((
                f"Semana {step.week}",
                f"{step.demand}",
                f"{step.workforce_start}",
                f"{step.workforce_assigned}",
                f"{step.hired_count}",
                f"{step.excess_count}",
                f"${step.hiring_cost:,.2f}",
                f"${step.excess_cost:,.2f}",
                f"${step.stage_cost:,.2f}",
                f"${step.accumulated_cost:,.2f}",
            ))
            is_opt.append(True)

        self.plan_table.set_rows(rows, is_opt)

        # Explicación del compromiso de costos (trade-off)
        analysis_lines = [
            f"1. Costo Mínimo Obtenido: ${result.total_minimal_cost:,.2f} cubriendo el 100% de los requerimientos.",
            "2. Estrategia en Semana 2: Contratar 3 obreros para alcanzar 8 (demanda es 7). Paga $300 por 1 excedente,",
            "   pero ahorra $400 del costo fijo al no tener que contratar nuevamente en la Semana 3 (demanda = 8).",
            "3. Estrategia en Semana 4: Reducir personal a 6 en vez de 4. Retiene 2 obreros ($600 de excedente),",
            "   evitando el costo de contratación de $800 ($400 fijo + 2*$200) al comenzar la Semana 5 (demanda = 6).",
            "4. Conclusión: La Programación Dinámica anticipa demandas futuras optimizando el costo global del proyecto.",
        ]
        self.analysis_body.configure(text="\n".join(analysis_lines))
