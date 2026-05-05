from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.exceptions import AppException
from app.services.sucamec_estados import cancel_job, create_job, get_job, get_result_file, get_result_files, save_input_excel


router = APIRouter(prefix="/api/sucamec", tags=["sucamec"])


@router.post("/estados-carne/upload")
def upload_estados_carne_input(file: UploadFile = File(...)):
    try:
        upload = save_input_excel(file.file, file.filename or "")
    except ValueError as error:
        raise AppException(400, str(error))
    except Exception as error:
        raise AppException(500, f"No se pudo guardar el archivo: {error}")
    finally:
        file.file.close()

    return {"ok": True, "message": "Archivo cargado correctamente", **upload}


@router.post("/estados-carne/runs")
def start_estados_carne_run(grupo: str = Form("JV"), input_filename: str = Form(...)):
    try:
        job = create_job(grupo, input_filename)
    except ValueError as error:
        raise AppException(400, str(error))
    except Exception as error:
        raise AppException(500, f"No se pudo iniciar el flujo: {error}")

    return {"ok": True, "message": "Flujo iniciado", "job": job}


@router.get("/estados-carne/runs/{job_id}")
def get_estados_carne_run(job_id: str):
    job = get_job(job_id)
    if not job:
        raise AppException(404, "No se encontro la ejecucion solicitada")

    return {"ok": True, "job": job}


@router.post("/estados-carne/runs/{job_id}/cancel")
def cancel_estados_carne_run(job_id: str):
    try:
        job = cancel_job(job_id)
    except ValueError as error:
        raise AppException(404, str(error))
    except Exception as error:
        raise AppException(500, f"No se pudo cancelar la ejecucion: {error}")

    return {"ok": True, "message": "Ejecucion cancelada", "job": job}


@router.get("/estados-carne/runs/{job_id}/download")
def download_estados_carne_result(job_id: str):
    result_files = get_result_files(job_id)
    if not result_files:
        raise AppException(404, "No hay resultado disponible para descargar")

    if len(result_files) == 1:
        path = Path(result_files[0])
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=path.name,
        )

    archive = BytesIO()
    with ZipFile(archive, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for path in result_files:
            zip_file.write(path, arcname=path.name)
    archive.seek(0)

    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="resultados_estados_{job_id}.zip"'},
    )


@router.get("/estados-carne/runs/{job_id}/download/primary")
def download_estados_carne_primary_result(job_id: str):
    result_file = get_result_file(job_id)
    if not result_file:
        raise AppException(404, "No hay resultado principal disponible para descargar")

    path = Path(result_file)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name,
    )
