"""
Pruebas unitarias para el algoritmo de Programación Dinámica (DynamicProgrammingWorkforceSolver).
Verifica rigurosamente el costo óptimo de $3,300 y los valores de cada etapa.
"""

from src.domain.entities import WorkforceParameters
from src.infrastructure.dp_solver import DynamicProgrammingWorkforceSolver


def test_taha_ujap_problem_exact_solution():
    """
    Verifica que el problema oficial de la UJAP / Hamdy Taha:
    Demanda = [5, 7, 8, 4, 6]
    C_excedente = 300, K = 400, c = 200, x0 = 0
    tenga un costo mínimo global de exactamente $3,300.
    """
    params = WorkforceParameters(
        demands=(5, 7, 8, 4, 6),
        excess_holding_cost=300.0,
        hiring_fixed_cost=400.0,
        hiring_variable_cost=200.0,
        initial_workforce=0,
    )
    solver = DynamicProgrammingWorkforceSolver()
    result = solver.solve(params)

    # 1. Costo global óptimo
    assert result.total_minimal_cost == 3300.0

    # 2. Número de etapas evaluadas
    assert len(result.stages) == 5

    # 3. Trayectoria de la política óptima
    policy = result.optimal_policy
    assert len(policy) == 5

    # Semana 1: se contratan 5 trabajadores (de 0 a 5).
    # Costo = 400 + 200*5 = 1400. Exceso = 0.
    assert policy[0].week == 1
    assert policy[0].workforce_start == 0
    assert policy[0].workforce_assigned == 5
    assert policy[0].hired_count == 5
    assert policy[0].excess_count == 0
    assert policy[0].stage_cost == 1400.0
    assert policy[0].accumulated_cost == 1400.0

    # Semana 2: de 5 sube a 8 (se contratan 3).
    # Costo contratación = 400 + 200*3 = 1000.
    # Exceso = 8 - 7 = 1. Costo exceso = 300*1 = 300. Total = 1300.
    assert policy[1].week == 2
    assert policy[1].workforce_start == 5
    assert policy[1].workforce_assigned == 8
    assert policy[1].hired_count == 3
    assert policy[1].excess_count == 1
    assert policy[1].stage_cost == 1300.0
    assert policy[1].accumulated_cost == 2700.0

    # Semana 3: de 8 se mantiene en 8.
    # Contratados = 0, Exceso = 8 - 8 = 0. Costo = 0.
    assert policy[2].week == 3
    assert policy[2].workforce_start == 8
    assert policy[2].workforce_assigned == 8
    assert policy[2].hired_count == 0
    assert policy[2].excess_count == 0
    assert policy[2].stage_cost == 0.0
    assert policy[2].accumulated_cost == 2700.0

    # Semana 4: de 8 baja a 6.
    # Contratados = 0, Exceso = 6 - 4 = 2. Costo exceso = 300*2 = 600.
    assert policy[3].week == 4
    assert policy[3].workforce_start == 8
    assert policy[3].workforce_assigned == 6
    assert policy[3].hired_count == 0
    assert policy[3].excess_count == 2
    assert policy[3].stage_cost == 600.0
    assert policy[3].accumulated_cost == 3300.0

    # Semana 5: de 6 se mantiene en 6.
    # Contratados = 0, Exceso = 6 - 6 = 0. Costo = 0.
    assert policy[4].week == 5
    assert policy[4].workforce_start == 6
    assert policy[4].workforce_assigned == 6
    assert policy[4].hired_count == 0
    assert policy[4].excess_count == 0
    assert policy[4].stage_cost == 0.0
    assert policy[4].accumulated_cost == 3300.0


def test_stages_values_consistency():
    params = WorkforceParameters(
        demands=(5, 7, 8, 4, 6),
        excess_holding_cost=300.0,
        hiring_fixed_cost=400.0,
        hiring_variable_cost=200.0,
        initial_workforce=0,
    )
    solver = DynamicProgrammingWorkforceSolver()
    result = solver.solve(params)

    # Etapa 5 (semana 5, demanda 6)
    s5 = result.get_stage_by_number(5)
    assert s5 is not None
    # Si entramos con x4 = 4: contratar 2 cuesta 400 + 400 = 800
    assert s5.get_optimal_cost(4) == 800.0
    # Si entramos con x4 = 6: costo 0
    assert s5.get_optimal_cost(6) == 0.0
    # Si entramos con x4 = 8: costo 0
    assert s5.get_optimal_cost(8) == 0.0

    # Etapa 4 (semana 4, demanda 4)
    s4 = result.get_stage_by_number(4)
    assert s4 is not None
    # Con estado x3 = 8, decisión óptima x4* = 6 con costo 600
    assert s4.get_optimal_decisions(8) == [6]
    assert s4.get_optimal_cost(8) == 600.0

    # Etapa 1 (semana 1, x0 = 0)
    s1 = result.get_stage_by_number(1)
    assert s1 is not None
    assert s1.get_optimal_decisions(0) == [5]
    assert s1.get_optimal_cost(0) == 3300.0
