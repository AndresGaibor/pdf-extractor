"""
Modelos para validación de extracción de PDFs reales.
"""

from dataclasses import dataclass, field


@dataclass
class FieldMismatch:
    """Representa un campo que no coincide entre esperado y actual."""
    participante: str
    field: str
    expected: str
    actual: str


@dataclass
class ValidationDiff:
    """Diferencias entre un resultado esperado y el extraído."""
    pdf_name: str
    expected_rows: int
    actual_rows: int
    missing_participants: list[str] = field(default_factory=list)
    extra_participants: list[str] = field(default_factory=list)
    field_mismatches: list[FieldMismatch] = field(default_factory=list)
    matched_participants: int = 0
    total_expected_participants: int = 0

    @property
    def participant_match_rate(self) -> float:
        if self.total_expected_participants == 0:
            return 1.0
        return self.matched_participants / self.total_expected_participants

    @property
    def row_count_difference(self) -> int:
        return abs(self.expected_rows - self.actual_rows)

    @property
    def is_passing(self) -> bool:
        return (
            self.row_count_difference <= 0
            and len(self.field_mismatches) == 0
            and len(self.missing_participants) == 0
        )

    def to_dict(self) -> dict:
        return {
            "pdf": self.pdf_name,
            "expected_rows": self.expected_rows,
            "actual_rows": self.actual_rows,
            "matched_participants": self.matched_participants,
            "total_expected_participants": self.total_expected_participants,
            "participant_match_rate": round(self.participant_match_rate, 3),
            "missing_participants": self.missing_participants,
            "extra_participants": self.extra_participants,
            "field_mismatches": [
                {
                    "participante": m.participante,
                    "field": m.field,
                    "expected": m.expected,
                    "actual": m.actual,
                }
                for m in self.field_mismatches
            ],
            "is_passing": self.is_passing,
        }


@dataclass
class ValidationReport:
    """Reporte completo de una corrida de validación."""
    diffs: list[ValidationDiff] = field(default_factory=list)
    pdfs_processed: int = 0
    pdfs_passed: int = 0
    pdfs_failed: int = 0
    total_errors: list[str] = field(default_factory=list)

    @property
    def overall_pass_rate(self) -> float:
        if self.pdfs_processed == 0:
            return 1.0
        return self.pdfs_passed / self.pdfs_processed

    @property
    def is_passing(self) -> bool:
        return self.pdfs_failed == 0

    def to_dict(self) -> dict:
        return {
            "pdfs_processed": self.pdfs_processed,
            "pdfs_passed": self.pdfs_passed,
            "pdfs_failed": self.pdfs_failed,
            "overall_pass_rate": round(self.overall_pass_rate, 3),
            "errors": self.total_errors,
            "diffs": [d.to_dict() for d in self.diffs],
        }
