"""
Módulo de entidades del dominio.
Contiene las entidades y objetos de valor que encapsulan las reglas del modelo
de Programación Dinámica para la planificación del tamaño de la fuerza laboral.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict
from .exceptions import InvalidDemandError, InvalidCostError, InvalidWorkforceError


@dataclass(frozen=True)
class WorkforceParameters:
    """
    Parámetros de configuración del modelo de fuerza de trabajo.
    Inmutable para garantizar la integridad en toda la arquitectura.
    """
    demands: Tuple[int, ...]
    excess_holding_cost: float = 300.0      # Costo por trabajador excedente semanal ($300)
    hiring_fixed_cost: float = 400.0        # Costo fijo por realizar contrataciones ($400)
    hiring_variable_cost: float = 200.0     # Costo variable por trabajador contratado ($200)
    initial_workforce: int = 0             # Fuerza de trabajo al inicio del horizonte (x0 = 0)
    max_workforce_capacity: int | None = None  # Cota superior para decisiones x_i

    def __post_init__(self) -> None:
        """Valida que los parámetros cumplan las reglas de negocio del problema."""
        if not self.demands:
            raise InvalidDemandError("La lista de demandas semanales no puede estar vacía.")

        for idx, d in enumerate(self.demands, start=1):
            if not isinstance(d, int) or d < 1:
                raise InvalidDemandError(
                    f"La demanda de la semana {idx} debe ser un entero positivo mayor o igual a 1 (valor recibido: {d})."
                )

        if self.excess_holding_cost < 0:
            raise InvalidCostError("El costo de mano de obra excedente no puede ser negativo.")

        if self.hiring_fixed_cost < 0:
            raise InvalidCostError("El costo fijo de contratación no puede ser negativo.")

        if self.hiring_variable_cost < 0:
            raise InvalidCostError("El costo variable de contratación no puede ser negativo.")

        if self.initial_workforce < 0:
            raise InvalidWorkforceError("La fuerza de trabajo inicial (x0) no puede ser negativa.")

        if self.max_workforce_capacity is not None and self.max_workforce_capacity < max(self.demands):
            raise InvalidWorkforceError(
                f"La capacidad máxima ({self.max_workforce_capacity}) no puede ser menor que la demanda máxima requerida ({max(self.demands)})."
            )

    @property
    def num_weeks(self) -> int:
        """Número total de semanas / etapas."""
        return len(self.demands)

    @property
    def max_demand(self) -> int:
        """Demanda máxima requerida a lo largo de todo el horizonte."""
        return max(self.demands)

    @property
    def effective_max_workforce(self) -> int:
        """Cota superior calculada para evaluar las decisiones."""
        return self.max_workforce_capacity if self.max_workforce_capacity is not None else self.max_demand


@dataclass(frozen=True)
class DecisionEvaluation:
    """
    Evaluación de una alternativa de decisión (x_i) dado un estado previo (x_{i-1})
    en la etapa i según la ecuación de recurrencia de Bellman.
    """
    stage: int                 # Número de semana / etapa (1..N)
    state_prev: int            # x_{i-1}: trabajadores disponibles al inicio de la semana
    decision_curr: int         # x_i: trabajadores asignados en la semana
    demand: int                # b_i: demanda mínima requerida
    excess_workers: int        # max(0, x_i - b_i)
    excess_cost: float         # Costo por retener personal excedente
    hired_workers: int         # max(0, x_i - x_{i-1})
    hiring_cost: float         # Costo de contratación (fijo + variable)
    stage_immediate_cost: float # Costo directo de la etapa = excess_cost + hiring_cost
    future_cost: float         # f_{i+1}(x_i): costo óptimo acumulado futuro
    total_cost: float          # stage_immediate_cost + future_cost
    is_optimal: bool = False   # True si es una de las decisiones que minimiza el costo para este estado


@dataclass
class StageTable:
    """
    Tabla de Programación Dinámica para una etapa específica.
    Agrupa todas las combinaciones evaluadas de estados y decisiones.
    """
    stage_number: int                          # Semana i (ej. 5, 4, 3, 2, 1)
    demand: int                                # b_i requerida en esta etapa
    evaluations: List[DecisionEvaluation] = field(default_factory=list)
    best_decisions_by_state: Dict[int, List[int]] = field(default_factory=dict)
    best_costs_by_state: Dict[int, float] = field(default_factory=dict)

    def get_optimal_decisions(self, state_prev: int) -> List[int]:
        """Retorna las decisiones óptimas x_i* para un estado inicial x_{i-1}."""
        return self.best_decisions_by_state.get(state_prev, [])

    def get_optimal_cost(self, state_prev: int) -> float:
        """Retorna el costo óptimo f_i(x_{i-1}) para un estado inicial."""
        return self.best_costs_by_state.get(state_prev, float("inf"))

    def get_distinct_states(self) -> List[int]:
        """Retorna la lista ordenada de estados previos x_{i-1} evaluados."""
        return sorted(list(self.best_costs_by_state.keys()))


@dataclass(frozen=True)
class PolicyStep:
    """
    Detalle de ejecución de la política óptima para una semana en particular.
    """
    week: int                   # Semana (1..N)
    demand: int                 # b_i requerida
    workforce_start: int        # x_{i-1}: personal que venía de la semana anterior
    workforce_assigned: int     # x_i*: personal asignado finalmente
    hired_count: int            # Personal contratado
    excess_count: int           # Personal excedente retenido
    hiring_cost: float          # Costo de contratación de la semana
    excess_cost: float          # Costo de mano de obra excedente
    stage_cost: float           # Costo total incurrido en la semana
    accumulated_cost: float     # Costo acumulado hasta esta semana


@dataclass
class OptimizationResult:
    """
    Resultado completo de la optimización del modelo de programación dinámica.
    Contiene la descomposición por etapas, la trayectoria óptima y costos finales.
    """
    parameters: WorkforceParameters
    stages: List[StageTable]                  # Tablas de cada etapa (habitualmente orden 5 a 1)
    optimal_policy: List[PolicyStep]          # Trayectoria óptima semana a semana
    total_minimal_cost: float                 # Costo mínimo total (ej. $3300)
    alternative_policies: List[List[PolicyStep]] = field(default_factory=list)

    def get_stage_by_number(self, stage_num: int) -> StageTable | None:
        """Busca una etapa específica por su número."""
        for s in self.stages:
            if s.stage_number == stage_num:
                return s
        return None
