"""
Módulo de interfaces (Protocolos) de la capa de aplicación.
Define los contratos abstractos que debe cumplir la infraestructura,
garantizando la inversión de dependencias propia de Clean Architecture.
"""

from typing import Protocol
from src.domain.entities import WorkforceParameters, OptimizationResult


class IWorkforceSolver(Protocol):
    """Interfaz para los algoritmos de resolución del modelo de fuerza de trabajo."""

    def solve(self, parameters: WorkforceParameters) -> OptimizationResult:
        """
        Ejecuta el algoritmo de programación dinámica y retorna el resultado
        completo con etapas y política óptima.
        """
        ...


class IReportExporter(Protocol):
    """Interfaz para los exportadores de reportes detallados."""

    def export(self, result: OptimizationResult, target_path: str) -> str:
        """
        Genera y almacena el reporte formateado paso a paso en el archivo destino.
        Retorna la ruta absoluta del archivo generado.
        """
        ...
