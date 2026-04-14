"""Tests de integración con patrones reales de BOE para magistrados y jueces.

Estos tests cubren los patrones problemáticos encontrados en los PDFs reales:
- Sección del Tribunal de Instancia
- Adscripción territorial
- (antes ...) alias históricos
- pasará a desempeñar separación origen/destino
- provincias explícitas
- bloques de corte (exclusiones, incidencias)
"""


from src.infrastructure.pdf.organ_extractor import extract_organs
from src.infrastructure.pdf.organ_selector import (
    pick_best_organo,
    _looks_like_alias,
)
from src.infrastructure.pdf.participant_parser import extract_participant
from src.infrastructure.pdf.cargo_parser import extract_cargo
from src.infrastructure.pdf.row_parser import (
    split_origin_destination,
)
from src.infrastructure.pdf.paragraph_splitter import (
    build_candidate_paragraphs,
    _is_cutoff_block,
)


class TestSeccionTribunalInstancia:
    """Tests para el patrón 'Sección ... del Tribunal de Instancia de ...'"""

    def test_seccion_instruccion_barcelona(self):
        text = "plaza número 2 de la Sección de Instrucción del Tribunal de Instancia de Barcelona"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal de Instancia"
        assert "Barcelona" in results[0].locality

    def test_seccion_violencia_mujer_madrid(self):
        text = "plaza número 1 de la Sección de Violencia sobre la Mujer del Tribunal de Instancia de Madrid"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal de Instancia"
        assert "Madrid" in results[0].locality
        assert "Violencia" in results[0].seccion

    def test_seccion_civil_instruccion_baeza(self):
        text = "Sección Civil y de Instrucción del Tribunal de Instancia de Baeza"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal de Instancia"

    def test_seccion_familia_infancia_capacidad(self):
        text = "Sección de Familia, Infancia y Capacidad del Tribunal de Instancia de Matarò"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].organ_type == "Tribunal de Instancia"
        assert "Matarò" in results[0].locality

    def test_plaza_numero_extraida(self):
        text = "plaza número 3 de la Sección de lo Penal del Tribunal de Instancia de Valencia"
        results = extract_organs(text)
        assert len(results) == 1
        assert results[0].numero_plaza == "3"


class TestAdscripcionTerritorial:
    """Tests para 'juez/jueza de adscripción territorial'."""

    def test_jueza_adscripcion_tsj(self):
        text = "jueza de adscripción territorial del Tribunal Superior de Justicia de Cataluña, provincia de Girona"
        results = extract_organs(text)
        assert len(results) >= 1
        # Debe encontrar el TSJ
        tsj_matches = [r for r in results if "Superior" in r.organ_type]
        assert len(tsj_matches) >= 1

    def test_juez_adscripcion_tsj_valencia(self):
        text = "juez de adscripción territorial del Tribunal Superior de Justicia de la Comunitat Valenciana"
        results = extract_organs(text)
        tsj_matches = [r for r in results if "Superior" in r.organ_type]
        assert len(tsj_matches) >= 1


class TestAliasHistorico:
    """Tests para '(antes ...)' aliases."""

    def test_alias_detected(self):
        text = "Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13)"
        results = extract_organs(text)
        assert len(results) >= 1
        # El alias debe estar capturado
        assert results[0].alias_historico == "JP 13"

    def test_alias_jinstr(self):
        text = "Sección de Instrucción del Tribunal de Instancia de Barcelona (antes JINSTR 1)"
        results = extract_organs(text)
        assert len(results) >= 1
        assert "JINSTR" in results[0].alias_historico or "JINSTR 1" in results[0].alias_historico

    def test_looks_like_alias(self):
        assert _looks_like_alias("JPI 14") is True
        assert _looks_like_alias("JCA 9") is True
        assert _looks_like_alias("JINSTR 3") is True
        assert _looks_like_alias("Audiencia Provincial") is False


class TestOriginDestinationSplit:
    """Tests para la separación por 'pasará a desempeñar'."""

    def test_splits_correctly(self):
        text = (
            "Uno. Doña María García, magistrada de la "
            "Audiencia Provincial de Sevilla, pasará a desempeñar "
            "su puesto en la Audiencia Provincial de Cádiz."
        )
        origen, destino = split_origin_destination(text)
        assert "Audiencia Provincial de Sevilla" in origen
        assert "Audiencia Provincial de Cádiz" in destino
        assert "pasará a desempeñar" in destino

    def test_no_split_when_no_separator(self):
        text = "Dos. Don Carlos, juez del Tribunal Supremo."
        origen, destino = split_origin_destination(text)
        assert origen == text
        assert destino == ""

    def test_best_organo_from_origin(self):
        text = (
            "magistrada de la Audiencia Provincial de Sevilla, "
            "especialista en menores"
        )
        organs = extract_organs(text)
        match = pick_best_organo(organs, text)
        assert match is not None
        assert "Audiencia Provincial" in match.organ_type


class TestCargoExtraction:
    """Tests para extracción robusta de cargo."""

    def test_magistrada(self):
        text = "Uno. Doña Ana López, magistrada, especialista en menores, pasará..."
        cargo = extract_cargo(text)
        assert "magistrada" in cargo.lower() or "especialista" in cargo.lower()

    def test_jueza_adscripcion(self):
        text = "Dos. Doña María García, jueza de adscripción territorial del TSJ de Cataluña"
        cargo = extract_cargo(text)
        assert "adscripción" in cargo.lower()

    def test_magistrado_especialista(self):
        text = "Tres. Don Pedro Martín, magistrado, especialista del orden jurisdiccional contencioso-administrativo"
        cargo = extract_cargo(text)
        assert "magistrado" in cargo.lower()

    def test_juez_que_sirve(self):
        text = "Cuatro. Don Jorge Pedro, juez que sirve en la Audiencia Provincial de Valencia"
        cargo = extract_cargo(text)
        assert "juez" in cargo.lower()


class TestCutoffBlocks:
    """Tests para detección de bloques de corte."""

    def test_excluir_solicitudes(self):
        text = "Excluir las siguientes solicitudes de traslado por no cumplir los requisitos."
        assert _is_cutoff_block(text) is True

    def test_incidencias(self):
        text = "Incidencias: La incidencia que en la resolución de los presentes expedientes"
        assert _is_cutoff_block(text) is True

    def test_contra_presente_disposicion(self):
        text = "Contra la presente disposición cabe interponer recurso."
        assert _is_cutoff_block(text) is True

    def test_normal_paragraph_not_cutoff(self):
        text = "Doña María García, magistrada de la Audiencia Provincial"
        assert _is_cutoff_block(text) is False

    def test_cutoff_stops_paragraph_grouping(self):
        text = (
            "Uno. Doña María, magistrada, pasará a la AP de Sevilla.\n\n"
            "Dos. Don Carlos, juez, pasará al TI de Madrid.\n\n"
            "Excluir las siguientes solicitudes.\n\n"
            "Tres. Esto no debe parsearse."
        )
        result = build_candidate_paragraphs(text)
        assert len(result) == 2
        assert not any("Esto no debe parsearse" in p for p in result)


class TestSalaTSJ:
    """Tests para 'Sala de ... del Tribunal Superior de Justicia'."""

    def test_sala_contencioso_navarra(self):
        text = "Sala de lo Contencioso-Administrativo del Tribunal Superior de Justicia de Navarra"
        results = extract_organs(text)
        assert len(results) >= 1
        tsj = [r for r in results if "Superior" in r.organ_type]
        assert len(tsj) >= 1
        assert "Navarra" in tsj[0].locality


class TestRealParagraphs:
    """Tests con párrafos reales recortados de BOE."""

    def test_full_paragraph_ap_to_ap(self):
        text = (
            "Uno. Doña María García López, magistrada, de la "
            "Audiencia Provincial de A Coruña, pasará a desempeñar "
            "su puesto en la Audiencia Provincial de A Coruña."
        )
        participant = extract_participant(text)
        assert "María García López" in participant

        results = extract_organs(text)
        assert len(results) >= 1

    def test_full_paragraph_with_before_alias(self):
        text = (
            "Dos. Don Juan Pérez, magistrado, de la "
            "Sección de lo Penal del Tribunal de Instancia de Madrid (antes JP 13), "
            "pasará a desempeñar su puesto en la "
            "Sección de lo Civil del Tribunal de Instancia de Barcelona."
        )
        participant = extract_participant(text)
        assert "Juan Pérez" in participant

        results = extract_organs(text)
        assert len(results) >= 2
        # El alias no debe ser un órgano principal
        alias_matches = [r for r in results if "JP 13" in r.raw]
        assert len(alias_matches) == 0

    def test_full_paragraph_adscripcion(self):
        text = (
            "Tres. Doña Ana Rodríguez, jueza de adscripción territorial del "
            "Tribunal Superior de Justicia de Cataluña, provincia de Girona, "
            "pasará a desempeñar su puesto en el Juzgado de lo Social nº 2 de Barcelona."
        )
        participant = extract_participant(text)
        assert "Ana Rodríguez" in participant

        cargo = extract_cargo(text)
        assert "adscripción" in cargo.lower()
