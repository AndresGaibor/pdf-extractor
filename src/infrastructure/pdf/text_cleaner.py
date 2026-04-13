"""
Limpieza de cabeceras y ruido de documentos BOE.

Cada función elimina un tipo específico de ruido del documento,
permitiendo depurar y probar cada limpieza de forma aislada.
"""

import re


def clean_boe_headers(text: str) -> str:
    """
    Elimina cabeceras principales del BOE (título + página).

    Maneja variantes con asteriscos, negritas y diferentes formatos.
    """
    # Cabecera completa con número de página
    text = re.sub(
        r'#+\s*\*{0,2}\s*BOLETÍN\s+OFICIAL\s+DEL\s+ESTADO\s*\*{0,2}\s*'
        r'.*?Pág\.\s*\d+\s*\*{0,2}',
        ' ', text, flags=re.DOTALL
    )
    # Cabecera sin número de página
    text = re.sub(
        r'#+\s*\*{0,2}\s*BOLETÍN\s+OFICIAL\s+DEL\s+ESTADO\s*\*{0,2}',
        ' ', text
    )
    return text


def clean_boe_issn(text: str) -> str:
    """
    Elimina líneas con ISSN y URL del BOE.
    """
    text = re.sub(
        r'\*{0,2}\s*https?://www\.boe\.es\s*\*{0,2}.*?ISSN[:\s]*[\d\-X]+\s*\*{0,2}',
        ' ', text, flags=re.DOTALL
    )
    return text


def collapse_blank_lines(text: str) -> str:
    """
    Colapsa múltiples líneas en blanco en un solo salto de línea doble.
    """
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text


def clean_all_boe_noise(text: str) -> str:
    """
    Aplica todas las limpiezas de ruido BOE en un solo paso.
    """
    text = clean_boe_headers(text)
    text = clean_boe_issn(text)
    text = collapse_blank_lines(text)
    return text
