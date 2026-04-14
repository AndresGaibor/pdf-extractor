"""
Parser de párrafos individuales para extraer campos de ExtractedRow.

Pipeline por etapas con rangos absolutos:
1. Extraer participante (participant_parser)
2. Extraer cargo (cargo_parser)
3. Separar origen/destino por "pasará a desempeñar" → TextBlock con rangos
4. Filtrar órganos por rango (organ_selector)
5. Elegir mejor órgano por scoring (organ_selector)
6. Resolver provincia/localidad
7. Construir ExtractedRow

Trabaja exclusivamente sobre OrganMatch pre-extraídos, nunca re-extrae.
"""

import logging
import re
from typing import Optional

from src.domain.models.extracted_data import ExtractedRow
from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.parse_models import OrganMatch, TextBlock
from src.infrastructure.pdf.participant_parser import extract_participant
from src.infrastructure.pdf.cargo_parser import extract_cargo
from src.infrastructure.pdf.organ_selector import pick_best_organo, select_organs_by_block

logger = logging.getLogger(__name__)

# Separador clave entre origen y destino en BOE
PASARA_SEPARATOR = "pasará a desempeñar"


def split_origin_destination(parrafo: str) -> tuple[TextBlock, TextBlock | None]:
    """
    Divide el párrafo en bloque de origen y bloque de destino
    usando el separador 'pasará a desempeñar'.

    Devuelve TextBlock con posiciones absolutas en el párrafo original.
    """
    if PASARA_SEPARATOR in parrafo:
        idx = parrafo.index(PASARA_SEPARATOR)
        bloque_origen = TextBlock(
            text=parrafo[:idx].strip(),
            start=0,
            end=idx,
        )
        bloque_destino = TextBlock(
            text=parrafo[idx:].strip(),
            start=idx,
            end=len(parrafo),
        )
        return (bloque_origen, bloque_destino)

    # Si no hay separador, todo es origen
    return (TextBlock(text=parrafo, start=0, end=len(parrafo)), None)


def extract_provincias_explicitas(
    texto: str,
    organ_matches: list[OrganMatch],
) -> dict[int, str]:
    """
    Detecta menciones explícitas de "provincia de ..." y las asigna
    al tribunal más cercano por distancia en el texto.

    Devuelve un dict {indice_tribunal: provincia}.
    """
    if not organ_matches or not texto:
        return {}

    texto_normalizado = re.sub(r'\s+', ' ', texto)
    patron_provincia = re.compile(
        r',\s*provincia\s+de\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s\-]+)',
        re.IGNORECASE
    )

    resultado: dict[int, str] = {}
    for match_prov in patron_provincia.finditer(texto_normalizado):
        provincia = match_prov.group(1).strip()
        provincia = re.sub(r'[.,;:\s]+$', '', provincia)
        pos_provincia = match_prov.start()

        tribunal_mas_cercano = -1
        menor_distancia = float('inf')

        for i, organ in enumerate(organ_matches):
            pos_tribunal = texto_normalizado.find(organ.raw)
            if pos_tribunal == -1:
                continue
            distancia = pos_provincia - (pos_tribunal + len(organ.raw))
            if 0 <= distancia < menor_distancia:
                menor_distancia = distancia
                tribunal_mas_cercano = i

        if tribunal_mas_cercano >= 0:
            resultado[tribunal_mas_cercano] = provincia

    return resultado


def parse_paragraph(
    parrafo: str,
    organ_matches: list[OrganMatch],
    transform_service: TransformDataService,
    debug: bool = False,
) -> ExtractedRow | None:
    """
    Parsea un párrafo completo y devuelve un ExtractedRow si es válido.

    Pipeline:
    1. Extraer participante (regex anclada)
    2. Extraer cargo (reglas estructuradas)
    3. Dividir por "pasará a desempeñar" → TextBlocks con rangos
    4. Filtrar órganos por rango en cada bloque
    5. Elegir mejor órgano por scoring
    6. Resolver provincia/localidad
    """
    # 1. Extraer participante
    participante = extract_participant(parrafo)
    if not participante or len(participante.split()) < 2:
        return None

    # Limpiar prefijos de tratamiento
    participante = participante.replace("Doña ", "").replace("Don ", "")

    # 2. Extraer cargo
    cargo = extract_cargo(parrafo)

    # 3. Dividir por "pasará a desempeñar"
    bloque_origen, bloque_destino = split_origin_destination(parrafo)

    # 4. Filtrar órganos por rango en cada bloque
    _ = select_organs_by_block(organ_matches, bloque_origen)  # para debug
    _ = select_organs_by_block(organ_matches, bloque_destino) if bloque_destino else []

    # 5. Elegir mejor órgano de cada bloque (scoring)
    origen_match = pick_best_organo(organ_matches, bloque_origen)
    destino_match = pick_best_organo(organ_matches, bloque_destino) if bloque_destino else None

    # Extraer provincias explícitas
    provincias = extract_provincias_explicitas(parrafo, organ_matches)

    # 6. Resolver origen
    tribunal_origen = ""
    prov_loc_origen = ""
    if origen_match:
        tribunal_origen = _build_organ_label(origen_match)

        idx_origen = _find_organ_index(organ_matches, origen_match)
        if idx_origen is not None and idx_origen in provincias:
            prov_loc_origen = transform_service.resolve_localidad(
                provincias[idx_origen], origen_match.raw
            )
        else:
            prov_loc_origen = transform_service.resolve_localidad(
                origen_match.locality, origen_match.raw
            )

    # 7. Resolver destino
    tribunal_destino = ""
    prov_loc_destino = ""
    if destino_match:
        tribunal_destino = _build_organ_label(destino_match)

        idx_destino = _find_organ_index(organ_matches, destino_match)
        if idx_destino is not None and idx_destino in provincias:
            prov_loc_destino = transform_service.resolve_localidad(
                provincias[idx_destino], destino_match.raw
            )
        else:
            prov_loc_destino = transform_service.resolve_localidad(
                destino_match.locality, destino_match.raw
            )

    return ExtractedRow(
        participante=participante,
        cargo=cargo,
        tribunal_origen=tribunal_origen,
        tribunal_destino=tribunal_destino,
        prov_loc_origen=prov_loc_origen,
        prov_loc_destino=prov_loc_destino,
    )


def parse_paragraph_debug(
    parrafo: str,
    organ_matches: list[OrganMatch],
    transform_service: TransformDataService,
) -> Optional:
    """
    Versión de parse_paragraph con trazabilidad completa.

    Devuelve un ParagraphParseResult con toda la información del proceso.
    """
    from src.infrastructure.pdf.parse_models import ParagraphParseResult, ParseIssue

    issues: list[ParseIssue] = []

    # 1. Extraer participante
    participante = extract_participant(parrafo)
    if not participante or len(participante.split()) < 2:
        issues.append(ParseIssue(
            paragraph_preview=parrafo[:200],
            stage="participant",
            error="Participante vacío o menos de 2 palabras",
        ))
        return ParagraphParseResult(
            raw_text=parrafo,
            participante="",
            issues=issues,
        )

    participante = participante.replace("Doña ", "").replace("Don ", "")

    # 2. Extraer cargo
    cargo = extract_cargo(parrafo)

    # 3. Dividir por "pasará a desempeñar"
    bloque_origen, bloque_destino = split_origin_destination(parrafo)

    # 4. Filtrar órganos por rango
    organos_origen = select_organs_by_block(organ_matches, bloque_origen)
    organos_destino = select_organs_by_block(organ_matches, bloque_destino) if bloque_destino else []

    # 5. Elegir mejor órgano
    origen_match = pick_best_organo(organ_matches, bloque_origen)
    destino_match = pick_best_organo(organ_matches, bloque_destino) if bloque_destino else None

    if not origen_match:
        issues.append(ParseIssue(
            paragraph_preview=parrafo[:200],
            stage="origin_organs",
            error="No se encontró órgano de origen en el bloque",
            context=f"Órganos disponibles: {len(organos_origen)}",
        ))

    if bloque_destino and not destino_match:
        issues.append(ParseIssue(
            paragraph_preview=parrafo[:200],
            stage="destination_organs",
            error="No se encontró órgano de destino en el bloque",
            context=f"Órganos disponibles: {len(organos_destino)}",
        ))

    # Extraer provincias
    provincias = extract_provincias_explicitas(parrafo, organ_matches)

    # 6. Resolver origen
    tribunal_origen = ""
    prov_loc_origen = ""
    if origen_match:
        tribunal_origen = _build_organ_label(origen_match)
        idx_origen = _find_organ_index(organ_matches, origen_match)
        if idx_origen is not None and idx_origen in provincias:
            prov_loc_origen = transform_service.resolve_localidad(
                provincias[idx_origen], origen_match.raw
            )
        else:
            prov_loc_origen = transform_service.resolve_localidad(
                origen_match.locality, origen_match.raw
            )

    # 7. Resolver destino
    tribunal_destino = ""
    prov_loc_destino = ""
    if destino_match:
        tribunal_destino = _build_organ_label(destino_match)
        idx_destino = _find_organ_index(organ_matches, destino_match)
        if idx_destino is not None and idx_destino in provincias:
            prov_loc_destino = transform_service.resolve_localidad(
                provincias[idx_destino], destino_match.raw
            )
        else:
            prov_loc_destino = transform_service.resolve_localidad(
                destino_match.locality, destino_match.raw
            )

    return ParagraphParseResult(
        raw_text=parrafo,
        participante=participante,
        cargo=cargo,
        bloque_origen=bloque_origen,
        bloque_destino=bloque_destino,
        organos_origen=organos_origen,
        organos_destino=organos_destino,
        origen_elegido=origen_match,
        destino_elegido=destino_match,
        tribunal_origen=tribunal_origen,
        tribunal_destino=tribunal_destino,
        prov_loc_origen=prov_loc_origen,
        prov_loc_destino=prov_loc_destino,
        issues=issues,
    )


def _build_organ_label(organ: OrganMatch) -> str:
    """Construye la etiqueta completa del órgano con sección si aplica."""
    label = organ.organ_type
    if organ.seccion:
        label = f"{organ.seccion} del {organ.organ_type}"
    return label


def _find_organ_index(
    organ_matches: list[OrganMatch],
    target: OrganMatch,
) -> Optional[int]:
    """Encuentra el índice de un órgano en la lista por posición."""
    for i, organ in enumerate(organ_matches):
        if organ.start == target.start and organ.end == target.end:
            return i
        if organ.raw == target.raw:
            return i
    return None
