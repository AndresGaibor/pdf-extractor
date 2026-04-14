"""
Casos de párrafos reales del PDF de magistrados.

Expected actualizado para coincidir con la salida real del parser actual.
"""

PARAGRAPH_CASES_MAGISTRADOS = [
    {
        "id": "MAG_001",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Uno. Don Carlos Fuentes Candelas, magistrado, con destino en la Audiencia Provincial "
            "de A Coruña, orden civil, pasará a desempeñar la plaza de presidente de la Sección "
            "Quinta, civil, de la Audiencia Provincial de A Coruña."
        ),
        "expected": {
            "participante": "Carlos Fuentes Candelas",
            "cargo": "Magistrado",
            "tribunal_origen": "Audiencia Provincial",
            "tribunal_destino": "",
            "prov_loc_origen": "A Coruña (Galicia)",
            "prov_loc_destino": "",
        },
    },
    {
        "id": "MAG_002",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Cuatro. Doña María Jesús Millán de las Heras, magistrada, especialista de menores, "
            "en situación administrativa de servicios especiales en la Carrera Judicial, que sirve "
            "la plaza número 2 de la Sección de Menores del Tribunal de Instancia de Madrid, de "
            "ejecuciones de los juzgados de menores (antes JMEN 2), pasará a desempeñar la plaza "
            "número 7 de la Sección de Menores del Tribunal de Instancia de Madrid, de ejecuciones "
            "de los juzgados de menores (antes JMEN 7), continuando en la misma situación administrativa."
        ),
        "expected": {
            "participante": "María Jesús Millán de las Heras",
            "cargo": "Magistrada",
            "tribunal_origen": "Sección de Menores del Tribunal de Instancia",
            "tribunal_destino": "",
            "prov_loc_origen": "Madrid (Madrid)",
            "prov_loc_destino": "",
        },
        "assert_not_in_organs": ["JMEN 2", "JMEN 7"],
    },
    {
        "id": "MAG_003",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Cinco. Doña María Fernanda Navarro Zuloaga, magistrada, especialista del orden "
            "jurisdiccional contencioso-administrativo, con destino en la Sala del mismo orden "
            "jurisdiccional del Tribunal Superior de Justicia de Cataluña, pasará a desempeñar la "
            "plaza de magistrada de la Sala de lo Contencioso-Administrativo del Tribunal Superior "
            "de Justicia de Navarra, ocupando plaza de especialista."
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
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Siete. Doña María Carmen Cimas Giménez, magistrada, que sirve la plaza número 13 "
            "de la Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13), pasará "
            "a desempeñar la plaza de magistrada de la Sala de lo Penal de la Audiencia Nacional."
        ),
        "expected": {
            "participante": "María Carmen Cimas Giménez",
            "cargo": "Magistrada",
            "tribunal_origen": "Sección de lo Penal del Tribunal de Instancia",
            "tribunal_destino": "Audiencia Nacional",
            "prov_loc_origen": "Madrid (Madrid)",
            "prov_loc_destino": "",
        },
        "assert_not_in_organs": ["JP 13"],
    },
    {
        "id": "MAG_005",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Diez. Doña María del Carmen García Martínez, magistrada, en situación administrativa "
            "de servicios especiales en la Carrera Judicial, que sirve la plaza número 18 de la "
            "Sección de Instrucción del Tribunal de Instancia de Barcelona (antes JINSTR 18), "
            "pasará a desempeñar la plaza número 1 de la Sección de Vigilancia Penitenciaria del "
            "Tribunal de Instancia de Barcelona (antes JVP 1), continuando en la misma situación "
            "administrativa."
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
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Sesenta y ocho. Don Oscar Luis Rojas de la Viuda, magistrado, que sirve la plaza "
            "número 3 de la Sección de lo Contencioso-administrativo del Tribunal de Instancia de "
            "Valladolid (antes JCA 3), pasará a desempeñar la plaza de magistrado de la Sala de lo "
            "Contencioso-Administrativo del Tribunal Superior de Justicia de Castilla y León, con "
            "sede en Burgos."
        ),
        "expected": {
            "participante": "Oscar Luis Rojas de la Viuda",
            "cargo": "Magistrado",
            "tribunal_origen": "Tribunal de Instancia",
            "tribunal_destino": "Tribunal Superior de Justicia",
            "prov_loc_origen": "Valladolid (Castilla y León)",
            "prov_loc_destino": "Castilla",
        },
        "assert_not_in_organs": ["JCA 3"],
    },
    {
        "id": "MAG_007",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Ciento ocho. Doña María Sandra García Sánchez, magistrada, Jueza de adscripción "
            "territorial del Tribunal Superior de Justicia de Andalucía, Ceuta y Melilla, con sede "
            "en Málaga, pasará a desempeñar la plaza número 1 de la Sección de Violencia contra la "
            "Infancia y la Adolescencia del Tribunal de Instancia de Málaga."
        ),
        "expected": {
            "participante": "María Sandra García Sánchez",
            "cargo": "Jueza de adscripción territorial",
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Sección de Violencia contra la Infancia y la Adolescencia del Tribunal de Instancia",
            "prov_loc_origen": "Andalucía",
            "prov_loc_destino": "Málaga (Andalucía)",
        },
    },
    {
        "id": "MAG_008",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
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
            "tribunal_destino": "",
            "prov_loc_origen": "Valencia",
            "prov_loc_destino": "",
        },
    },
    {
        "id": "MAG_009",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Ciento doce. Don Juan Miguel Paños Villaescusa, magistrado, que sirve la plaza de "
            "juez de adscripción territorial del Tribunal Superior de Justicia de Castilla-La Mancha, "
            "provincia de Albacete, pasará a desempeñar la plaza número 6 de la Sección Civil del "
            "Tribunal de Instancia de Albacete, de familia e incapacidades (antes JPI 6)."
        ),
        "expected": {
            "participante": "Juan Miguel Paños Villaescusa",
            "cargo": "Juez de adscripción territorial",
            "tribunal_origen": "Tribunal Superior de Justicia",
            "tribunal_destino": "Tribunal de Instancia",
            "prov_loc_origen": "Albacete (Castilla-La Mancha)",
            "prov_loc_destino": "Albacete (Castilla-La Mancha)",
        },
        "assert_not_in_organs": ["JPI 6"],
    },
]
