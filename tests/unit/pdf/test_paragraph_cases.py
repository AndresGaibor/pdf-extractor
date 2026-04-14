"""
Tests unitarios con párrafos reales de BOE para validar el pipeline completo.

Cada caso prueba:
- extract_participant
- extract_cargo
- extract_organs
- split_origin_destination
- parse_paragraph
"""

import pytest

from src.domain.services.transform_data import TransformDataService
from src.infrastructure.persistence.territories_repository_json import (
    TerritoriesRepositoryJSON,
)
from src.infrastructure.pdf.participant_parser import extract_participant
from src.infrastructure.pdf.cargo_parser import extract_cargo
from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.row_parser import (
    split_origin_destination,
    parse_paragraph,
)


@pytest.fixture(scope="module")
def transform_service():
    territories_repo = TerritoriesRepositoryJSON()
    return TransformDataService(territories_repo)


# ---------------------------------------------------------------------------
# Caso 1: Adscripción territorial simple
# ---------------------------------------------------------------------------
class TestAdscripcionTerritorial:
    """Carmen García Vallina con TSJ Cataluña, provincia de Girona."""

    PARAGRAPH = (
        "Uno. Doña Carmen García Vallina, jueza de adscripción territorial "
        "del Tribunal Superior de Justicia de Cataluña, provincia de Girona, "
        "pasará a desempeñar su puesto como jueza de adscripción territorial "
        "del Tribunal Superior de Justicia de Madrid."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "Carmen García Vallina"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert "adscripción" in result.lower()

    def test_organs_detected(self):
        results = extract_organs(self.PARAGRAPH)
        tsj = [r for r in results if "Superior" in r.organ_type]
        assert len(tsj) >= 2

    def test_split_origin_destination(self):
        origen, destino = split_origin_destination(self.PARAGRAPH)
        assert "Cataluña" in origen.text
        assert "Madrid" in destino.text
        assert origen.start == 0
        assert destino.end == len(self.PARAGRAPH)


# ---------------------------------------------------------------------------
# Caso 2: Sección Civil y de Instrucción
# ---------------------------------------------------------------------------
class TestSeccionCivilInstruccion:
    """María Ruiz García con origen Villacarrillo y destino Baeza."""

    PARAGRAPH = (
        "Dos. Doña María Ruiz García, jueza, que sirve la plaza número 2 "
        "de la Sección Civil y de Instrucción del Tribunal de Instancia "
        "de Villacarrillo, pasará a desempeñar la plaza número 1 de la "
        "Sección Civil y de Instrucción del Tribunal de Instancia de Baeza, "
        "con competencia en violencia sobre la mujer."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "María Ruiz García"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert result in ["jueza", "Jueza"]

    def test_organs_detected(self):
        results = extract_organs(self.PARAGRAPH)
        ti = [r for r in results if "Instancia" in r.organ_type]
        assert len(ti) >= 2

    def test_split(self):
        origen, destino = split_origin_destination(self.PARAGRAPH)
        assert "Villacarrillo" in origen.text
        assert "Baeza" in destino.text


# ---------------------------------------------------------------------------
# Caso 3: Destino con Sección de Instrucción
# ---------------------------------------------------------------------------
class TestDestinoInstruccionAlgeciras:
    """Andrea Domínguez González con destino Algeciras."""

    PARAGRAPH = (
        "Tres. Doña Andrea Domínguez González, jueza, que sirve la plaza "
        "número 3 de la Sección Civil y de Instrucción del Tribunal de "
        "Instancia de Chiclana de la Frontera, pasará a desempeñar la plaza "
        "número 5 de la Sección de Instrucción del Tribunal de Instancia "
        "de Algeciras, mientras su titular don Jerónimo García San Martín "
        "se encuentre en la situación administrativa de servicios especiales."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "Andrea Domínguez González"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert result in ["jueza", "Jueza"]

    def test_organs_detected(self):
        results = extract_organs(self.PARAGRAPH)
        # Must find at least 2 Tribunal de Instancia
        ti = [r for r in results if "Instancia" in r.organ_type]
        assert len(ti) >= 2

    def test_split(self):
        origen, destino = split_origin_destination(self.PARAGRAPH)
        assert "Chiclana" in origen.text
        assert "Algeciras" in destino.text


# ---------------------------------------------------------------------------
# Caso 4: Nombre sin Don/Doña
# ---------------------------------------------------------------------------
class TestNombreSinTratamiento:
    """Ana Belén Ortiz Roca con destino Sección de Familia, Infancia y Capacidad."""

    PARAGRAPH = (
        "Quince. Ana Belén Ortiz Roca, jueza, que sirve la plaza número 3 "
        "de la Sección Civil y de Instrucción del Tribunal de Instancia "
        "de Igualada, pasará a desempeñar la plaza número 1 de la Sección "
        "de Familia, Infancia y Capacidad del Tribunal de Instancia de Matarò."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "Ana Belén Ortiz Roca"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert result in ["jueza", "Jueza"]

    def test_organs_detected(self):
        results = extract_organs(self.PARAGRAPH)
        assert len(results) >= 2

    def test_split(self):
        origen, destino = split_origin_destination(self.PARAGRAPH)
        assert "Igualada" in origen.text
        assert "Matarò" in destino.text


# ---------------------------------------------------------------------------
# Caso 5: TSJ con Sala
# ---------------------------------------------------------------------------
class TestTSJConSala:
    """María Fernanda Navarro Zuloaga con origen Cataluña y destino Navarra."""

    PARAGRAPH = (
        "Catorce. Doña María Fernanda Navarro Zuloaga, magistrada, de la "
        "Sala de lo Contencioso-Administrativo del Tribunal Superior de "
        "Justicia de Cataluña, pasará a desempeñar su puesto en la Sala "
        "de lo Contencioso-Administrativo del Tribunal Superior de Justicia "
        "de Navarra."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "María Fernanda Navarro Zuloaga"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert "magistrada" in result.lower()

    def test_organs_detected(self):
        results = extract_organs(self.PARAGRAPH)
        tsj = [r for r in results if "Superior" in r.organ_type]
        assert len(tsj) >= 2


# ---------------------------------------------------------------------------
# Caso 6: Tribunal de Instancia con alias (antes ...)
# ---------------------------------------------------------------------------
class TestTribunalInstanciaConAlias:
    """María Carmen Cimas Giménez con (antes JP 13) y destino Audiencia Nacional."""

    PARAGRAPH = (
        "Diecisiete. Doña María Carmen Cimas Giménez, magistrada, de la "
        "Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13), "
        "pasará a desempeñar su puesto en la Audiencia Nacional."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "María Carmen Cimas Giménez"

    def test_alias_captured(self):
        results = extract_organs(self.PARAGRAPH)
        # At least one organ should have alias_historico
        alias_organs = [r for r in results if r.alias_historico]
        assert len(alias_organs) >= 1
        assert "JP 13" in alias_organs[0].alias_historico

    def test_split(self):
        origen, destino = split_origin_destination(self.PARAGRAPH)
        assert "Madrid" in origen.text
        assert "Audiencia Nacional" in destino.text


# ---------------------------------------------------------------------------
# Caso 7: Caso que no debe procesarse (Incidencias)
# ---------------------------------------------------------------------------
class TestIncidenciasNoDebeProcesarse:
    """Veintiuno. Incidencias... no debe generar fila normal."""

    PARAGRAPH = (
        "Veintiuno. Incidencias. Derivadas de la valoración, como mérito "
        "preferente, del idioma y el derecho propio de las Comunidades "
        "Autónomas. Obtiene la plaza número 2 de la Sección de Instrucción "
        "del Tribunal de Instancia de Barcelona."
    )

    def test_participant_invalid(self):
        # "Incidencias" should not be extracted as a participant name
        result = extract_participant(self.PARAGRAPH)
        # Either empty or something that doesn't look like "Incidencias"
        assert "incidencias" not in result.lower() if result else True


# ---------------------------------------------------------------------------
# Caso 8: Nombre con "del" en apellidos
# ---------------------------------------------------------------------------
class TestNombreConDel:
    """Nombre con 'del' en los apellidos."""

    PARAGRAPH = (
        "Cinco. Don Pedro del Río Martínez, juez, que sirve en el Juzgado "
        "de Primera Instancia de Sevilla, pasará a desempeñar su puesto "
        "en el Juzgado de lo Penal de Cádiz."
    )

    def test_participant(self):
        result = extract_participant(self.PARAGRAPH)
        assert result == "Pedro del Río Martínez"

    def test_cargo(self):
        result = extract_cargo(self.PARAGRAPH)
        assert result in ["juez", "Juez"]


# ---------------------------------------------------------------------------
# Tests del pipeline completo con parse_paragraph
# ---------------------------------------------------------------------------
class TestParseParagraphFull:
    """Tests del pipeline completo parse_paragraph con casos reales."""

    def test_full_parse_adscripcion(self, transform_service):
        paragraph = (
            "Uno. Doña Carmen García Vallina, jueza de adscripción territorial "
            "del Tribunal Superior de Justicia de Cataluña, provincia de Girona, "
            "pasará a desempeñar su puesto como jueza de adscripción territorial "
            "del Tribunal Superior de Justicia de Madrid."
        )
        organs = extract_organs(paragraph)
        row = parse_paragraph(paragraph, organs, transform_service)

        assert row is not None
        assert row.participante == "Carmen García Vallina"
        assert "adscripción" in row.cargo.lower()

    def test_full_parse_seccion_ti(self, transform_service):
        paragraph = (
            "Tres. Doña Andrea Domínguez González, jueza, que sirve la plaza "
            "número 3 de la Sección Civil y de Instrucción del Tribunal de "
            "Instancia de Chiclana de la Frontera, pasará a desempeñar la plaza "
            "número 5 de la Sección de Instrucción del Tribunal de Instancia "
            "de Algeciras."
        )
        organs = extract_organs(paragraph)
        row = parse_paragraph(paragraph, organs, transform_service)

        assert row is not None
        assert row.participante == "Andrea Domínguez González"
        assert "Instancia" in row.tribunal_origen
        assert "Instancia" in row.tribunal_destino

    def test_full_parse_sin_tratamiento(self, transform_service):
        paragraph = (
            "Quince. Ana Belén Ortiz Roca, jueza, que sirve la plaza número 3 "
            "de la Sección Civil y de Instrucción del Tribunal de Instancia "
            "de Igualada, pasará a desempeñar la plaza número 1 de la Sección "
            "de Familia, Infancia y Capacidad del Tribunal de Instancia de Matarò."
        )
        organs = extract_organs(paragraph)
        row = parse_paragraph(paragraph, organs, transform_service)

        assert row is not None
        assert row.participante == "Ana Belén Ortiz Roca"
        assert "Matarò" in row.prov_loc_destino or row.tribunal_destino
