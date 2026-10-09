"""
Pruebas unitarias para las entidades y validaciones del dominio.
"""

import pytest
from src.domain.entities import (
    WorkforceParameters,
    DecisionEvaluation,
    StageTable,
    PolicyStep,
)
from src.domain.exceptions import (
    InvalidDemandError,
    InvalidCostError,
    InvalidWorkforceError,
)


def test_workforce_parameters_creation_valid():
    params = WorkforceParameters(
        demands=(5, 7, 8, 4, 6),
        excess_holding_cost=300.0,
        hiring_fixed_cost=400.0,
        hiring_variable_cost=200.0,
        initial_workforce=0,
    )
    assert params.num_weeks == 5
    assert params.max_demand == 8
    assert params.effective_max_workforce == 8


def test_workforce_parameters_empty_demands_raises():
    with pytest.raises(InvalidDemandError):
        WorkforceParameters(demands=())


def test_workforce_parameters_negative_demand_raises():
    with pytest.raises(InvalidDemandError):
        WorkforceParameters(demands=(5, -2, 8))


def test_workforce_parameters_negative_cost_raises():
    with pytest.raises(InvalidCostError):
        WorkforceParameters(demands=(5, 7), excess_holding_cost=-10)

    with pytest.raises(InvalidCostError):
        WorkforceParameters(demands=(5, 7), hiring_fixed_cost=-50)

    with pytest.raises(InvalidCostError):
        WorkforceParameters(demands=(5, 7), hiring_variable_cost=-100)


def test_workforce_parameters_negative_initial_workforce_raises():
    with pytest.raises(InvalidWorkforceError):
        WorkforceParameters(demands=(5, 7), initial_workforce=-1)


def test_workforce_parameters_capacity_lower_than_demand_raises():
    with pytest.raises(InvalidWorkforceError):
        WorkforceParameters(demands=(5, 7, 8), max_workforce_capacity=6)


def test_stage_table_helper_methods():
    table = StageTable(
        stage_number=5,
        demand=6,
        best_decisions_by_state={4: [6], 5: [6], 6: [6]},
        best_costs_by_state={4: 800.0, 5: 600.0, 6: 0.0},
    )
    assert table.get_optimal_decisions(4) == [6]
    assert table.get_optimal_cost(5) == 600.0
    assert table.get_optimal_cost(999) == float("inf")
    assert table.get_distinct_states() == [4, 5, 6]
