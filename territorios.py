import os
import json
import urllib.request
import re
import unicodedata
from pathlib import Path

DATA_URL = "https://raw.githubusercontent.com/frontid/ComunidadesProvinciasPoblaciones/master/arbol.json"
DATA_FILE = Path(__file__).parent / "territorios_espana.json"

_PROVINCIAS = {}
_MUNICIPIOS = {}

# Alias comunes para comunidades y provincias que en el texto pueden estar diferentes al JSON oficial.
ALIAS_PROVINCIAS = {
    "islas baleares": "Balears, Illes",
    "baleares": "Balears, Illes",
    "illes balears": "Balears, Illes",
    "las palmas": "Palmas, Las",
    "la coruña": "Coruña, A",
    "a coruña": "Coruña, A",
    "alava": "Araba/Álava",
    "araba": "Araba/Álava",
    "alicante": "Alicante/Alacant",
    "alacant": "Alicante/Alacant",
    "castellon": "Castellón/Castelló",
    "castello": "Castellón/Castelló",
    "valencia": "Valencia/València",
    "vizcaya": "Bizkaia",
    "girona": "Girona",
    "gerona": "Girona",
    "lleida": "Lleida",
    "lerida": "Lleida",
    "ourense": "Ourense",
    "orense": "Ourense",
    "guipuzcoa": "Gipuzkoa"
}

ALIAS_CCAA = {
    "cataluña": "Cataluńa",
    "castilla la mancha": "Castilla - La Mancha",
    "castilla-la mancha": "Castilla - La Mancha",
    "comunidad valenciana": "Comunitat Valenciana",
    "valencia": "Comunitat Valenciana",
    "islas canarias": "Canarias",
    "comunidad de madrid": "Madrid, Comunidad de"
}

PRETTY_NAMES_CCAA = {
    "Madrid, Comunidad de": "Madrid",
    "Balears, Illes": "Islas Baleares",
    "Cataluńa": "Cataluña",
    "Comunitat Valenciana": "Comunidad Valenciana",
    "Navarra, Comunidad Foral de": "Navarra",
    "Asturias, Principado de": "Asturias",
    "Murcia, Región de": "Murcia",
    "Rioja, La": "La Rioja",
    "Castilla - La Mancha": "Castilla-La Mancha"
}

PRETTY_NAMES_PROVINCIA = {
    "Coruña, A": "A Coruña",
    "Balears, Illes": "Islas Baleares",
    "Alicante/Alacant": "Alicante",
    "Castellón/Castelló": "Castellón",
    "Valencia/València": "Valencia",
    "Araba/Álava": "Álava",
    "Bizkaia": "Vizcaya",
    "Gipuzkoa": "Guipúzcoa",
    "Palmas, Las": "Las Palmas"
}

PALABRAS_EXCLUIDAS_MUNICIPIOS = {
    "san", "los", "las", "del", "sur", "norte", "este", "oeste", "val", "paz",
    "real", "sala", "civil", "penal", "social"
}

def _normalizar(texto: str) -> str:
    """Elimina tildes, pasa a minúsculas y elimina espacios extras."""
    if not texto:
        return ""
    # Normalizar apóstrofos tipográficos a rectos
    texto = str(texto).replace('\u2018', "'").replace('\u2019', "'")
    # Eliminar espacios alrededor de apóstrofos (ej. "l' hospitalet" -> "l'hospitalet")
    texto = re.sub(r"\s*'\s*", "'", texto)
    # NFKD descompone caracteres (ej: á -> a + ´)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip()

def cargar_datos():
    global _PROVINCIAS, _MUNICIPIOS
    if _PROVINCIAS and _MUNICIPIOS:
        return
        
    if not DATA_FILE.exists():
        print(f"Descargando base de datos de territorios en {DATA_FILE}...")
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        comunidades = json.load(f)
        
    for ccaa in comunidades:
        ccaa_name = ccaa["label"]
        for prov in ccaa.get("provinces", []):
            prov_name = prov["label"]
            prov_norm = _normalizar(prov_name)
            
            _PROVINCIAS[prov_norm] = (prov_name, ccaa_name)
            
            # Tratar nombre compuesto tipo "Alicante/Alacant" guardando ambas partes
            if '/' in prov_name:
                partes = prov_name.split('/')
                for p in partes:
                    _PROVINCIAS[_normalizar(p)] = (prov_name, ccaa_name)

            for muni in prov.get("towns", []):
                muni_name = muni["label"]
                # Formatear nombres tipo "Prat de Llobregat, El" a "El Prat de Llobregat"
                if ", " in muni_name:
                    partes_muni = muni_name.split(", ")
                    if len(partes_muni) == 2:
                        muni_name_invertido = f"{partes_muni[1]} {partes_muni[0]}"
                        muni_norm_inv = _normalizar(muni_name_invertido)
                        if len(muni_norm_inv) >= 3 and muni_norm_inv not in PALABRAS_EXCLUIDAS_MUNICIPIOS:
                            _MUNICIPIOS[muni_norm_inv] = (prov_name, ccaa_name)
                
                muni_norm = _normalizar(muni_name)
                if len(muni_norm) >= 3 and muni_norm not in PALABRAS_EXCLUIDAS_MUNICIPIOS:
                    _MUNICIPIOS[muni_norm] = (prov_name, ccaa_name)

    # Añadir alias manuales a PROVINCIAS
    valores_provincias = list(_PROVINCIAS.values())
    for alias, oficial in ALIAS_PROVINCIAS.items():
        tupla_correcta = None
        for prov_original, ccaa in valores_provincias:
            if prov_original == oficial:
                tupla_correcta = (prov_original, ccaa)
                break
        
        if tupla_correcta:
            _PROVINCIAS[_normalizar(alias)] = tupla_correcta

def extraer_provincia_y_ccaa(texto: str) -> tuple:
    """
    Dada una cadena de texto (ej. "Juzgado de Madrid"), busca la provincia 
    o el municipio más largo que se encuentre en él y devuelve una tupla 
    (Provincia, Comunidad Autónoma).
    
    Retorna (None, None) si no encuentra coincidencia.
    """
    if not texto:
        return None, None
        
    cargar_datos()
    texto_norm = _normalizar(texto)
    
    # 1. Buscar CCAA directas (ej. Tribunal Superior de Justicia de Cataluña)
    ccaa_ordenadas = sorted(list(set(ccaa for prov, ccaa in _PROVINCIAS.values())), key=len, reverse=True)
    for ccaa_nombre in ccaa_ordenadas:
        ccaa_norm = _normalizar(ccaa_nombre)
        patron = r'\b' + re.escape(ccaa_norm) + r'\b'
        if re.search(patron, texto_norm):
            return _formatear_salida(None, ccaa_nombre)
            
    for alias_ccaa, nombre_oficial in ALIAS_CCAA.items():
        patron = r'\b' + re.escape(_normalizar(alias_ccaa)) + r'\b'
        if re.search(patron, texto_norm):
            return _formatear_salida(None, nombre_oficial)

    # 2. Buscar Provincias primero (más precisas)
    provincias_ordenadas = sorted(_PROVINCIAS.keys(), key=len, reverse=True)
    for prov_norm in provincias_ordenadas:
        if len(prov_norm) <= 2: continue
        
        # Buscar como palabra completa usando límites de palabra \b
        patron = r'\b' + re.escape(prov_norm) + r'\b'
        if re.search(patron, texto_norm):
            return _formatear_salida(*_PROVINCIAS[prov_norm])
            
    # 2. Si no hay provincia, buscar Municipio
    # Ordenar por longitud descendente para coincidencias más específicas primero
    municipios_ordenados = sorted(_MUNICIPIOS.keys(), key=len, reverse=True)
    for muni_norm in municipios_ordenados:
        if len(muni_norm) < 3: continue 
        
        patron = r'\b' + re.escape(muni_norm) + r'\b'
        if re.search(patron, texto_norm):
            return _formatear_salida(*_MUNICIPIOS[muni_norm])

    return None, None

def _formatear_salida(provincia_oficial, ccaa_oficial):
    prov = None
    if provincia_oficial:
        prov = PRETTY_NAMES_PROVINCIA.get(provincia_oficial, provincia_oficial)
        
    ccaa = None
    if ccaa_oficial:
        ccaa = PRETTY_NAMES_CCAA.get(ccaa_oficial, ccaa_oficial)
        
    return prov, ccaa

if __name__ == '__main__':
    # Pruebas manuales
    textos_prueba = [
        "Juzgado de Primera Instancia e Instrucción nº 1 de Las Palmas de Gran Canaria",
        "Tribunal Superior de Justicia de Illes Balears",
        "Juzgado de Móstoles",
        "Juzgado de Paz de Vic",
        "Audiencia Provincial de A Coruña",
        "Juzgado de lo Penal de Alicante"
    ]
    
    for t in textos_prueba:
        print(f"Texto: '{t}' -> Resultado: {extraer_provincia_y_ccaa(t)}")
