# app.py
from __future__ import annotations

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject


MM_TO_PT = 72.0 / 25.4  # 1 inch = 25.4mm, 1 pt = 1/72 inch


def mm_to_pt(mm: float) -> float:
    return float(mm) * MM_TO_PT


def crop_pdf(
    reader: PdfReader,
    bottom_mm: float = 0.0,
    top_mm: float = 0.0,
    left_mm: float = 0.0,
    right_mm: float = 0.0,
) -> PdfWriter:
    """
    각 페이지의 CropBox/MediaBox를 (mm 단위)로 잘라냅니다.
    - bottom_mm: 아래에서 잘라낼 길이
    - top_mm: 위에서 잘라낼 길이
    - left_mm: 왼쪽에서 잘라낼 길이
    - right_mm: 오른쪽에서 잘라낼 길이
    """
    if any(v < 0 for v in (bottom_mm, top_mm, left_mm, right_mm)):
        raise ValueError("Crop values must be >= 0")

    b = mm_to_pt(bottom_mm)
    t = mm_to_pt(top_mm)
    l = mm_to_pt(left_mm)
    r = mm_to_pt(right_mm)

    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        # pypdf에서 page.mediabox/cropbox는 RectangleObject처럼 동작
        media = page.mediabox

        # 원본 MediaBox 좌표 (pt)
        x0 = float(media.left)
        y0 = float(media.bottom)
        x1 = float(media.right)
        y1 = float(media.top)

        new_x0 = x0 + l
        new_y0 = y0 + b
        new_x1 = x1 - r
        new_y1 = y1 - t

        if new_x1 <= new_x0 or new_y1 <= new_y0:
            raise ValueError(
                f"Invalid crop on page {i+1}: result size <= 0 "
                f"(page size: {(x1-x0):.2f}x{(y1-y0):.2f} pt, "
                f"crop: L{l:.2f} R{r:.2f} T{t:.2f} B{b:.2f} pt)"
            )

        rect = RectangleObject([new_x0, new_y0, new_x1, new_y1])

        # MediaBox는 그대로 두고 CropBox만 변경하는 방식이 일반적으로 안전함
        page.cropbox = rect

        # 일부 뷰어/툴이 TrimBox/BleedBox 등을 참고하는 경우가 있어 같이 맞춰주면 좋음
        try:
            page.trimbox = rect
            page.bleedbox = rect
            page.artbox = rect
        except Exception:
            pass

        writer.add_page(page)

    return writer
