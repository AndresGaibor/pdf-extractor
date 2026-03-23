import json
import urllib.request
import re
import unicodedata
from pathlib import Path
from typing import Tuple, Optional
from src.domain.interfaces.territories_repository import ITerritoriesRepository

DATA_URL = "https://raw.githubusercontent.com/frontid/ComunidadesProvinciasPoblaciones/master/arbol.json"
DATA_FILE = Path(__file__).parent.parent.parent / "territorios_espana.json"

class TerritoriesRepositoryJSON(ITerritoriesRepository):
    # Alias comunes para comunidades y provincias
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

    def __init__(self):
        self._provincias = {}
        self._municipios = {}
        self._cargar_datos()

    def _normalizar(self, texto: str) -> str:
        if not texto:
            return ""
        texto = str(texto).replace('\u2018', "'").replace('\u2019', "'")
        texto = re.sub(r"\s*'\s*", "'", texto)
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
        return texto.lower().strip()

    def _cargar_datos(self):
        if not DATA_FILE.exists():
            print(f"Descargando base de datos de territorios en {DATA_FILE}...")
            urllib.request.urlretrieve(DATA_URL, DATA_FILE)
            
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            comunidades = json.load(f)
            
        for ccaa in comunidades:
            ccaa_name = ccaa["label"]
            for prov in ccaa.get("provinces", []):
                prov_name = prov["label"]
                prov_norm = self._normalizar(prov_name)
                
                self._provincias[prov_norm] = (prov_name, ccaa_name)
                
                if '/' in prov_name:
                    partes = prov_name.split('/')
                    for p in partes:
                        self._provincias[self._normalizar(p)] = (prov_name, ccaa_name)

                for muni in prov.get("towns", []):
                    muni_name = muni["label"]
                    if ", " in muni_name:
                        partes_muni = muni_name.split(", ")
                        if len(partes_muni) == 2:
                            muni_name_invertido = f"{partes_muni[1]} {partes_muni[0]}"
                            muni_norm_inv = self._normalizar(muni_name_invertido)
                            if len(muni_norm_inv) >= 3 and muni_norm_inv not in self.PALABRAS_EXCLUIDAS_MUNICIPIOS:
                                self._municipios[muni_norm_inv] = (prov_name, ccaa_name)
                    
                    muni_norm = self._normalizar(muni_name)
                    if len(muni_norm) >= 3 and muni_norm not in self.PALABRAS_EXCLUIDAS_MUNICIPIOS:
                        self._municipios[muni_norm] = (prov_name, ccaa_name)

        # Añadir alias manuales a PROVINCIAS
        valores_provincias = list(self._provincias.values())
        for alias, oficial in self.ALIAS_PROVINCIAS.items():
            tupla_correcta = None
            for prov_original, ccaa in valores_provincias:
                if prov_original == oficial:
                    tupla_correcta = (prov_original, ccaa)
                    break
            
            if tupla_correcta:
                self._provincias[self._normalizar(alias)] = tupla_correcta

    def get_provincia_and_ccaa(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        if not text:
            return None, None
            
        texto_norm = self._normalizar(text)
        
        # 1. Buscar CCAA directas
        ccaa_ordenadas = sorted(list(set(ccaa for prov, ccaa in self._provincias.values())), key=len, reverse=True)
        for ccaa_nombre in ccaa_ordenadas:
            ccaa_norm = self._normalizar(ccaa_nombre)
            patron = r'\b' + re.escape(ccaa_norm) + r'\b'
            if re.search(patron, texto_norm):
                return self._formatear_salida(None, ccaa_nombre)
                
        for alias_ccaa, nombre_oficial in self.ALIAS_CCAA.items():
            patron = r'\b' + re.escape(self._normalizar(alias_ccaa)) + r'\b'
            if re.search(patron, texto_norm):
                return self._formatear_salida(None, nombre_oficial)

        # 2. Buscar Provincias
        provincias_ordenadas = sorted(self._provincias.keys(), key=len, reverse=True)
        for prov_norm in provincias_ordenadas:
            if len(prov_norm) <= 2:
                continue
            patron = r'\b' + re.escape(prov_norm) + r'\b'
            if re.search(patron, texto_norm):
                return self._formatear_salida(*self._provincias[prov_norm])
                
        # 3. Buscar Municipios
        municipios_ordenados = sorted(self._municipios.keys(), key=len, reverse=True)
        for muni_norm in municipios_ordenados:
            if len(muni_norm) < 3:
                continue
            patron = r'\b' + re.escape(muni_norm) + r'\b'
            if re.search(patron, texto_norm):
                return self._formatear_salida(*self._municipios[muni_norm])

        return None, None

    def _formatear_salida(self, provincia_oficial, ccaa_oficial):
        prov = None
        if provincia_oficial:
            prov = self.PRETTY_NAMES_PROVINCIA.get(provincia_oficial, provincia_oficial)
            
        ccaa = None
        if ccaa_oficial:
            ccaa = self.PRETTY_NAMES_CCAA.get(ccaa_oficial, ccaa_oficial)
            
        return prov, ccaa
