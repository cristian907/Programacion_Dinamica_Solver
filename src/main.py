"""
Punto de Entrada Principal (Main Entry Point).
Configura el contenedor de inyección de dependencias (Clean Architecture)
e inicia la aplicación en modo Interfaz Gráfica (GUI) o Consola (CLI).
"""

import sys
import os
import argparse
from typing import Optional

# Asegurar que el directorio raíz del proyecto esté en el path de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.dp_solver import DynamicProgrammingWorkforceSolver
from src.infrastructure.text_exporter import TextReportExporter
from src.application.use_cases import (
    SolveWorkforceModelUseCase,
    ExportReportUseCase,
    GetDefaultProblemUseCase,
)
from src.presentation.controllers import WorkforceController


def build_controller() -> WorkforceController:
    """Ensambla las dependencias respetando el principio de inversión de dependencias."""
    solver = DynamicProgrammingWorkforceSolver()
    exporter = TextReportExporter()

    solve_use_case = SolveWorkforceModelUseCase(solver=solver)
    export_use_case = ExportReportUseCase(exporter=exporter)
    default_problem_use_case = GetDefaultProblemUseCase()

    return WorkforceController(
        solve_use_case=solve_use_case,
        export_use_case=export_use_case,
        default_problem_use_case=default_problem_use_case,
    )


def run_cli_mode(controller: WorkforceController, export_path: Optional[str] = None) -> int:
    """Ejecuta el modelo en la consola y opcionalmente exporta el reporte a archivo."""
    print("=" * 80)
    print("UNIVERSIDAD JOSÉ ANTONIO PÁEZ - ESCUELA DE COMPUTACIÓN")
    print("RESOLUCIÓN POR PROGRAMACIÓN DINÁMICA: MODELO DE FUERZA DE TRABAJO")
    print("=" * 80)

    default_dto = controller.get_default_parameters()
    result, err = controller.solve(
        demands=default_dto.demands,
        excess_cost=default_dto.excess_holding_cost,
        hiring_fixed=default_dto.hiring_fixed_cost,
        hiring_var=default_dto.hiring_variable_cost,
        initial_workforce=default_dto.initial_workforce,
    )

    if err or result is None:
        print(f"[ERROR]: {err}")
        return 1

    exporter = TextReportExporter()
    print(exporter.generate_report_string(result))

    target = export_path or "salidas_problema.txt"
    success, msg = controller.export_report(target)
    print("\n" + "-" * 80)
    print(msg)
    print("-" * 80)
    return 0


def run_gui_mode(controller: WorkforceController) -> int:
    """Inicia la interfaz gráfica moderna en CustomTkinter."""
    try:
        from src.presentation.views.main_window import MainWindow

        # También pre-generamos el archivo salidas_problema.txt por conveniencia del estudiante
        default_dto = controller.get_default_parameters()
        res, _ = controller.solve(
            demands=default_dto.demands,
            excess_cost=default_dto.excess_holding_cost,
            hiring_fixed=default_dto.hiring_fixed_cost,
            hiring_var=default_dto.hiring_variable_cost,
            initial_workforce=default_dto.initial_workforce,
        )
        if res:
            controller.export_report("salidas_problema.txt")

        app = MainWindow(controller=controller)
        app.mainloop()
        return 0
    except Exception as e:
        print(f"[AVISO]: No se pudo iniciar el entorno gráfico ({e}). Iniciando en modo consola...")
        return run_cli_mode(controller)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Modelo de Tamaño de la Fuerza de Trabajo en Programación Dinámica (UJAP)"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Ejecutar en modo consola e imprimir todas las tablas paso por paso.",
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Ruta donde guardar el reporte en texto (por defecto: salidas_problema.txt).",
    )
    args = parser.parse_args()

    controller = build_controller()

    if args.cli or args.export:
        sys.exit(run_cli_mode(controller, args.export))
    else:
        # Modo GUI por defecto
        # Si no hay variable DISPLAY, caer a CLI limpiamente
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            print("[INFO]: No se detectó servidor de pantalla gráfico. Ejecutando en consola...")
            sys.exit(run_cli_mode(controller))
        else:
            sys.exit(run_gui_mode(controller))


if __name__ == "__main__":
    main()
