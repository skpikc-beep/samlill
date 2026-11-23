#!/usr/bin/env python3
"""
Kitchen Shop Drawings & Execution Boards — Rev P1
Builds a 10-page A3 landscape PDF for the open-plan kitchen & dining project.
All dimensions in millimetres, indicative from the Enscape visualisation
(2026-11-15) — to be verified on site before fabrication.
"""
import os, io, random, math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image
from reportlab.lib.utils import ImageReader

PAGE_W, PAGE_H = 420*mm, 297*mm
FRAME = 7*mm
TITLE_H = 19*mm
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Kitchen_Shop_Drawings_and_Execution_Boards_Rev-P1_2026-11-22.pdf")

# ---------- palette ----------
INK    = HexColor('#211D18')
PAPER  = HexColor('#FCFBF8')
PANEL  = HexColor('#F3F0EA')
PANELA = HexColor('#EAE6DD')
LINE   = HexColor('#D9D4C9')
OAK    = HexColor('#C9A875')
BRASS  = HexColor('#A98548')
TAUPE  = HexColor('#8A7F71')
OAKW   = HexColor('#E3CDA4')   # oak veneer fill (drawn elevations)
OAKD   = HexColor('#8A6B3F')   # oak grain line
CASH   = HexColor('#CFC4B6')   # cashmere matt lacquer
CREAM  = HexColor('#EDEAE3')   # warm off-white lacquer
BLACK  = HexColor('#242220')   # black appliances / frames
QUARTZ = HexColor('#F6F4EF')   # white quartz
GREIGE = HexColor('#DAD2C2')   # microcement feature soffit
VEIN   = HexColor('#CFC8BB')   # quartz vein

def A(name): return os.path.join(ASSETS, name)

# ---------- image helper (center-crop to box aspect, JPEG) ----------
_cache = {}
def crop_image(path, aspect):
    key = (path, round(aspect, 3))
    if key in _cache: return _cache[key]
    im = Image.open(path).convert('RGB')
    w, h = im.size
    a = w / h
    if a > aspect:
        nw = int(h * aspect); x = (w - nw)//2; im = im.crop((x, 0, x+nw, h))
    else:
        nh = int(w / aspect); y = (h - nh)//2; im = im.crop((0, y, w, y+nh))
    _cache[key] = ImageReader(im)
    return _cache[key]

def ref_image(c, path, x, y, w, h, caption=None, caption_h=7.2*mm):
    """Draw a bordered, center-cropped reference render with optional caption bar."""
    cap = caption_h if caption else 0
    iy = y + cap; ih = h - cap
    c.drawImage(crop_image(path, w/ih), x, iy, width=w, height=ih)
    if caption:
        c.setFillColor(INK); c.rect(x, y, w, cap, stroke=0, fill=1)
        t = c.beginText(x + 2*mm, y + cap/2 - 1.6)
        t.setFont('Helvetica-Bold', 4.6); t.setFillColor(PAPER); t.setCharSpace(0.5)
        t.textOut(caption.upper()); t.setCharSpace(0)
        c.drawText(t)
    c.setStrokeColor(INK); c.setLineWidth(1.1); c.rect(x, y, w, h, stroke=1, fill=0)

# ---------- text helpers ----------
def wrap(text, font, size, max_w):
    lines, cur = [], ''
    for word in text.split():
        trial = (cur + ' ' + word).strip()
        if stringWidth(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines

def micro(c, x, y, s, color=TAUPE, size=4.6, track=1.4):
    t = c.beginText(x, y)
    t.setFont('Helvetica-Bold', size); t.setFillColor(color); t.setCharSpace(track)
    t.textOut(s.upper()); t.setCharSpace(0)
    c.drawText(t)

def hline(c, x1, x2, y, w=0.7, color=LINE, dash=None):
    c.saveState(); c.setStrokeColor(color); c.setLineWidth(w)
    if dash: c.setDash(dash, 0)
    c.line(x1, y, x2, y); c.restoreState()

def vline(c, x, y1, y2, w=0.7, color=LINE, dash=None):
    c.saveState(); c.setStrokeColor(color); c.setLineWidth(w)
    if dash: c.setDash(dash, 0)
    c.line(x, y1, x, y2); c.restoreState()

# ---------- generic table ----------
def table(c, x, y_top, col_widths, rows, pad=2.0*mm, default_size=6.1):
    """rows: list of (height, cells); cell = str | dict(t,b,fill,col,size,a). Returns bottom y."""
    y = y_top
    tw = sum(col_widths)
    for h, cells in rows:
        y -= h
        cx = x
        for i, cell in enumerate(cells):
            cw = col_widths[i]
            cell = {'t': cell} if isinstance(cell, str) else dict(cell)
            t     = cell.get('t', '')
            font  = 'Helvetica-Bold' if cell.get('b') else 'Helvetica'
            fill  = cell.get('fill')
            col   = cell.get('col', INK)
            size  = cell.get('size', default_size)
            align = cell.get('a', 'l')
            if fill is not None:
                c.setFillColor(fill); c.rect(cx, y, cw, h, stroke=0, fill=1)
            c.setFillColor(col); c.setFont(font, size)
            lines = wrap(str(t), font, size, cw - 2*pad)
            lh = size * 1.24
            ty = y + h/2 + (len(lines)-1)*lh/2 - size*0.36
            for ln in lines:
                if align == 'c':   c.drawCentredString(cx + cw/2, ty, ln)
                elif align == 'r': c.drawRightString(cx + cw - pad, ty, ln)
                else:              c.drawString(cx + pad, ty, ln)
                ty -= lh
            cx += cw
        hline(c, x, x + tw, y, 0.6, LINE)
    c.setStrokeColor(INK); c.setLineWidth(1.1); c.rect(x, y, tw, y_top - y, stroke=1, fill=0)
    cx = x
    for cw in col_widths[:-1]:
        cx += cw; vline(c, cx, y, y_top, 0.7, LINE)
    return y

def header_row(labels, h=6.4*mm, fill=INK):
    return (h, [dict(t=l, b=True, fill=fill, col=PAPER, size=6.0, a='l') for l in labels])

# ---------- dimensions ----------
def hdim(c, x1, x2, y_line, y_ref, label, size=5.4, above=True):
    c.setStrokeColor(INK); c.setLineWidth(0.7)
    y_ext = y_ref - 1.0*mm if y_ref < y_line else y_ref + 1.0*mm
    y_end = y_line + 1.7*mm if above else y_line - 1.7*mm
    c.line(x1, y_ext, x1, y_end); c.line(x2, y_ext, x2, y_end)
    c.line(x1, y_line, x2, y_line)
    for xx in (x1, x2):
        c.line(xx-1.15*mm, y_line-1.15*mm, xx+1.15*mm, y_line+1.15*mm)
    if label:
        c.setFont('Helvetica-Bold', size); c.setFillColor(INK)
        ty = y_line + 1.15*mm if above else y_line - 3.4*mm
        c.drawCentredString((x1+x2)/2, ty, label)

def vdim(c, y1, y2, x_line, x_ref, label, size=5.4, right=False):
    c.setStrokeColor(INK); c.setLineWidth(0.7)
    x_ext = x_ref - 1.0*mm if x_ref < x_line else x_ref + 1.0*mm
    x_end = x_line + 1.7*mm if right else x_line - 1.7*mm
    c.line(x_ext, y1, x_end, y1); c.line(x_ext, y2, x_end, y2)
    c.line(x_line, y1, x_line, y2)
    for yy in (y1, y2):
        c.line(x_line-1.15*mm, yy-1.15*mm, x_line+1.15*mm, yy+1.15*mm)
    if label:
        c.saveState(); c.translate(x_line - 1.3*mm if not right else x_line + 1.3*mm, (y1+y2)/2)
        c.rotate(90); c.setFont('Helvetica-Bold', size); c.setFillColor(INK)
        c.drawCentredString(0, -1.6 if not right else -1.2, label); c.restoreState()

def tag(c, x, y, s, w=None, fill=INK, col=PAPER, size=5.6, h=4.6*mm):
    font = 'Helvetica-Bold'
    tw = w if w else stringWidth(s, font, size) + 3.6*mm
    c.setFillColor(fill); c.roundRect(x, y, tw, h, 1.3*mm, stroke=0, fill=1)
    c.setFillColor(col); c.setFont(font, size)
    c.drawCentredString(x + tw/2, y + h/2 - size*0.36, s)
    return tw

# ---------- material helpers for drawings ----------
def oak_fill(c, x, y, w, h, grain=True):
    c.setFillColor(OAKW); c.rect(x, y, w, h, stroke=0, fill=1)
    if grain:
        c.saveState()
        p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
        c.setStrokeColor(OAKD); c.setLineWidth(0.45); c.setStrokeAlpha(0.22)
        rnd = random.Random(11)
        xx = x + 3*mm
        while xx < x + w - 2*mm:
            c.line(xx, y, xx + (rnd.random()-0.5)*4*mm, y + h); xx += 4.6*mm + rnd.random()*2.2*mm
        c.restoreState()
    c.setStrokeColor(INK); c.setStrokeAlpha(1); c.setLineWidth(0.9); c.rect(x, y, w, h, stroke=1, fill=0)

def quartz_fill(c, x, y, w, h, vein=True):
    c.setFillColor(QUARTZ); c.rect(x, y, w, h, stroke=0, fill=1)
    if vein:
        c.saveState()
        p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
        c.setStrokeColor(VEIN); c.setLineWidth(0.7); c.setStrokeAlpha(0.9)
        c.bezier(x+w*0.05, y+h*0.78, x+w*0.30, y+h*0.66, x+w*0.44, y+h*0.40, x+w*0.72, y+h*0.30)
        c.bezier(x+w*0.28, y+h*0.95, x+w*0.48, y+h*0.72, x+w*0.58, y+h*0.52, x+w*0.96, y+h*0.42)
        c.restoreState()
    c.setStrokeColor(INK); c.setLineWidth(0.9); c.rect(x, y, w, h, stroke=1, fill=0)

def appliance_fill(c, x, y, w, h):
    c.setFillColor(BLACK); c.rect(x, y, w, h, stroke=0, fill=1)
    c.saveState()
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(HexColor('#FFFFFF')); c.setLineWidth(1.6); c.setStrokeAlpha(0.10)
    c.line(x + w*0.12, y, x + w*0.44, y + h)
    c.line(x + w*0.30, y, x + w*0.62, y + h)
    c.restoreState()
    c.setStrokeColor(INK); c.setStrokeAlpha(1); c.setLineWidth(0.9); c.rect(x, y, w, h, stroke=1, fill=0)

def label_ink(c, x, y, s, size=4.7, color=INK, b=True):
    c.setFillColor(color); c.setFont('Helvetica-Bold' if b else 'Helvetica', size)
    c.drawString(x, y, s)

# ---------- page frame / header / title block ----------
def frame_board(c, board_no, board_title, scale_txt, page_title=None):
    c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # double frame
    c.setStrokeColor(INK); c.setLineWidth(2.0); c.rect(FRAME, FRAME, PAGE_W-2*FRAME, PAGE_H-2*FRAME, stroke=1, fill=0)
    c.setLineWidth(0.6);    c.rect(FRAME+1.5*mm, FRAME+1.5*mm, PAGE_W-2*FRAME-3*mm, PAGE_H-2*FRAME-3*mm, stroke=1, fill=0)
    inner_l = FRAME + 1.5*mm; inner_r = PAGE_W - FRAME - 1.5*mm
    # header
    hy = PAGE_H - FRAME - 6.2*mm
    micro(c, inner_l + 2*mm, hy, 'SAMLILL — INTERIOR ARCHITECTURE & FIT-OUT', size=5.0, track=1.6)
    _t = c.beginText(); _t.setFont('Helvetica-Bold', 6.6); _t.setFillColor(INK); _t.setCharSpace(1.15)
    _msg = 'OPEN-PLAN KITCHEN & DINING — PRIVATE RESIDENCE · AMMAN'
    _t.setTextOrigin(PAGE_W/2 - (stringWidth(_msg, 'Helvetica-Bold', 6.6) + 1.15 * len(_msg)) / 2, hy)
    _t.textOut(_msg); _t.setCharSpace(0)
    c.drawText(_t)
    _lbl = 'EXECUTION BOARD'
    micro(c, inner_r - 2*mm - (stringWidth(_lbl, 'Helvetica-Bold', 5.0) + 1.6*(len(_lbl)-1)), hy,
          _lbl, color=INK, size=5.0, track=1.6)
    hline(c, inner_l, inner_r, hy - 3.1*mm, 0.8, BRASS)
    # title block
    tb_top = FRAME + TITLE_H
    c.setLineWidth(1.1); c.setStrokeColor(INK); c.line(inner_l, tb_top, inner_r, tb_top)
    c1 = inner_l + 128*mm; c2 = inner_l + 279*mm
    vline(c, c1, FRAME, tb_top, 0.8, INK); vline(c, c2, FRAME, tb_top, 0.8, INK)
    hline(c, inner_l, inner_r, FRAME + TITLE_H/2, 0.7, INK)
    # col 1 — project
    micro(c, inner_l + 2*mm, tb_top - 3.4*mm, 'PROJECT', size=4.2)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 8.2)
    c.drawString(inner_l + 2*mm, FRAME + TITLE_H/2 + 1.35*mm, 'OPEN-PLAN KITCHEN & DINING')
    micro(c, inner_l + 2*mm, FRAME + TITLE_H/2 - 4.4*mm, 'CLIENT', size=4.2)
    label_ink(c, inner_l + 16*mm, FRAME + TITLE_H/2 - 4.4*mm - 0.2, 'PRIVATE RESIDENCE', size=4.7)
    micro(c, inner_l + 2*mm, FRAME + 2.6*mm, 'LOCATION', size=4.2)
    label_ink(c, inner_l + 16*mm, FRAME + 2.4*mm, 'AMMAN, JORDAN', size=4.7)
    # col 2 — board title
    micro(c, c1 + 2*mm, tb_top - 3.4*mm, 'BOARD TITLE', size=4.2)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 9.4)
    lines = wrap(board_title.upper(), 'Helvetica-Bold', 9.4, c2 - c1 - 5*mm)
    ty = FRAME + TITLE_H/2 + 2.15*mm + (len(lines)-1)*4.1*mm
    for ln in lines:
        c.drawString(c1 + 2*mm, ty, ln); ty -= 4.1*mm
    micro(c, c1 + 2*mm, FRAME + TITLE_H/2 - 4.4*mm, 'PAPER', size=4.2)
    label_ink(c, c1 + 14*mm, FRAME + TITLE_H/2 - 4.6*mm, 'A3 · 420×297 mm', size=4.7)
    micro(c, c1 + 2*mm, FRAME + 2.6*mm, 'UNITS', size=4.2)
    label_ink(c, c1 + 14*mm, FRAME + 2.4*mm, 'MILLIMETRES', size=4.7)
    micro(c, c1 + 42*mm, FRAME + TITLE_H/2 - 4.4*mm, 'SCALE', size=4.2)
    label_ink(c, c1 + 54*mm, FRAME + TITLE_H/2 - 4.6*mm, scale_txt, size=4.7)
    micro(c, c1 + 42*mm, FRAME + 2.6*mm, 'SOURCE', size=4.2)
    label_ink(c, c1 + 54*mm, FRAME + 2.4*mm, 'ENSCAPE 2026-11-15', size=4.7)
    # col 3 — drawing no
    micro(c, c2 + 2*mm, tb_top - 3.4*mm, 'DRAWING NO', size=4.2)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 14.5)
    c.drawString(c2 + 2*mm, FRAME + TITLE_H/2 + 0.45*mm, board_no)
    micro(c, c2 + 2*mm, FRAME + TITLE_H/2 - 4.4*mm, 'DATE', size=4.2)
    label_ink(c, c2 + 13*mm, FRAME + TITLE_H/2 - 4.6*mm, '2026-11-22', size=4.7)
    micro(c, c2 + 2*mm, FRAME + 2.6*mm, 'REV', size=4.2)
    label_ink(c, c2 + 11*mm, FRAME + 2.4*mm, 'P1 — FOR CLIENT REVIEW', size=4.7)
    # disclaimer above title block
    c.setFillColor(TAUPE); c.setFont('Helvetica', 4.6)
    c.drawCentredString(PAGE_W/2, tb_top + 1.6*mm,
        'ALL DIMENSIONS INDICATIVE — DERIVED FROM 3D VISUALISATION. VERIFY ON SITE BEFORE FABRICATION.  ·  DO NOT SCALE FROM DRAWING.')
    return inner_l + 2*mm, tb_top + 6*mm, inner_r - 2*mm, hy - 6*mm

# ============================================================================
# K-00 — COVER & DRAWING INDEX
# ============================================================================
def page_k00(c):
    frame_board(c, 'K-00', 'Cover & drawing index', 'NTS')
    micro(c, 12*mm, 253*mm, 'EXECUTION BOARD SET · REV P1 · ISSUED FOR CLIENT REVIEW', color=BRASS, size=6.0, track=2.0)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 29.5)
    c.drawString(12*mm, 226*mm, 'OPEN-PLAN KITCHEN & DINING')
    _t = c.beginText(12*mm, 210.5*mm)
    _t.setFont('Helvetica-Bold', 14.5); _t.setFillColor(BRASS); _t.setCharSpace(3.2)
    _t.textOut('SHOP DRAWINGS & EXECUTION BOARDS'); _t.setCharSpace(0)
    c.drawText(_t)
    hline(c, 12*mm, 84*mm, 202.5*mm, 1.6, BRASS)
    micro(c, 12*mm, 194.5*mm,
          'JOINERY · APPLIANCES · LIGHTING · MATERIALS · FF&E — KITCHEN, ISLAND, COFFEE BAR & DINING   |   PRIVATE RESIDENCE, AMMAN, JORDAN   |   2026-11-22',
          size=5.2, track=0.8)

    ref_image(c, A('scene_1_154523.jpg'), 12*mm, 42*mm, 236*mm, 132*mm,
              'HERO VIEW — ENSCAPE SCENE 1 · 15:45 — VISUAL INTENT ONLY', caption_h=7.6*mm)

    micro(c, 12*mm, 33.6*mm,
          'READ THIS SET — DIMS IN MM · INDICATIVE FROM VISUALISATION · VERIFY ON SITE · CODES MT/AP/L/FE/SP CROSS-REFER SCHEDULES · SCALE PER BOARD, NTS OTHERWISE',
          size=4.9, track=0.5)

    # right column — drawing index
    micro(c, 258*mm, 190*mm, 'DRAWING INDEX', color=INK, size=6.2, track=2.0)
    hline(c, 258*mm, 411.5*mm, 186.4*mm, 1.0, INK)
    rows = [
        ('K-00', 'Cover & drawing index (this board)', 'NTS'),
        ('K-01', 'General arrangement plan — kitchen · island · dining', '1:50'),
        ('K-02', 'Elevation A — main wall · tall units · sink & window', '1:30'),
        ('K-03', 'Elevations B & C — coffee bar (west) · east tall unit & niche', '1:25 · 1:20'),
        ('K-04', 'Island — cook & seating elevations · waterfall & hood details', '1:15 · 1:10'),
        ('K-05', 'Reflected ceiling plan — coves · downlights · pendants', '1:50'),
        ('K-06', 'Materials & finishes schedule — codes MT-01…17', 'NTS'),
        ('K-07', 'Appliance schedule & services points — codes AP/SP', 'NTS'),
        ('K-08', 'Lighting & electrical schedule — codes L/E', 'NTS'),
        ('K-09', 'FF&E schedule · execution notes · revisions & sign-off', 'NTS'),
    ]
    y = 170.5*mm
    for code, title, scale in rows:
        hline(c, 258*mm, 411.5*mm, y + 12.0*mm, 0.5, LINE)
        c.setFillColor(INK); c.setFont('Helvetica-Bold', 7.6)
        c.drawString(258*mm, y + 4.4*mm, code)
        c.setFillColor(INK); c.setFont('Helvetica', 6.0)
        for i, ln in enumerate(wrap(title, 'Helvetica', 6.0, 108*mm)):
            c.drawString(272*mm, y + 6.9*mm - i*3.1*mm, ln)
        micro(c, 258*mm, y + 1.0*mm, 'SCALE ' + scale, size=3.6, track=0.8)
        y -= 12.35*mm
    hline(c, 258*mm, 411.5*mm, y + 12.1*mm, 0.9, INK)
    c.showPage()

# ============================================================================
# K-01 — GENERAL ARRANGEMENT PLAN (1:50)
# ============================================================================
def page_k01(c):
    frame_board(c, 'K-01', 'General arrangement plan — kitchen · island · dining', '1:50')
    micro(c, 12*mm, 253*mm, 'KITCHEN + DINING — GA PLAN @ 1:50', size=6.0, track=1.6)

    k = 1/50
    px0, py0 = 22*mm, 84*mm          # paper origin (room SW)
    def X(x): return px0 + x*mm*k
    def Y(y): return py0 + y*mm*k

    # ---- walls (240 thick) ----
    c.setFillColor(PANELA); c.setStrokeColor(INK); c.setLineWidth(1.3)
    c.rect(X(0), Y(6060), (9600)*mm*k, 240*mm*k, stroke=1, fill=1)   # north
    c.rect(X(0), Y(0), 240*mm*k, 6300*mm*k, stroke=1, fill=1)        # west
    c.rect(X(9360), Y(0), 240*mm*k, 6300*mm*k, stroke=1, fill=1)     # east
    # south wall stubs with opening to living/hall
    c.rect(X(0), Y(0), 2500*mm*k, 240*mm*k, stroke=1, fill=1)
    c.rect(X(6100), Y(0), 3500*mm*k, 240*mm*k, stroke=1, fill=1)
    c.setFillColor(TAUPE); c.setFont('Helvetica', 5.0)
    c.drawCentredString(X(4300), Y(120) - 1.2*mm, 'OPEN TO LIVING / HALL')

    # ---- glazing openings (black alu frames + oak venetian blinds) ----
    def glazing_north(x1, x2):
        y0, y1 = Y(6060), Y(6300)
        c.setFillColor(PAPER); c.rect(X(x1), y0, (x2-x1)*mm*k, y1-y0, stroke=0, fill=1)
        c.setLineWidth(1.6); c.setStrokeColor(INK)
        c.line(X(x1), Y(6075), X(x2), Y(6075)); c.line(X(x1), Y(6270), X(x2), Y(6270))
        step = 600
        xx = x1 + step
        c.setLineWidth(0.9)
        while xx < x2 - 50:
            c.line(X(xx), Y(6075), X(xx), Y(6270)); xx += step
    def glazing_west(y1, y2):
        x0, x1 = X(0), X(240)
        c.setFillColor(PAPER); c.rect(x0, Y(y1), x1-x0, (y2-y1)*mm*k, stroke=0, fill=1)
        c.setLineWidth(1.6); c.setStrokeColor(INK)
        c.line(X(15), Y(y1), X(15), Y(y2)); c.line(X(225), Y(y1), X(225), Y(y2))
        yy = y1 + 600
        c.setLineWidth(0.9)
        while yy < y2 - 50:
            c.line(X(15), Y(yy), X(225), Y(yy)); yy += 600
    glazing_north(0, 750)          # dining corner (north leg)
    glazing_west(3900, 6300)       # dining corner (west leg)
    # door leaf + swing on west glazing
    c.setLineWidth(1.4); c.setStrokeColor(INK)
    c.line(X(60), Y(3900), X(60), Y(3900 + 1000))
    c.saveState(); c.setDash([1.6, 1.6], 0); c.setLineWidth(0.6)
    p = c.beginPath(); p.arc(X(60 - 1000), Y(3900), X(60 + 1000), Y(3900 + 2000), 0, 90); c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    # ---- back run: tall units A1,A2 / panels / A5 / niche A6 / end panel ----
    def rect_r(x1, y1, x2, y2, fill=None, stroke=INK, lw=0.9, grain=False):
        if fill is not None:
            c.setFillColor(fill); c.rect(X(x1), Y(y1), (x2-x1)*mm*k, (y2-y1)*mm*k, stroke=0, fill=1)
        if grain:
            oak_fill(c, X(x1), Y(y1), (x2-x1)*mm*k, (y2-y1)*mm*k)
        else:
            c.setStrokeColor(stroke); c.setLineWidth(lw)
            c.rect(X(x1), Y(y1), (x2-x1)*mm*k, (y2-y1)*mm*k, stroke=1, fill=0)
    rect_r(950, 5440, 1700, 6060, grain=True)     # A1 tall tower
    rect_r(1700, 5440, 2650, 6060, fill=BLACK)    # A2 fridge (black)
    rect_r(2650, 5440, 2800, 6060, grain=True)    # end panel
    # base run + counter
    rect_r(2800, 5440, 7000, 6060, fill=CREAM)    # cabinets
    rect_r(2800, 5480, 7000, 6060, stroke=INK, lw=1.1)   # counter line (front edge bold)
    # vitrines (wall) over base run
    rect_r(2800, 5710, 3250, 6060, fill=PANELA, lw=1.0)
    rect_r(5750, 5710, 6200, 6060, fill=PANELA, lw=1.0)
    # sink (black composite) + tap
    rect_r(4450, 5560, 5150, 5920, fill=BLACK)
    c.setFillColor(BLACK); c.circle(X(4800), Y(5920), 0.9*mm, stroke=0, fill=1)
    # dishwasher mark
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 4.4)
    c.drawCentredString(X(6500), Y(5720), 'AP-05')
    # window over sink (in north wall) + east window
    glazing_north(3250, 5750)
    glazing_east = None  # east wall window drawn below
    c.setFillColor(PAPER); c.rect(X(9360), Y(4300), 240*mm*k, (6300-4300)*mm*k, stroke=0, fill=1)
    c.setLineWidth(1.6); c.setStrokeColor(INK)
    c.line(X(9375), Y(4300), X(9375), Y(6300)); c.line(X(9525), Y(4300), X(9525), Y(6300))
    c.setLineWidth(0.9); yy = 4300 + 600
    while yy < 6300 - 50:
        c.line(X(9375), Y(yy), X(9525), Y(yy)); yy += 600
    # east tall unit + niche
    rect_r(7000, 5440, 7700, 6060, grain=True)    # A5
    rect_r(7700, 5440, 8500, 6060, grain=True)    # A6 niche enclosure
    c.setFillColor(HexColor('#3B342B'))
    c.rect(X(7740), Y(5480), (800-80)*mm*k, (570)*mm*k, stroke=0, fill=1)
    for px in (7950, 8150, 8350):
        c.setFillColor(OAKD); c.circle(X(px), Y(5720), 0.85*mm, stroke=0, fill=1)
    rect_r(8500, 5440, 8600, 6060, grain=True)    # A7

    # ---- island ----
    rect_r(3300, 3300, 6600, 4450, fill=QUARTZ)
    quartz_fill(c, X(3300), Y(3300), 3300*mm*k, 1150*mm*k)
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect(X(3300), Y(3300), 3300*mm*k, 1150*mm*k, stroke=1, fill=0)
    # cabinet line south face (seating side overhang)
    hline(c, X(3300), X(6600), Y(3560), 0.7, VEIN)
    # hob zone
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.setDash([1.8, 1.4], 0)
    c.rect(X(4150), Y(3850), 1600*mm*k, 700*mm*k, stroke=1, fill=0); c.setDash([], 0)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 4.6)
    c.drawCentredString(X(4950), Y(4190), 'AP-06 HOB')
    # centreline
    vline(c, X(4950), Y(3050), Y(6050), 0.6, TAUPE, dash=[5, 1.5, 1, 1.5])
    c.setFont('Helvetica-Bold', 4.6); c.setFillColor(TAUPE)
    c.drawString(X(4950) + 1.2*mm, Y(3080), 'CL')
    # bar stools (2)
    for sx in (4100, 5300):
        c.setFillColor(HexColor('#CFC4B6')); c.circle(X(sx), Y(2950), 3.4*mm, stroke=1, fill=1)
        c.setStrokeColor(INK); c.setLineWidth(0.7); c.circle(X(sx), Y(2950), 3.4*mm, stroke=1, fill=0)

    # ---- dining table + 6 chairs ----
    c.setFillColor(QUARTZ); c.setStrokeColor(INK); c.setLineWidth(1.1)
    c.roundRect(X(650), Y(3300), 1900*mm*k, 950*mm*k, 4*mm, stroke=1, fill=1)
    COGNAC = HexColor('#B07B4A')
    chair_positions = [(1150, 3060), (1750, 3060), (2350, 3060), (1150, 4490), (1750, 4490), (2350, 4490)]
    for cx_, cy_ in chair_positions:
        c.setFillColor(COGNAC); c.roundRect(X(cx_-230), Y(cy_-230), 460*mm*k, 460*mm*k, 2*mm, stroke=1, fill=1)
        c.setFillColor(HexColor('#CFC4B6')); c.roundRect(X(cx_-150), Y(cy_-150), 300*mm*k, 300*mm*k, 1.5*mm, stroke=0, fill=1)

    # ---- coffee bar (west wall) ----
    rect_r(240, 300, 790, 2400, grain=True)       # C1 low floating counter
    c.setFillColor(INK)                            # black steel end frame
    c.rect(X(240), Y(300), (790-240)*mm*k, 130*mm*k, stroke=0, fill=1)
    rect_r(240, 330, 560, 2400, stroke=INK, lw=0.8)   # C2 vitrines (shallow)
    rect_r(240, 2400, 900, 3900, grain=True)      # C3 pantry
    c.setLineWidth(2.2); c.setStrokeColor(INK)    # pantry shadow gap
    c.line(X(240), Y(3250), X(900), Y(3250))

    # ---- structural column E1 ----
    rect_r(1050, 1350, 1650, 1950, grain=True)

    # ---- module tags ----
    def plan_tag(x, y, s): tag(c, X(x), Y(y), s)
    plan_tag(1000, 5630, 'A1'); plan_tag(1950, 5630, 'A2')
    tag(c, X(4525), Y(5700), 'AP-08', fill=PAPER, col=INK, size=4.6, h=3.8*mm)
    plan_tag(7130, 5630, 'A5'); plan_tag(7980, 5630, 'A6')
    plan_tag(4680, 3600, 'B1')
    plan_tag(330, 1210, 'C1'); plan_tag(330, 2450, 'C2'); plan_tag(430, 3530, 'C3')
    plan_tag(1205, 1520, 'E1')

    # ---- dimensions ----
    def chain_x(x1, x2, y_line, label, row=0):
        hdim(c, X(x1), X(x2), Y(y_line), Y(6300), None, size=4.2)
        c.setFont('Helvetica-Bold', 4.2); c.setFillColor(INK)
        c.drawCentredString((X(x1)+X(x2))/2, Y(y_line) + (1.15 if row == 0 else 5.6)*mm, label)
    for i, (a, b, l) in enumerate([(0,950,'950'),(950,1700,'750'),(1700,2650,'950'),(2650,2800,'150'),
                                   (2800,7000,'4200'),(7000,7700,'700'),(7700,8500,'800'),(8500,8600,'100'),(8600,9600,'1000')]):
        chain_x(a, b, 6400, l, row=i % 2)
    hdim(c, X(0), X(9600), Y(7260), Y(6300), '9600 — OVERALL', size=5.0)
    vdim(c, Y(0), Y(6300), 16.0*mm, X(0), '6300 — OVERALL', size=5.0)
    # island dims
    hdim(c, X(3300), X(6600), Y(4720), Y(4450), '3300', size=4.6)
    vdim(c, Y(3300), Y(4450), X(6880), X(6600), '1150', size=4.6, right=True)
    # clearance island–counter front
    c.setLineWidth(0.7); c.setStrokeColor(INK)
    c.saveState(); c.setDash([1.5, 1.5], 0)
    c.line(X(4950), Y(4450), X(4950), Y(5460)); c.restoreState()
    for yy in (4450, 5460):
        c.line(X(4870), Y(yy), X(5030), Y(yy))
    c.saveState(); c.translate(X(4950) + 1.6*mm, Y(4930)); c.rotate(90)
    c.setFont('Helvetica-Bold', 4.2); c.setFillColor(INK)
    c.drawCentredString(0, 0, '1010 CLR'); c.restoreState()

    # ---- north arrow + scale bar ----
    nx, ny = 202*mm, 237*mm
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.circle(nx, ny, 5.2*mm, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(nx, ny - 3.4*mm); p.lineTo(nx + 1.6*mm, ny + 0.5*mm); p.lineTo(nx, ny + 3.6*mm); p.lineTo(nx - 1.6*mm, ny + 0.5*mm); p.close()
    c.setFillColor(INK); c.drawPath(p, stroke=0, fill=1)
    c.setFont('Helvetica-Bold', 7.2); c.setFillColor(INK); c.drawCentredString(nx, ny - 9.2*mm, 'N')
    # scale bar 0-2 m
    sb_x, sb_y = 16*mm, 52*mm
    for i in range(4):
        c.setFillColor(INK if i % 2 == 0 else PAPER)
        c.rect(sb_x + i*10*mm, sb_y, 10*mm, 2.4*mm, stroke=1, fill=1)
    for i, l in enumerate(['0', '500', '1000', '1500', '2000']):
        micro(c, sb_x + i*10*mm - 1.6*mm, sb_y - 4.2*mm, l, size=3.6, track=0.3)
    micro(c, sb_x, sb_y + 4.6*mm, 'SCALE 1:50 (mm)', size=4.2, track=1.2)

    # ===== right-hand notes column =====
    rx = 262*mm; rw = 411.5*mm - rx
    y = 253*mm
    micro(c, rx, y, 'ZONE LEGEND', color=INK, size=5.6, track=1.6); y -= 4*mm
    y = table(c, rx, y, [16*mm, rw - 16*mm], [
        header_row(['ZONE', 'DESCRIPTION'], h=5.4*mm),
        (6.6*mm, [dict(t='A', b=True, a='c'), 'Back run & tall wall — ovens · fridge · sink · window (K-02)']),
        (6.6*mm, [dict(t='B', b=True, a='c'), 'Island & ceiling-mounted hood (K-04)']),
        (6.6*mm, [dict(t='C', b=True, a='c'), 'Coffee bar, vitrines & tall pantry — west wall (K-03)']),
        (6.6*mm, [dict(t='D', b=True, a='c'), 'Dining — table & 6 chairs (K-09)']),
        (6.6*mm, [dict(t='E', b=True, a='c'), 'Oak-clad structural column · marble skirting']),
        (6.6*mm, [dict(t='F', b=True, a='c'), 'Floor-to-ceiling glazing · oak venetian blinds']),
        (6.6*mm, [dict(t='G', b=True, a='c'), 'Floor — 900×900 porcelain, light grey, honed']),
        (6.6*mm, [dict(t='H', b=True, a='c'), 'Ceiling coves & lighting (K-05 / K-08)']),
    ], default_size=5.2)
    y -= 6*mm
    micro(c, rx, y, 'KEY NOTES', color=INK, size=5.6, track=1.6); y -= 4.6*mm
    notes = [
        'All dimensions indicative — derived from Enscape visualisation; verify on site prior to fabrication; discrepancies via RFI.',
        'Base units D 560 (+ 640 worktop); tall units D 620. Plinth 100 recessed 25. Shadow gaps 10, black.',
        'Island — gas & power only; floor box with isolation valve accessible within carcass (SP-01). No water to island.',
        'Sink at back wall under window; dishwasher right of sink; quartz upstand 920–1080.',
        'Window to have oak venetian blind (MT-10); east window same.',
        'Column clad in matching MT-01 oak; skirting 120 quartz MT-05 throughout.',
        'Floor — straight lay, centred on island CL. Grout joints max 2 mm; honed, rectified.',
        'Door leaf on west glazing — hardware per window supplier; sweeps sealed.',
        'Protect all finished work; remove protection only at handover snag.',
    ]
    c.setFont('Helvetica', 5.1); c.setFillColor(INK)
    for i, n in enumerate(notes, 1):
        lines = wrap(f'{i}.  {n}', 'Helvetica', 5.1, rw)
        for ln in lines:
            c.drawString(rx, y, ln); y -= 2.9*mm
        y -= 0.9*mm
    y -= 2*mm
    micro(c, rx, y, 'CLEARANCES', color=INK, size=5.6, track=1.6); y -= 4*mm
    y = table(c, rx, y, [rw - 30*mm, 30*mm], [
        header_row(['LOCATION', 'CLEAR'], h=5.2*mm),
        (5.4*mm, ['Counter front — island', dict(t='1010', a='c', b=True)]),
        (5.4*mm, ['Island — dining table', dict(t='750', a='c', b=True)]),
        (5.4*mm, ['Stool pull-out zone', dict(t='450', a='c', b=True)]),
        (5.4*mm, ['Vitrine — above counter', dict(t='520', a='c', b=True)]),
    ], default_size=5.0)
    y -= 5*mm
    ref_image(c, A('scene_2.jpg'), rx, 34*mm, rw, min(y - 36*mm, 52*mm),
              'SCENE 2 — OVERALL VIEW (VISUAL REFERENCE)', caption_h=6.2*mm)
    c.showPage()

# ============================================================================
# K-02 — ELEVATION A: MAIN WALL (1:30)
# ============================================================================
def page_k02(c):
    frame_board(c, 'K-02', 'Elevation A — main wall · tall units · sink & window', '1:30')
    micro(c, 12*mm, 253*mm, 'ELEVATION A — MAIN WALL · 1:30 · LOOKING NORTH', size=6.0, track=1.6)

    base_y = 92*mm; TOP = 2700
    def R(x): return 14*mm + x/30*mm      # real mm -> paper x
    def H(h): return base_y + h/30*mm     # real mm -> paper y

    # floor line + ceiling cut
    hline(c, 10*mm, 280*mm, base_y, 1.6, INK)
    for xx in range(12, 279, 9):
        c.line(xx*mm, base_y, (xx-4)*mm, base_y - 3.2*mm)
    vline(c, 14*mm, H(0), H(2700), 0.5, LINE, dash=[4, 2])
    # feature soffit band (microcement) 2450–2700
    c.setFillColor(GREIGE); c.rect(14*mm, H(2450), R(7650)-14*mm, H(2700)-H(2450), stroke=0, fill=1)
    hline(c, 14*mm, R(7650), H(2450), 0.8, INK)
    hline(c, 14*mm, R(7650), H(2700), 1.0, TAUPE, dash=[3, 2])
    micro(c, R(7650) + 1.5*mm, H(2565), 'FEATURE SOFFIT MT-11', size=3.6, track=0.5)

    # helper: door channel groove (recessed pull, black 2mm)
    def groove(x1, x2, h, lw=2.0):
        c.setStrokeColor(BLACK); c.setLineWidth(lw); c.line(R(x1), H(h), R(x2), H(h))
    def hairline_h(x1, x2, h):
        hline(c, R(x1), R(x2), H(h), 0.5, HexColor('#B9B2A4'))

    # ---------- A1 : tall tower 0–750 ----------
    oak_fill(c, R(0), H(0), R(750)-R(0), H(2450)-H(0))
    appliance_fill(c, R(60), H(1500), R(750)-R(120), H(1830)-H(1500))   # microwave
    appliance_fill(c, R(60), H(700),  R(750)-R(120), H(1340)-H(700))    # oven
    appliance_fill(c, R(60), H(450),  R(750)-R(120), H(620)-H(450))     # warming drawer
    c.setStrokeColor(HexColor('#FFFFFF')); c.setStrokeAlpha(0.25); c.setLineWidth(0.6)
    c.line(R(110), H(1620), R(690), H(1620)); c.line(R(110), H(1010), R(690), H(1010))
    c.setStrokeAlpha(1)
    for gx in (H(1830), H(1500), H(1340), H(700), H(620), H(450), H(2450)):
        pass
    hairline_h(0, 750, 1850); groove(0, 750, 1850, 1.8)
    groove(0, 750, 700, 1.8); groove(0, 750, 450, 1.8); groove(0, 750, 1500, 1.4)
    # plinth
    c.setFillColor(HexColor('#101010')); c.rect(R(0)+1.2*mm, H(0), R(750)-R(0)-2.4*mm, H(100)-H(0), stroke=0, fill=1)
    tag(c, R(300), H(2240), 'A1')
    micro(c, R(375)-12*mm, H(1630), 'MICRO AP-02', color=PAPER, size=3.2, track=0.3)
    micro(c, R(375)-8.5*mm, H(995), 'OVEN AP-01', color=PAPER, size=3.2, track=0.3)

    # ---------- A2 : fridge 750–1700 ----------
    appliance_fill(c, R(760), H(0), R(1700)-R(760), H(2100)-H(0))
    vline(c, (R(750)+R(1700))/2, H(0), H(2100), 1.6, HexColor('#0E0D0B'))
    # handles
    c.setStrokeColor(HexColor('#3F3E3B')); c.setLineWidth(1.3)
    mid = (R(750)+R(1700))/2
    c.line(mid - 2.6*mm, H(950), mid - 2.6*mm, H(1850)); c.line(mid + 2.6*mm, H(950), mid + 2.6*mm, H(1850))
    oak_fill(c, R(750), H(2100), R(1700)-R(750), H(2450)-H(2100))
    groove(750, 1700, 2100, 1.8)
    tag(c, R(1120), H(2225), 'A2')
    micro(c, R(880), H(1050), 'AP-04', color=PAPER, size=4.0, track=0.6)

    # ---------- end panel ----------
    oak_fill(c, R(1700), H(0), R(1850)-R(1700), H(2450)-H(0))

    # ---------- BASE RUN 1850–6050 ----------
    # cabinets
    c.setFillColor(CREAM); c.rect(R(1850), H(100), R(6050)-R(1850), H(900)-H(100), stroke=0, fill=1)
    # plinth
    c.setFillColor(HexColor('#101010')); c.rect(R(1850)+1.2*mm, H(0), R(6050)-R(1850)-2.4*mm, H(100)-H(0), stroke=0, fill=1)
    # door/drawer divisions every 600mm
    for dx in (2450, 3050, 3650, 4250, 4850, 6050):
        vline(c, R(dx), H(100), H(900), 0.6, HexColor('#B9B2A4'))
    groove(1850, 6050, 830, 1.6)   # top shadow line under worktop
    groove(3650, 4250, 470, 1.6)
    groove(5850, 6050, 470, 1.6); groove(5850, 6050, 280, 1.6)
    # sink zone divisions emphasised: dishwasher 5250–5850
    steel = HexColor('#B9B9BC')
    c.setFillColor(steel); c.rect(R(5250), H(100), R(5850)-R(5250), H(900)-H(100), stroke=0, fill=1)
    c.setFillColor(HexColor('#2B2B2D')); c.rect(R(5250), H(820), R(5850)-R(5250), H(900)-H(820), stroke=0, fill=1)
    groove(5250, 5850, 800, 2.2)
    micro(c, R(5305), H(400), 'AP-05', size=6.2)
    c.setFillColor(INK)
    # worktop (quartz) 900–920
    quartz_fill(c, R(1846), H(900), R(6054)-R(1846), H(920)-H(900)+1.2*mm, vein=False)
    # splashback 920–1080
    quartz_fill(c, R(1850), H(920), R(6050)-R(1850), H(1080)-H(920), vein=True)
    # sink + gooseneck tap
    c.setFillColor(BLACK); c.roundRect(R(3500), H(920), R(4200)-R(3500), 1.5*mm, 0.7*mm, stroke=0, fill=1)
    c.setStrokeColor(BLACK); c.setLineWidth(1.7)
    tapx = R(3850)
    p = c.beginPath(); p.moveTo(tapx, H(920)); p.lineTo(tapx, H(1330))
    p.curveTo(tapx, H(1480), tapx + 8.5*mm, H(1480), tapx + 8.5*mm, H(1295))
    c.drawPath(p, stroke=1, fill=0)
    c.circle(tapx, H(920), 0.9*mm, stroke=0, fill=1)
    # window 2300–4800, h 1100–2380 (rel), oak venetian blinds
    win_x1, win_x2, win_y1, win_y2 = R(2300), R(4800), H(1100), H(2380)
    c.setStrokeColor(INK); c.setLineWidth(2.6); c.rect(win_x1, win_y1, win_x2-win_x1, win_y2-win_y1, stroke=1, fill=0)
    c.setFillColor(HexColor('#DCE9EF')); c.rect(win_x1, win_y1, win_x2-win_x1, win_y2-win_y1, stroke=0, fill=1)
    # blind slats (lowered 42%)
    slat_bottom = win_y2 - (win_y2-win_y1)*0.42
    c.setStrokeColor(HexColor('#8F6B3F')); c.setLineWidth(0.75)
    yy = win_y2 - 2.2*mm
    while yy > slat_bottom:
        c.line(win_x1+1.2*mm, yy, win_x2-1.2*mm, yy); yy -= 1.55*mm
    c.setLineWidth(1.4); c.line(win_x1, slat_bottom, win_x2, slat_bottom)
    # blind housing + cord
    c.setFillColor(HexColor('#6E4F2A')); c.rect(win_x1, win_y2, win_x2-win_x1, 2.2*mm, stroke=0, fill=1)
    c.setStrokeColor(HexColor('#3B2E1E')); c.setLineWidth(0.7)
    cx = win_x1 + (win_x2-win_x1)*0.72
    c.line(cx, win_y2, cx, slat_bottom - 4*mm)
    # sashes split
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.line((win_x1+win_x2)/2, win_y1, (win_x1+win_x2)/2, win_y2)
    micro(c, win_x1 + 2*mm, win_y2 + 3.6*mm, 'F1 — VENETIAN OAK BLINDS', size=3.6, track=0.5)
    # vitrines 1850–2300 & 4800–5250, h 1350–2250
    for vx1, vx2 in ((1850, 2300), (4800, 5250)):
        vx, vw = R(vx1), R(vx2)-R(vx1)
        vy, vh = H(1350), H(2250)-H(1350)
        c.setFillColor(HexColor('#2E2C29')); c.rect(vx, vy, vw, vh, stroke=0, fill=1)
        c.setStrokeColor(INK); c.setLineWidth(2.2); c.rect(vx, vy, vw, vh, stroke=1, fill=0)
        # glass sheen
        c.setStrokeAlpha(0.22); c.setStrokeColor(PAPER); c.setLineWidth(1.5)
        c.line(vx + vw*0.14, vy, vx + vw*0.44, vy + vh)
        c.setStrokeAlpha(1)
        # shelves + ceramics silhouettes
        c.setStrokeColor(HexColor('#57544F')); c.setLineWidth(0.9)
        for sy in (vy + vh*0.33, vy + vh*0.62):
            c.line(vx + 1.5*mm, sy, vx + vw - 1.5*mm, sy)
        rnd = random.Random(int(vx1))
        for row_y in (vy + vh*0.08, vy + vh*0.40, vy + vh*0.70):
            xx = vx + 2.5*mm
            while xx < vx + vw - 4*mm:
                pw, ph = 2.4*mm + rnd.random()*2.0*mm, 3.4*mm + rnd.random()*2.6*mm
                c.setFillColor(HexColor('#7A6A55') if rnd.random() > 0.4 else HexColor('#4E4A44'))
                c.rect(xx, row_y, pw, ph, stroke=0, fill=1); xx += pw + 1.7*mm
        # LED strip top inner
        c.setStrokeColor(BRASS); c.setLineWidth(0.9); c.line(vx + 1.2*mm, vy + vh - 1.2*mm, vx + vw - 1.2*mm, vy + vh - 1.2*mm)
    tag(c, R(1990), H(2285), 'V1'); tag(c, R(4940), H(2285), 'V2')

    # ---------- A5 : east tall tower 6050–6750 ----------
    oak_fill(c, R(6050), H(0), R(6750)-R(6050), H(2450)-H(0))
    appliance_fill(c, R(6100), H(1350), R(6700)-R(6100), H(1950)-H(1350))
    c.setStrokeColor(HexColor('#FFFFFF')); c.setStrokeAlpha(0.22); c.setLineWidth(0.6)
    c.line(R(6140), H(1620), R(6660), H(1620)); c.setStrokeAlpha(1)
    groove(6050, 6750, 1350, 1.8); groove(6050, 6750, 1950, 1.8); groove(6050, 6750, 2300, 1.8)
    c.setFillColor(HexColor('#101010')); c.rect(R(6050)+1.2*mm, H(0), R(6750)-R(6050)-2.4*mm, H(100)-H(0), stroke=0, fill=1)
    tag(c, R(6230), H(2240), 'A5')
    micro(c, R(6125), H(1630), 'AP-09', color=PAPER, size=3.6, track=0.4)

    # ---------- A6 : pendant niche 6750–7550 ----------
    oak_fill(c, R(6750), H(0), R(7550)-R(6750), H(2450)-H(0))
    c.setFillColor(HexColor('#3B342B'))
    c.rect(R(6790), H(150), R(7510)-R(6790), H(2450)-H(150), stroke=0, fill=1)
    # step + plinth LED
    c.setFillColor(OAKW); c.rect(R(6750)-2*mm, H(0), R(7550)-R(6750)+4*mm, H(150), stroke=1, fill=1)
    c.setStrokeColor(BRASS); c.setLineWidth(1.4); c.line(R(6790), H(158), R(7510), H(158))
    c.setStrokeAlpha(0.35); c.setLineWidth(3.6); c.line(R(6790), H(170), R(7510), H(170)); c.setStrokeAlpha(1)
    # pendants — staggered drops
    for i, (px_, drop_bottom) in enumerate([(6990, 1650), (7150, 1775), (7310, 1900)]):
        top_y = H(2450); bot_y = H(drop_bottom)
        c.setStrokeColor(HexColor('#1A1712')); c.setLineWidth(0.9)
        c.line(R(px_), top_y, R(px_), bot_y + 9*mm)
        c.setFillColor(OAKD)
        bell = c.beginPath()
        bell.moveTo(R(px_)-4.6*mm, bot_y + 9*mm); bell.curveTo(R(px_)-5.4*mm, bot_y + 2.2*mm,
                                                              R(px_)-3.2*mm, bot_y,
                                                              R(px_), bot_y)
        bell.curveTo(R(px_)+3.2*mm, bot_y, R(px_)+5.4*mm, bot_y + 2.2*mm, R(px_)+4.6*mm, bot_y + 9*mm)
        bell.close(); c.drawPath(bell, stroke=1, fill=1)
        c.setFillColor(BRASS); c.circle(R(px_), top_y, 1.15*mm, stroke=0, fill=1)
        c.setFillColor(HexColor('#F5D9A0')); c.circle(R(px_), bot_y - 0.8*mm, 1.0*mm, stroke=0, fill=1)
    tag(c, R(7010), H(2280), 'A6', fill=PAPER, col=INK)

    # ---------- A7 end panel ----------
    oak_fill(c, R(7550), H(0), R(7650)-R(7550), H(2450)-H(0))

    # ---------- dimensions ----------
    segs = [(0,750,'750'),(750,1700,'950'),(1700,1850,'150'),(1850,6050,'4200'),(6050,6750,'700'),(6750,7550,'800'),(7550,7650,'100')]
    chain_y = H(2700) + 7.5*mm
    for a, b, l in segs:
        hdim(c, R(a), R(b), chain_y, H(2700), l, size=4.2, above=True)
    hdim(c, R(0), R(7650), chain_y + 9.5*mm, H(2700), '7650 — RUN LENGTH', size=4.8)
    vdim(c, H(0), H(2700), 11.5*mm, 14*mm, 'CLG +2700', size=4.5)
    vdim(c, H(0), H(920), 274.5*mm, R(7650), '+920', size=4.4, right=True)

    # ===== right column — module schedule =====
    rx = 306*mm; rw = 411.5*mm - rx
    micro(c, rx, 253*mm, 'MODULE SCHEDULE', color=INK, size=5.6, track=1.6)
    table_bottom = table(c, rx, 249*mm, [11*mm, 42*mm, 22*mm, rw-75*mm], [
        header_row(['CODE', 'MODULE', 'FINISH', 'REMARKS'], h=5.6*mm),
        (11*mm, [dict(t='A1', b=True, a='c'), 'Tall tower — micro + oven + warming drawer', 'MT-01 + MT-07', 'AP-01/02/03; doors venue-matched, 10 gaps']),
        (11*mm, [dict(t='A2', b=True, a='c'), 'Fridge surround + panel above', 'MT-01', 'AP-04 side-by-side; 25 gaps sides; grille above']),
        (11*mm, [dict(t='V1 V2', b=True, a='c'), 'Display vitrines ×2', 'MT-06 + MT-17', 'LED L-07; ceramics display; carcass 18']),
        (11*mm, [dict(t='BASE', b=True, a='c'), 'Base run — sink + DW zone', 'MT-03', 'D 560; AP-05, AP-08; channel pulls']),
        (11*mm, [dict(t='A5', b=True, a='c'), 'Coffee / compact oven tower', 'MT-01 + MT-07', 'AP-09 @ 1350–1950 (CL 1650)']),
        (11*mm, [dict(t='A6', b=True, a='c'), 'Pendant niche — 3 pendants', 'MT-01 + MT-13', 'L-05 staggered; L-06 plinth LED; step 150']),
        (11*mm, [dict(t='A7', b=True, a='c'), 'End panel — 20 thick', 'MT-01', 'Shadow gap MT-06 to wall']),
    ], default_size=4.9)
    ny = table_bottom - 5*mm
    micro(c, rx, ny, 'NOTES', color=INK, size=5.2, track=1.6)
    notes = [
        'Oak veneer MT-01 — vertical grain, matched pairs either side of appliances; book-match across doors.',
        'Shadow gaps 10 — black inserts, MT-06; no proud handles anywhere on this wall.',
        'Pelmet/scribe from 2450 to 2700 in MT-11 microcement; ceiling cut line shown dashed.',
        'Vitrines — black frame MT-06, glass MT-17; interiors black; LED warm 2700K.',
        'All modules & appliance cut-outs to be site-measured; appliance clearances per manufacturer.',
    ]
    c.setFillColor(INK)
    ny -= 5*mm
    for n in notes:
        for ln in wrap('•  ' + n, 'Helvetica', 5.0, rw):
            c.setFont('Helvetica', 5.0); c.drawString(rx, ny, ln); ny -= 2.85*mm
        ny -= 0.8*mm
    ref_image(c, A('scene_4.jpg'), rx, 33*mm, rw, min(ny - 8*mm, 58*mm),
              'MAIN WALL — ENSCAPE SCENE 4', caption_h=6.2*mm)
    c.showPage()

# ============================================================================
# K-03 — ELEVATIONS B (COFFEE BAR, WEST) & C (EAST TALL UNIT & NICHE)
# ============================================================================
def page_k03(c):
    frame_board(c, 'K-03', 'Elevations B & C — coffee bar · east tall unit & niche', '1:25 · 1:20')

    # ---------- LEFT HALF — ELEVATION B · COFFEE BAR (1:25) ----------
    micro(c, 12*mm, 248*mm, 'ELEVATION B — COFFEE BAR & PANTRY (WEST WALL) · 1:25', size=5.6, track=1.3)
    base_y = 120*mm
    def R(x): return 14*mm + x/25*mm          # rel mm -> paper x
    def H(h): return base_y + h/25*mm         # rel mm -> paper y

    hline(c, 10*mm, 200*mm, base_y, 1.6, INK)
    for xx in range(13, 199, 9):
        c.line(xx*mm, base_y, (xx-4)*mm, base_y - 3.0*mm)
    vline(c, 10*mm, H(0), H(2700), 0.5, LINE, dash=[4, 2])
    hline(c, 10*mm, 200*mm, H(2700), 0.9, TAUPE, dash=[3, 2])

    # C1 floating console 0–2250, fascia 520–900 + quartz top 900–920
    oak_fill(c, R(0), H(520), R(2250)-R(0), H(900)-H(520))
    c.setLineWidth(1.4); c.setStrokeColor(BLACK)
    c.line(R(0), H(660), R(2250), H(660))            # drawer reveal
    vline(c, R(1125), H(520), H(900), 0.7, HexColor('#8A6B3F'))
    groove_x = R(0), R(2250)
    quartz_fill(c, R(-40), H(900), R(2250)-R(0)+1.6*mm, 2.4*mm, vein=False)
    # backsplash 920–1400
    quartz_fill(c, R(0), H(920), R(2250)-R(0), H(1400)-H(920), vein=True)
    # black steel leg frame at south end + stretcher + shelf
    c.setStrokeColor(BLACK); c.setLineWidth(2.6)
    for lx in (R(25), R(180)):
        c.line(lx, H(0), lx, H(520))
    c.line(R(0), H(60), R(205), H(60))
    c.setLineWidth(1.5); c.line(R(0), H(300), R(205), H(300))
    # machines & styling silhouettes on the counter
    # espresso machine (stainless)
    c.setFillColor(HexColor('#B9B9BC')); c.rect(R(1180), H(920), R(1500)-R(1180), H(1335)-H(920), stroke=1, fill=1)
    c.setFillColor(BLACK); c.rect(R(1180), H(920), R(1500)-R(1180), 2.1*mm, stroke=0, fill=1)
    c.rect(R(1260), H(845), 3.6*mm, 2.6*mm, stroke=0, fill=1)   # group head
    c.setStrokeColor(BLACK); c.setLineWidth(1.6)
    c.line(R(1400), H(920), R(1525), H(845))                    # portafilter handle
    # capsule machine (white)
    c.setFillColor(PAPER); c.roundRect(R(380), H(920), R(680)-R(380), H(1235)-H(920), 2.2*mm, stroke=1, fill=1)
    c.setFillColor(BLACK); c.circle(R(475), H(1150), 0.9*mm, stroke=0, fill=1)
    c.setStrokeColor(BLACK); c.setLineWidth(1.2); c.line(R(640), H(1235), R(680), H(1305))
    # tray + canisters + stems vase
    c.setFillColor(OAKD); c.rect(R(760), H(920), R(1090)-R(760), 1.6*mm, stroke=0, fill=1)
    for i, (cx_, w_, h_) in enumerate([(800, 52, 190), (880, 40, 130), (950, 62, 220)]):
        c.setFillColor(HexColor('#D8CDBE')); c.rect(R(cx_), H(920+16), R(cx_+w_)-R(cx_), H(920+16+h_)-H(920+16), stroke=1, fill=1)
    c.setStrokeColor(HexColor('#5E6B54')); c.setLineWidth(0.7)
    for dx in (-14, 0, 12):
        c.line(R(1750)+dx, H(920), R(1750)+dx*2.2, H(1385))
    c.setFillColor(PAPER); c.roundRect(R(1715), H(920), 4.0*mm, 6.2*mm, 1.2*mm, stroke=1, fill=1)
    # C2 vitrines 0–2250, y 1450–2150 — 4 glass doors, black frames, lit
    doors = [(40, 520), (590, 1070), (1140, 1620), (1690, 2170)]
    rnd = random.Random(23)
    for i, (dx1, dx2) in enumerate(doors):
        vx, vw = R(dx1), R(dx2)-R(dx1); vy, vh = H(1450), H(2150)-H(1450)
        c.setFillColor(HexColor('#26241F')); c.rect(vx, vy, vw, vh, stroke=0, fill=1)
        c.setStrokeColor(INK); c.setLineWidth(2.2); c.rect(vx, vy, vw, vh, stroke=1, fill=0)
        c.setStrokeColor(HexColor('#57544F')); c.setLineWidth(0.8)
        for sy in (vy + vh*0.36, vy + vh*0.66):
            c.line(vx + 1.5*mm, sy, vx + vw - 1.5*mm, sy)
        for row_y in (vy + vh*0.09, vy + vh*0.42, vy + vh*0.72):
            xx = vx + 2.2*mm
            while xx < vx + vw - 3.6*mm:
                pw = 2.0*mm + rnd.random()*1.6*mm; ph = 2.6*mm + rnd.random()*2.0*mm
                c.setFillColor(HexColor('#8A8074') if rnd.random() > 0.45 else HexColor('#4A463F'))
                c.rect(xx, row_y, pw, ph, stroke=0, fill=1); xx += pw + 1.5*mm
        c.setStrokeColor(BRASS); c.setLineWidth(0.8)
        c.line(vx + 1.2*mm, vy + vh - 1.1*mm, vx + vw - 1.2*mm, vy + vh - 1.1*mm)
    tag(c, R(1015), H(2195), 'C2')
    # C3 tall pantry 2400–3700, y 0–2450
    oak_fill(c, R(2400), H(100), R(3700)-R(2400), H(2450)-H(100))
    c.setFillColor(HexColor('#101010')); c.rect(R(2400)+1.1*mm, H(0), R(3700)-R(2400)-2.2*mm, H(100)-H(0), stroke=0, fill=1)
    c.setStrokeColor(BLACK); c.setLineWidth(2.4); c.line(R(2400), H(850), R(3700), H(850))   # shadow gap / drawer
    for ry in (1560, 2150):
        hline(c, R(2400), R(3700), H(ry), 0.8, HexColor('#8A6B3F'))
    vline(c, R(3050), H(100), H(2450), 0.8, HexColor('#8A6B3F'))
    tag(c, R(2970), H(2270), 'C3')
    tag(c, R(1050), H(960) - 1*mm, 'C1')

    # dims
    hdim(c, R(0), R(2250), H(2700) + 6.2*mm, H(2700), '2250', size=4.4)
    hdim(c, R(2400), R(3700), H(2700) + 6.2*mm, H(2700), '1300', size=4.4)
    hdim(c, R(0), R(3700), H(2700) + 14.0*mm, H(2700), 'WEST WALL RUN 3700', size=4.8)
    vdim(c, H(0), H(900), 12.3*mm, 14*mm, '+900', size=4.3)

    # module lines under drawing
    ly = 96*mm
    mods = [
        ('C1', 'Floating console — MT-01, L 2250 × D 540, quartz top + backsplash slab'),
        ('C2', 'Glass vitrines ×4 — black frame MT-06, glass MT-17, LED L-08, L 512 each'),
        ('C3', 'Tall pantry — MT-01, L 1300, full height 2450; shadow gap at +850'),
        ('SPL', 'Backsplash — MT-04 quartz, full width, 920–1400'),
    ]
    for code, desc in mods:
        tag(c, 12*mm, ly - 1.2*mm, code, fill=PANEL, col=INK, size=4.4, h=3.9*mm)
        for ln in wrap(desc, 'Helvetica', 4.8, 72*mm):
            c.setFillColor(INK); c.setFont('Helvetica', 4.8)
            c.drawString(22*mm, ly, ln); ly -= 2.75*mm
        ly -= 0.9*mm
    ref_image(c, A('scene_14.jpg'), 118*mm, 33*mm, 88*mm, 62*mm,
              'COFFEE BAR — ENSCAPE SCENE 14', caption_h=5.6*mm)

    # divider
    vline(c, 207*mm, 33*mm, 260*mm, 1.0, LINE)

    # ---------- RIGHT HALF — ELEVATION C · EAST TALL UNIT & NICHE (1:20) ----------
    micro(c, 214*mm, 255*mm, 'ELEVATION C — EAST TALL UNIT & NICHE · 1:20', size=5.6, track=1.3)
    base_y2 = 110*mm
    def R2(x): return 214*mm + x/20*mm
    def H2(h): return base_y2 + h/20*mm

    hline(c, 212*mm, 340*mm, base_y2, 1.5, INK)
    vline(c, 214*mm, H2(0), H2(2700), 0.5, LINE, dash=[4, 2])
    hline(c, 212*mm, 340*mm, H2(2700), 0.9, TAUPE, dash=[3, 2])

    # A5 tower 0–700
    oak_fill(c, R2(0), H2(100), R2(700)-R2(0), H2(2450)-H2(100))
    c.setFillColor(HexColor('#101010')); c.rect(R2(0)+1.0*mm, H2(0), R2(700)-R2(0)-2.0*mm, H2(100)-H2(0), stroke=0, fill=1)
    appliance_fill(c, R2(48), H2(1350), R2(700)-R2(96), H2(1950)-H2(1350))
    c.setStrokeColor(HexColor('#FFFFFF')); c.setStrokeAlpha(0.22); c.setLineWidth(0.6)
    c.line(R2(90), H2(1640), R2(610), H2(1640)); c.setStrokeAlpha(1)
    groove2 = lambda x1, x2, h, lw=1.6: (c.setStrokeColor(BLACK), c.setLineWidth(lw),
                                          c.line(R2(x1), H2(h), R2(x2), H2(h)))
    groove2(0, 700, 1350); groove2(0, 700, 1950); groove2(0, 700, 2300)
    vline(c, (R2(0)+R2(700))/2, H2(100), H2(1350), 0.6, HexColor('#8A6B3F'))
    vline(c, (R2(0)+R2(700))/2, H2(1950), H2(2450), 0.6, HexColor('#8A6B3F'))
    tag(c, R2(255), H2(2230), 'A5')

    # A6 niche 700–1500
    oak_fill(c, R2(700), H2(0), R2(1500)-R2(700), H2(2450)-H2(0))
    c.setFillColor(HexColor('#3B342B'))
    c.rect(R2(740), H2(160), R2(1460)-R2(740), H2(2450)-H2(160), stroke=0, fill=1)
    c.setFillColor(OAKW); c.rect(R2(700)-2.2*mm, H2(0), R2(1500)-R2(700)+4.4*mm, H2(160), stroke=1, fill=1)
    c.setStrokeColor(BRASS); c.setLineWidth(1.4); c.line(R2(740), H2(168), R2(1460), H2(168))
    c.setStrokeAlpha(0.35); c.setLineWidth(3.4); c.line(R2(740), H2(180), R2(1460), H2(180)); c.setStrokeAlpha(1)
    # pendants — staggered drops (bottoms +1660 / +1775 / +1890 AFF)
    for px_, drop_bottom in [(845, 1660), (1065, 1775), (1285, 1890)]:
        top_y, bot_y = H2(2450), H2(drop_bottom)
        c.setStrokeColor(HexColor('#1A1712')); c.setLineWidth(0.8)
        c.line(R2(px_), top_y, R2(px_), bot_y + 7.2*mm)
        c.setFillColor(OAKD)
        bell = c.beginPath()
        bell.moveTo(R2(px_)-3.7*mm, bot_y + 7.2*mm)
        bell.curveTo(R2(px_)-4.4*mm, bot_y + 1.8*mm, R2(px_)-2.6*mm, bot_y, R2(px_), bot_y)
        bell.curveTo(R2(px_)+2.6*mm, bot_y, R2(px_)+4.4*mm, bot_y + 1.8*mm, R2(px_)+3.7*mm, bot_y + 7.2*mm)
        bell.close(); c.drawPath(bell, stroke=1, fill=1)
        c.setFillColor(BRASS); c.circle(R2(px_), top_y, 1.0*mm, stroke=0, fill=1)
        c.setFillColor(HexColor('#F5D9A0')); c.circle(R2(px_), bot_y - 0.7*mm, 0.85*mm, stroke=0, fill=1)
    tag(c, R2(1000), H2(2280), 'A6', fill=PAPER, col=INK)

    # end panel 1500–1700
    oak_fill(c, R2(1500), H2(0), R2(1700)-R2(1500), H2(2450)-H2(0))

    # dims
    hdim(c, R2(0), R2(700), H2(2700) + 2.4*mm, H2(2700), '700', size=4.3)
    hdim(c, R2(700), R2(1500), H2(2700) + 2.4*mm, H2(2700), '800', size=4.3)
    hdim(c, R2(1500), R2(1700), H2(2700) + 2.4*mm, H2(2700), '200', size=4.3)
    vdim(c, H2(0), H2(2450), 208*mm, 214*mm, '+2450', size=4.3)
    # appliance CL leader
    c.setStrokeColor(TAUPE); c.setLineWidth(0.7)
    c.line(R2(700)+2*mm, H2(1650), R2(700)+14*mm, H2(1650))
    micro(c, R2(700)+15*mm, H2(1650)+0.6*mm, 'AP-09 CL 1650', size=3.8, track=0.4)

    # right column — notes + ref image
    nx_ = 330*mm
    micro(c, nx_, 232*mm, 'NICHE & TOWER', color=INK, size=5.2, track=1.5)
    ny = 226*mm
    notes = [
        'A5 — AP-09 built-in appliance @ 1350–1950; doors MT-01 above & below',
        'A6 — open niche: 3× woven pendant (L-05), bottoms @ +1660 / +1775 / +1890 AFF',
        'Plinth step 160 — LED L-06 recessed behind lip, warm 2700K',
        'Back panel — MT-01 oak, grain vertical; end panel 200 scribes to wall',
        'Pendant drivers accessible inside A5 pelmet (230 V isolation)',
    ]
    for n in notes:
        for ln in wrap('•  ' + n, 'Helvetica', 4.6, 76*mm):
            c.setFillColor(INK); c.setFont('Helvetica', 4.6); c.drawString(nx_, ny, ln); ny -= 2.6*mm
        ny -= 0.7*mm
    ref_image(c, A('scene_1_130238.jpg'), nx_, 33*mm, 78*mm, 58*mm,
              'EAST NICHE — SCENE 1', caption_h=5.6*mm)
    c.showPage()

# ============================================================================
# K-04 — ISLAND (1:15) + DETAILS (1:10 / 1:20)
# ============================================================================
def page_k04(c):
    frame_board(c, 'K-04', 'Island — cook & seating elevations · details', '1:15 · 1:10 · 1:20')

    # ---------- ELEVATION D — COOK SIDE (NORTH) · 1:15 ----------
    micro(c, 12*mm, 248*mm, 'ELEVATION D — COOK SIDE (NORTH) · 1:15', size=5.6, track=1.3)
    base_y = 168*mm
    def R(x): return 12*mm + x/15*mm
    def H(h): return base_y + h/15*mm

    hline(c, 10*mm, 240*mm, base_y, 1.5, INK)
    for xx in range(13, 239, 9):
        c.line(xx*mm, base_y, (xx-4)*mm, base_y - 2.8*mm)
    # waterfall end panels (quartz) full height
    quartz_fill(c, R(0), H(0), 2.6*mm, H(920)-H(0), vein=False)
    quartz_fill(c, R(3300)-2.6*mm, H(0), 2.6*mm, H(920)-H(0), vein=False)
    # plinth (recessed)
    c.setFillColor(HexColor('#101010')); c.rect(R(0)+2.6*mm+1.0*mm, H(0), R(3300)-R(0)-2*2.6*mm-2.0*mm, H(80)-H(0), stroke=0, fill=1)
    # cabinets — warm off-white, drawer stacks
    c.setFillColor(CREAM); c.rect(R(0)+2.6*mm, H(80), R(3300)-R(0)-2*2.6*mm, H(900)-H(80), stroke=0, fill=1)
    for dx in (1100, 2200):
        vline(c, R(dx), H(80), H(900), 0.6, HexColor('#B9B2A4'))
    for gy in (400, 640):
        c.setStrokeColor(BLACK); c.setLineWidth(1.7); c.line(R(0)+2.6*mm, H(gy), R(3300)-2.6*mm, H(gy))
    # worktop
    quartz_fill(c, R(0), H(900), R(3300), 2.6*mm, vein=False)
    # flush hob mark on top edge
    c.setStrokeColor(BLACK); c.setLineWidth(2.6)
    c.line(R(1150), H(920)+0.9*mm, R(2150), H(920)+0.9*mm)
    label_ink(c, R(1280), H(920) + 4.6*mm, 'AP-06 — FLUSH GAS HOB, 4 BURNERS', size=4.3)
    tag(c, R(1520), H(520) - 2*mm, 'I3')
    tag(c, R(260), H(200), 'I1', fill=INK, col=PAPER)
    tag(c, R(2500), H(200), 'I1', fill=INK, col=PAPER)
    # dims
    hdim(c, R(0), R(3300), H(920) + 11*mm, H(920), '3300 — ISLAND', size=4.6)
    vdim(c, H(0), H(920), 8.2*mm, 12*mm, '+920', size=4.3)
    hdim(c, R(1150), R(2150), H(920) + 18*mm, H(920) + 0*mm, '1000 HOB ZONE', size=4.0)

    # ---------- ELEVATION E — SEATING SIDE (SOUTH) · 1:15 ----------
    micro(c, 12*mm, 128*mm, 'ELEVATION E — SEATING SIDE (SOUTH) · 1:15', size=5.6, track=1.3)
    base_y2 = 62*mm
    def H2(h): return base_y2 + h/15*mm

    hline(c, 10*mm, 240*mm, base_y2, 1.5, INK)
    for xx in range(13, 239, 9):
        c.line(xx*mm, base_y2, (xx-4)*mm, base_y2 - 2.4*mm)
    # waterfall end panels
    quartz_fill(c, R(0), H2(0), 2.6*mm, H2(920)-H2(0), vein=False)
    quartz_fill(c, R(3300)-2.6*mm, H2(0), 2.6*mm, H2(920)-H2(0), vein=False)
    # plinth
    c.setFillColor(HexColor('#101010')); c.rect(R(0)+2.6*mm+1.0*mm, H2(0), R(3300)-R(0)-2*2.6*mm-2.0*mm, H2(80)-H2(0), stroke=0, fill=1)
    # end drawer banks — cashmere, 2 deep drawers each (banks 800 each)
    for bx1, bx2 in ((0, 800), (2500, 3300)):
        c.setFillColor(CASH); c.rect(R(bx1)+(2.6*mm if bx1 == 0 else 0), H2(80),
                                     (R(bx2)-R(bx1)) - (2.6*mm if bx1 == 0 else 2.6*mm), H2(900)-H2(80), stroke=0, fill=1)
        c.setStrokeColor(BLACK); c.setLineWidth(1.7)
        x_a = R(bx1)+(2.6*mm if bx1 == 0 else 0); x_b = R(bx2)-(0 if bx1 == 0 else 2.6*mm)
        c.line(x_a, H2(470), x_b, H2(470))
    # knee recess — oak back panel, open to underside of worktop
    oak_fill(c, R(800), H2(80), R(2500)-R(800), H2(900)-H2(80))
    c.setFillColor(HexColor('#241F18')); c.rect(R(800)+1.6*mm, H2(80)+1.6*mm, R(2500)-R(800)-3.2*mm, H2(900)-H2(80)-1.6*mm, stroke=0, fill=1)
    oak_fill(c, R(800)+1.6*mm, H2(80)+1.6*mm, R(2500)-R(800)-3.2*mm, H2(900)-H2(80)-3.2*mm)
    # worktop — 300 overhang beyond recess face
    quartz_fill(c, R(0), H2(900), R(3300), 2.6*mm, vein=True)
    tag(c, R(320), H2(220), 'I4'); tag(c, R(2690), H2(220), 'I4')
    tag(c, R(1570), H2(120), 'I2')
    hdim(c, R(0), R(3300), base_y2 - 5.5*mm, base_y2, '3300 — ISLAND', size=4.6, above=False)
    hdim(c, R(800), R(2500), base_y2 - 11.5*mm, base_y2, '1700 KNEE', size=4.0, above=False)

    # ---------- RIGHT COLUMN — DETAILS ----------
    rx = 262*mm
    # DET 1 — waterfall mitre (1:10)
    micro(c, rx, 248*mm, 'DETAIL 1 — WATERFALL MITRE · SCALE 1:10', size=5.2, track=1.4)
    box = (rx, 156*mm, 148*mm, 84*mm)   # x, y, w, h
    bx, by, bw, bh = box
    c.setFillColor(PAPER); c.rect(bx, by, bw, bh, stroke=1, fill=1)
    # drawing: top slab + side slab, 45 deg mitre at outer corner (top-right)
    tx, ty = bx + 8*mm, by + bh - 14*mm        # top slab left edge, vertical center of slab
    slab = 7.2*mm                               # exaggerated 20mm stone
    # top slab
    quartz_fill(c, tx, ty - slab, bw - 34*mm, slab, vein=True)
    # side slab below (waterfall)
    quartz_fill(c, tx + bw - 34*mm - slab, ty - slab - 42*mm, slab, 42*mm + slab, vein=False)
    # mitre joint line 45
    c.setStrokeColor(INK); c.setLineWidth(0.9)
    c.line(tx + bw - 34*mm, ty, tx + bw - 34*mm - slab, ty - slab)
    # carcass behind
    c.setFillColor(PANELA); c.rect(tx, ty - slab - 12*mm, bw - 34*mm - slab, 12*mm, stroke=1, fill=1)
    # bracket
    c.setFillColor(INK)
    p = c.beginPath()
    p.moveTo(tx + bw - 40*mm, ty - slab); p.lineTo(tx + bw - 52*mm, ty - slab - 12*mm); p.lineTo(tx + bw - 40*mm, ty - slab - 12*mm); p.close()
    c.drawPath(p, stroke=0, fill=1)
    # leaders + labels
    lx = tx + bw - 12*mm
    micro(c, lx - 6*mm, ty - 2.4*mm, '20', size=4.4, track=0.2)
    micro(c, lx - 6*mm, ty - slab - 2.6*mm, '20', size=4.4, track=0.2)
    c.setFont('Helvetica', 4.0); c.setFillColor(INK)
    c.drawString(lx - 6*mm, ty - slab - 6.6*mm, 'MT-04')
    c.drawString(tx, ty - slab - 20*mm, '45° MITRE')
    c.drawString(tx, ty - slab - 25.5*mm, 'SHADOW GAP 10')
    c.drawString(tx, ty - slab - 31*mm, '18mm CARCASS')
    # vertical connector notes left
    c.drawString(bx + 4*mm, by + 4*mm, 'WATERFALL END — 45° MITRE, CONTINUOUS VEIN')

    # DET 2 — hood & cove section (1:20)
    micro(c, rx, 146*mm, 'DETAIL 2 — HOOD & COVE SECTION · SCALE 1:20', size=5.2, track=1.4)
    bx, by, bw, bh = rx, 34*mm, 148*mm, 104*mm
    c.setFillColor(PAPER); c.rect(bx, by, bw, bh, stroke=1, fill=1)
    # ceiling cut (top) + dropped cove soffit with GREIGE band
    ceil_y = by + bh - 6*mm
    soffit_y = ceil_y - 9*mm
    c.setFillColor(GREIGE); c.rect(bx + 4*mm, soffit_y, bw - 8*mm, ceil_y - soffit_y, stroke=0, fill=1)
    hline(c, bx + 4*mm, bx + bw - 4*mm, ceil_y, 1.4, INK)
    micro(c, bx + 5*mm, ceil_y + 1.3*mm, 'CLG +2700', size=3.6, track=0.4)
    # cove recess — inner drop with LED lines
    inset = 16*mm
    c.setFillColor(PAPER); c.rect(bx + inset, soffit_y - 5*mm, bw - 2*inset, 5*mm, stroke=0, fill=1)
    for yy in (soffit_y + 1.6*mm, soffit_y - 2.9*mm):
        c.setStrokeColor(BRASS); c.setLineWidth(1.5); c.line(bx + inset + 1*mm, yy, bx + bw - inset - 1*mm, yy)
        c.setStrokeAlpha(0.3); c.setLineWidth(4.2); c.line(bx + inset + 1*mm, yy, bx + bw - inset - 1*mm, yy); c.setStrokeAlpha(1)
    # hood box (black) + chimney to soffit
    hood_w = 34*mm; hood_x = bx + bw/2 - hood_w/2
    hood_y0, hood_y1 = by + 52*mm, by + 66*mm
    c.setFillColor(BLACK); c.rect(hood_x, hood_y0, hood_w, hood_y1 - hood_y0, stroke=1, fill=1)
    c.rect(hood_x + hood_w/2 - 5*mm, hood_y1, 10*mm, soffit_y - 5*mm - hood_y1, stroke=1, fill=1)
    # counter + hob reference (below)
    ct_y = by + 12*mm
    quartz_fill(c, bx + 10*mm, ct_y, bw - 20*mm, 2.4*mm, vein=False)
    c.setStrokeColor(BLACK); c.setLineWidth(1.8)
    c.line(bx + bw/2 - 9*mm, ct_y + 3.2*mm, bx + bw/2 + 9*mm, ct_y + 3.2*mm)
    # clearance arrow hood <-> hob
    cx0 = bx + bw - 14*mm
    c.setStrokeColor(INK); c.setLineWidth(0.8)
    c.line(cx0, ct_y + 4*mm, cx0, hood_y0)
    p = c.beginPath(); p.moveTo(cx0 - 1.4*mm, ct_y + 8.4*mm); p.lineTo(cx0, ct_y + 4*mm); p.lineTo(cx0 + 1.4*mm, ct_y + 8.4*mm); p.close()
    c.drawPath(p, stroke=0, fill=1)
    p = c.beginPath(); p.moveTo(cx0 - 1.4*mm, hood_y0 - 4.4*mm); p.lineTo(cx0, hood_y0); p.lineTo(cx0 + 1.4*mm, hood_y0 - 4.4*mm); p.close()
    c.drawPath(p, stroke=0, fill=1)
    micro(c, cx0 + 1.6*mm, (ct_y + hood_y0)/2, '700', size=4.0, track=0.2)
    # labels
    lx = bx + 4*mm
    c.setFont('Helvetica-Bold', 4.6); c.setFillColor(INK)
    c.drawString(lx, by + 38*mm, 'AP-07 — 900 CEILING BOX HOOD')
    c.setFont('Helvetica', 4.2)
    c.drawString(lx, by + 32.8*mm, 'Mount to cove framing — 4× M10; duct Ø150 via soffit (SP-06)')
    c.drawString(lx, by + 27.6*mm, 'LED L-01 both returns of cove A; hood LED integral')
    c.drawString(lx, by + 22.4*mm, 'If no duct route: recirculating kit, carbon filters, replace 12 mths')
    c.showPage()

# ============================================================================
# K-05 — REFLECTED CEILING PLAN (1:50)
# ============================================================================
def page_k05(c):
    frame_board(c, 'K-05', 'Reflected ceiling plan — coves · downlights · pendants', '1:50')
    micro(c, 12*mm, 253*mm, 'RCP — COVES & LIGHTING LAYOUT @ 1:50', size=6.0, track=1.6)

    k = 1/50
    px0, py0 = 22*mm, 84*mm
    def X(x): return px0 + x*mm*k
    def Y(y): return py0 + y*mm*k

    # room outline (hairline)
    c.setStrokeColor(INK); c.setLineWidth(1.2)
    c.rect(X(0), Y(0), 9600*mm*k, 6300*mm*k, stroke=1, fill=0)
    # walls (thin) + glazing indication
    c.setLineWidth(2.2)
    c.line(X(0), Y(6060), X(9600), Y(6060))
    c.line(X(0), Y(0), X(0), Y(6300)); c.line(X(9600), Y(0), X(9600), Y(6300))
    # glazing tags
    for gx, gy, gl in [(325, 6300, 'F1'), (375, 3900, 'F2'), (9600, 5300, 'F3')]:
        c.setFillColor(INK); c.circle(X(gx), Y(gy), 1.7*mm, stroke=0, fill=1)
        micro(c, X(gx) + 2.4*mm, Y(gy) + 0.4*mm, gl, size=4.0, track=0.3)
    # island + table outlines (dashed)
    c.setStrokeColor(TAUPE); c.setLineWidth(0.8); c.setDash([2.2, 1.8], 0)
    c.rect(X(3300), Y(3300), 3300*mm*k, 1150*mm*k, stroke=1, fill=0)
    c.roundRect(X(650), Y(3300), 1900*mm*k, 950*mm*k, 4*mm, stroke=1, fill=0)
    c.setDash([], 0)
    vline(c, X(4950), Y(3050), Y(6050), 0.5, TAUPE, dash=[5, 1.5, 1, 1.5])

    # cove A — island (double concentric rectangle), centred (4950, 3875)
    def cove(cx, cy, w, d, label):
        for (ww, dd, lw) in ((w, d, 1.5), (w*0.66, d*0.62, 1.2)):
            c.setStrokeColor(BRASS); c.setLineWidth(lw + 2.6); c.setStrokeAlpha(0.28)
            c.rect(X(cx-ww/2), Y(cy-dd/2), ww*mm*k, dd*mm*k, stroke=1, fill=0)
            c.setStrokeAlpha(1); c.setLineWidth(lw)
            c.rect(X(cx-ww/2), Y(cy-dd/2), ww*mm*k, dd*mm*k, stroke=1, fill=0)
        c.setFillColor(BRASS); c.setFont('Helvetica-Bold', 5.2)
        c.drawString(X(cx - w/2) + 2*mm, Y(cy + d/2) - 4.6*mm, label)
    cove(4950, 3875, 4800, 2100, 'COVE A — L-01')
    # cove B — dining, centred (1650, 3775)
    cove(1650, 3775, 3000, 1800, 'COVE B — L-02')

    # downlights (DL-01..10)
    def dl(x, y, no):
        c.setFillColor(INK); c.circle(X(x), Y(y), 1.15*mm, stroke=0, fill=1)
        c.setFillColor(PAPER); c.circle(X(x), Y(y), 0.42*mm, stroke=0, fill=1)
        micro(c, X(x) + 1.6*mm, Y(y) - 0.9*mm, no, size=3.3, track=0.1)
    for x, y, no in [(3200, 5300, 'DL-01'), (4300, 5300, 'DL-02'), (5400, 5300, 'DL-03'), (6500, 5300, 'DL-04'),
                     (3000, 1500, 'DL-05'), (6500, 1500, 'DL-06'), (1500, 2800, 'DL-07'), (7500, 2500, 'DL-08'),
                     (480, 900, 'DL-09'), (480, 2100, 'DL-10')]:
        dl(x, y, no)
    # island task DLs inside cove A inner corners
    for x, y, no in [(3950, 3400, 'DL-I1'), (5950, 3400, 'DL-I2'), (3950, 4350, 'DL-I3'), (5950, 4350, 'DL-I4')]:
        c.setFillColor(BRASS); c.circle(X(x), Y(y), 1.15*mm, stroke=0, fill=1)
        micro(c, X(x) + 1.6*mm, Y(y) - 0.9*mm, no, size=3.3, track=0.1)

    # pendants (niche) + plinth LED
    for px in (7950, 8150, 8350):
        c.setFillColor(OAKD); c.circle(X(px), Y(5720), 1.7*mm, stroke=1, fill=1)
    micro(c, X(7950) - 3*mm, Y(5720) + 3.0*mm, 'L-05', size=3.6, track=0.3)
    hline(c, X(7740), X(8460), Y(5485), 1.4, BRASS)

    # sink bulkhead linear LED (L-09) above window
    hline(c, X(3250), X(5750), Y(5560), 2.0, BRASS)
    micro(c, X(4250), Y(5430), 'L-09', size=3.6, track=0.3)

    # hood mount plate on cove A centre
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.setDash([1.6, 1.3], 0)
    c.rect(X(4950-200), Y(3875-200), 400*mm*k, 400*mm*k, stroke=1, fill=0); c.setDash([], 0)
    micro(c, X(4950) + 4*mm, Y(3875) + 2.5*mm, 'HOOD MNT PLATE — AP-07', size=3.4, track=0.2)

    # north arrow + scale bar
    nx, ny = 202*mm, 237*mm
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.circle(nx, ny, 5.2*mm, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(nx, ny - 3.4*mm); p.lineTo(nx + 1.6*mm, ny + 0.5*mm); p.lineTo(nx, ny + 3.6*mm); p.lineTo(nx - 1.6*mm, ny + 0.5*mm); p.close()
    c.setFillColor(INK); c.drawPath(p, stroke=0, fill=1)
    c.setFont('Helvetica-Bold', 7.2); c.drawCentredString(nx, ny - 9.2*mm, 'N')
    sb_x, sb_y = 22*mm, 52*mm
    for i in range(4):
        c.setFillColor(INK if i % 2 == 0 else PAPER)
        c.rect(sb_x + i*10*mm, sb_y, 10*mm, 2.4*mm, stroke=1, fill=1)
    for i, l in enumerate(['0', '500', '1000', '1500', '2000']):
        micro(c, sb_x + i*10*mm - 1.6*mm, sb_y - 4.2*mm, l, size=3.6, track=0.3)
    micro(c, sb_x, sb_y + 4.6*mm, 'SCALE 1:50 (mm)', size=4.2, track=1.2)

    # ===== right-hand column =====
    rx = 262*mm; rw = 411.5*mm - rx
    y = 253*mm
    micro(c, rx, y, 'LIGHTING LAYOUT NOTES', color=INK, size=5.6, track=1.6); y -= 5.4*mm
    notes = [
        'Cove A (island) — two concentric recessed coves, continuous LED L-01, dimmable; hood mount plate centred on island CL.',
        'Cove B (dining) — two concentric coves, LED L-02, dimmable; dining table centred beneath.',
        'DL-01…04 — task lights in back-run soffit, aligned to worktop edges (300 max spacing).',
        'DL-05…10 — general ambient, even spread, no downlight directly above seating positions.',
        'DL-I1…I4 — island task spots inside cove A, 60 deg beam, on separate scene.',
        'L-05 pendants in niche — staggered drops; see K-03 Elevation C for drop heights (+1660 / +1775 / +1890).',
        'L-06 plinth LED + L-07/L-08 vitrine LEDs — one switched circuit, on with scene EVENING.',
        'L-09 — linear bulkhead light above sink window, glare-controlled, own switch.',
        'All LED 3000K, CRI min 92 (kitchen) / 90 (general), 24 V constant-voltage.',
        'Drivers located in cove A void — access via two removable cove panels; 230 V isolation.',
    ]
    for n in notes:
        for ln in wrap('•  ' + n, 'Helvetica', 5.0, rw):
            c.setFillColor(INK); c.setFont('Helvetica', 5.0); c.drawString(rx, y, ln); y -= 2.75*mm
        y -= 0.8*mm
    y -= 3.5*mm
    micro(c, rx, y, 'RCP SYMBOLS', color=INK, size=5.6, track=1.6); y -= 4.6*mm
    sym_y = y
    # symbol samples
    sy = sym_y
    c.setStrokeColor(BRASS); c.setLineWidth(1.5); c.line(rx, sy + 1.2*mm, rx + 10*mm, sy + 1.2*mm)
    micro(c, rx + 13*mm, sy, 'COVE LED — RECESSED, CONTINUOUS', size=4.3, track=0.4); sy -= 6.4*mm
    c.setFillColor(INK); c.circle(rx + 5*mm, sy + 1.6*mm, 1.15*mm, stroke=0, fill=1)
    micro(c, rx + 13*mm, sy, 'DOWNLIGHT — 80mm RECESSED', size=4.3, track=0.4); sy -= 6.4*mm
    c.setFillColor(OAKD); c.circle(rx + 5*mm, sy + 1.6*mm, 1.7*mm, stroke=1, fill=1)
    micro(c, rx + 13*mm, sy, 'PENDANT — WOVEN SHADE, E27', size=4.3, track=0.4); sy -= 6.4*mm
    c.setStrokeColor(INK); c.setLineWidth(1.0); c.setDash([1.6, 1.3], 0)
    c.rect(rx + 2.2*mm, sy + 0.4*mm, 5.6*mm, 2.6*mm, stroke=1, fill=0); c.setDash([], 0)
    micro(c, rx + 13*mm, sy, 'HOOD MOUNTING PLATE', size=4.3, track=0.4); sy -= 6.4*mm
    c.setStrokeColor(BRASS); c.setLineWidth(2.0); c.line(rx, sy + 1.2*mm, rx + 10*mm, sy + 1.2*mm)
    micro(c, rx + 13*mm, sy, 'LINEAR STRIP — SURFACE/RECESSED', size=4.3, track=0.4)
    y = sy - 8*mm
    ref_image(c, A('scene_12.jpg'), rx, 33*mm, rw, min(y - 35*mm, 46*mm),
              'DINING COVE — ENSCAPE SCENE 12', caption_h=6.0*mm)
    c.showPage()

# ============================================================================
# K-06 — MATERIALS & FINISHES SCHEDULE (NTS)
# ============================================================================
def page_k06(c):
    frame_board(c, 'K-06', 'Materials & finishes schedule', 'NTS')
    micro(c, 12*mm, 253*mm, 'MATERIALS & FINISHES — CODE MT-xx', size=6.0, track=1.6)

    rows = [
        ('MT-01', '#E3CDA4', 'Oak veneer, rift-sawn, vertical grain, matt — book-matched pairs either side of appliances; FSC-certified', 'Tall units A1/A2/A5/A6/A7, column E1, coffee console C1, pantry C3, niche backs', 'Sheen max 10%; veneer sealed natural; no visible joints within a door'),
        ('MT-02', '#CFC4B6', 'Cashmere matt lacquer, warm beige', 'Island seating-side drawer banks I4', 'Hand-sanded matt; RAL ~1000 greige family; touch-up kit to client'),
        ('MT-03', '#EDEAE3', 'Warm off-white matt lacquer', 'Back-run base cabinets; island cook-side banks I1/I3', 'Sheen max 10%; anti-fingerprint; colour to be approved against sample'),
        ('MT-04', '#F6F4EF', 'Engineered quartz, white with soft grey-gold veining, 20 mm, honed', 'Worktops, island waterfall ends + top, upstand/splashback, table top FE-01', '45 deg mitre waterfalls; factory cut-outs; joints colour-matched on site'),
        ('MT-05', '#ECE8DE', 'Quartz skirting, 120 high, same batch as MT-04', 'Column E1 and all walls at floor line', 'Mitred corners; adhesive bed full'),
        ('MT-06', '#242220', 'Black matt aluminium, anodised', 'Recessed channel pulls, shadow-gap inserts (10), sockets, tap body, R-frame profiles', 'Anodised, not painted; PVD black for tap (MT-14 pairing)'),
        ('MT-07', '#1B1A17', 'Black glass / black stainless', 'AP-01, AP-02, AP-03, AP-06, AP-07, AP-09 appliances', 'Per manufacturer; fingerprint-resistant preferred'),
        ('MT-08', '#B9B9BC', 'Stainless steel, brushed No.4', 'AP-05 dishwasher front; AP-11 espresso machine', 'Grain direction consistent vertical'),
        ('MT-09', '#D8D5CF', 'Porcelain 900 × 900, light warm grey, honed, rectified', 'Floor throughout kitchen + dining', 'Straight lay centred on island CL; grout joints max 2 mm; matching quartz skirting'),
        ('MT-10', '#8F6B3F', 'Oak venetian blinds, 50 mm slats, oiled', 'F1 sink window, F3 east window', 'Matching oiled oak; black wand control; slats aligned when raised'),
        ('MT-11', '#DAD2C2', 'Microcement, warm greige', 'Feature soffit above back wall (2450–2700), fireplace-style pier faces', 'Seamless, sealed matt; sample panel on site before application'),
        ('MT-12', '#FCFBF8', 'Warm white matt emulsion', 'All remaining walls and ceiling', 'VOC max 10 g/L; sheen 5%; two coats over plaster'),
        ('MT-13', '#A98548', 'Brushed brass', 'Stool ferrules, chair tips, pendant caps, cove LED trims, drawer inlay line', 'Clear-lacquered to limit tarnishing; do not use abrasive cleaners'),
        ('MT-14', '#2A2A28', 'Black composite / PVD black', 'Sink AP-08; tap body finish', 'SILGRANIT-type; matte; scratch-resistant'),
        ('MT-15', '#B07B4A', 'Cognac / camel leather (shell) + grey woven fabric (seat pad)', 'Dining chairs FE-02', 'Leather aniline; fabric rub count min 40k Martindale'),
        ('MT-16', '#C9C3B8', 'Grey boucle upholstery', 'Bar stools FE-03', 'Rub count min 40k Martindale; removable covers'),
        ('MT-17', '#3E3E3B', 'Clear toughened glass 4 mm + black frame', 'Vitrines V1, V2, coffee bar C2', 'Toughened; low-iron; interior black; LED-ready'),
    ]
    table_rows = [header_row(['CODE', 'SAMPLE', 'DESCRIPTION', 'LOCATION', 'REMARKS'], h=6.0*mm)]
    for code, hexc, desc, loc, rem in rows:
        table_rows.append((7.35*mm, [dict(t=code, b=True, a='c', size=5.4),
                                      dict(t='', fill=HexColor(hexc)),
                                      dict(t=desc, size=4.35),
                                      dict(t=loc, size=4.35),
                                      dict(t=rem, size=4.35)]))
    table(c, 12*mm, 246*mm, [15*mm, 20*mm, 128*mm, 108*mm, 128.5*mm], table_rows, pad=1.6*mm)

    ny = 246*mm - 6.0*mm - 17*7.35*mm - 6*mm
    micro(c, 12*mm, ny, 'APPROVAL OF SAMPLES', color=INK, size=5.2, track=1.6)
    c.setFillColor(INK); c.setFont('Helvetica', 5.2)
    for ln in wrap('Client to approve physical samples of MT-01 (veneer), MT-02/03 (lacquers), MT-04 (quartz), MT-09 (floor) before any order is placed. Lead times: veneer panels 4–6 weeks, quartz 2–3 weeks, bespoke joinery 6–8 weeks after approval. All adhesives, sealers and paints low-VOC.', 'Helvetica', 5.2, 399.5*mm):
        c.drawString(12*mm, ny - 4.6*mm, ln); ny -= 3.1*mm
    # sign-off cells
    cells = ['VENEER MT-01 / MT-02 / MT-03', 'QUARTZ MT-04 / SKIRTING MT-05', 'FLOOR MT-09 / BLINDS MT-10']
    cw = 399.5*mm / 3
    for i, cell in enumerate(cells):
        x = 12*mm + i*cw
        c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(0.9)
        c.rect(x + 1.5*mm, 33.5*mm, cw - 3*mm, 11*mm, stroke=1, fill=1)
        micro(c, x + 4*mm, 33.5*mm + 6.6*mm, cell, size=4.2, track=0.6)
        label_ink(c, x + 4*mm, 33.5*mm + 2.2*mm, 'SIGN / DATE  ______________________', size=5.2)
    c.showPage()

# ============================================================================
# K-07 — APPLIANCE SCHEDULE & SERVICES POINTS (NTS)
# ============================================================================
def page_k07(c):
    frame_board(c, 'K-07', 'Appliance schedule & services points', 'NTS')
    micro(c, 12*mm, 253*mm, 'APPLIANCES — CODE AP-xx (INDICATIVE — CONFIRM MODELS)', size=6.0, track=1.4)

    aps = [
        ('AP-01', 'Oven, 60 cm, built-in, multifunction', 'Black glass; ~70 L; multifunction, pyrolytic preferred; as visualised (brand: Teka-style); model TBC', 1, 'A1', '220–240 V — dedicated 16 A + RCD 30 mA; rear vent per mfr; door swing clear'),
        ('AP-02', 'Microwave oven, built-in', 'Black glass; ~38 L; grill/combi preferred; as visualised; model TBC', 1, 'A1', 'Dedicated 16 A; keep clearances per mfr'),
        ('AP-03', 'Warming drawer, built-in', 'Black glass, ~14 L; as visualised below oven', 1, 'A1', '10 A; fused spur above unit'),
        ('AP-04', 'Fridge / freezer, side-by-side', '~910 W × 2100 H × 700 D; matt black; Class A++ (as visualised); model TBC', 1, 'A2', '13 A; 25 mm side/rear gaps; if ice & water — capped CW + filter position'),
        ('AP-05', 'Dishwasher, 60 cm, full-size', 'Stainless front; top-edge controls; A+++; as visualised', 1, 'Base run (5250–5850)', '13 A; 1/2" supply; waste with anti-siphon loop to 40 mm stack'),
        ('AP-06', 'Hob, gas, 4-burner', 'Cast-iron pan supports; flame-failure device each burner; flush-fit black glass/brass', 1, 'Island I3', 'GAS floor box — isolation valve in island; certified fitter; FFD mandatory; 700 min to hood'),
        ('AP-07', 'Hood, 90 cm, ceiling-box, island', 'Black; ≥750 m3/h; 2 + intensive speeds; integral LED; remote + wall control; model TBC', 1, 'Island CL', '13 A + duct Ø150 via cove (SP-06); recirculating kit if no duct route; make-up air check'),
        ('AP-08', 'Sink, inset/undermount, single bowl', 'Black composite; ~500 × 400; drainer groove right; as visualised', 1, 'Base run (3500–4200)', '1/2" HW + CW flexible taps; 40 mm waste; trap with rodding access'),
        ('AP-09', 'Coffee system / compact oven', 'Built-in coffee system or compact oven — black glass; niche @ 1350–1950 AFF; model TBC', 1, 'A5', '13 A; if plumb-in coffee: capped CW + drainage stub'),
        ('AP-10', 'Mixer tap, gooseneck', 'Black gooseneck with pull-out spray; PVD finish MT-06', 1, 'Sink', '1/2" flexible connections; isolation valves both sides'),
        ('AP-11', 'Espresso machine, manual', 'Stainless prosumer, single group; as visualised; model TBC', 1, 'C1', '13 A dedicated; water via internal reservoir — not plumbed'),
        ('AP-12', 'Capsule machine', 'White, as visualised; model TBC', 1, 'C1', '13 A'),
    ]
    table_rows = [header_row(['CODE', 'APPLIANCE', 'INDICATIVE SPEC', 'QTY', 'LOC', 'SERVICES / NOTES'], h=5.6*mm)]
    for code, item, spec, qty, loc, svc in aps:
        table_rows.append((8.15*mm, [dict(t=code, b=True, a='c', size=5.2),
                                      dict(t=item, size=4.5, b=True),
                                      dict(t=spec, size=4.2),
                                      dict(t=str(qty), a='c', size=5.2),
                                      dict(t=loc, size=4.2),
                                      dict(t=svc, size=4.2)]))
    table(c, 12*mm, 246*mm, [14*mm, 62*mm, 122*mm, 11*mm, 44*mm, 146.5*mm], table_rows, pad=1.5*mm)

    sy = 246*mm - 5.6*mm - 12*8.15*mm - 5.5*mm
    micro(c, 12*mm, sy, 'SERVICES POINTS — CODE SP-xx', color=INK, size=5.2, track=1.5)
    sps = [
        ('SP-01', 'Island floor box — GAS isolation + 2× 13 A sockets', 'Accessible within island carcass; flex connector max 1.2 m; gas cert. test', 'Island I3'),
        ('SP-02', 'Oven circuit — 16 A, RCD', 'Home-run to DB; labelled; isolator above oven housing', 'A1'),
        ('SP-03', 'Microwave circuit — 16 A, RCD', 'As SP-02', 'A1'),
        ('SP-04', 'Warming drawer — 10 A fused spur', 'Isolator above unit', 'A1'),
        ('SP-05', 'Fridge — 13 A', '13 A socket behind fridge tower; side panel removable', 'A2'),
        ('SP-06', 'Hood — 13 A + duct Ø150', 'Route via cove A to external wall (E or N); if not feasible — recirculating kit', 'Island / cove'),
        ('SP-07', 'Dishwasher — 13 A + water + waste', 'Anti-siphon loop as mfr instructions; waste to 40 mm stack', 'Base run'),
        ('SP-08', 'Sink — HW + CW 1/2" + 40 mm waste', 'Isolation valves; trap with access; HW from nearest cylinder', 'Base run'),
        ('SP-09', 'Coffee tower — 13 A (+ CW capped if plumb-in)', 'Depends on AP-09 selection — confirm before first fix', 'A5'),
        ('SP-10', 'Coffee bar — 3× 13 A', 'Machines + grinder/kettle + spare; all one DB way', 'C1'),
        ('SP-11', 'Lighting drivers — 1× 13 A', 'Cove A void; drivers Plinth/Vitrine/Task on same circuit; service loop', 'Cove A'),
        ('SP-12', 'Scene controller — 230 V', 'Wall-mounted at room entries; 4 scenes + off; DALI or trailing-edge dimming', 'Entry wall'),
    ]
    sp_rows = [header_row(['SP', 'SERVICE', 'REQUIREMENT', 'LOCATION'], h=5.0*mm)]
    for code, svc, req, loc in sps:
        sp_rows.append((5.35*mm, [dict(t=code, b=True, a='c', size=4.5),
                                   dict(t=svc, size=4.0, b=True),
                                   dict(t=req, size=3.8),
                                   dict(t=loc, size=4.0)]))
    table(c, 12*mm, sy - 4.5*mm, [14*mm, 118*mm, 200*mm, 67.5*mm], sp_rows, pad=1.5*mm)

    micro(c, 12*mm, 33.4*mm,
          'ALL MODELS INDICATIVE — CONFIRM BEFORE ORDER. JOINERY CUT-OUTS TO BE VERIFIED AGAINST CONFIRMED APPLIANCE TEMPLATES. VENTILATION: FRIDGE 25 MIN ALL AROUND; OVEN 50 MIN REAR. NO SOCKETS WITHIN 600 OF SINK.',
          size=4.6, track=0.4)
    c.showPage()

# ============================================================================
# K-08 — LIGHTING & ELECTRICAL SCHEDULE (NTS)
# ============================================================================
def page_k08(c):
    frame_board(c, 'K-08', 'Lighting & electrical schedule', 'NTS')
    micro(c, 12*mm, 253*mm, 'LIGHTING — CODE L-xx', size=6.0, track=1.5)

    ls = [
        ('L-01', 'Island cove — 2 concentric recessed runs', 'LED tape 24 V, 3000 K, CRI min 92, 14 W/m; ALU profile + opal diffuser; continuous, no dark spots; dimmable', '2 runs × ~6.0 m', 'D1', 'COVE A — see K-05; driver in cove void'),
        ('L-02', 'Dining cove — 2 concentric recessed runs', 'As L-01', '2 runs × ~4.0 m', 'D2', 'COVE B — see K-05'),
        ('L-03', 'General downlights DL-01…10', '80 mm recessed, fixed white trim, 3000 K, CRI 90, 60 deg beam, IP20', '10', 'D3', 'SOFFIT (DL-01…04) + ceiling; 300 min spacing'),
        ('L-04', 'Island task spots DL-I1…I4', '80 mm recessed; 60 deg beam; 3000 K; in cove A inner corners', '4', 'D1', 'Task scene — 100% with COOK'),
        ('L-05', 'Pendant trio — niche', 'Woven/ratan bell, 160–200 Ø; E27 2700 K dimmable; drops bottoms @ +1660 / +1775 / +1890 AFF', '3', 'D4', 'Staggered drops; brass caps'),
        ('L-06', 'Niche plinth LED', 'Recessed 10 × 10 ALU profile, opal diffuser, 5 W/m, 2700 K', '1 × 800 mm', 'D4', 'Behind 160 step lip; grazing the step'),
        ('L-07', 'Vitrine LED — back run V1, V2', 'Vertical strips both sides per vitrine; 2700 K; opal; dimmable', '4 strips', 'D4', 'Interior black; 5 W/m max'),
        ('L-08', 'Vitrine LED — coffee bar C2', 'As L-07', '8 strips', 'D4', 'Per door; driver in pantry pelmet'),
        ('L-09', 'Sink bulkhead linear', 'Linear 2400 mm, 3000 K, CRI 90, glare-controlled (deep louvred profile); dimmable', '1', 'D3', 'Own switch; on with GENERAL scene'),
        ('L-10', 'Hood light — integral', 'Supplied with AP-07', '1', 'D5', 'Switches with hood'),
        ('L-11', 'Coffee counter task strip', 'Under-vitrine strip, 2050 mm, 3000 K; OPTIONAL — confirm on site', '1', 'D4', 'Optional line item; exclude if not required'),
    ]
    table_rows = [header_row(['CODE', 'LOCATION / ITEM', 'SPECIFICATION', 'QTY', 'CKT', 'REMARKS'], h=5.4*mm)]
    for code, loc, spec, qty, ckt, rem in ls:
        table_rows.append((7.0*mm, [dict(t=code, b=True, a='c', size=5.0),
                                     dict(t=loc, size=4.2, b=True),
                                     dict(t=spec, size=3.9),
                                     dict(t=qty, size=4.4, a='c'),
                                     dict(t=ckt, size=4.4, a='c'),
                                     dict(t=rem, size=4.0)]))
    table(c, 12*mm, 246*mm, [13*mm, 68*mm, 148*mm, 17*mm, 11*mm, 142.5*mm], table_rows, pad=1.5*mm)

    my = 246*mm - 5.4*mm - 11*7.0*mm - 5.5*mm
    # ---- left: control philosophy (scenes) ----
    micro(c, 12*mm, my, 'CONTROL PHILOSOPHY — 4 SCENES', color=INK, size=5.2, track=1.5)
    scenes = [
        ('SCENE', 'D1 COVE A + TASK', 'D2 COVE B', 'D3 GEN + L-09', 'D4 NICHE + VITRINES'),
        ('ARRIVAL', '40 %', '40 %', '100 %', '30 %'),
        ('COOK', '100 % (task 100 %)', '60 %', '70 %', '60 %'),
        ('DINING', '30 %', '80 %', '20 %', '70 %'),
        ('EVENING', '10 %', '20 %', '0 %', '20 %'),
    ]
    scene_rows = []
    for i, row in enumerate(scenes):
        if i == 0:
            scene_rows.append(header_row(row, h=5.2*mm))
        else:
            scene_rows.append((5.6*mm, [dict(t=row[0], b=True), dict(t=row[1], a='c'), dict(t=row[2], a='c'), dict(t=row[3], a='c'), dict(t=row[4], a='c')]))
    table(c, 12*mm, my - 4.5*mm, [26*mm, 44*mm, 32*mm, 38*mm, 50*mm], scene_rows, default_size=4.4)
    cy = my - 4.5*mm - 5.2*mm - 4*5.6*mm - 5*mm
    for ln in wrap('All dim circuits trailing-edge; scene controller at room entries (see SP-12). 230 V, 50 Hz. All finals on RCBO 30 mA. Drivers accessible; removable cove panels marked on RCP.',
                   'Helvetica', 4.6, 190*mm):
        c.setFillColor(TAUPE); c.setFont('Helvetica', 4.6); c.drawString(12*mm, cy, ln); cy -= 2.6*mm

    # ---- right: electrical points ----
    rx = 222*mm
    micro(c, rx, my, 'ELECTRICAL POINTS — CODE E-xx', color=INK, size=5.2, track=1.5)
    es = [
        ('E-01', 'Oven + microwave — 2× 16 A RCD', 'A1 tower'),
        ('E-02', 'Warming drawer — 10 A fused spur', 'A1 tower'),
        ('E-03', 'Fridge — 13 A socket (behind tower)', 'A2'),
        ('E-04', 'Dishwasher — 13 A + anti-siphon', 'Base run'),
        ('E-05', 'Hood — 13 A (SP-06 duct same route)', 'Island'),
        ('E-06', 'Island floor box — 2× 13 A + GAS iso', 'Island carcass'),
        ('E-07', 'Coffee tower — 13 A (optional CW cap)', 'A5'),
        ('E-08', 'Coffee bar — 3× 13 A (machines + spare)', 'C1'),
        ('E-09', 'Under-cabinet / vitrine drivers — 13 A', 'Cove / pantry pelmet'),
        ('E-10', 'Scene controller — 230 V', 'Entry wall ×2'),
    ]
    e_rows = [header_row(['E', 'POINT', 'LOCATION'], h=5.0*mm)]
    for code, pt, loc in es:
        e_rows.append((5.35*mm, [dict(t=code, b=True, a='c', size=4.4),
                                  dict(t=pt, size=4.1),
                                  dict(t=loc, size=4.1)]))
    table(c, rx, my - 4.5*mm, [14*mm, 118*mm, 56.5*mm], e_rows, pad=1.4*mm)

    ny = my - 4.5*mm - 5.0*mm - 10*5.35*mm - 5*mm
    micro(c, rx, ny, 'NOTES', color=INK, size=5.2, track=1.5); ny -= 4.6*mm
    notes = [
        'No sockets within 600 mm of sink or 150 mm of gas.',
        'All sockets switched, white? black — black anodised to match MT-06.',
        'Island has no sockets on seating side (child safety); floor box serves appliances.',
        'Lighting on separate DB way; label all ways.',
    ]
    for n in notes:
        for ln in wrap('•  ' + n, 'Helvetica', 4.5, 188.5*mm):
            c.setFillColor(INK); c.setFont('Helvetica', 4.5); c.drawString(rx, ny, ln); ny -= 2.6*mm
        ny -= 0.7*mm
    c.showPage()

# ============================================================================
# K-09 — FF&E · EXECUTION NOTES · REVISIONS & SIGN-OFF (NTS)
# ============================================================================
def page_k09(c):
    frame_board(c, 'K-09', 'FF&E schedule · execution notes · revisions & sign-off', 'NTS')
    micro(c, 12*mm, 253*mm, 'FF&E — CODE FE-xx', size=6.0, track=1.6)

    fes = [
        ('FE-01', 'Dining table', 'Rounded-rectangle top 1900 × 950, engineered quartz/sintered stone, white with grey vein (match MT-04); black steel trestle base with levelling feet; as visualised', 1, 'D'),
        ('FE-02', 'Dining chair', 'Curved shell — cognac aniline leather; seat pad grey woven; black metal legs; brass ferrules', 6, 'D'),
        ('FE-03', 'Bar stool', 'Fully upholstered — grey boucle seat and back; black metal legs; brass footrest ring; seat height 650; swivel? no', 2, 'B1'),
        ('FE-04', 'Styling lot — vases, bowls, books, trays', 'Per visualisation (scene 6/7/13); by owner; not in joinery package; indicative only', '1 lot', 'D · C1'),
        ('FE-05', 'Wall art / mirrors', 'NOT SPECIFIED IN THIS STAGE — excluded from this package', '—', '—'),
    ]
    table_rows = [header_row(['CODE', 'ITEM', 'SPECIFICATION', 'QTY', 'LOC'], h=5.4*mm)]
    for code, item, spec, qty, loc in fes:
        table_rows.append((7.6*mm, [dict(t=code, b=True, a='c', size=5.0),
                                     dict(t=item, b=True, size=4.6),
                                     dict(t=spec, size=4.2),
                                     dict(t=str(qty), a='c', size=4.8),
                                     dict(t=loc, size=4.4, a='c')]))
    table(c, 12*mm, 246*mm, [15*mm, 62*mm, 252*mm, 26*mm, 44.5*mm], table_rows, pad=1.6*mm)

    # ---------- GENERAL EXECUTION NOTES ----------
    micro(c, 12*mm, 158*mm, 'GENERAL EXECUTION NOTES', color=INK, size=5.6, track=1.6)
    notes_left = [
        'Scope — kitchen joinery, island, niche, coffee bar, dining loose furniture. MEP first-fix/second-fix by others unless noted.',
        'Dimensions — all indicative from 3D visualisation (±). Site-measure before fabrication; issue marked-up verification drawings to designer for sign-off.',
        'Carcasses — 18 mm moisture-resistant MDF / plywood; edges banded 2 mm PVC or matching veneer. Backs min 8 mm; drawers plywood sides.',
        'Fronts — 19 mm; vertical grain matched across doors; 10 mm shadow gaps with black inserts; gaps uniform, ±0.5 mm.',
        'Hardware — concealed 110 deg hinges with soft-close; 3D adjustment; undermount full-extension runners, rated 40 kg; channel recessed pulls, black.',
        'Finishes — matt lacquer max 10% sheen; veneer sealed with natural hardwax oil or matt PU; no gloss anywhere.',
        'Worktops — 20 mm quartz; waterfall ends mitred 45 deg; site joints colour-matched; support brackets at waterfall returns; unsupported spans max 1200.',
        'Island services — gas + 2× 13 A in floor box; flexible gas connector max 1.2 m with isolation; certified gas fitter; leak test before handover.',
    ]
    notes_right = [
        'Water zones — silicone seal all worktop-to-sink and splashback joints; dishwasher and under-sink tray + leak sensor; waste traps with rodding access.',
        'Electrical — RCBO 30 mA finals; island floor box sealed to IP4X; drivers accessible; all circuits labelled at DB.',
        'Tolerances — cabinets ±1.5 mm over 2 m; worktop flatness 2 mm over 2 m; scribe to walls 10–20 mm as required; skirting mitred.',
        'Coordination — joinery drawings to suit confirmed appliance templates ±5 mm; MEP penetrations drawn through joinery before manufacture.',
        'Protection — all finished surfaces wrapped/boarded until handover; no cutting or adhesive work on site without protection in place.',
        'Handover — O&M manuals (care, cleaning, appliance warranties); 2 site visits: pre-install survey + final snag; defects response 10 working days.',
        'Variations — any change to this package in writing through the RFI/VO process; verbal instructions not accepted for fabrication.',
        'Warranty — joinery 12 months workmanship; appliances per manufacturer; stone against fabrication defects 24 months.',
    ]
    def note_col(x, notes, y_start, width):
        y = y_start
        for i, n in enumerate(notes):
            for ln in wrap(f'{i+1}.  {n}' if x < 200*mm else f'{i+9}.  {n}', 'Helvetica', 5.0, width):
                c.setFillColor(INK); c.setFont('Helvetica', 5.0); c.drawString(x, y, ln); y -= 2.75*mm
            y -= 0.9*mm
        return y
    note_col(12*mm, notes_left, 152.5*mm, 188*mm)
    note_col(212*mm, notes_right, 152.5*mm, 190*mm)

    # ---------- REVISION HISTORY ----------
    ry = 66*mm
    micro(c, 12*mm, ry, 'REVISION HISTORY', color=INK, size=5.2, track=1.6)
    rev_rows = [
        header_row(['REV', 'DATE', 'DESCRIPTION', 'DRAWN', 'CHECKED', 'STATUS'], h=4.8*mm),
        (5.4*mm, [dict(t='P1', b=True, a='c'), '2026-11-22', 'Issued for client review — generated from Enscape visualisation (2026-11-15); dimensions indicative', 'SAMLILL', '—', 'FOR REVIEW']),
    ]
    table(c, 12*mm, ry - 3.6*mm, [12*mm, 26*mm, 236*mm, 28*mm, 26*mm, 71.5*mm], rev_rows, default_size=4.4)

    # ---------- APPROVALS ----------
    ay = 40*mm
    micro(c, 12*mm, ay + 6.4*mm, 'SIGN-OFF', color=INK, size=5.2, track=1.6)
    cells = ['CLIENT — PRIVATE RESIDENCE', 'DESIGNER — SAMLILL INTERIOR ARCHITECTURE', 'CONTRACTOR — FIT-OUT']
    cw = 399.5*mm / 3
    for i, cell in enumerate(cells):
        x = 12*mm + i*cw
        c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(0.9)
        c.rect(x + 1.5*mm, 26.5*mm, cw - 3*mm, ay - 28.5*mm + 4.2*mm, stroke=1, fill=1)
        micro(c, x + 4*mm, ay - 4.6*mm, cell, size=4.0, track=0.5)
        label_ink(c, x + 4*mm, 31.5*mm, 'NAME ________________________', size=5.0)
        label_ink(c, x + 4*mm, 27.6*mm, 'SIGN / DATE _________________', size=5.0)
    c.showPage()

# ============================================================================
def build():
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle('Open-Plan Kitchen & Dining — Shop Drawings and Execution Boards — Rev P1')
    c.setAuthor('SAMLILL — Interior Architecture & Fit-Out')
    c.setSubject('Kitchen shop drawings and execution boards')
    c.setCreator('build_boards.py')
    for fn in (page_k00, page_k01, page_k02, page_k03, page_k04, page_k05, page_k06, page_k07, page_k08, page_k09):
        fn(c)
        print('built', fn.__name__)
    c.save()
    print('saved', OUT, os.path.getsize(OUT), 'bytes')

if __name__ == '__main__':
    build()
