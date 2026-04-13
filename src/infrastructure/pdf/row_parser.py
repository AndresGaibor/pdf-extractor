"""
Parser de párrafos individuales para extraer campos de ExtractedRow.

Cada función tiene una sola responsabilidad:
- extraer participante
- extraer cargo
- extraer provincias explícitas
- separar origen/destino por "pasará a desempeñar"
- construir la fila final
"""

import logging
import re
from typing import Optional

from src.domain.models.extracted_data import ExtractedRow
from src.domain.services.transform_data import TransformDataService
from src.infrastructure.pdf.organ_patterns import CARGO_SEPARATORS
from src.infrastructure.pdf.parse_models import OrganMatch

logger = logging.getLogger(__name__)

# Separador clave entre origen y destino en BOE
PASARA_SEPARATOR = "pasará a desempeñar"


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

    Extrae la categoría base: magistrado/a, juez/jueza,
    con posibles calificativos como "de adscripción territorial",
    "especialista en ...", etc.
    """
    partes_punto = parrafo.split('.', 1)
    if len(partes_punto) < 2:
        return ""
    parte = partes_punto[1]
    partes_coma = parte.split(',')
    if len(partes_coma) < 2:
        # Intentar extraer cargo sin coma (ej: "juez que sirve ...")
        return _extract_cargo_no_coma(parte)

    # El cargo está entre la primera y segunda coma
    cargo_bruto = partes_coma[1].strip()

    # Detectar patrones especiales de cargo
    cargo_especial = _detect_special_cargo(cargo_bruto)
    if cargo_especial:
        return cargo_especial

    # Cortar en el primer separador de cargo encontrado
    for separador in CARGO_SEPARATORS:
        if separador in cargo_bruto:
            cargo_bruto = cargo_bruto.split(separador)[0]

    # Limpiar observaciones administrativas
    cargo_bruto = _clean_cargo_observaciones(cargo_bruto)

    return cargo_bruto.strip()


def _extract_cargo_no_coma(texto: str) -> str:
    """
    Extrae cargo cuando no hay coma separadora.
    Ej: "juez que sirve en la Audiencia Provincial de ..."
    """
    m = re.match(
        r'\s*(?:Don|Doña)?\s*[\w\s]+?,?\s*(juez[a]?|magistrad[a]?)\s',
        texto, re.IGNORECASE
    )
    if m:
        return m.group(1).strip().capitalize()

    m = re.search(
        r'(juez[a]?|magistrad[a]?)\s+de\s+adscripci[oó]n\s+territorial',
        texto, re.IGNORECASE
    )
    if m:
        return f"{m.group(1).strip().capitalize()} de adscripción territorial"

    return ""


def _detect_special_cargo(cargo_bruto: str) -> str:
    """
    Detecta cargos especiales que no siguen el patrón simple.
    """
    # "juez/jueza de adscripción territorial"
    m = re.search(
        r'(juez[a]?|magistrad[a]?)\s+de\s+adscripci[oó]n\s+territorial',
        cargo_bruto, re.IGNORECASE
    )
    if m:
        return f"{m.group(1).strip().capitalize()} de adscripción territorial"

    # "magistrado/a especialista en ..."
    m = re.search(
        r'(magistrad[a]?)\s*,\s*especialista\s+(?:en|del)',
        cargo_bruto, re.IGNORECASE
    )
    if m:
        return f"{m.group(1).strip().capitalize()} especialista"

    # "en situación administrativa de servicios especiales"
    if re.search(r'servicios\s+especiales', cargo_bruto, re.IGNORECASE):
        m = re.match(r'(magistrad[a]?|juez[a]?)', cargo_bruto, re.IGNORECASE)
        if m:
            return f"{m.group(1).strip().capitalize()} (servicios especiales)"

    return ""


def _clean_cargo_observaciones(cargo: str) -> str:
    """
    Limpia observaciones administrativas del cargo.
    """
    # Quitar "en situación administrativa..."
    cargo = re.sub(
        r'\s*,?\s*en\s+situaci[oó]n\s+administrativa.*',
        '', cargo, flags=re.IGNORECASE
    )
    # Quitar "mientras su titular..."
    cargo = re.sub(
        r'\s*,?\s*mientras\s+su\s+titular.*',
        '', cargo, flags=re.IGNORECASE
    )
    return cargo.strip()


def split_origin_destination(parrafo: str) -> tuple[str, str]:
    """
    Divide el párrafo en bloque de origen y bloque de destino
    usando el separador 'pasará a desempeñar'.

    Devuelve (bloque_origen, bloque_destino).
    """
    if PASARA_SEPARATOR in parrafo:
        idx = parrafo.index(PASARA_SEPARATOR)
        bloque_origen = parrafo[:idx]
        bloque_destino = parrafo[idx:]
        return (bloque_origen, bloque_destino)

    # Si no hay separador, todo es origen
    return (parrafo, "")


def extract_best_organo(
    text: str,
) -> Optional[OrganMatch]:
    """
    Extrae el mejor órgano de un bloque de texto (origen o destino).

    Busca el órgano más específico y representativo, ignorando
    aliases "(antes ...)" y referencias secundarias.
    """
    from src.infrastructure.pdf.organ_extractor import extract_organs

    matches = extract_organs(text)

    # Filtrar aliases
    matches = [m for m in matches if not _looks_like_alias(m.raw)]

    if not matches:
        return None

    # Devolver el primer órgano detectado (suele ser el más relevante)
    return matches[0]


def _looks_like_alias(raw: str) -> bool:
    """
    Detecta si un órgano parece ser un alias histórico tipo 'JPI 14'.
    """
    if re.match(r'^(antes\s+)?[A-Z]+(?:\s*\d+)?$', raw.strip(), re.IGNORECASE):
        return True
    if len(raw.split()) <= 2 and re.search(r'\d', raw):
        return True
    return False


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

    Usa la estrategia de dividir por 'pasará a desempeñar' para separar
    origen y destino en vez de tomar los dos primeros órganos.
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

    # Dividir por "pasará a desempeñar"
    bloque_origen, bloque_destino = split_origin_destination(parrafo)

    # Extraer mejor órgano de cada bloque
    origen_match = extract_best_organo(bloque_origen)
    destino_match = extract_best_organo(bloque_destino) if bloque_destino else None

    # Extraer provincias explícitas
    provincias = extract_provincias_explicitas(parrafo, organ_matches)

    # Resolver origen
    tribunal_origen = ""
    prov_loc_origen = ""
    if origen_match:
        tribunal_origen = origen_match.organ_type
        if origen_match.seccion:
            tribunal_origen = f"{origen_match.seccion} del {origen_match.organ_type}"

        idx_origen = _find_organ_index(organ_matches, origen_match)
        if idx_origen is not None and idx_origen in provincias:
            prov_loc_origen = transform_service.resolve_localidad(
                provincias[idx_origen], origen_match.raw
            )
        else:
            prov_loc_origen = transform_service.resolve_localidad(
                origen_match.locality, origen_match.raw
            )

    # Resolver destino
    tribunal_destino = ""
    prov_loc_destino = ""
    if destino_match:
        tribunal_destino = destino_match.organ_type
        if destino_match.seccion:
            tribunal_destino = f"{destino_match.seccion} del {destino_match.organ_type}"

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
