"""
Tests unitarios de participant_parser.py con párrafos reales de BOE.

Solo valida extracción de participante, sin depender del pipeline completo.
"""

import pytest

from src.infrastructure.pdf.participant_parser import extract_participant


PARTICIPANT_CASES = [
    (
        "Uno. Doña Carmen García Vallina, jueza de adscripción territorial del Tribunal "
        "Superior de Justicia de Cataluña, provincia de Girona, pasará a desempeñar la plaza "
        "de jueza de adscripción territorial del Tribunal Superior de Justicia de Madrid.",
        "Carmen García Vallina",
    ),
    (
        "Quince. Ana Belén Ortiz Roca, jueza, que sirve la plaza número 3 de la Sección "
        "Civil y de Instrucción del Tribunal de Instancia de Cornellà de Llobregat, pasará "
        "a desempeñar la plaza número 1 de la Sección de Familia, Infancia y Capacidad del "
        "Tribunal de Instancia de Matarò, de familia y capacidad.",
        "Ana Belén Ortiz Roca",
    ),
    (
        "Cuatro. Doña María Jesús Millán de las Heras, magistrada, especialista de menores, "
        "en situación administrativa de servicios especiales en la Carrera Judicial, que sirve "
        "la plaza número 2 de la Sección de Menores del Tribunal de Instancia de Madrid, de "
        "ejecuciones de los juzgados de menores (antes JMEN 2), pasará a desempeñar la plaza "
        "número 7 de la Sección de Menores del Tribunal de Instancia de Madrid, de ejecuciones "
        "de los juzgados de menores (antes JMEN 7), continuando en la misma situación administrativa.",
        "María Jesús Millán de las Heras",
    ),
    (
        "Sesenta y ocho. Don Oscar Luis Rojas de la Viuda, magistrado, que sirve la plaza "
        "número 3 de la Sección de lo Contencioso-administrativo del Tribunal de Instancia de "
        "Valladolid (antes JCA 3), pasará a desempeñar la plaza de magistrado de la Sala de lo "
        "Contencioso-Administrativo del Tribunal Superior de Justicia de Castilla y León, con "
        "sede en Burgos.",
        "Oscar Luis Rojas de la Viuda",
    ),
]


@pytest.mark.parametrize("paragraph, expected", PARTICIPANT_CASES)
def test_extract_participant_real_cases(paragraph, expected):
    assert extract_participant(paragraph) == expected
