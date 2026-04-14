"""
Helpers compartidos para tests de parsing de PDFs BOE.
"""


def norm(value: str) -> str:
    """
    Normaliza un valor para comparación tolerante.

    - Colapsa espacios múltiples
    - Elimina espacios al inicio/final
    - NO quita tildes
    """
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()
