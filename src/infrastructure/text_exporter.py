"""
Módulo del exportador de reportes en archivo de texto (Infraestructura).
Genera un informe completo, riguroso y detallado con todas las etapas de programación
dinámica paso por paso y el plan óptimo final.
"""

import os
from datetime import datetime
from src.domain.entities import OptimizationResult, StageTable
from src.application.interfaces import IReportExporter


class TextReportExporter(IReportExporter):
    """Generador de reportes en formato texto (.txt)."""

    def export(self, result: OptimizationResult, target_path: str) -> str:
        """Genera el contenido del reporte y lo guarda en disco."""
        directory = os.path.dirname(target_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        content = self.generate_report_string(result)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return os.path.abspath(target_path)

    def generate_report_string(self, result: OptimizationResult) -> str:
        """Construye la cadena de texto con el informe completo formateado."""
        params = result.parameters
        lines = []

        # Encabezado Académico
        lines.append("=" * 88)
        lines.append("UNIVERSIDAD JOSÉ ANTONIO PÁEZ")
        lines.append("FACULTAD DE INGENIERÍA - ESCUELA DE COMPUTACIÓN")
        lines.append("MÉTODOS CUANTITATIVOS / INVESTIGACIÓN DE OPERACIONES")
        lines.append("MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO (PROGRAMACIÓN DINÁMICA)")
        lines.append("=" * 88)
        lines.append(f"Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 1. Enunciado y Parámetros
        lines.append("-" * 88)
        lines.append("1. DEFINICIÓN DEL PROBLEMA Y PARÁMETROS DE ENTRADA")
        lines.append("-" * 88)
        lines.append("Un contratista estima la fuerza de trabajo necesaria durante las siguientes 5 semanas.")
        lines.append(f"Demandas semanales (b_i): {list(params.demands)}")
        for idx, d in enumerate(params.demands, start=1):
            lines.append(f"  • Semana {idx} (b_{idx}): {d} trabajadores")
        lines.append("")
        lines.append(f"Costo por excedente de mano de obra (C1): ${params.excess_holding_cost:,.2f} / trabajador / semana")
        lines.append(f"Costo fijo por contratación (K):         ${params.hiring_fixed_cost:,.2f} por evento")
        lines.append(f"Costo variable por contratación (c):     ${params.hiring_variable_cost:,.2f} / trabajador contratado")
        lines.append(f"Fuerza de trabajo inicial (x0):          {params.initial_workforce} trabajadores")
        lines.append(f"Cota máxima efectiva evaluada:           {params.effective_max_workforce} trabajadores")
        lines.append("")

        # 2. Formulación Matemática
        lines.append("-" * 88)
        lines.append("2. FORMULACIÓN DEL MODELO DE PROGRAMACIÓN DINÁMICA")
        lines.append("-" * 88)
        lines.append("• Etapas (i): Semanas del proyecto, con i = 1, 2, ..., N (N = 5 semanas).")
        lines.append("• Variable de Estado (x_{i-1}): Número de trabajadores disponibles de la semana anterior.")
        lines.append("• Variable de Decisión (x_i): Número de trabajadores empleados en la semana i actual.")
        lines.append("  Restricción de factibilidad: x_i >= b_i (debe cubrirse la demanda mínima).")
        lines.append("")
        lines.append("• Funciones de Costo Inmediato:")
        lines.append("  - Costo de mano de obra excedente: C_exceso(x_i) = C1 * (x_i - b_i)")
        lines.append("  - Costo de contratación:           C_contr(x_{i-1}, x_i) = K + c*(x_i - x_{i-1}) si x_i > x_{i-1}, sino 0")
        lines.append("  - Costo de etapa:                  g_i(x_{i-1}, x_i) = C_exceso(x_i) + C_contr(x_{i-1}, x_i)")
        lines.append("")
        lines.append("• Ecuación Recursiva de Bellman (Hacia Atrás):")
        lines.append("  f_i(x_{i-1}) = min { g_i(x_{i-1}, x_i) + f_{i+1}(x_i) } para x_i >= b_i")
        lines.append("  Condición de frontera: f_{N+1}(x_N) = 0")
        lines.append("")

        # 3. Tablas de Programación Dinámica Etapa por Etapa
        lines.append("-" * 88)
        lines.append("3. DESARROLLO PASO A PASO POR ETAPAS (RECURSIÓN HACIA ATRÁS)")
        lines.append("-" * 88)

        for stage in result.stages:
            sn = stage.stage_number
            lines.append("")
            lines.append(f">>> ETAPA {sn} (SEMANA {sn}) - Demanda Requerida b_{sn} = {stage.demand} trabajadores")
            lines.append("~" * 88)
            header = (
                f"{'x_{' + str(sn-1) + '}':^6} | "
                f"{'x_' + str(sn):^5} | "
                f"{'Exceso':^6} | "
                f"{'C_Exceso':^9} | "
                f"{'Contr.':^6} | "
                f"{'C_Contr':^9} | "
                f"{'C_Etapa':^9} | "
                f"{'f_{' + str(sn+1) + '}':^9} | "
                f"{'Total':^9} | "
                f"{'Óptimo?':^7}"
            )
            lines.append(header)
            lines.append("-" * len(header))

            # Ordenar evaluaciones por estado y luego decisión
            sorted_evals = sorted(stage.evaluations, key=lambda e: (e.state_prev, e.decision_curr))
            curr_state = None
            for ev in sorted_evals:
                if curr_state is not None and ev.state_prev != curr_state:
                    lines.append("-" * len(header))
                curr_state = ev.state_prev

                opt_marker = "  ***  " if ev.is_optimal else ""
                row_str = (
                    f"{ev.state_prev:^6} | "
                    f"{ev.decision_curr:^5} | "
                    f"{ev.excess_workers:^6} | "
                    f"${ev.excess_cost:>7.0f} | "
                    f"{ev.hired_workers:^6} | "
                    f"${ev.hiring_cost:>7.0f} | "
                    f"${ev.stage_immediate_cost:>7.0f} | "
                    f"${ev.future_cost:>7.0f} | "
                    f"${ev.total_cost:>7.0f} | "
                    f"{opt_marker:^7}"
                )
                lines.append(row_str)

            lines.append("-" * len(header))
            lines.append(f"Resumen de Óptimos para Etapa {sn}:")
            for st in stage.get_distinct_states():
                opts = stage.get_optimal_decisions(st)
                cost = stage.get_optimal_cost(st)
                lines.append(f"  • Si x_{sn-1} = {st:2d}  ===>  x_{sn}* = {opts} con Costo Mínimo f_{sn}({st}) = ${cost:,.2f}")
            lines.append("")

        # 4. Plan Óptimo de la Fuerza Laboral
        lines.append("=" * 88)
        lines.append("4. POLÍTICA Y PLAN DE FUERZA DE TRABAJO ÓPTIMO (TRAYECTORIA FINAL)")
        lines.append("=" * 88)
        plan_header = (
            f"{'Semana':^7} | "
            f"{'Demanda':^7} | "
            f"{'Disp.(x_{i-1})':^13} | "
            f"{'Asign.(x_i*)':^12} | "
            f"{'Contratados':^11} | "
            f"{'Excedente':^9} | "
            f"{'C.Contrat':^10} | "
            f"{'C.Exced':^9} | "
            f"{'C.Semanal':^10} | "
            f"{'C.Acumulado':^11}"
        )
        lines.append(plan_header)
        lines.append("-" * len(plan_header))

        for step in result.optimal_policy:
            row_plan = (
                f"{step.week:^7} | "
                f"{step.demand:^7} | "
                f"{step.workforce_start:^13} | "
                f"{step.workforce_assigned:^12} | "
                f"{step.hired_count:^11} | "
                f"{step.excess_count:^9} | "
                f"${step.hiring_cost:>8.2f} | "
                f"${step.excess_cost:>7.2f} | "
                f"${step.stage_cost:>8.2f} | "
                f"${step.accumulated_cost:>9.2f}"
            )
            lines.append(row_plan)

        lines.append("-" * len(plan_header))
        lines.append("")
        lines.append(f"COSTO TOTAL MÍNIMO DE LA OPERACIÓN: ${result.total_minimal_cost:,.2f}")
        lines.append("")

        # Explicación de Decisiones Gerenciales
        lines.append("-" * 88)
        lines.append("5. ANÁLISIS Y CONCLUSIONES GERENCIALES")
        lines.append("-" * 88)
        lines.append("• En la Semana 1: Se parte con 0 trabajadores y se contratan 5 para cubrir la demanda b_1 = 5.")
        lines.append("  Costo: Fijo $400 + (5 * $200) = $1,400.")
        lines.append("• En la Semana 2: La demanda sube a 7, pero la política óptima contrata 3 trabajadores adicionales")
        lines.append("  elevando la plantilla a 8 (cubriendo la demanda máxima de la semana 3 por adelantado).")
        lines.append("  Esto evita incurrir nuevamente en el costo fijo de contratación ($400) en la semana 3,")
        lines.append("  compensando con creces el costo de retener 1 trabajador en exceso ($300) en la semana 2.")
        lines.append("• En la Semana 3: Se mantienen los 8 trabajadores sin nuevas contrataciones ni excedentes (Costo = $0).")
        lines.append("• En la Semana 4: La demanda cae a 4. El contratista reduce la fuerza laboral a 6 (no a 4),")
        lines.append("  conservando 2 trabajadores excedentes (Costo = 2 * $300 = $600). Esta decisión previene")
        lines.append("  tener que re-contratar en la Semana 5 cuando la demanda vuelva a subir a 6 (ahorrando $800 de contratación).")
        lines.append("• En la Semana 5: Se mantienen exactamente los 6 trabajadores requeridos (Costo = $0).")
        lines.append(f"• Total acumulado óptimo: ${result.total_minimal_cost:,.2f}.")
        lines.append("=" * 88)

        return "\n".join(lines)
