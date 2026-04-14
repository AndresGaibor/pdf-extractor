"""
Tests unitarios de cargo_parser.py con párrafos reales de BOE.
"""

import pytest

from src.infrastructure.pdf.cargo_parser import extract_cargo


CARGO_CASES = [
    (
        (
            "Dos. Doña María Ruiz García, jueza, que sirve la plaza número 2 de la Sección "
            "Civil y de Instrucción del Tribunal de Instancia de Villacarrillo, pasará a "
            "desempeñar la plaza número 1 de la Sección Civil y de Instrucción del Tribunal "
            "de Instancia de Baeza, con competencia en violencia sobre la mujer."
        ),
        "Jueza",
    ),
    (
        (
            "Uno. Doña Carmen García Vallina, jueza de adscripción territorial del Tribunal "
            "Superior de Justicia de Cataluña, provincia de Girona, pasará a desempeñar la plaza "
            "de jueza de adscripción territorial del Tribunal Superior de Justicia de Madrid."
        ),
        "Jueza de adscripción territorial",
    ),
    (
        (
            "Cinco. Doña María Fernanda Navarro Zuloaga, magistrada, especialista del orden "
            "jurisdiccional contencioso-administrativo, con destino en la Sala del mismo orden "
            "jurisdiccional del Tribunal Superior de Justicia de Cataluña, pasará a desempeñar la "
            "plaza de magistrada de la Sala de lo Contencioso-Administrativo del Tribunal Superior "
            "de Justicia de Navarra, ocupando plaza de especialista."
        ),
        "Magistrada especialista",
    ),
    (
        (
            "Diez. Doña María del Carmen García Martínez, magistrada, en situación administrativa "
            "de servicios especiales en la Carrera Judicial, que sirve la plaza número 18 de la "
            "Sección de Instrucción del Tribunal de Instancia de Barcelona (antes JINSTR 18), "
            "pasará a desempeñar la plaza número 1 de la Sección de Vigilancia Penitenciaria del "
            "Tribunal de Instancia de Barcelona (antes JVP 1), continuando en la misma situación "
            "administrativa."
        ),
        "Magistrada (servicios especiales)",
    ),
    (
        (
            "Uno. Don Carlos Fuentes Candelas, magistrado, con destino en la Audiencia Provincial "
            "de A Coruña, orden civil, pasará a desempeñar la plaza de presidente de la Sección "
            "Quinta, civil, de la Audiencia Provincial de A Coruña."
        ),
        "Magistrado",
    ),
]


@pytest.mark.parametrize("paragraph, expected", CARGO_CASES)
def test_extract_cargo_real_cases(paragraph, expected):
    assert extract_cargo(paragraph) == expected
