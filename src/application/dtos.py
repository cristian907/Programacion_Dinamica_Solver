"""
Módulo de Objetos de Transferencia de Datos (DTOs).
Desacopla la capa de presentación de la capa de dominio.
"""

from dataclasses import dataclass
from typing import Sequence
from src.domain.entities import OptimizationResult


@dataclass(frozen=True)
class SolveProblemDTO:
    """Datos de entrada enviados desde la interfaz de usuario o CLI para resolver el problema."""
    demands: Sequence[int]
    excess_holding_cost: float = 300.0
    hiring_fixed_cost: float = 400.0
    hiring_variable_cost: float = 200.0
    initial_workforce: int = 0
    max_workforce_capacity: int | None = None


@dataclass(frozen=True)
class ExportReportDTO:
    """Datos de entrada para la exportación del reporte a archivo de texto."""
    result: OptimizationResult
    target_path: str
