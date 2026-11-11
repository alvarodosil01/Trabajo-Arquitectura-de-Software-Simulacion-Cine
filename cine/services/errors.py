"""Errores del dominio, independientes de HTTP."""


class NotFoundError(ValueError):
    pass


class ConflictError(ValueError):
    pass
