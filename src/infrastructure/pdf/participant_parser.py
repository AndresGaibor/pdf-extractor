"""
Parser de participantes con enfoque por capas, no regex gigante.

Estrategia:
1. Localizar el primer punto del item (fin de la numeración)
2. Tomar el contenido posterior
3. Eliminar tratamiento opcional (Don, Doña, D., Dña.)
4. Tomar el segmento hasta la primera coma
5. Validar que parece nombre real
"""

import re

# Prefijos de tratamiento a eliminar
TREATMENT_PREFIXES = re.compile(
    r'^(?:Don|Doña|D[ño]a?\.?|D\.)\s+',
    re.IGNORECASE
)

# Términos que NO deben aparecer en un nombre válido
FORBIDDEN_IN_NAME = re.compile(
    r'\b(?:juez|jueza|magistrad|tribunal|audiencia|sección|sala|'
    r'juzgado|oficina\s+de\s+justicia|pasará|plaza|provincia|'
    r'servicios\s+especiales|situaci[oó]n\s+administrativa|'
    r'excluir|solicitudes|incidencias|resoluci[oó]n|'
    r'recurso|preferencias|art[ií]culos|Ley Org[aá]nica)\b',
    re.IGNORECASE
)


def extract_participant(parrafo: str) -> str:
    """
    Extrae el nombre del participante usando un enfoque por capas.

    No intenta modelar toda la gramática BOE con una regex.
    En su lugar, aplica pasos secuenciales simples.
    """
    if not parrafo or not parrafo.strip():
        return ""

    texto = parrafo.strip()

    # Paso 1: Localizar primer punto (fin de la numeración)
    idx_punto = _find_first_period(texto)
    if idx_punto < 0:
        return ""

    # Paso 2: Tomar contenido después del punto
    despues_punto = texto[idx_punto + 1:].strip()
    if not despues_punto:
        return ""

    # Paso 3: Eliminar tratamiento opcional
    despues_tratamiento = _strip_treatment(despues_punto)

    # Paso 4: Tomar segmento hasta primera coma
    nombre_candidato = _take_until_comma(despues_tratamiento)

    # Paso 5: Validar
    if _looks_like_name(nombre_candidato):
        return nombre_candidato.strip()

    return ""


def _find_first_period(text: str) -> int:
    """
    Encuentra el índice del primer punto que termina la numeración BOE.

    Busca patrones como "Uno.", "Veintitres.", "Ciento cinco.", etc.
    El punto debe estar precedido por al menos una letra mayúscula
    (inicio de la numeración textual).
    """
    # Patrón: palabra(s) con mayúscula inicial seguida(s) de punto
    match = re.match(r'[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ\s]*?\.', text)
    if match:
        return match.end() - 1  # índice del punto

    return -1


def _strip_treatment(text: str) -> str:
    """Elimina prefijos de tratamiento: Don, Doña, D., Dña."""
    result = TREATMENT_PREFIXES.sub('', text)
    return result.strip()


def _take_until_comma(text: str) -> str:
    """
    Toma el contenido hasta la primera coma que cierra el nombre.

    Maneja casos como "María del Carmen Pérez," donde "del" es parte
    del nombre, no un separador de cargo.
    """
    # La coma que cierra el nombre suele ir tras el apellido completo
    idx = text.find(',')
    if idx > 0:
        return text[:idx].strip()

    # Si no hay coma, intentar hasta " del " o " de " (podría ser nombre compuesto)
    # pero solo si parece un nombre corto
    for sep in [' del ', ' de la ', ' de ']:
        idx = text.find(sep)
        if idx > 0:
            # Verificar si hay una coma después del "del/de" (que sí cierra el nombre)
            comma_after_sep = text.find(',', idx + len(sep))
            if comma_after_sep > 0:
                # Hay una coma después, usar esa
                return text[:comma_after_sep].strip()

            # Tomar hasta el separador, pero verificar que el resultado
            # tiene al menos 2 palabras (nombre + apellido)
            candidate = text[:idx].strip()
            if len(candidate.split()) >= 2:
                return candidate

    # Fallback: tomar todo hasta encontrar un verbo o término de órgano
    # Cortar en el primer "pasará", "que sirve", "plaza"
    for term in [' pasará', ' que sirve', ' plaza', ' especialista']:
        idx = text.lower().find(term)
        if idx > 0:
            candidate = text[:idx].strip()
            if len(candidate.split()) >= 2:
                return candidate

    return text.strip()


def _looks_like_name(text: str) -> bool:
    """
    Valida que el texto parece un nombre real de persona.

    Reglas:
    - Mínimo 2 palabras
    - La primera palabra empieza con mayúscula
    - No contiene términos típicos de cargo u órgano
    - No es demasiado largo (máx ~8 palabras)
    - No contiene puntos internos (los nombres no tienen ".")
    """
    if not text:
        return False

    palabras = text.split()

    if len(palabras) < 2:
        return False

    if len(palabras) > 8:
        return False

    # Primera palabra debe empezar con mayúscula
    if not palabras[0][0].isupper():
        return False

    # Un nombre real no contiene puntos internos
    if '.' in text:
        return False

    # No debe contener términos prohibidos
    if FORBIDDEN_IN_NAME.search(text):
        return False

    return True
