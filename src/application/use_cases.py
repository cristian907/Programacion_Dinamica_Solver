"""
Módulo de Casos de Uso de la aplicación.
Orquesta el flujo de negocio invocando las entidades de dominio y los servicios de infraestructura.
"""

from typing import Tuple
from src.domain.entities import WorkforceParameters, OptimizationResult
from .interfaces import IWorkforceSolver, IReportExporter
from .dtos import SolveProblemDTO, ExportReportDTO


class SolveWorkforceModelUseCase:
    """Caso de uso principal: Resuelve el modelo de fuerza laboral mediante Programación Dinámica."""

    def __init__(self, solver: IWorkforceSolver) -> None:
        self._solver = solver

    def execute(self, dto: SolveProblemDTO) -> OptimizationResult:
        """
        Valida los parámetros de entrada creando la entidad de dominio y
        ejecuta la resolución algorítmica.
        """
        params = WorkforceParameters(
            demands=tuple(dto.demands),
            excess_holding_cost=float(dto.excess_holding_cost),
            hiring_fixed_cost=float(dto.hiring_fixed_cost),
            hiring_variable_cost=float(dto.hiring_variable_cost),
            initial_workforce=int(dto.initial_workforce),
            max_workforce_capacity=dto.max_workforce_capacity,
        )
        return self._solver.solve(params)


class ExportReportUseCase:
    """Caso de uso: Exporta las salidas paso por paso y el plan óptimo a un archivo .txt."""

    def __init__(self, exporter: IReportExporter) -> None:
        self._exporter = exporter

    def execute(self, dto: ExportReportDTO) -> str:
        """Invoca al exportador para persistir el reporte formateado."""
        return self._exporter.export(dto.result, dto.target_path)


class GetDefaultProblemUseCase:
    """Caso de uso: Provee los parámetros oficiales del problema asignado (UJAP)."""

    DEFAULT_DEMANDS: Tuple[int, ...] = (5, 7, 8, 4, 6)
    DEFAULT_EXCESS_COST: float = 300.0
    DEFAULT_HIRING_FIXED: float = 400.0
    DEFAULT_HIRING_VAR: float = 200.0
    DEFAULT_INITIAL_WORKFORCE: int = 0

    def execute(self) -> SolveProblemDTO:
        return SolveProblemDTO(
            demands=self.DEFAULT_DEMANDS,
            excess_holding_cost=self.DEFAULT_EXCESS_COST,
            hiring_fixed_cost=self.DEFAULT_HIRING_FIXED,
            hiring_variable_cost=self.DEFAULT_HIRING_VAR,
            initial_workforce=self.DEFAULT_INITIAL_WORKFORCE,
            max_workforce_capacity=None,
        )
