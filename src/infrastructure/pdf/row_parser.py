"""
Parser de párrafos individuales para extraer campos de ExtractedRow.

Cada función tiene una sola responsabilidad:
- extraer participante
- extraer cargo
- extraer provincias explícitas
- construir la fila final
"""

import logging
import re
from typing import Optional

from src.domain.models.extracted_data import ExtractedRow
from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.organ_patterns import CARGO_SEPARATORS
from src.infrastructure.pdf.parse_models import (
    OrganMatch,
)

logger = logging.getLogger(__name__)


def extract_participant(parrafo: str) -> str:
    """
    Extrae el nombre del participante de un párrafo numerado.

    Formato esperado: "1. Doña Ana Pérez, ...".
    Busca el texto después del primer punto y antes de la primera coma.
    """
    partes = parrafo.split('.')
    if len(partes) < 2:
        return ""
    parte_despues_punto = partes[1]
    nombre = parte_despues_punto.split(',')[0].strip()
    return nombre


def extract_cargo(parrafo: str) -> str:
    """
    Extrae el cargo del participante.

    Formato esperado: "..., Jueza del Juzgado de...".
    Busca el texto después de la segunda coma y antes del separador de cargo.
    """
    partes_punto = parrafo.split('.', 1)
    if len(partes_punto) < 2:
        return ""
    parte = partes_punto[1]
    partes_coma = parte.split(',')
    if len(partes_coma) < 2:
        return ""
    cargo_bruto = partes_coma[1].strip()

    # Cortar en el primer separador de cargo encontrado
    for separador in CARGO_SEPARATORS:
        if separador in cargo_bruto:
            cargo_bruto = cargo_bruto.split(separador)[0]

    return cargo_bruto.strip()


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
) -> Optional[ExtractedRow]:
    """
    Parsea un párrafo completo y devuelve un ExtractedRow si es válido.

    Este es el punto de entrada principal para el parsing de un párrafo.
    Coordina la extracción de participante, cargo, órganos y provincias.
    """
    parrafo[:200]

    # Extraer participante
    participante = extract_participant(parrafo)
    if not participante or len(participante.split()) < 2:
        return None

    # Limpiar prefijos de tratamiento
    participante = participante.replace("Doña ", "").replace("Don ", "")

    # Extraer cargo
    cargo = extract_cargo(parrafo)

    # Extraer provincias explícitas
    provincias = extract_provincias_explicitas(parrafo, organ_matches)

    # Resolver origen y destino
    tribunal_origen = ""
    tribunal_destino = ""
    prov_loc_origen = ""
    prov_loc_destino = ""

    if organ_matches:
        # Origen: primer tribunal
        primer_organ = organ_matches[0]
        tribunal_origen = primer_organ.organ_type

        if 0 in provincias:
            prov_loc_origen = transform_service.resolve_localidad(
                provincias[0], primer_organ.raw
            )
        else:
            prov_loc_origen = transform_service.resolve_localidad(
                primer_organ.locality, primer_organ.raw
            )

        # Destino: segundo tribunal (si existe)
        if len(organ_matches) > 1:
            segundo_organ = organ_matches[1]
            tribunal_destino = segundo_organ.organ_type

            if 1 in provincias:
                prov_loc_destino = transform_service.resolve_localidad(
                    provincias[1], segundo_organ.raw
                )
            else:
                prov_loc_destino = transform_service.resolve_localidad(
                    segundo_organ.locality, segundo_organ.raw
                )

    return ExtractedRow(
        participante=participante,
        cargo=cargo,
        tribunal_origen=tribunal_origen,
        tribunal_destino=tribunal_destino,
        prov_loc_origen=prov_loc_origen,
        prov_loc_destino=prov_loc_destino,
    )
