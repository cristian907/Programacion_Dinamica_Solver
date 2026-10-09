"""
Pestaña de Etapas Paso a Paso de Programación Dinámica.
Permite inspeccionar cada etapa (de la 5 a la 1) con sus tablas completas de evaluación
de estados y decisiones, resaltando las alternativas óptimas.
"""

import customtkinter as ctk
from typing import Optional, List
from src.domain.entities import OptimizationResult, StageTable
from ..components.table_view import ModernTableView


class StagesTab(ctk.CTkFrame):
    """Pestaña para visualizar las tablas de cada etapa de la recursión hacia atrás."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._current_result: Optional[OptimizationResult] = None
        self._current_stage_idx: int = 0  # 0 corresponds to first stage in backward list (Stage N)

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Barra Superior: Selector de Etapa y Navegación
        top_bar = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=10)
        top_bar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            top_bar,
            text="◀ Anterior",
            width=100,
            command=self._on_prev_stage,
            fg_color="#34495e",
            hover_color="#2c3e50",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.prev_btn.grid(row=0, column=0, padx=10, pady=10)

        # Selector segmentado de etapas
        self.stage_seg = ctk.CTkSegmentedButton(
            top_bar,
            values=["Etapa 5", "Etapa 4", "Etapa 3", "Etapa 2", "Etapa 1"],
            command=self._on_segment_selected,
            selected_color="#2980b9",
            selected_hover_color="#1f618d",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.stage_seg.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.next_btn = ctk.CTkButton(
            top_bar,
            text="Siguiente ▶",
            width=100,
            command=self._on_next_stage,
            fg_color="#34495e",
            hover_color="#2c3e50",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.next_btn.grid(row=0, column=2, padx=10, pady=10)

        # Encabezado Informativo de la Etapa
        self.info_card = ctk.CTkFrame(self, fg_color="#1e2124", corner_radius=8)
        self.info_card.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.info_card.grid_columnconfigure(0, weight=1)

        self.stage_title_lbl = ctk.CTkLabel(
            self.info_card,
            text="Etapa Seleccionada",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db",
        )
        self.stage_title_lbl.grid(row=0, column=0, padx=15, pady=(8, 2), sticky="w")

        self.stage_formula_lbl = ctk.CTkLabel(
            self.info_card,
            text="Ecuación de Bellman: f_i(x_{i-1}) = min { g_i(x_{i-1}, x_i) + f_{i+1}(x_i) }",
            font=ctk.CTkFont(size=12),
            text_color="#bdc3c7",
        )
        self.stage_formula_lbl.grid(row=1, column=0, padx=15, pady=(0, 8), sticky="w")

        # Tabla Moderna con Evaluaciones
        table_columns = [
            ("state_prev", "Estado Inicial (x_{i-1})", 140),
            ("decision", "Decisión (x_i)", 100),
            ("demand", "Demanda (b_i)", 100),
            ("excess", "Exceso", 80),
            ("excess_cost", "Costo Exceso ($)", 120),
            ("hired", "Contratados", 100),
            ("hiring_cost", "Costo Contr. ($)", 120),
            ("immediate_cost", "C. Etapa ($)", 100),
            ("future_cost", "C. Futuro f_{i+1} ($)", 130),
            ("total_cost", "Costo Total ($)", 110),
            ("is_optimal", "¿Es Óptimo?", 110),
        ]
        self.table = ModernTableView(self, columns=table_columns)
        self.table.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Panel Inferior: Resumen de Óptimos
        self.summary_card = ctk.CTkFrame(self, fg_color="#23272a", corner_radius=8)
        self.summary_card.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.summary_card.grid_columnconfigure(0, weight=1)

        self.summary_lbl = ctk.CTkLabel(
            self.summary_card,
            text="Resumen de Decisiones Óptimas para esta Etapa:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2ecc71",
        )
        self.summary_lbl.grid(row=0, column=0, padx=15, pady=(8, 4), sticky="w")

        self.summary_details_lbl = ctk.CTkLabel(
            self.summary_card,
            text="Ejecute la optimización para visualizar los cálculos paso a paso.",
            font=ctk.CTkFont(size=12),
            text_color="#ecf0f1",
            justify="left",
        )
        self.summary_details_lbl.grid(row=1, column=0, padx=15, pady=(0, 8), sticky="w")

    def display_result(self, result: OptimizationResult) -> None:
        """Actualiza la pestaña con los resultados de la optimización."""
        self._current_result = result
        if not result.stages:
            return

        # Actualizar opciones del segmented button
        stage_names = [f"Etapa {s.stage_number}" for s in result.stages]
        self.stage_seg.configure(values=stage_names)
        self._current_stage_idx = 0
        self.stage_seg.set(stage_names[0])

        self._render_current_stage()

    def _render_current_stage(self) -> None:
        if not self._current_result or not self._current_result.stages:
            return

        stages = self._current_result.stages
        idx = max(0, min(self._current_stage_idx, len(stages) - 1))
        stage = stages[idx]
        sn = stage.stage_number

        # Actualizar segmented button
        stage_names = [f"Etapa {s.stage_number}" for s in stages]
        self.stage_seg.set(stage_names[idx])

        # Actualizar encabezado
        self.stage_title_lbl.configure(
            text=f"ETAPA {sn} (Semana {sn}) — Demanda Requerida b_{sn} = {stage.demand} trabajadores"
        )
        future_idx = sn + 1
        future_term = f"f_{future_idx}(x_{sn})" if sn < len(stages) else "0 (Frontera final)"
        self.stage_formula_lbl.configure(
            text=f"Ecuación recursiva: f_{sn}(x_{sn-1}) = min [ C_exceso(x_{sn}) + C_contr(x_{sn-1}, x_{sn}) + {future_term} ]"
        )

        # Rellenar tabla
        rows_data = []
        is_opt_flags = []

        sorted_evals = sorted(stage.evaluations, key=lambda e: (e.state_prev, e.decision_curr))
        for ev in sorted_evals:
            opt_str = "★ ÓPTIMO" if ev.is_optimal else ""
            rows_data.append((
                f"x_{sn-1} = {ev.state_prev}",
                f"{ev.decision_curr}",
                f"{ev.demand}",
                f"{ev.excess_workers}",
                f"${ev.excess_cost:,.0f}",
                f"{ev.hired_workers}",
                f"${ev.hiring_cost:,.0f}",
                f"${ev.stage_immediate_cost:,.0f}",
                f"${ev.future_cost:,.0f}",
                f"${ev.total_cost:,.0f}",
                opt_str,
            ))
            is_opt_flags.append(ev.is_optimal)

        self.table.set_rows(rows_data, is_opt_flags)

        # Rellenar resumen de óptimos
        summary_lines = []
        for state in stage.get_distinct_states():
            opts = stage.get_optimal_decisions(state)
            cost = stage.get_optimal_cost(state)
            opts_str = ", ".join(str(o) for o in opts)
            summary_lines.append(
                f"• Si el personal entrante es x_{sn-1} = {state}  ➔  Decisión Óptima x_{sn}* = {opts_str}  (Costo f_{sn}({state}) = ${cost:,.2f})"
            )
        self.summary_details_lbl.configure(text="\n".join(summary_lines))

    def _on_segment_selected(self, value: str) -> None:
        if not self._current_result:
            return
        stage_names = [f"Etapa {s.stage_number}" for s in self._current_result.stages]
        if value in stage_names:
            self._current_stage_idx = stage_names.index(value)
            self._render_current_stage()

    def _on_prev_stage(self) -> None:
        if not self._current_result:
            return
        if self._current_stage_idx > 0:
            self._current_stage_idx -= 1
            self._render_current_stage()

    def _on_next_stage(self) -> None:
        if not self._current_result:
            return
        if self._current_stage_idx < len(self._current_result.stages) - 1:
            self._current_stage_idx += 1
            self._render_current_stage()
