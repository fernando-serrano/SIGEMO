from pathlib import Path

from openpyxl import Workbook

from app.services import sucamec_estados

TMP_DIR = Path(__file__).resolve().parent / ".tmp"


def _write_workbook(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    workbook.close()


def test_validate_input_excel_accepts_expected_columns():
    path = TMP_DIR / "entrada_valida.xlsx"
    _write_workbook(path, ["NRO DOCUMENTO", "NOMBRE"], [["00123456", "Persona Uno"], ["87654321", "Persona Dos"]])

    result = sucamec_estados._validate_input_excel(path)

    assert result["validation"]["is_valid"] is True
    assert result["validation"]["total_records"] == 2
    assert result["validation"]["document_column"] == "NRO DOCUMENTO"
    assert result["preview"][0]["nro_documento"] == "00123456"


def test_validate_input_excel_rejects_unexpected_columns():
    path = TMP_DIR / "entrada_columnas_invalidas.xlsx"
    _write_workbook(path, ["NRO DOCUMENTO", "APELLIDOS"], [["00123456", "Persona Uno"]])

    try:
        sucamec_estados._validate_input_excel(path)
    except ValueError as error:
        assert "Columnas no permitidas" in str(error)
    else:
        raise AssertionError("Expected ValueError for unexpected columns")


def test_cell_to_text_preserving_zeros_uses_excel_number_format():
    path = TMP_DIR / "entrada_ceros.xlsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["NRO DOCUMENTO"])
    sheet.append([123])
    sheet["A2"].number_format = "00000000"
    workbook.save(path)
    workbook.close()

    result = sucamec_estados._validate_input_excel(path)

    assert result["preview"][0]["nro_documento"] == "00000123"


def test_max_concurrent_jobs_defaults_to_one(monkeypatch):
    monkeypatch.delenv("ESTADOS_GADSO_MAX_CONCURRENT_JOBS", raising=False)

    assert sucamec_estados._max_concurrent_jobs() == 1


def test_job_timeout_has_safe_default(monkeypatch):
    monkeypatch.delenv("ESTADOS_GADSO_JOB_TIMEOUT_MINUTES", raising=False)

    assert sucamec_estados._job_timeout_seconds() == 120 * 60
