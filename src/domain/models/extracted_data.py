from dataclasses import dataclass, asdict

@dataclass
class ExtractedRow:
    participante: str
    cargo: str
    tribunal_origen: str
    tribunal_destino: str
    prov_loc_origen: str
    prov_loc_destino: str

    def to_dict(self):
        return {
            "Participante": self.participante,
            "Tipo de funcionaria": self.cargo,
            "Tipo de tribunal de origen": self.tribunal_origen,
            "Tipo de tribunal de destino": self.tribunal_destino,
            "Provincia/Localidad de origen": self.prov_loc_origen,
            "Provincia/Localidad de destino": self.prov_loc_destino,
        }
