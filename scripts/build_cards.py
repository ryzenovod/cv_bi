"""Build the cards and QR from vector geometry. Run from any directory.

Dependencies: reportlab, pypdf, qrcode, fonttools, Pillow.
SITE_URL is the only QR destination; changing it also changes the printed URL.
"""
from pathlib import Path
from io import BytesIO
import json
from xml.sax.saxutils import escape
import qrcode
from fontTools.ttLib import TTFont as FontToolsFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, CMYKColor
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'design'
OUT = ROOT / 'output/pdf'
TMP = ROOT / 'tmp/fonts'
for folder in (DESIGN, OUT, TMP):
    folder.mkdir(parents=True, exist_ok=True)
SITE_URL = 'https://ryzenovod.github.io/cv_bi/'
PAPER, INK, GOLD, MUTED = '#F8F5EF', '#342C39', '#AE8744', '#736B72'
FONTS = {}
for name, source, weight in [('Serif', 'CormorantGaramond', 500), ('Sans', 'Manrope', 400)]:
    font = instantiateVariableFont(FontToolsFont(ROOT / f'assets/fonts/{source}.ttf'), {'wght': weight})
    target = TMP / f'{name}.ttf'
    font.save(target)
    pdfmetrics.registerFont(TTFont(name, str(target)))
    FONTS[name] = font

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4, box_size=20)
qr.add_data(SITE_URL)
qr.make(fit=True)
MATRIX = qr.get_matrix()
qr.make_image(fill_color=INK, back_color='white').save(DESIGN / 'qr-site.png')


class Art:
    """One geometry source, used for SVG and PDF. Coordinates: 10 units/mm."""
    def __init__(self, pdf=None, outline=True, foil=False):
        self.pdf, self.outline, self.foil = pdf, outline, foil
        self.parts = []

    def rect(self, x, y, w, h, color):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{color}"/>')
        if self.pdf:
            self.pdf.setFillColor(HexColor(color))
            self.pdf.rect(x, y, w, h, stroke=0, fill=1)

    def line(self, x1, y1, x2, y2, color, width=1):
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}"/>')
        if self.pdf:
            self.pdf.setStrokeColor(HexColor(color))
            self.pdf.setLineWidth(width)
            self.pdf.line(x1,y1,x2,y2)

    def text(self, x, y, value, size, font='Sans', color=INK):
        if self.outline:
            f = FONTS[font]
            scale = size / f['head'].unitsPerEm
            gs, cmap = f.getGlyphSet(), f.getBestCmap()
            advance = x
            for ch in value:
                glyph = gs[cmap[ord(ch)]]
                pen = SVGPathPen(gs)
                glyph.draw(pen)
                if pen.getCommands():
                    self.parts.append(f'<path d="{pen.getCommands()}" transform="translate({advance:g},{y:g}) scale({scale:g},-{scale:g})" fill="{color}"/>')
                advance += glyph.width * scale
        else:
            family = 'Cormorant Garamond' if font == 'Serif' else 'Manrope'
            self.parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{500 if font == "Serif" else 400}" fill="{color}">{escape(value)}</text>')
        if self.pdf:
            self.pdf.saveState()
            self.pdf.translate(x, y)
            self.pdf.scale(1,-1)
            self.pdf.setFont(font, size)
            self.pdf.setFillColor(HexColor(color))
            self.pdf.drawString(0,0,value)
            self.pdf.restoreState()

    def serpent(self, x, y, scale=1, color=GOLD):
        commands = [
            [('M',111,64),('C',130,31,98,13,75,26),('C',49,41,56,69,78,88),('L',113,118),('C',138,141,123,158,91,164),('C',62,169,61,190,88,201),('C',105,208,102,220,87,226)],
            [('M',30,96),('L',150,96),('C',141,128,121,143,90,143),('C',59,143,39,128,30,96),('Z',)],
            [('M',90,144),('L',90,225)], [('M',62,228),('L',118,228)],
        ]
        self.parts.append(f'<g transform="translate({x},{y}) scale({scale})" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none">')
        if self.pdf:
            self.pdf.saveState(); self.pdf.translate(x,y); self.pdf.scale(scale,scale)
            self.pdf.setStrokeColor(CMYKColor(0,0,0,1) if self.foil else HexColor(color)); self.pdf.setLineWidth(4)
            self.pdf.setLineCap(1); self.pdf.setLineJoin(1)
        for commands_one in commands:
            data = ' '.join(c[0] + ' '.join(str(n) for n in c[1:]) for c in commands_one)
            self.parts.append(f'<path d="{data}"/>')
            if self.pdf:
                p = self.pdf.beginPath()
                for c in commands_one:
                    if c[0] == 'M': p.moveTo(*c[1:])
                    elif c[0] == 'L': p.lineTo(*c[1:])
                    elif c[0] == 'C': p.curveTo(*c[1:])
                    else: p.close()
                self.pdf.drawPath(p,stroke=1,fill=0)
        self.parts.append('</g>')
        head = 'M106 56L124 66L107 75Q111 65 106 56Z'
        self.parts.append(f'<path d="{head}" transform="translate({x},{y}) scale({scale})" fill="{color}"/>')
        if self.pdf:
            self.pdf.setFillColor(CMYKColor(0,0,0,1) if self.foil else HexColor(color)); p = self.pdf.beginPath()
            p.moveTo(106,56); p.lineTo(124,66); p.lineTo(107,75)
            p.curveTo(109.667,68.333,109.333,62,106,56); p.close()
            self.pdf.drawPath(p,stroke=0,fill=1); self.pdf.restoreState()

    def qr(self, x, y, size):
        n = len(MATRIX)
        unit = size/n
        self.rect(x,y,size,size,'#FFFFFF')
        for row, values in enumerate(MATRIX):
            for col, active in enumerate(values):
                if active:
                    self.rect(x+col*unit,y+row*unit,unit,unit,INK)

    def svg(self, path, background=True):
        styles = ''
        if not self.outline:
            styles = '<style>@font-face{font-family:"Cormorant Garamond";src:url("../assets/fonts/CormorantGaramond.ttf")}@font-face{font-family:Manrope;src:url("../assets/fonts/Manrope.ttf")}</style>'
        path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="90mm" height="50mm" viewBox="0 0 900 500">' + styles + ''.join(self.parts) + '</svg>')


def front(a):
    if a.foil:
        a.serpent(59,119,1.05,'#000000')
        return
    a.rect(-30,-30,960,560,PAPER)
    a.serpent(59,119,1.05)
    a.line(277,83,277,417,'#CDBB9D',1)
    a.text(330,148,'Елизавета',51,'Serif')
    a.text(330,202,'Антипова',62,'Serif')
    a.text(333,253,'Бизнес-аналитик',23)
    a.line(333,283,805,283,'#DDD4C8',1)
    a.text(333,326,'+7 (902) 979-22-90',23)
    a.text(333,362,'lizzzucker@gmail.com',23)
    a.text(333,417,'Данные · BI · Бизнес-процессы',19,color=MUTED)


def back(a):
    a.rect(-30,-30,960,560,PAPER)
    a.text(65,116,'Елизавета Антипова',32,'Serif')
    a.text(66,151,'Бизнес-аналитик',19,color=MUTED)
    a.line(66,204,133,204,GOLD,2)
    a.text(65,263,'Опыт работы',38,'Serif')
    a.text(65,306,'и контакты',38,'Serif')
    a.text(66,354,'Наведите камеру на QR-код',18,color=MUTED)
    a.text(66,426,SITE_URL.removeprefix('https://'),17,color=MUTED)
    a.qr(557,113,280)


def pdf_document(filename, funcs, bleed=False, foil=False):
    w,h = (96,56) if bleed else (90,50)
    raw = BytesIO()
    c = canvas.Canvas(raw,pagesize=(w*mm,h*mm),pageCompression=1)
    c.setTitle('Елизавета Антипова | Business card' + (' | Gold foil mask' if foil else ''))
    c.setAuthor('Елизавета Антипова')
    for fn in funcs:
        c.saveState()
        c.translate((3 if bleed else 0)*mm, (h-(3 if bleed else 0))*mm)
        c.scale(mm/10,-mm/10)
        fn(Art(c,foil=foil))
        c.restoreState()
        c.showPage()
    c.save()
    reader = PdfReader(raw)
    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        if bleed:
            page.trimbox=RectangleObject([3*mm,3*mm,93*mm,53*mm])
            page.bleedbox=RectangleObject([0,0,96*mm,56*mm])
    writer.add_metadata({'/Title': reader.metadata.title, '/Author':'Елизавета Антипова'})
    with (OUT / filename).open('wb') as f:
        writer.write(f)


for name, fn in [('front',front),('back',back)]:
    for outlined in [True,False]:
        art=Art(outline=outlined)
        fn(art)
        art.svg(DESIGN / f'card-{name}{"" if outlined else "-editable"}.svg')
foil_art=Art(foil=True)
front(foil_art)
foil_art.svg(DESIGN/'gold-foil-mask.svg',background=False)
standalone=Art()
standalone.qr(0,0,900)
(DESIGN/'qr-site.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 900">'+''.join(standalone.parts)+'</svg>')
pdf_document('business-card-90x50.pdf',[front,back])
pdf_document('business-card-print-bleed-3mm.pdf',[front,back],bleed=True)
pdf_document('gold-foil-mask-bleed-3mm.pdf',[front],bleed=True,foil=True)
(DESIGN/'qr-payload.json').write_text(json.dumps({'url':SITE_URL,'error_correction':'Q','quiet_zone_modules':4,'matrix_modules':len(MATRIX)-8,'printed_size_mm':28},indent=2)+'\n')
print('Created 3 PDFs, outlined and editable SVG cards, foil mask, PNG/SVG QR.')
