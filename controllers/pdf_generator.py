import base64
import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas


class AgreementContract:
    width, height = letter

    def __init__(self, job_info):
        self.job = job_info
        self.pdf = None
        self.buffer = io.BytesIO()
        self.canvas = Canvas(self.buffer, pagesize=letter, bottomup=0)
        self.canvas.setLineWidth(.3)

        self.create_pdf()

    def create_pdf(self):
        self.set_pdf_header()
        self.set_pdf_body()
        self.save_pdf()

    def set_pdf_header(self):
        self.canvas.setFont('Times-Bold', 20)
        self.canvas.drawCentredString(self.width/2, inch, "Agreement Contract")

    def set_pdf_body(self):
        self.canvas.setFont('Times-Roman', 12)
        self.canvas.drawString(inch, 2*inch, self.job['title'])

    def get_pdf(self):
        return self.pdf

    def save_pdf(self):
        self.canvas.showPage()
        self.canvas.save()
        self.pdf = base64.b64encode(self.buffer.getvalue())
        self.buffer.close()

