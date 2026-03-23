from abc import ABC, abstractmethod
from typing import Tuple, Optional

class ITerritoriesRepository(ABC):
    @abstractmethod
    def get_provincia_and_ccaa(self, text: str) -> Tuple[Optional[str], Optional[Optional[str]]]:
        """
        Dada una cadena de texto, busca la provincia o el municipio 
        y devuelve una tupla (Provincia, Comunidad Autónoma).
        """
        pass
