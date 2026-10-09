"""
Módulo del resolvedor de Programación Dinámica (Infraestructura).
Implementa la interfaz IWorkforceSolver utilizando recursión hacia atrás (backward recursion)
conforme al modelo clásico de investigación de operaciones (Hamdy A. Taha).
"""

from typing import List, Dict, Set
from src.domain.entities import (
    WorkforceParameters,
    DecisionEvaluation,
    StageTable,
    PolicyStep,
    OptimizationResult,
)
from src.application.interfaces import IWorkforceSolver


class DynamicProgrammingWorkforceSolver(IWorkforceSolver):
    """
    Resolvedor de programación dinámica determinística para el problema de
    planificación de tamaño de la fuerza laboral.
    """

    def solve(self, parameters: WorkforceParameters) -> OptimizationResult:
        """
        Ejecuta la optimización recursiva hacia atrás desde la etapa N hasta la etapa 1,
        y luego reconstruye la trayectoria óptima hacia adelante (forward traceback).
        """
        n_stages = parameters.num_weeks
        effective_max = parameters.effective_max_workforce

        # stages_dict guardará la tabla de cada etapa indexada por su número (1..N)
        stages_dict: Dict[int, StageTable] = {}

        # Determinar los estados válidos/posibles para cada etapa
        # Para la etapa 1: solo x0 (parámetro inicial)
        # Para la etapa i > 1: x_{i-1} puede tomar valores entre la demanda de la semana anterior y el máximo
        possible_states_by_stage: Dict[int, List[int]] = {}
        possible_states_by_stage[1] = [parameters.initial_workforce]

        for i in range(2, n_stages + 1):
            prev_demand = parameters.demands[i - 2]
            # Los estados posibles que entrega la semana i-1 son al menos su demanda
            possible_states_by_stage[i] = list(range(prev_demand, effective_max + 1))

        # Recursión hacia atrás: de la etapa N a la etapa 1
        for stage_num in range(n_stages, 0, -1):
            demand_curr = parameters.demands[stage_num - 1]
            valid_states = possible_states_by_stage[stage_num]

            # Decisiones posibles x_i: deben satisfacer la demanda actual (x_i >= b_i)
            # y no superar la cota máxima del horizonte
            possible_decisions = list(range(demand_curr, effective_max + 1))

            evaluations: List[DecisionEvaluation] = []
            best_decisions: Dict[int, List[int]] = {}
            best_costs: Dict[int, float] = {}

            # Para cada estado entrante x_{i-1}
            for state_prev in valid_states:
                min_cost_for_state = float("inf")
                state_evaluations: List[DecisionEvaluation] = []

                for decision_curr in possible_decisions:
                    # 1. Costo por personal excedente conservado: C1 * (x_i - b_i)
                    excess_workers = max(0, decision_curr - demand_curr)
                    excess_cost = parameters.excess_holding_cost * excess_workers

                    # 2. Costo por contratación: K + c * (x_i - x_{i-1}) si x_i > x_{i-1}
                    if decision_curr > state_prev:
                        hired_workers = decision_curr - state_prev
                        hiring_cost = (
                            parameters.hiring_fixed_cost
                            + parameters.hiring_variable_cost * hired_workers
                        )
                    else:
                        hired_workers = 0
                        hiring_cost = 0.0

                    stage_immediate_cost = excess_cost + hiring_cost

                    # 3. Costo futuro acumulado: f_{i+1}(x_i)
                    if stage_num == n_stages:
                        future_cost = 0.0
                    else:
                        next_stage = stages_dict[stage_num + 1]
                        future_cost = next_stage.get_optimal_cost(decision_curr)

                    total_cost = stage_immediate_cost + future_cost

                    if total_cost < min_cost_for_state:
                        min_cost_for_state = total_cost

                    state_evaluations.append(
                        DecisionEvaluation(
                            stage=stage_num,
                            state_prev=state_prev,
                            decision_curr=decision_curr,
                            demand=demand_curr,
                            excess_workers=excess_workers,
                            excess_cost=excess_cost,
                            hired_workers=hired_workers,
                            hiring_cost=hiring_cost,
                            stage_immediate_cost=stage_immediate_cost,
                            future_cost=future_cost,
                            total_cost=total_cost,
                            is_optimal=False,
                        )
                    )

                # Identificar cuáles decisiones alcanzaron el costo mínimo óptimo
                optimal_decisions_for_state: List[int] = []
                for ev in state_evaluations:
                    is_opt = abs(ev.total_cost - min_cost_for_state) < 1e-6
                    if is_opt:
                        optimal_decisions_for_state.append(ev.decision_curr)
                    evaluations.append(
                        DecisionEvaluation(
                            stage=ev.stage,
                            state_prev=ev.state_prev,
                            decision_curr=ev.decision_curr,
                            demand=ev.demand,
                            excess_workers=ev.excess_workers,
                            excess_cost=ev.excess_cost,
                            hired_workers=ev.hired_workers,
                            hiring_cost=ev.hiring_cost,
                            stage_immediate_cost=ev.stage_immediate_cost,
                            future_cost=ev.future_cost,
                            total_cost=ev.total_cost,
                            is_optimal=is_opt,
                        )
                    )

                best_decisions[state_prev] = optimal_decisions_for_state
                best_costs[state_prev] = min_cost_for_state

            stage_table = StageTable(
                stage_number=stage_num,
                demand=demand_curr,
                evaluations=evaluations,
                best_decisions_by_state=best_decisions,
                best_costs_by_state=best_costs,
            )
            stages_dict[stage_num] = stage_table

        # Lista de etapas en orden decreciente (de N a 1) habitual en P.D.
        ordered_stages = [stages_dict[i] for i in range(n_stages, 0, -1)]

        # Reconstrucción de la política óptima (Forward Traceback)
        optimal_policy = self._reconstruct_policy(
            parameters, stages_dict, parameters.initial_workforce
        )

        total_minimal_cost = stages_dict[1].get_optimal_cost(parameters.initial_workforce)

        # Buscar posibles trayectorias alternativas si existen empates
        all_trajectories = self._reconstruct_all_trajectories(
            parameters, stages_dict, parameters.initial_workforce
        )
        alternative_policies = (
            all_trajectories[1:] if len(all_trajectories) > 1 else []
        )

        return OptimizationResult(
            parameters=parameters,
            stages=ordered_stages,
            optimal_policy=optimal_policy,
            total_minimal_cost=total_minimal_cost,
            alternative_policies=alternative_policies,
        )

    def _reconstruct_policy(
        self,
        parameters: WorkforceParameters,
        stages: Dict[int, StageTable],
        initial_workforce: int,
    ) -> List[PolicyStep]:
        """Reconstruye paso a paso la política óptima primaria."""
        policy: List[PolicyStep] = []
        current_state = initial_workforce
        accumulated_cost = 0.0

        for stage_num in range(1, parameters.num_weeks + 1):
            stage_table = stages[stage_num]
            demand = parameters.demands[stage_num - 1]
            optimal_decisions = stage_table.get_optimal_decisions(current_state)

            if not optimal_decisions:
                raise RuntimeError(
                    f"No se encontró decisión factible para la etapa {stage_num} con estado {current_state}."
                )

            # Seleccionar la primera decisión óptima
            chosen_decision = optimal_decisions[0]

            # Calcular métricas de la semana
            excess = max(0, chosen_decision - demand)
            excess_cost = parameters.excess_holding_cost * excess

            if chosen_decision > current_state:
                hired = chosen_decision - current_state
                hiring_cost = (
                    parameters.hiring_fixed_cost
                    + parameters.hiring_variable_cost * hired
                )
            else:
                hired = 0
                hiring_cost = 0.0

            stage_cost = excess_cost + hiring_cost
            accumulated_cost += stage_cost

            step = PolicyStep(
                week=stage_num,
                demand=demand,
                workforce_start=current_state,
                workforce_assigned=chosen_decision,
                hired_count=hired,
                excess_count=excess,
                hiring_cost=hiring_cost,
                excess_cost=excess_cost,
                stage_cost=stage_cost,
                accumulated_cost=accumulated_cost,
            )
            policy.append(step)
            current_state = chosen_decision

        return policy

    def _reconstruct_all_trajectories(
        self,
        parameters: WorkforceParameters,
        stages: Dict[int, StageTable],
        initial_workforce: int,
    ) -> List[List[PolicyStep]]:
        """Busca todas las ramas óptimas si hubiera empates en los costos."""
        paths: List[List[int]] = []

        def dfs(stage_num: int, current_state: int, current_path: List[int]) -> None:
            if stage_num > parameters.num_weeks:
                paths.append(list(current_path))
                return
            stage_table = stages[stage_num]
            opt_decisions = stage_table.get_optimal_decisions(current_state)
            for d in opt_decisions:
                dfs(stage_num + 1, d, current_path + [d])

        dfs(1, initial_workforce, [])

        results: List[List[PolicyStep]] = []
        for path in paths:
            policy: List[PolicyStep] = []
            curr_state = initial_workforce
            acc_cost = 0.0
            for idx, decision in enumerate(path, start=1):
                demand = parameters.demands[idx - 1]
                excess = max(0, decision - demand)
                excess_cost = parameters.excess_holding_cost * excess
                if decision > curr_state:
                    hired = decision - curr_state
                    hiring_cost = (
                        parameters.hiring_fixed_cost
                        + parameters.hiring_variable_cost * hired
                    )
                else:
                    hired = 0
                    hiring_cost = 0.0
                weekly_cost = excess_cost + hiring_cost
                acc_cost += weekly_cost
                policy.append(
                    PolicyStep(
                        week=idx,
                        demand=demand,
                        workforce_start=curr_state,
                        workforce_assigned=decision,
                        hired_count=hired,
                        excess_count=excess,
                        hiring_cost=hiring_cost,
                        excess_cost=excess_cost,
                        stage_cost=weekly_cost,
                        accumulated_cost=acc_cost,
                    )
                )
                curr_state = decision
            results.append(policy)

        return results
