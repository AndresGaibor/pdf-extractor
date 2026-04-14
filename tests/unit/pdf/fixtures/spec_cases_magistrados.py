"""
Casos de especificación semántica del PDF de magistrados.

Representan la verdad funcional correcta según el BOE, no el comportamiento
actual del extractor.

Clasificación:
- "active": deben pasar
- "xfail": representan bugs actuales del extractor
- "pending_semantics": requieren decisión funcional sobre cargo/granularidad
"""

SPEC_CASES_MAGISTRADOS = [
    {
        "id": "MAG_001",
        "status": "xfail",
        "reason": "El extractor actual deja este destino vacío.",
        "paragraph": (
            "Uno. Don Carlos Fuentes Candelas, magistrado, con destino en la Audiencia Provincial "
            "de A Coruña, orden civil, pasará a desempeñar la plaza de presidente de la Sección "
            "Quinta, civil, de la Audiencia Provincial de A Coruña."
        ),
        "expected": {
            "participante": "Carlos Fuentes Candelas",
            "cargo": "Magistrado",
            "tribunal_origen": "Audiencia Provincial",
            "tribunal_destino": "Audiencia Provincial",
            "prov_loc_origen": "A Coruña",
            "prov_loc_destino": "A Coruña",
        },
    },
    {
        "id": "MAG_002",
        "status": "xfail",
        "reason": "El extractor actual pierde el destino completo en este caso y debe verificarse que los aliases no se usen como órgano.",
        "paragraph": (
            "Cuatro. Doña María Jesús Millán de las Heras, magistrada, especialista de "
            "menores, en situación administrativa de servicios especiales en la Carrera Judicial, que "
            "sirve la plaza número 2 de la Sección de Menores del Tribunal de Instancia de Madrid, "
            "de ejecuciones de los juzgados de menores (antes JMEN 2), pasará a desempeñar la "
            "plaza número 7 de la Sección de Menores del Tribunal de Instancia de Madrid, de "
            "ejecuciones de los juzgados de menores (antes JMEN 7), continuando en la misma "
            "situación administrativa."
        ),
        "expected": {
            "participante": "María Jesús Millán de las Heras",
            "cargo": "Magistrada",
            "tribunal_origen": "Sección de Menores del Tribunal de Instancia",
            "tribunal_destino": "Sección de Menores del Tribunal de Instancia",
            "prov_loc_origen": "Madrid",
            "prov_loc_destino": "Madrid",
        },
        "assert_not_in_organs": ["JMEN 2", "JMEN 7"],
    },
    {
        "id": "MAG_003",
        "status": "active",
        "paragraph": (
            "Cinco. Doña María Fernanda Navarro Zuloaga, magistrada, especialista del orden "
            "jurisdiccional contencioso-administrativo, con destino en la Sala del mismo orden "
            "jurisdiccional del Tribunal Superior de Justicia de Cataluña, pasará a desempeñar la "
            "plaza de magistrada de la Sala de lo Contencioso-Administrativo del Tribunal Superior de "
            "Justicia de Navarra, ocupando plaza de especialista."
        ),
        "expected": {
            "participante": "María Fernanda Navarro Zuloaga",
            "cargo": "Magistrada especialista",
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Cataluña",
            "prov_loc_destino": "Navarra (Navarra)",
        },
    },
    {
        "id": "MAG_004",
        "status": "xfail",
        "reason": "El extractor actual deja el destino vacío; el alias histórico JP 13 no debe detectarse como órgano.",
        "paragraph": (
            "Siete. Doña María Carmen Cimas Giménez, magistrada, que sirve la plaza número 13 "
            "de la Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13), pasará a "
            "desempeñar la plaza de magistrada de la Sala de lo Penal de la Audiencia Nacional."
        ),
        "expected": {
            "participante": "María Carmen Cimas Giménez",
            "cargo": "Magistrada",
            "tribunal_origen": "Sección de lo Penal del Tribunal de Instancia",
            "tribunal_destino": "Audiencia Nacional",
            "prov_loc_origen": "Madrid",
            "prov_loc_destino": "",
        },
        "assert_not_in_organs": ["JP 13"],
    },
    {
        "id": "MAG_005",
        "status": "active",
        "paragraph": (
            "Diez. Doña María del Carmen García Martínez, magistrada, en situación "
            "administrativa de servicios especiales en la Carrera Judicial, que sirve la plaza "
            "número 18 de la Sección de Instrucción del Tribunal de Instancia de Barcelona (antes "
            "JINSTR 18), pasará a desempeñar la plaza número 1 de la Sección de Vigilancia "
            "Penitenciaria del Tribunal de Instancia de Barcelona (antes JVP 1), continuando en la "
            "misma situación administrativa."
        ),
        "expected": {
            "participante": "María del Carmen García Martínez",
            "cargo": "Magistrada (servicios especiales)",
            "tribunal_origen": "Sección de Instrucción del Tribunal de Instancia",
            "tribunal_destino": "Sección de Vigilancia Penitenciaria del Tribunal de Instancia",
            "prov_loc_origen": "Barcelona (Cataluña)",
            "prov_loc_destino": "Barcelona (Cataluña)",
        },
        "assert_not_in_organs": ["JINSTR 18", "JVP 1"],
    },
    {
        "id": "MAG_006",
        "status": "xfail",
        "reason": "La salida actual trunca la localidad del destino; no usar el baseline actual como verdad.",
        "paragraph": (
            "Sesenta y ocho. Don Oscar Luis Rojas de la Viuda, magistrado, que sirve la plaza "
            "número 3 de la Sección de lo Contencioso-administrativo del Tribunal de Instancia de "
            "Valladolid (antes JCA 3), pasará a desempeñar la plaza de magistrado de la Sala de lo "
            "Contencioso-Administrativo del Tribunal Superior de Justicia de Castilla y León, con sede "
            "en Burgos."
        ),
        "expected": {
            "participante": "Oscar Luis Rojas de la Viuda",
            "cargo": "Magistrado",
            "tribunal_origen": "Sección de lo Contencioso-administrativo del Tribunal de Instancia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Valladolid",
            "prov_loc_destino": "PENDING_DECISION_SEDE_TSJ",
        },
        "assert_not_in_organs": ["JCA 3"],
    },
    {
        "id": "MAG_007",
        "status": "pending_semantics",
        "reason": "No congelar hasta decidir si el cargo debe reflejar categoría base o función/plaza; también decidir qué debe ir en prov_loc_origen para 'con sede en Málaga'.",
        "paragraph": (
            "Ciento ocho. Doña María Sandra García Sánchez, magistrada, Jueza de "
            "adscripción territorial del Tribunal Superior de Justicia de Andalucía, Ceuta y Melilla, con "
            "sede en Málaga, pasará a desempeñar la plaza número 1 de la Sección de Violencia "
            "contra la Infancia y la Adolescencia del Tribunal de Instancia de Málaga."
        ),
        "expected_candidate_options": {
            "cargo": ["Magistrada", "Jueza de adscripción territorial"],
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Sección de Violencia contra la Infancia y la Adolescencia del Tribunal de Instancia",
            "prov_loc_origen": ["Andalucía", "Málaga", "Andalucía, Ceuta y Melilla"],
            "prov_loc_destino": "Málaga",
        },
    },
    {
        "id": "MAG_008",
        "status": "xfail",
        "reason": "El extractor actual asigna mal la provincia de origen y pierde el destino.",
        "paragraph": (
            "Ciento once. Doña Laura Cristina Morell Aldana, magistrada, que sirve la plaza de "
            "jueza de adscripción territorial del Tribunal Superior de Justicia de la Comunidad "
            "Valenciana, provincia de Castellón, pasará a desempeñar la plaza de jueza de "
            "adscripción territorial del Tribunal Superior de Justicia de la Comunidad Valenciana, "
            "provincia de Valencia."
        ),
        "expected": {
            "participante": "Laura Cristina Morell Aldana",
            "cargo": "Jueza de adscripción territorial",
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Castellón",
            "prov_loc_destino": "Valencia",
        },
    },
    {
        "id": "MAG_009",
        "status": "pending_semantics",
        "reason": "No congelar hasta decidir si el cargo debe reflejar categoría base o función/plaza y si el órgano de destino debe guardarse con granularidad completa.",
        "paragraph": (
            "Ciento doce. Don Juan Miguel Paños Villaescusa, magistrado, que sirve la plaza de "
            "juez de adscripción territorial del Tribunal Superior de Justicia de Castilla-La Mancha, "
            "provincia de Albacete, pasará a desempeñar la plaza número 6 de la Sección Civil del "
            "Tribunal de Instancia de Albacete, de familia e incapacidades (antes JPI 6)."
        ),
        "expected_candidate_options": {
            "cargo": ["Magistrado", "Juez de adscripción territorial"],
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": [
                "Tribunal de Instancia",
                "Sección Civil del Tribunal de Instancia",
            ],
            "prov_loc_origen": "Albacete",
            "prov_loc_destino": "Albacete",
        },
        "assert_not_in_organs": ["JPI 6"],
    },
]
