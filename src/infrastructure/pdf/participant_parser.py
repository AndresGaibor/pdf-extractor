"""
Parser de participantes con regex anclada al inicio del párrafo.

Reemplaza el enfoque split('.') por una regex que modela la gramática
real de la numeración BOE:
    (Numeración). (Don/Doña) Nombre Apellido,
"""

import re

# Regex para extraer el nombre del participante.
# Captura: numeración + tratamiento opcional + nombre completo + coma de cierre
PARTICIPANT_RE = re.compile(
    r'^'
    # Numeración textual: "Uno", "Veintitres", "Ciento cinco", etc.
    r'(?:Uno|Dos|Tres|Cuatro|Cinco|Seis|Siete|Ocho|Nueve|Diez|'
    r'Once|Doce|Trece|Catorce|Quince|Dieciseis|Diecisiete|Dieciocho|'
    r'Diecinueve|Veinte|Veintiuno|Veintidos|Veintitres|Veinticuatro|'
    r'Veinticinco|Veintiseis|Veintisiete|Veintiocho|Veintinueve|'
    r'Treinta(?:\s+y\s+\w+)?|'
    r'Cuarenta(?:\s+y\s+\w+)?|'
    r'Cincuenta(?:\s+y\s+\w+)?|'
    r'Sesenta|Setenta|Ochenta|Noventa|'
    r'Ciento(?:\s+\w+)?|'
    r'(?:Dos|Tres|Cuatro|Quin|Seis|Set|Och|Nove)cientos(?:\s+\w+)?|'
    r'Mil)'
    r'\.\s+'
    # Tratamiento opcional: Don, Doña, D., Dña.
    r'(?:D[ao]n[a]?\.\s+)?'
    # Nombre: empieza con mayúscula, contiene letras, espacios, guiones, apóstrofes
    r'([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ\-\']+)'
    # Seguido de coma o " del " o " de " que cierra el nombre
    r'(?=\s*[,]|(?:\s+del\s|\s+de\s|\s+que\s))',
    re.IGNORECASE,
)


def extract_participant(parrafo: str) -> str:
    """
    Extrae el nombre del participante usando regex anclada.

    Soporta:
    - "Uno. Doña María García López, Jueza del..."
    - "Dos. Don Carlos Rodríguez Martínez, Letrado..."
    - "Tres. Ana Belén Ortiz Roca, jueza..."
    - "Veintiuno. María del Carmen Pérez, magistrada..."

    Devuelve "" si no encuentra participante válido.
    """
    if not parrafo:
        return ""

    match = PARTICIPANT_RE.match(parrafo.strip())
    if match:
        nombre = match.group(1).strip()
        # Validar que parece un nombre real (al menos 2 palabras o "del/de" en medio)
        if _looks_like_name(nombre):
            return nombre

    # Fallback: intentar split('.') como antes
    return _extract_fallback(parrafo)


def _looks_like_name(text: str) -> bool:
    """Verifica que el texto parece un nombre de persona."""
    if not text:
        return False
    palabras = text.split()
    if len(palabras) < 2:
        return False
    # Al menos la primera palabra debe empezar con mayúscula
    if not palabras[0][0].isupper():
        return False
    return True


def _extract_fallback(parrafo: str) -> str:
    """
    Fallback con split('.') para párrafos que no matchean la regex principal.
    """
    partes = parrafo.split('.')
    if len(partes) < 2:
        return ""

    parte_despues_punto = partes[1]
    # Quitar tratamiento si existe
    parte_despues_punto = re.sub(r'^(?:Don|Doña)\s+', '', parte_despues_punto)
    nombre = parte_despues_punto.split(',')[0].strip()

    if _looks_like_name(nombre):
        return nombre

    return ""
