"""
Módulo de generación de gráficos analíticos (Infraestructura).
Crea visualizaciones modernas utilizando matplotlib para incrustar en la GUI.
"""

from typing import Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from src.domain.entities import OptimizationResult


class ChartService:
    """Generador de gráficos estadísticos y comparativos para la solución del modelo."""

    @staticmethod
    def create_workforce_figure(result: OptimizationResult) -> Figure:
        """
        Genera una figura con 2 subgráficos:
        1. Comparación entre Demanda Requerida (b_i) y Fuerza Laboral Asignada (x_i*).
        2. Desglose de Costos Semanales (Contratación vs Excedente) y Costo Acumulado.
        """
        policy = result.optimal_policy
        weeks = [f"Semana {p.week}" for p in policy]
        demands = [p.demand for p in policy]
        assigned = [p.workforce_assigned for p in policy]
        hiring_costs = [p.hiring_cost for p in policy]
        excess_costs = [p.excess_cost for p in policy]
        acc_costs = [p.accumulated_cost for p in policy]

        # Estilo visual moderno y limpio
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=100)
        fig.patch.set_facecolor("#1e2124")

        for ax in (ax1, ax2):
            ax.set_facecolor("#282b30")
            ax.tick_params(colors="#e0e0e0")
            ax.xaxis.label.set_color("#e0e0e0")
            ax.yaxis.label.set_color("#e0e0e0")
            ax.title.set_color("#ffffff")
            for spine in ax.spines.values():
                spine.set_color("#424549")
            ax.grid(color="#424549", linestyle="--", linewidth=0.6, alpha=0.7)

        # Gráfico 1: Demanda vs Asignados
        x_indices = list(range(len(weeks)))
        width = 0.35

        bars1 = ax1.bar(
            [x - width / 2 for x in x_indices],
            demands,
            width=width,
            label="Demanda Requerida (b_i)",
            color="#3498db",
            edgecolor="#2980b9",
            alpha=0.9,
        )
        bars2 = ax1.bar(
            [x + width / 2 for x in x_indices],
            assigned,
            width=width,
            label="Trabajadores Asignados (x_i*)",
            color="#2ecc71",
            edgecolor="#27ae60",
            alpha=0.9,
        )

        # Valores sobre las barras
        for bar in bars1:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.1, f"{int(h)}",
                     ha="center", va="bottom", color="#ffffff", fontsize=9, fontweight="bold")

        for bar in bars2:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.1, f"{int(h)}",
                     ha="center", va="bottom", color="#ffffff", fontsize=9, fontweight="bold")

        ax1.set_xticks(x_indices)
        ax1.set_xticklabels(weeks, fontsize=9)
        ax1.set_ylabel("Cantidad de Trabajadores", fontsize=10)
        ax1.set_title("Demanda Requerida vs Fuerza Laboral Asignada", fontsize=11, fontweight="bold")
        ax1.legend(facecolor="#1e2124", edgecolor="#424549", labelcolor="#e0e0e0", fontsize=9)
        ax1.set_ylim(0, max(max(demands), max(assigned)) + 2)

        # Gráfico 2: Desglose de Costos Semanales y Acumulado
        b_hiring = ax2.bar(
            x_indices,
            hiring_costs,
            width=0.45,
            label="Costo Contratación ($)",
            color="#e74c3c",
            edgecolor="#c0392b",
            alpha=0.85,
        )
        b_excess = ax2.bar(
            x_indices,
            excess_costs,
            bottom=hiring_costs,
            width=0.45,
            label="Costo Excedente ($)",
            color="#f39c12",
            edgecolor="#d35400",
            alpha=0.85,
        )

        # Línea de Costo Acumulado en eje secundario
        ax2_sec = ax2.twinx()
        ax2_sec.plot(x_indices, acc_costs, color="#9b59b6", marker="o", linewidth=2.2, label="Costo Acumulado ($)")
        ax2_sec.tick_params(colors="#d2b4de")
        ax2_sec.set_ylabel("Costo Acumulado ($)", color="#d2b4de", fontsize=10)
        ax2_sec.spines["right"].set_color("#8e44ad")
        ax2_sec.spines["left"].set_color("#424549")
        ax2_sec.spines["top"].set_color("#424549")
        ax2_sec.spines["bottom"].set_color("#424549")

        ax2.set_xticks(x_indices)
        ax2.set_xticklabels(weeks, fontsize=9)
        ax2.set_ylabel("Costo Semanal Incurrido ($)", fontsize=10)
        ax2.set_title("Estructura de Costos por Semana", fontsize=11, fontweight="bold")

        # Unificar leyendas
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_sec.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, facecolor="#1e2124", edgecolor="#424549", labelcolor="#e0e0e0", fontsize=8.5, loc="upper right")

        fig.tight_layout()
        return fig
