import re

def obtener_participante(parrafo):
    texto = parrafo

    # Dividir por el primer punto, tomar la segunda parte, dividir por coma y limpiar
    partes = texto.split('.')
    if len(partes) < 2:
        return ""
    parte_despues_punto = partes[1]  # ' Pepito Perez, fiscal,'
    nombre = parte_despues_punto.split(',')[0].strip()  # 'Pepito Perez'

    return nombre

def extraer_cargo(texto):
    # Dividir por el primer punto y tomar la segunda parte
    partes_punto = texto.split('.', 1)
    if len(partes_punto) < 2:
        return ""
    parte = partes_punto[1]
    
    # Dividir por comas y tomar el segundo elemento (después del nombre)
    partes_coma = parte.split(',')
    if len(partes_coma) < 2:
        return ""
    cargo_bruto = partes_coma[1].strip()
    
    # Si tiene "del" o "de", quedarse solo con lo que está antes
    for separador in [' del ', ' de ', ' que sirve ']:
        if separador in cargo_bruto:
            cargo_bruto = cargo_bruto.split(separador)[0]
    
    return cargo_bruto.strip()

def extraer_organos_judiciales(texto):
    """
    Extrae TODOS los órganos judiciales españoles en orden de aparición.
    Captura: Tribunales, Audiencias, Juzgados (todos los tipos), Oficinas de Justicia.
    """
    # Normalizar espacios pero preservar estructura
    texto = re.sub(r'\s+', ' ', texto)
    
    # Normalizar apóstrofos tipográficos a rectos (ej. L\u2019Hospitalet -> L'Hospitalet)
    texto = texto.replace('\u2018', "'").replace('\u2019', "'")
    
    # Delimitador común: el nombre del lugar se extiende hasta puntuación o palabras clave
    # que indican el fin del nombre del órgano judicial
    LUGAR = r"[A-ZÁÉÍÓÚÜÑL'][\wáéíóúüñÁÉÍÓÚÜÑ\s\-']+"
    # Lookahead para delimitar dónde termina el nombre del lugar
    FIN = r'(?=\s*[,.:;()]|\s+(?:pasará|había|tramit|resolv|remit|interpon|admit|dictad|también|previamente|finalmente|y\s+(?:al|el|la|los|las|del|de)|que\s+sirve|de\s+(?:familia|adscripción))|\s*$)'
    
    # Patrón maestro: de más específico a menos específico para evitar cortes prematuros
    patron = re.compile(rf'''
        (?:
            # 1. Altos Tribunales
            Tribunal\s+Supremo(?:\s+\([^)]+\))?
            |Tribunal\s+Constitucional
            |Audiencia\s+Nacional(?:\s+de\s+[\w\s]+)?
            
            # 2. Órganos Territoriales Mayores (TSJ y AP)
            |Tribunal\s+Superior\s+de\s+Justicia\s+de\s+{LUGAR}{FIN}
            |Audiencia\s+Provincial\s+de\s+{LUGAR}{FIN}
            
            # 3. Reforma 2024/2025 (Tribunales de Instancia y Oficinas de Justicia)
            |Tribunal\s+(?:Central\s+)?de\s+Instancia(?:\s+(?:de\s+)?{LUGAR})?{FIN}
            |Oficina\s+de\s+Justicia\s+de\s+{LUGAR}{FIN}
            
            # 4. Juzgados Centrales
            |Juzgado(?:s)?\s+Central(?:es)?\s+de\s+(?:Instrucción|lo\s+Penal|Menores|Vigilancia\s+Penitenciaria|lo\s+Contencioso-Administrativo)(?:\s+nº?\s*\d+)?
            
            # 5. Juzgados Especializados Ordinarios
            |Juzgado\s+de\s+(?:
                Primera\s+Instancia(?:\s+e\s+Instrucción)?
                |Instrucción
                |lo\s+Mercantil
                |lo\s+Penal
                |lo\s+Social
                |lo\s+Contencioso[\-\s]Administrativo
                |Violencia\s+(?:sobre\s+la\s+Mujer|de\s+Género)
                |Menores
                |Vigilancia\s+Penitenciaria
                |Paz
            )(?:\s+(?:nº|n°|n\.|número|num\.?|Nº|N\.|No\.?)\s*\d+)?(?:\s+de\s+{LUGAR})?{FIN}
            
            # 6. Juzgados de denominación genérica
            |Juzgado\s+de\s+[\w\s]+?\s+de\s+{LUGAR}{FIN}
        )
    ''', re.VERBOSE | re.IGNORECASE)
    
    # Extraer manteniendo orden de aparición (usamos finditer, no findall)
    organos = []
    vistos = set()  # Para evitar duplicados exactos consecutivos, pero mantener orden
    
    for match in patron.finditer(texto):
        organo = match.group(0).strip()
        
        # Limpieza fina: quitar puntuación final suelta pero mantener contenido
        organo = re.sub(r'[;:,.\s]+$', '', organo)
        
        # Normalizar espacios internos
        organo = re.sub(r'\s+', ' ', organo)
        
        # Evitar duplicados exactos (mismo nombre exacto aparece dos veces seguidas o separado)
        if organo not in vistos:
            organos.append(organo)
            vistos.add(organo)
    
    return organos

def separar_tipo_y_localidad(tribunal: str) -> tuple:
    """
    Separa un nombre completo de tribunal en su tipo y su localidad.
    
    Ejemplo:
        "Juzgado de Primera Instancia nº 1 de Madrid" 
            -> ("Juzgado de Primera Instancia nº 1", "Madrid")
        "Tribunal Superior de Justicia de Cataluña"
            -> ("Tribunal Superior de Justicia", "Cataluña")
        "Tribunal Supremo"
            -> ("Tribunal Supremo", "")
    """
    if not tribunal:
        return ("", "")
    
    # Altos tribunales sin localidad
    if re.match(r'Tribunal\s+Supremo', tribunal, re.IGNORECASE):
        return (tribunal, "")
    if re.match(r'Tribunal\s+Constitucional', tribunal, re.IGNORECASE):
        return (tribunal, "")
    if re.match(r'Audiencia\s+Nacional', tribunal, re.IGNORECASE):
        return (tribunal, "")
    # Juzgados Centrales no tienen localidad (son todos de Madrid)
    if re.match(r'Juzgado(?:s)?\s+Central', tribunal, re.IGNORECASE):
        return (tribunal, "")
    
    # TSJ: "Tribunal Superior de Justicia de <LUGAR>"
    m = re.match(r'(Tribunal\s+Superior\s+de\s+Justicia)\s+de\s+(.+)', tribunal, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    
    # Audiencia Provincial: "Audiencia Provincial de <LUGAR>"
    m = re.match(r'(Audiencia\s+Provincial)\s+de\s+(.+)', tribunal, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    
    # Tribunal de Instancia: "Tribunal [Central] de Instancia [de <LUGAR>]"
    m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)\s+(?:de\s+)?(.+)', tribunal, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)$', tribunal, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), "")
    
    # Oficina de Justicia: "Oficina de Justicia de <LUGAR>"
    m = re.match(r'(Oficina\s+de\s+Justicia)\s+de\s+(.+)', tribunal, re.IGNORECASE)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    
    # Juzgados especializados: "Juzgado de <especialización> [nº N] de <LUGAR>"
    # Patrón: capturar todo hasta el último "de <LUGAR>"
    # Especializaciones conocidas para no cortar mal
    especializaciones = (
        r'Primera\s+Instancia(?:\s+e\s+Instrucción)?'
        r'|Instrucción'
        r'|lo\s+Mercantil'
        r'|lo\s+Penal'
        r'|lo\s+Social'
        r'|lo\s+Contencioso[\-\s]Administrativo'
        r'|Violencia\s+(?:sobre\s+la\s+Mujer|de\s+Género)'
        r'|Menores'
        r'|Vigilancia\s+Penitenciaria'
        r'|Paz'
    )
    
    m = re.match(
        rf'(Juzgado\s+de\s+(?:{especializaciones})'
        rf'(?:\s+(?:nº|n°|n\.|número|num\.?|Nº|N\.|No\.?)\s*\d+)?)'
        rf'\s+de\s+(.+)',
        tribunal, re.IGNORECASE
    )
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    
    # Juzgado genérico: "Juzgado de <algo> de <LUGAR>" - buscar el último "de <LUGAR>"
    m = re.match(r'(Juzgado\s+.+?)\s+de\s+([A-ZÁÉÍÓÚÜÑL\'][^\n]+)$', tribunal, re.IGNORECASE)
    if m:
        # Verificar que la última parte parece un lugar (empieza con mayúscula)
        posible_lugar = m.group(2).strip()
        if posible_lugar and posible_lugar[0].isupper():
            return (m.group(1).strip(), posible_lugar)
    
    # Si no se pudo separar, devolver todo como tipo sin localidad
    return (tribunal, "")


def extraer_provincias_explicitas(texto, tribunales):
    """
    Busca el patrón ', provincia de X' en el texto y lo asocia al tribunal
    que lo precede. Devuelve un diccionario {índice_tribunal: provincia_explícita}.
    
    Ejemplo: "Tribunal Superior de Justicia de Cataluña, provincia de Girona"
    -> {0: "Girona"} (si ese es el primer tribunal)
    """
    if not tribunales or not texto:
        return {}
    
    texto_normalizado = re.sub(r'\s+', ' ', texto)
    
    # Buscar todas las ocurrencias de ", provincia de X"
    patron_provincia = re.compile(
        r',\s*provincia\s+de\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s\-]+)',
        re.IGNORECASE
    )
    
    resultado = {}
    
    for match_prov in patron_provincia.finditer(texto_normalizado):
        provincia = match_prov.group(1).strip()
        # Limpiar puntuación final
        provincia = re.sub(r'[.,;:\s]+$', '', provincia)
        pos_provincia = match_prov.start()
        
        # Encontrar qué tribunal precede a esta ", provincia de X"
        tribunal_mas_cercano = -1
        menor_distancia = float('inf')
        
        for i, tribunal in enumerate(tribunales):
            # Buscar la posición del tribunal en el texto
            pos_tribunal = texto_normalizado.find(tribunal)
            if pos_tribunal == -1:
                continue
            
            # La provincia debe estar DESPUÉS del tribunal
            distancia = pos_provincia - (pos_tribunal + len(tribunal))
            if 0 <= distancia < menor_distancia:
                menor_distancia = distancia
                tribunal_mas_cercano = i
        
        if tribunal_mas_cercano >= 0:
            resultado[tribunal_mas_cercano] = provincia
    
    return resultado
