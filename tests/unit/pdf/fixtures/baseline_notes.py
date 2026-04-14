"""
Notas sobre el baseline actual del extractor.

NO convertir estos datos en expected semántico.
Representan el comportamiento actual (con bugs) para medir regresión técnica.
"""

CURRENT_BASELINE = {
    "jueces": {
        "pdf_name": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
        "expected_resolutive_rows_in_pdf": 20,  # Uno a Veinte
        "current_rows_in_excel": 13,
        "missing_rows": 7,
        "known_issues": [
            "Varios destinos vacíos",
            "Posible pérdida de secciones completas",
            "Primeros casos del documento afectados por corte temprano",
        ],
    },
    "magistrados": {
        "pdf_name": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "expected_resolutive_rows_in_pdf": 169,  # Uno a Ciento sesenta y nueve
        "current_rows_in_excel": 170,
        "extra_rows": 1,
        "known_issues": [
            "Muchos destinos vacíos",
            "Al menos 1 fila espuria capturada de bloques no resolutivos",
            "Aliases como (antes JPI 14) detectados como órganos",
        ],
    },
}

# Decisiones funcionales pendientes antes de activar pending_semantics
PENDING_DECISIONS = {
    "cargo_semantics": {
        "description": "Qué significa el campo `cargo`",
        "options": {
            "base_category": "Categoría base: Magistrado, Magistrada, Juez, Jueza",
            "role_plaza": "Función/plaza: Juez de adscripción territorial, etc.",
        },
        "affected_cases": ["JUE_004", "MAG_007", "MAG_009"],
    },
    "organ_granularity": {
        "description": "Granularidad del campo `tribunal_*`",
        "options": {
            "base_organ": "Tipo base: Tribunal de Instancia, TSJ",
            "full_label": "Etiqueta completa: Sección X del Tribunal de Instancia",
        },
    },
    "prov_loc_tsj": {
        "description": "Qué guardar en `prov_loc_*` para TSJ con 'provincia de' o 'con sede en'",
        "options": {
            "territory": "Territorio base del TSJ",
            "province": "Provincia/sede concreta",
            "composite": "Normalización compuesta",
        },
        "affected_cases": ["MAG_006", "MAG_007", "MAG_008"],
    },
}
