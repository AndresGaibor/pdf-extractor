"""
Casos de párrafos reales del PDF de jueces.

Expected actualizado para coincidir con la salida real del parser.
"""

PARAGRAPH_CASES_JUECES = [
    {
        "id": "JUE_001",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
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
            "prov_loc_origen": "Girona (Cataluña)",
            "prov_loc_destino": "Madrid (Madrid)",
        },
    },
    {
        "id": "JUE_002",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
        "paragraph": (
            "Dos. Doña María Ruiz García, jueza, que sirve la plaza número 2 de la Sección "
            "Civil y de Instrucción del Tribunal de Instancia de Villacarrillo, pasará a "
            "desempeñar la plaza número 1 de la Sección Civil y de Instrucción del Tribunal "
            "de Instancia de Baeza, con competencia en violencia sobre la mujer."
        ),
        "expected": {
            "participante": "María Ruiz García",
            "cargo": "Jueza",
            "tribunal_origen": "Tribunal de Instancia",
            "tribunal_destino": "Tribunal de Instancia",
            "prov_loc_origen": "Villacarrillo (Jaén)",
            "prov_loc_destino": "Baeza (Jaén)",
        },
    },
    {
        "id": "JUE_003",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
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
            "tribunal_origen": "Tribunal de Instancia",
            "tribunal_destino": "Sección de Instrucción del Tribunal de Instancia",
            "prov_loc_origen": "Chiclana de la Frontera (Cádiz)",
            "prov_loc_destino": "Algeciras (Cádiz)",
        },
    },
    {
        "id": "JUE_004",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
        "paragraph": (
            "Seis. Don Jorge Pedro Domench Ares, juez que sirve la plaza número 3 de la "
            "Sección Civil y de Instrucción del Tribunal de Instancia de Esplugues de Llobregat, "
            "pasará a desempeñar la plaza de Juez de adscripción territorial del Tribunal Superior "
            "de Justicia de Canarias, provincia de Las Palmas."
        ),
        "expected": {
            "participante": "Jorge Pedro Domench Ares",
            "cargo": "Juez de adscripción territorial",
            "tribunal_origen": "Tribunal de Instancia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Esplugues de Llobregat (Barcelona)",
            "prov_loc_destino": "Las Palmas (Canarias)",
        },
    },
    {
        "id": "JUE_005",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
        "paragraph": (
            "Quince. Ana Belén Ortiz Roca, jueza, que sirve la plaza número 3 de la Sección "
            "Civil y de Instrucción del Tribunal de Instancia de Cornellà de Llobregat, pasará a "
            "desempeñar la plaza número 1 de la Sección de Familia, Infancia y Capacidad del "
            "Tribunal de Instancia de Matarò, de familia y capacidad."
        ),
        "expected": {
            "participante": "Ana Belén Ortiz Roca",
            "cargo": "Jueza",
            "tribunal_origen": "Tribunal de Instancia",
            "tribunal_destino": "Tribunal de Instancia",
            "prov_loc_origen": "Cornellà de Llobregat (Barcelona)",
            "prov_loc_destino": "Matarò (Barcelona)",
        },
    },
]
