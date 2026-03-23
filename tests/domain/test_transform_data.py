from src.domain.services.transform_data import TransformDataService


class FakeTerritoriesRepository:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def get_provincia_and_ccaa(self, text: str):
        self.calls.append(text)
        return self.responses[text]


def test_resolve_localidad_formats_municipality_with_province():
    repo = FakeTerritoriesRepository({"Dos Hermanas": ("Sevilla", "Andalucía")})
    service = TransformDataService(repo)

    result = service.resolve_localidad("Dos Hermanas", "Juzgado de lo Penal de Dos Hermanas")

    assert result == "Dos Hermanas (Sevilla)"
    assert repo.calls == ["Dos Hermanas"]


def test_resolve_localidad_formats_province_with_ccaa():
    repo = FakeTerritoriesRepository({"Sevilla": ("Sevilla", "Andalucía")})
    service = TransformDataService(repo)

    result = service.resolve_localidad("Sevilla", "Audiencia Provincial de Sevilla")

    assert result == "Sevilla (Andalucía)"
    assert repo.calls == ["Sevilla"]


def test_resolve_localidad_falls_back_to_complete_text_when_needed():
    repo = FakeTerritoriesRepository({"Sala de Sevilla": ("Sevilla", "Andalucía")})
    service = TransformDataService(repo)

    result = service.resolve_localidad("", "Sala de Sevilla")

    assert result == "Sevilla (Andalucía)"
    assert repo.calls == ["Sala de Sevilla"]
