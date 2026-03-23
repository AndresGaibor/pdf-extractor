import pymupdf4llm
import re
import tempfile
import os
from typing import List
from src.domain.models.extracted_data import ExtractedRow
from src.domain.interfaces.extraction_interfaces import IPDFExtractor
from src.domain.services.transform_data import TransformDataService
from src.domain.constants import NUMERACION

class PyMuPDFExtractor(IPDFExtractor):
    def __init__(self, transform_service: TransformDataService):
        self.transform_service = transform_service

    def extract_from_path(self, file_path: str) -> List[ExtractedRow]:
        md_text = pymupdf4llm.to_markdown(file_path)
        return self._extraer_datos(md_text)

    def extract_from_bytes(self, file_bytes: bytes) -> List[ExtractedRow]:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            md_text = pymupdf4llm.to_markdown(tmp_path)
            return self._extraer_datos(md_text)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _limpiar_cabeceras_boe(self, texto: str) -> str:
        texto = re.sub(
            r'#+\s*\*{0,2}\s*BOLETÍN\s+OFICIAL\s+DEL\s+ESTADO\s*\*{0,2}\s*'
            r'.*?Pág\.\s*\d+\s*\*{0,2}',
            ' ', texto, flags=re.DOTALL
        )
        texto = re.sub(
            r'#+\s*\*{0,2}\s*BOLETÍN\s+OFICIAL\s+DEL\s+ESTADO\s*\*{0,2}',
            ' ', texto
        )
        texto = re.sub(
            r'\*{0,2}\s*https?://www\.boe\.es\s*\*{0,2}.*?ISSN[:\s]*[\d\-X]+\s*\*{0,2}',
            ' ', texto, flags=re.DOTALL
        )
        texto = re.sub(r'\n\s*\n\s*\n+', '\n\n', texto)
        return texto

    def _extraer_datos(self, md_text: str) -> List[ExtractedRow]:
        md_text = self._limpiar_cabeceras_boe(md_text)
        parrafos = [p.strip() for p in md_text.split('\n\n') if p.strip()]

        parrafos_filtrados = []
        for parrafo in parrafos:
            if parrafo.startswith(tuple(NUMERACION)):
                parrafos_filtrados.append(parrafo)
            elif parrafos_filtrados:
                parrafos_filtrados[-1] += ' ' + parrafo

        filas = []
        for parrafo in parrafos_filtrados:
            try:
                row = self._extraer_fila(parrafo)
                if row:
                    filas.append(row)
            except Exception:
                continue
        return filas

    def _extraer_fila(self, parrafo: str) -> ExtractedRow:
        participante = self._obtener_participante(parrafo)
        if not participante or len(participante.split()) < 2:
            return None

        cargo = self._extraer_cargo(parrafo)
        tribunales = self._extraer_organos_judiciales(parrafo)

        tribunal_origen = ""
        tribunal_destino = ""
        prov_loc_origen = ""
        prov_loc_destino = ""

        if tribunales:
            provincias_explicitas = self._extraer_provincias_explicitas(parrafo, tribunales)

            tipo_orig, localidad_orig = self._separar_tipo_y_localidad(tribunales[0])
            tribunal_origen = tipo_orig

            if 0 in provincias_explicitas:
                prov_loc_origen = self.transform_service.resolve_localidad(provincias_explicitas[0], tribunales[0])
            else:
                prov_loc_origen = self.transform_service.resolve_localidad(localidad_orig, tribunales[0])

            if len(tribunales) > 1:
                tipo_dest, localidad_dest = self._separar_tipo_y_localidad(tribunales[1])
                tribunal_destino = tipo_dest

                if 1 in provincias_explicitas:
                    prov_loc_destino = self.transform_service.resolve_localidad(provincias_explicitas[1], tribunales[1])
                else:
                    prov_loc_destino = self.transform_service.resolve_localidad(localidad_dest, tribunales[1])

        return ExtractedRow(
            participante=participante.replace("Doña ", "").replace("Don ", ""),
            cargo=cargo,
            tribunal_origen=tribunal_origen,
            tribunal_destino=tribunal_destino,
            prov_loc_origen=prov_loc_origen,
            prov_loc_destino=prov_loc_destino
        )

    def _obtener_participante(self, parrafo: str) -> str:
        partes = parrafo.split('.')
        if len(partes) < 2:
            return ""
        parte_despues_punto = partes[1]
        nombre = parte_despues_punto.split(',')[0].strip()
        return nombre

    def _extraer_cargo(self, texto: str) -> str:
        partes_punto = texto.split('.', 1)
        if len(partes_punto) < 2:
            return ""
        parte = partes_punto[1]
        partes_coma = parte.split(',')
        if len(partes_coma) < 2:
            return ""
        cargo_bruto = partes_coma[1].strip()
        for separador in [' del ', ' de ', ' que sirve ']:
            if separador in cargo_bruto:
                cargo_bruto = cargo_bruto.split(separador)[0]
        return cargo_bruto.strip()

    def _extraer_organos_judiciales(self, texto: str) -> List[str]:
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.replace('\u2018', "'").replace('\u2019', "'")
        
        LUGAR = r"[A-ZÁÉÍÓÚÜÑL'][\wáéíóúüñÁÉÍÓÚÜÑ\s\-']+"
        FIN = r'(?=\s*[,.:;()]|\s+(?:pasará|había|tramit|resolv|remit|interpon|admit|dictad|también|previamente|finalmente|y\s+(?:al|el|la|los|las|del|de)|que\s+sirve|de\s+(?:familia|adscripción))|\s*$)'
        
        patron = re.compile(rf'''
            (?:
                Tribunal\s+Supremo(?:\s+\([^)]+\))?
                |Tribunal\s+Constitucional
                |Audiencia\s+Nacional(?:\s+de\s+[\w\s]+)?
                |Tribunal\s+Superior\s+de\s+Justicia\s+de\s+({LUGAR}{FIN})
                |Audiencia\s+Provincial\s+de\s+({LUGAR}{FIN})
                |Tribunal\s+(?:Central\s+)?de\s+Instancia(?:\s+(?:de\s+)?{LUGAR})?{FIN}
                |Oficina\s+de\s+Justicia\s+de\s+({LUGAR}{FIN})
                |Juzgado(?:s)?\s+Central(?:es)?\s+de\s+(?:Instrucción|lo\s+Penal|Menores|Vigilancia\s+Penitenciaria|lo\s+Contencioso-Administrativo)(?:\s+nº?\s*\d+)?
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
                |Juzgado\s+de\s+[\w\s]+?\s+de\s+({LUGAR}{FIN})
            )
        ''', re.VERBOSE | re.IGNORECASE)
        
        organos = []
        vistos = set()
        for match in patron.finditer(texto):
            organo = match.group(0).strip()
            organo = re.sub(r'[;:,.\s]+$', '', organo)
            organo = re.sub(r'\s+', ' ', organo)
            if organo not in vistos:
                organos.append(organo)
                vistos.add(organo)
        return organos

    def _separar_tipo_y_localidad(self, tribunal: str) -> tuple:
        if not tribunal:
            return ("", "")
        
        if re.match(r'Tribunal\s+Supremo', tribunal, re.IGNORECASE):
            return (tribunal, "")
        if re.match(r'Tribunal\s+Constitucional', tribunal, re.IGNORECASE):
            return (tribunal, "")
        if re.match(r'Audiencia\s+Nacional', tribunal, re.IGNORECASE):
            return (tribunal, "")
        if re.match(r'Juzgado(?:s)?\s+Central', tribunal, re.IGNORECASE):
            return (tribunal, "")
        
        m = re.match(r'(Tribunal\s+Superior\s+de\s+Justicia)\s+de\s+(.+)', tribunal, re.IGNORECASE)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        
        m = re.match(r'(Audiencia\s+Provincial)\s+de\s+(.+)', tribunal, re.IGNORECASE)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        
        m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)\s+(?:de\s+)?(.+)', tribunal, re.IGNORECASE)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        m = re.match(r'(Tribunal\s+(?:Central\s+)?de\s+Instancia)$', tribunal, re.IGNORECASE)
        if m:
            return (m.group(1).strip(), "")
        
        m = re.match(r'(Oficina\s+de\s+Justicia)\s+de\s+(.+)', tribunal, re.IGNORECASE)
        if m:
            return (m.group(1).strip(), m.group(2).strip())
        
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
        
        m = re.match(r'(Juzgado\s+.+?)\s+de\s+([A-ZÁÉÍÓÚÜÑL\'][^\n]+)$', tribunal, re.IGNORECASE)
        if m:
            posible_lugar = m.group(2).strip()
            if posible_lugar and posible_lugar[0].isupper():
                return (m.group(1).strip(), posible_lugar)
        
        return (tribunal, "")

    def _extraer_provincias_explicitas(self, texto: str, tribunales: List[str]) -> dict:
        if not tribunales or not texto:
            return {}
        
        texto_normalizado = re.sub(r'\s+', ' ', texto)
        patron_provincia = re.compile(
            r',\s*provincia\s+de\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s\-]+)',
            re.IGNORECASE
        )
        
        resultado = {}
        for match_prov in patron_provincia.finditer(texto_normalizado):
            provincia = match_prov.group(1).strip()
            provincia = re.sub(r'[.,;:\s]+$', '', provincia)
            pos_provincia = match_prov.start()
            
            tribunal_mas_cercano = -1
            menor_distancia = float('inf')
            
            for i, tribunal in enumerate(tribunales):
                pos_tribunal = texto_normalizado.find(tribunal)
                if pos_tribunal == -1:
                    continue
                distancia = pos_provincia - (pos_tribunal + len(tribunal))
                if 0 <= distancia < menor_distancia:
                    menor_distancia = distancia
                    tribunal_mas_cercano = i
            
            if tribunal_mas_cercano >= 0:
                resultado[tribunal_mas_cercano] = provincia
        
        return resultado
