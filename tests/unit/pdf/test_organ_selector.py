"""
Tests unitarios de organ_selector.py con párrafos reales de BOE.

Valida:
- Filtrado por bloque con TextBlock
- Scoring correcto
- Elección del órgano adecuado entre varios candidatos
"""


from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.organ_selector import pick_best_organo, select_organs_by_block
from src.infrastructure.pdf.row_parser import split_origin_destination
from src.infrastructure.pdf.parse_models import TextBlock


def test_pick_best_organo_andrea_dominguez():
    """
    Andrea Domínguez: origen sección civil e instrucción, destino sección instrucción.
    La cláusula 'mientras su titular...' no debe afectar la selección de destino.
    """
    paragraph = (
        "Tres. Doña Andrea Domínguez González, jueza, que sirve la plaza número 3 de la "
        "Sección Civil y de Instrucción del Tribunal de Instancia de Chiclana de la Frontera, "
        "pasará a desempeñar la plaza número 5 de la Sección de Instrucción del Tribunal de "
        "Instancia de Algeciras, mientras su titular don Jerónimo García San Martín se "
        "encuentre en la situación administrativa de servicios especiales en la Carrera Judicial."
    )

    organ_matches = extract_organs(paragraph)
    bloque_origen, bloque_destino = split_origin_destination(paragraph)

    origen = pick_best_organo(organ_matches, bloque_origen)
    destino = pick_best_organo(organ_matches, bloque_destino)

    assert origen is not None
    assert destino is not None

    assert origen.organ_type == "Tribunal de Instancia"
    assert origen.locality == "Chiclana de la Frontera"

    assert destino.seccion == "Sección de Instrucción"
    assert destino.locality == "Algeciras"


def test_pick_best_organo_maria_carmen_cimas():
    """
    María Carmen Cimas: origen con alias (antes JP 13), destino Audiencia Nacional.
    El alias no debe ser tomado como órgano.
    """
    paragraph = (
        "Siete. Doña María Carmen Cimas Giménez, magistrada, que sirve la plaza número 13 "
        "de la Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13), pasará "
        "a desempeñar la plaza de magistrada de la Sala de lo Penal de la Audiencia Nacional."
    )

    organ_matches = extract_organs(paragraph)
    bloque_origen, bloque_destino = split_origin_destination(paragraph)

    origen = pick_best_organo(organ_matches, bloque_origen)
    destino = pick_best_organo(organ_matches, bloque_destino)

    assert origen is not None
    assert destino is not None

    assert origen.seccion == "Sección de lo Penal"
    assert origen.locality == "Madrid"
    assert destino.organ_type == "Audiencia Nacional"


def test_select_organs_by_block_filters_by_range():
    """
    Verifica que select_organs_by_block filtra órganos por posición absoluta,
    no por substring matching.
    """
    paragraph = (
        "Uno. Doña María García, jueza de la Audiencia Provincial de Sevilla, "
        "pasará a desempeñar su puesto en la Audiencia Provincial de Cádiz."
    )

    organ_matches = extract_organs(paragraph)
    bloque_origen, bloque_destino = split_origin_destination(paragraph)

    organos_origen = select_organs_by_block(organ_matches, bloque_origen)
    organos_destino = select_organs_by_block(organ_matches, bloque_destino)

    # Each block should only contain organs from that side
    assert len(organos_origen) >= 1
    assert len(organos_destino) >= 1

    # Origin organs should be in origin block range
    for organ in organos_origen:
        assert bloque_origen.start <= organ.start < bloque_origen.end

    # Destination organs should be in destination block range
    for organ in organos_destino:
        assert bloque_destino.start <= organ.start < bloque_destino.end


def test_select_organs_by_block_empty_when_no_match():
    """Bloque vacío no debe devolver órganos."""
    organ_matches = extract_organs("Audiencia Provincial de Sevilla")
    empty_block = TextBlock(text="", start=1000, end=2000)

    result = select_organs_by_block(organ_matches, empty_block)
    assert result == []
