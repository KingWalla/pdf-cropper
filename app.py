# app.py
from pypdf import PdfReader, PdfWriter

def mm_to_pt(mm: float) -> float:
    """Convert millimeters to PDF points."""
    return mm * 72 / 25.4


def _page_bounds_pt(page):
    mb = page.mediabox
    return float(mb.left), float(mb.bottom), float(mb.right), float(mb.top)


def _ensure_min_area(left, bottom, right, top, min_w_pt, min_h_pt):
    if (right - left) <= min_w_pt or (top - bottom) <= min_h_pt:
        raise ValueError("Crop too large: remaining area below minimum size.")


def crop_bottom(page, cut_mm: float, *, min_w_mm=0, min_h_mm=0):
    cut_pt = mm_to_pt(cut_mm)
    min_w_pt = mm_to_pt(min_w_mm)
    min_h_pt = mm_to_pt(min_h_mm)

    left, bottom, right, top = _page_bounds_pt(page)
    new_bottom = bottom + cut_pt

    _ensure_min_area(left, new_bottom, right, top, min_w_pt, min_h_pt)

    page.cropbox.lower_left = (left, new_bottom)
    page.cropbox.upper_right = (right, top)
    return page


def crop_top(page, cut_mm: float, *, min_w_mm=0, min_h_mm=0):
    cut_pt = mm_to_pt(cut_mm)
    min_w_pt = mm_to_pt(min_w_mm)
    min_h_pt = mm_to_pt(min_h_mm)

    left, bottom, right, top = _page_bounds_pt(page)
    new_top = top - cut_pt

    _ensure_min_area(left, bottom, right, new_top, min_w_pt, min_h_pt)

    page.cropbox.lower_left = (left, bottom)
    page.cropbox.upper_right = (right, new_top)
    return page


def crop_left(page, cut_mm: float, *, min_w_mm=0, min_h_mm=0):
    cut_pt = mm_to_pt(cut_mm)
    min_w_pt = mm_to_pt(min_w_mm)
    min_h_pt = mm_to_pt(min_h_mm)

    left, bottom, right, top = _page_bounds_pt(page)
    new_left = left + cut_pt

    _ensure_min_area(new_left, bottom, right, top, min_w_pt, min_h_pt)

    page.cropbox.lower_left = (new_left, bottom)
    page.cropbox.upper_right = (right, top)
    return page


def crop_right(page, cut_mm: float, *, min_w_mm=0, min_h_mm=0):
    cut_pt = mm_to_pt(cut_mm)
    min_w_pt = mm_to_pt(min_w_mm)
    min_h_pt = mm_to_pt(min_h_mm)

    left, bottom, right, top = _page_bounds_pt(page)
    new_right = right - cut_pt

    _ensure_min_area(left, bottom, new_right, top, min_w_pt, min_h_pt)

    page.cropbox.lower_left = (left, bottom)
    page.cropbox.upper_right = (new_right, top)
    return page


def crop_margins(
    page,
    *,
    left_mm=0,
    right_mm=0,
    top_mm=0,
    bottom_mm=0,
    min_w_mm=20,
    min_h_mm=20,
):
    if bottom_mm:
        crop_bottom(page, bottom_mm, min_w_mm=min_w_mm, min_h_mm=min_h_mm)
    if top_mm:
        crop_top(page, top_mm, min_w_mm=min_w_mm, min_h_mm=min_h_mm)
    if left_mm:
        crop_left(page, left_mm, min_w_mm=min_w_mm, min_h_mm=min_h_mm)
    if right_mm:
        crop_right(page, right_mm, min_w_mm=min_w_mm, min_h_mm=min_h_mm)
    return page


def crop_pdf(reader: PdfReader, **kwargs) -> PdfWriter:
    writer = PdfWriter()
    for page in reader.pages:
        crop_margins(page, **kwargs)
        writer.add_page(page)
    return writer
