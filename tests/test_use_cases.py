"""
Pruebas unitarias para los casos de uso y la exportación de reportes.
"""

import os
from src.application.dtos import SolveProblemDTO, ExportReportDTO
from src.application.use_cases import (
    SolveWorkforceModelUseCase,
    ExportReportUseCase,
    GetDefaultProblemUseCase,
)
from src.infrastructure.dp_solver import DynamicProgrammingWorkforceSolver
from src.infrastructure.text_exporter import TextReportExporter


def test_solve_workforce_model_use_case():
    solver = DynamicProgrammingWorkforceSolver()
    use_case = SolveWorkforceModelUseCase(solver=solver)

    dto = SolveProblemDTO(
        demands=(5, 7, 8, 4, 6),
        excess_holding_cost=300.0,
        hiring_fixed_cost=400.0,
        hiring_variable_cost=200.0,
        initial_workforce=0,
    )
    result = use_case.execute(dto)

    assert result.total_minimal_cost == 3300.0
    assert len(result.optimal_policy) == 5


def test_export_report_use_case(tmp_path):
    solver = DynamicProgrammingWorkforceSolver()
    solve_uc = SolveWorkforceModelUseCase(solver=solver)
    dto = SolveProblemDTO(demands=(5, 7, 8, 4, 6))
    result = solve_uc.execute(dto)

    exporter = TextReportExporter()
    export_uc = ExportReportUseCase(exporter=exporter)

    target_file = tmp_path / "reporte_salidas.txt"
    export_dto = ExportReportDTO(result=result, target_path=str(target_file))
    saved_path = export_uc.execute(export_dto)

    assert os.path.exists(saved_path)
    with open(saved_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "UNIVERSIDAD JOSÉ ANTONIO PÁEZ" in content
    assert "MODELO DE TAMAÑO DE LA FUERZA DE TRABAJO" in content
    assert "ETAPA 5" in content
    assert "ETAPA 1" in content
    assert "COSTO TOTAL MÍNIMO DE LA OPERACIÓN: $3,300.00" in content


def test_get_default_problem_use_case():
    uc = GetDefaultProblemUseCase()
    dto = uc.execute()

    assert dto.demands == (5, 7, 8, 4, 6)
    assert dto.excess_holding_cost == 300.0
    assert dto.hiring_fixed_cost == 400.0
    assert dto.hiring_variable_cost == 200.0
    assert dto.initial_workforce == 0
