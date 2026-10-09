"""
Módulo del Controlador de Presentación.
Gestiona la interacción entre la interfaz gráfica / CLI y los casos de uso de la aplicación.
"""

from typing import Sequence, Tuple, Optional
from src.domain.entities import OptimizationResult
from src.domain.exceptions import DomainValidationError
from src.application.dtos import SolveProblemDTO, ExportReportDTO
from src.application.use_cases import (
    SolveWorkforceModelUseCase,
    ExportReportUseCase,
    GetDefaultProblemUseCase,
)


class WorkforceController:
    """Controlador que orquesta la ejecución del modelo y la exportación de resultados."""

    def __init__(
        self,
        solve_use_case: SolveWorkforceModelUseCase,
        export_use_case: ExportReportUseCase,
        default_problem_use_case: GetDefaultProblemUseCase,
    ) -> None:
        self._solve_use_case = solve_use_case
        self._export_use_case = export_use_case
        self._default_problem_use_case = default_problem_use_case
        self._last_result: Optional[OptimizationResult] = None

    @property
    def last_result(self) -> Optional[OptimizationResult]:
        """Retorna el último resultado calculado."""
        return self._last_result

    def get_default_parameters(self) -> SolveProblemDTO:
        """Obtiene la configuración por defecto del problema de la UJAP."""
        return self._default_problem_use_case.execute()

    def solve(
        self,
        demands: Sequence[int],
        excess_cost: float,
        hiring_fixed: float,
        hiring_var: float,
        initial_workforce: int,
        max_capacity: Optional[int] = None,
    ) -> Tuple[Optional[OptimizationResult], Optional[str]]:
        """
        Ejecuta la optimización.
        Retorna (OptimizationResult, None) en éxito, o (None, mensaje_error) si ocurre un error.
        """
        try:
            dto = SolveProblemDTO(
                demands=tuple(demands),
                excess_holding_cost=float(excess_cost),
                hiring_fixed_cost=float(hiring_fixed),
                hiring_variable_cost=float(hiring_var),
                initial_workforce=int(initial_workforce),
                max_workforce_capacity=max_capacity,
            )
            result = self._solve_use_case.execute(dto)
            self._last_result = result
            return result, None
        except DomainValidationError as e:
            return None, f"Error de Validación: {str(e)}"
        except ValueError as e:
            return None, f"Error de Entrada: Verifique que todos los números sean válidos. ({str(e)})"
        except Exception as e:
            return None, f"Error Inesperado: {str(e)}"

    def export_report(self, target_path: str) -> Tuple[bool, str]:
        """
        Exporta el último resultado calculado al archivo indicado.
        Retorna (True, ruta) si tuvo éxito o (False, mensaje_error).
        """
        if self._last_result is None:
            return False, "No hay ningún resultado disponible para exportar. Ejecute la optimización primero."

        try:
            dto = ExportReportDTO(result=self._last_result, target_path=target_path)
            path = self._export_use_case.execute(dto)
            return True, f"Reporte exportado exitosamente en:\n{path}"
        except Exception as e:
            return False, f"Error al exportar reporte: {str(e)}"
