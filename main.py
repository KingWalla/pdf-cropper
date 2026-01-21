# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pypdf import PdfReader
import io

from app import crop_pdf

app = FastAPI(title="PDF Cropper")

@app.get("/health")
def health():
    return {"ok": True}


@app.post("/crop")
async def crop_api(
    file: UploadFile = File(...),
    bottom_mm: float = 29,
    top_mm: float = 0,
    left_mm: float = 0,
    right_mm: float = 0,
):
    if file.content_type not in (None, "", "application/pdf"):
        raise HTTPException(status_code=400, detail="Expected a PDF file")

    try:
        pdf_bytes = await file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))

        writer = crop_pdf(
            reader,
            bottom_mm=bottom_mm,
            top_mm=top_mm,
            left_mm=left_mm,
            right_mm=right_mm,
        )

        out = io.BytesIO()
        writer.write(out)
        out.seek(0)

        return StreamingResponse(
            out,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=cropped.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
