"""
Casos de especificación semántica del PDF de jueces.

Representan la verdad funcional correcta según el BOE, no el comportamiento
actual del extractor.

Clasificación:
- "active": deben pasar
- "xfail": representan bugs actuales del extractor
- "pending_semantics": requieren decisión funcional sobre cargo/granularidad
"""

SPEC_CASES_JUECES = [
    {
        "id": "JUE_001",
        "status": "xfail",
        "reason": "El extractor actual no está resolviendo bien algunos casos de adscripción territorial al inicio del documento.",
        "paragraph": (
            "Uno. Doña Carmen García Vallina, jueza de adscripción territorial del Tribunal "
            "Superior de Justicia de Cataluña, provincia de Girona, pasará a desempeñar la plaza de "
            "jueza de adscripción territorial del Tribunal Superior de Justicia de Madrid."
        ),
        "expected": {
            "participante": "Carmen García Vallina",
            "cargo": "Jueza de adscripción territorial",
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Girona",
            "prov_loc_destino": "Madrid",
        },
    },
    {
        "id": "JUE_002",
        "status": "xfail",
        "reason": "El extractor actual pierde varios destinos y secciones en los primeros casos del PDF de jueces.",
        "paragraph": (
            "Dos. Doña María Ruiz García, jueza, que sirve la plaza número 2 de la Sección "
            "Civil y de Instrucción del Tribunal de Instancia de Villacarrillo, pasará a "
            "desempeñar la plaza número 1 de la Sección Civil y de Instrucción del Tribunal "
            "de Instancia de Baeza, con competencia en violencia sobre la mujer."
        ),
        "expected": {
            "participante": "María Ruiz García",
            "cargo": "Jueza",
            "tribunal_origen": "Sección Civil y de Instrucción del Tribunal de Instancia",
            "tribunal_destino": "Sección Civil y de Instrucción del Tribunal de Instancia",
            "prov_loc_origen": "Villacarrillo",
            "prov_loc_destino": "Baeza",
        },
    },
    {
        "id": "JUE_003",
        "status": "xfail",
        "reason": "El extractor actual no captura la sección completa del órgano de origen; devuelve solo 'Tribunal de Instancia'.",
        "paragraph": (
            "Tres. Doña Andrea Domínguez González, jueza, que sirve la plaza número 3 de la "
            "Sección Civil y de Instrucción del Tribunal de Instancia de Chiclana de la Frontera, "
            "pasará a desempeñar la plaza número 5 de la Sección de Instrucción del Tribunal de "
            "Instancia de Algeciras, mientras su titular don Jerónimo García San Martín se "
            "encuentre en la situación administrativa de servicios especiales en la Carrera Judicial."
        ),
        "expected": {
            "participante": "Andrea Domínguez González",
            "cargo": "Jueza",
            "tribunal_origen": "Sección Civil y de Instrucción del Tribunal de Instancia",
            "tribunal_destino": "Sección de Instrucción del Tribunal de Instancia",
            "prov_loc_origen": "Chiclana de la Frontera",
            "prov_loc_destino": "Algeciras",
        },
    },
    {
        "id": "JUE_004",
        "status": "pending_semantics",
        "reason": "No congelar hasta decidir si `cargo` representa categoría base (`Juez`) o función/plaza (`Juez de adscripción territorial`).",
        "paragraph": (
            "Seis. Don Jorge Pedro Domench Ares, juez que sirve la plaza número 3 de la "
            "Sección Civil y de Instrucción del Tribunal de Instancia de Esplugues de Llobregat, "
            "pasará a desempeñar la plaza de Juez de adscripción territorial del Tribunal Superior "
            "de Justicia de Canarias, provincia de Las Palmas."
        ),
        "expected_candidate_options": {
            "cargo": ["Juez", "Juez de adscripción territorial"],
            "tribunal_origen": "Sección Civil y de Instrucción del Tribunal de Instancia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Esplugues de Llobregat",
            "prov_loc_destino": "Las Palmas",
        },
    },
    {
        "id": "JUE_005",
        "status": "xfail",
        "reason": "El extractor actual deja este destino vacío; debe quedar cubierto como bug funcional.",
        "paragraph": (
            "Quince. Ana Belén Ortiz Roca, jueza, que sirve la plaza número 3 de la Sección "
            "Civil y de Instrucción del Tribunal de Instancia de Cornellà de Llobregat, pasará a "
            "desempeñar la plaza número 1 de la Sección de Familia, Infancia y Capacidad del "
            "Tribunal de Instancia de Matarò, de familia y capacidad."
        ),
        "expected": {
            "participante": "Ana Belén Ortiz Roca",
            "cargo": "Jueza",
            "tribunal_origen": "Sección Civil y de Instrucción del Tribunal de Instancia",
            "tribunal_destino": "Sección de Familia, Infancia y Capacidad del Tribunal de Instancia",
            "prov_loc_origen": "Cornellà de Llobregat",
            "prov_loc_destino": "Matarò",
        },
    },
]
