"""
Casos de bloques no resolutivos que no deben generar ExtractedRow.

Incluye: incidencias, exclusiones, recursos.
"""

NON_RESOLUTION_CASES = [
    {
        "id": "NONRES_JUE_001",
        "source_pdf": "BOE 09.02.26- Resolución concurso Jueces-zas (1).pdf",
        "paragraph": (
            "Veintiuno. Incidencias. Derivadas de la valoración, como mérito preferente, del "
            "idioma y el derecho propio de las Comunidades Autónomas. Obtiene la plaza número 2 "
            "de la Sección de Instrucción del Tribunal de Instancia de L'Hospitalet de Llobregat, "
            "la jueza Anna Pons Estebanell, con número de escalafón 470, con preferencia sobre "
            "los/as jueces/zas con mejor número de escalafón. Obtiene la plaza número 1 de la "
            "Sección de lo Penal del Tribunal de Instancia de Mataró, la jueza María Maianti "
            "Lázaro, con número de escalafón 512 con preferencia sobre los/as jueces/zas con "
            "mejor número de escalafón."
        ),
    },
    {
        "id": "NONRES_MAG_001",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Ciento setenta. Excluir las siguientes solicitudes:"
        ),
    },
    {
        "id": "NONRES_MAG_002",
        "source_pdf": "BOE 20.01.26 RESOLUCION CONCURSO MAGISTRADOS.pdf",
        "paragraph": (
            "Ciento setenta y uno. La incidencia que en la resolución de este concurso han tenido "
            "las preferencias de los artículos 329, 330 y 340 de la Ley Orgánica del Poder Judicial, "
            "ha sido la siguiente:"
        ),
    },
]
