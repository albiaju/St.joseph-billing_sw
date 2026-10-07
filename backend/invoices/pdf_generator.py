from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from num2words import num2words


def get_shop_settings():
    from settings_app.models import ShopSettings
    settings = ShopSettings.objects.first()
    if not settings:
        class Default:
            shop_name = "ST. JOSEPH'S HARDWARES"
            address = "New Extension, Madikeri - 571 201"
            mobile = "9902237176"
            gstin = "29ANWPD0218LIZO"
            bank_account_no = "348601010036056"
            bank_ifsc = "UBIN0900079"
            bank_name = "Union Bank of India, Madikeri"
        return Default()
    return settings


def amount_to_words(amount):
    try:
        rupees = int(amount)
        paise = round((float(amount) - rupees) * 100)
        words = num2words(rupees, lang='en_IN').title()
        if paise > 0:
            paise_words = num2words(paise, lang='en_IN').title()
            return f"{words} Rupees And {paise_words} Paise Only"
        return f"{words} Rupees Only"
    except:
        return ""


def generate_invoice_pdf(invoice):
    buf = BytesIO()
    shop = get_shop_settings()
    items = invoice.items.all()

    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4
    margin = 15 * mm
    content_w = W - 2 * margin

    def hline(y, lw=0.5, color=colors.black):
        c.setStrokeColor(color)
        c.setLineWidth(lw)
        c.line(margin, y, W - margin, y)

    # ── OUTER BORDER ──────────────────────────────────────────
    c.setStrokeColor(colors.HexColor("#3459EA"))
    c.setLineWidth(2)
    c.rect(margin, margin, content_w, H - 2 * margin)

    y = H - margin

    # ── TOP ROW: GSTIN / CASH BILL / Mobile ───────────────────
    y -= 8 * mm
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.black)
    c.drawString(margin + 3 * mm, y, f"GSTIN : {shop.gstin}")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#8B0000"))
    c.drawCentredString(W / 2, y, "CASH BILL")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.black)
    c.drawRightString(W - margin - 3 * mm, y, f"Mob : {shop.mobile}")

    # ── SHOP NAME ─────────────────────────────────────────────
    y -= 9 * mm
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#8B0000"))
    c.drawCentredString(W / 2, y, shop.shop_name)

    # ── ADDRESS ───────────────────────────────────────────────
    y -= 6 * mm
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.black)
    c.drawCentredString(W / 2, y, shop.address)

    y -= 4 * mm
    hline(y, lw=1, color=colors.HexColor("#8B0000"))

    # ── BILL NO & DATE ────────────────────────────────────────
    y -= 6 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 3 * mm, y, f"No.   {invoice.bill_number}")
    c.drawRightString(W - margin - 3 * mm, y,
                      f"Date : {invoice.date.strftime('%d/%m/%Y')}")

    # ── CUSTOMER ──────────────────────────────────────────────
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.drawString(margin + 3 * mm, y,
                 f"To : {invoice.customer_name or '___________________________'}")

    y -= 3 * mm
    hline(y)

    # ── TABLE COLUMNS ─────────────────────────────────────────
    col_x   = margin + 2 * mm
    col_par = margin + 16 * mm
    col_qty = W - margin - 68 * mm
    col_rat = W - margin - 48 * mm
    col_rs  = W - margin - 22 * mm
    col_ps  = W - margin - 3 * mm

    # Header
    y -= 5 * mm
    c.setFillColor(colors.HexColor("#f0f0f0"))
    c.rect(margin, y - 1.5 * mm, content_w, 6 * mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(col_x + 5 * mm, y, "Sl.")
    c.drawString(col_par, y, "Particulars")
    c.drawCentredString(col_qty + 8 * mm, y, "Qty")
    c.drawCentredString(col_rat + 8 * mm, y, "Rate")
    c.drawCentredString(col_rs + 8 * mm, y, "Amount")

    y -= 2 * mm
    hline(y)

    # ── ITEM ROWS ─────────────────────────────────────────────
    row_h = 6.5 * mm
    min_rows = 16
    c.setFont("Helvetica", 8.5)

    for i, item in enumerate(items):
        y -= row_h
        if i % 2 == 1:
            c.setFillColor(colors.HexColor("#fafafa"))
            c.rect(margin + 0.5, y - 1 * mm, content_w - 1, row_h, fill=1, stroke=0)
            c.setFillColor(colors.black)
        c.drawCentredString(col_x + 5 * mm, y, str(item.sl_no))
        c.drawString(col_par, y, str(item.particulars))
        qty_str = str(item.quantity).rstrip('0').rstrip('.')
        c.drawRightString(col_qty + 16 * mm, y, qty_str)
        c.drawRightString(col_rat + 16 * mm, y, f"{float(item.rate):,.2f}")
        c.drawRightString(col_rs + 16 * mm, y, f"{float(item.amount):,.2f}")

    # Empty filler rows
    items_count = len(list(items))
    for _ in range(max(0, min_rows - items_count)):
        y -= row_h

    hline(y)

    # ── TOTALS ────────────────────────────────────────────────
    def total_row(label, amount, bold=False, bg=None):
        nonlocal y
        y -= 5.5 * mm
        if bg:
            c.setFillColor(bg)
            c.rect(margin + 0.5, y - 1.5 * mm, content_w - 1, 5.5 * mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 8.5)
        c.drawRightString(col_ps - 30 * mm, y, label)
        c.drawRightString(col_ps, y, f"{float(amount):,.2f}")

    total_row("Subtotal  Rs.", invoice.subtotal)
    hline(y - 1.5 * mm, lw=0.3)
    total_row("SGST 9%   Rs.", invoice.sgst_amount)
    total_row("CGST 9%   Rs.", invoice.cgst_amount)
    hline(y - 1.5 * mm, lw=0.8, color=colors.HexColor("#8B0000"))
    total_row("TOTAL     Rs.", invoice.total_amount, bold=True,
              bg=colors.HexColor("#fff3f3"))

    y -= 3 * mm
    hline(y, lw=1, color=colors.HexColor("#8B0000"))

    # ── AMOUNT IN WORDS ───────────────────────────────────────
    y -= 6 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 3 * mm, y, "Rupees :")
    c.setFont("Helvetica", 8)
    c.drawString(margin + 20 * mm, y, amount_to_words(invoice.total_amount))

    y -= 4 * mm
    hline(y, lw=0.3)

    # ── BANK DETAILS + SIGNATURE ──────────────────────────────
    y -= 6 * mm
    c.setFont("Helvetica", 7.5)
    c.drawString(margin + 3 * mm, y, f"A/c No. : {shop.bank_account_no}")
    c.drawRightString(W - margin - 3 * mm, y, f"For {shop.shop_name}")

    y -= 5 * mm
    c.drawString(margin + 3 * mm, y, f"IFSC    : {shop.bank_ifsc}")

    y -= 5 * mm
    c.drawString(margin + 3 * mm, y, shop.bank_name)

    y -= 10 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - margin - 3 * mm, y, "Authorised Signature")
    c.line(W - margin - 45 * mm, y - 1 * mm, W - margin - 3 * mm, y - 1 * mm)

    # ── DISCLAIMER ────────────────────────────────────────────
    disc_y = margin + 5 * mm
    hline(disc_y + 4 * mm, lw=0.3)
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.grey)
    c.drawCentredString(W / 2, disc_y,
                        "Goods once sold cannot be taken back or exchanged.")

    c.save()
    buf.seek(0)
    return buf