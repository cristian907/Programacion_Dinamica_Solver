"""
Módulo de excepciones del dominio.
Define los errores de validación y reglas de negocio para el modelo de fuerza de trabajo.
"""

class DomainValidationError(Exception):
    """Excepción base para errores de validación en la capa de dominio."""
    pass


class InvalidDemandError(DomainValidationError):
    """Lanzada cuando las demandas de trabajadores no son válidas."""
    pass


class InvalidCostError(DomainValidationError):
    """Lanzada cuando alguno de los costos del modelo es negativo."""
    pass


class InvalidWorkforceError(DomainValidationError):
    """Lanzada cuando la fuerza de trabajo inicial no es válida."""
    pass
