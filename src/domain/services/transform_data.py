from src.domain.interfaces.territories_repository import ITerritoriesRepository

class TransformDataService:
    def __init__(self, territories_repo: ITerritoriesRepository):
        self.territories_repo = territories_repo

    def resolve_localidad(self, localidad_texto: str, texto_tribunal_completo: str) -> str:
        """
        Dado un nombre de localidad extraído del tribunal, devuelve una cadena
        formateada como 'Localidad (Provincia)' o 'Provincia (CCAA)' según corresponda.
        """
        if not localidad_texto:
            # Sin localidad separada, intentar extraer del texto completo del tribunal
            prov, ccaa = self.territories_repo.get_provincia_and_ccaa(texto_tribunal_completo)
            if prov and ccaa:
                return f"{prov} ({ccaa})"
            return prov or ccaa or ""

        prov, ccaa = self.territories_repo.get_provincia_and_ccaa(localidad_texto)

        # Si el repositorio devuelve la provincia (=localidad es municipio)
        if prov and prov != localidad_texto:
            return f"{localidad_texto} ({prov})"
        # Si la localidad ES la provincia, mostrar la CCAA
        if prov and ccaa:
            return f"{localidad_texto} ({ccaa})"
        # Si solo devolvió CCAA (la localidad era una CCAA misma, como "Cataluña")
        if ccaa and not prov:
            return localidad_texto
        # Fallback
        return localidad_texto
