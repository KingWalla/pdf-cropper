# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
    bottom_mm: float = Form(29.0),
    top_mm: float = Form(0.0),
    left_mm: float = Form(0.0),
    right_mm: float = Form(0.0),
):
    try:
        pdf_bytes = await file.read()

        # ✅ 여기만으로 충분히 검증됨
        if not pdf_bytes.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Expected a PDF file (signature)")

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
            headers={"Content-Disposition": 'attachment; filename="cropped.pdf"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
