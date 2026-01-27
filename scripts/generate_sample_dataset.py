from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.lib import colors
from PIL import Image, ImageDraw
from pathlib import Path

BASE_DIR = Path("data/samples")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Digital PDF 1
pdf1 = BASE_DIR / "invoice_001.pdf"
c = canvas.Canvas(str(pdf1), pagesize=A4)
c.setFont("Helvetica", 11)
c.drawString(50, 800, "Invoice No: INV-001")
c.drawString(50, 780, "Date: 2024-01-15")
c.drawString(50, 760, "Total Amount: 1,250.00")
table_data = [["Item","Quantity","Price"],["Laptop","1","1000"],["Mouse","1","250"]]
table = Table(table_data, colWidths=[150,100,100])
table.setStyle([("GRID",(0,0),(-1,-1),1,colors.black)])
table.wrapOn(c,50,600)
table.drawOn(c,50,600)
c.save()

# Digital PDF 2
pdf2 = BASE_DIR / "invoice_002.pdf"
c = canvas.Canvas(str(pdf2), pagesize=A4)
c.setFont("Helvetica", 11)
c.drawString(50, 800, "Invoice No: INV-002")
c.drawString(50, 780, "Date: 2024-02-01")
c.drawString(50, 760, "Total Amount: 3,500.00")
table_data = [["Service","Hours","Cost"],["Consulting","10","3000"],["Support","5","500"]]
table = Table(table_data, colWidths=[150,100,100])
table.setStyle([("GRID",(0,0),(-1,-1),1,colors.black)])
table.wrapOn(c,50,600)
table.drawOn(c,50,600)
c.save()

# Scanned-style PDF
img = Image.new("RGB",(1654,2339),"white")
draw = ImageDraw.Draw(img)
draw.text((100,200),"Invoice No: INV-003",fill="black")
draw.text((100,260),"Date: 2024-03-10",fill="black")
draw.text((100,320),"Total Amount: 750.00",fill="black")
img_pdf = BASE_DIR / "invoice_003_scanned.pdf"
img.convert("RGB").save(img_pdf)

print("✅ Sample dataset generated in data/samples/")
