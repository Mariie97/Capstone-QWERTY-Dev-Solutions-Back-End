from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus import Image
from datetime import date
from utilities import CITIES


class AgreementContract:

    def __init__(self, job_info, job_id):
        self.job_id = job_id
        self.job_info = job_info
        self.pdf = None

        self.generate_contract(job_info, job_id)

    def generate_contract(self, job_info, the_job_id):

        client_first_name = job_info['owner_name']
        client_last_name = job_info['owner_last']
        client_name = client_first_name + ' ' + client_last_name

        student_first_name = job_info['student_name']
        student_last_name = job_info['student_last']
        student_name = student_first_name + ' ' + student_last_name

        job_id = the_job_id
        job_title = job_info['title']
        job_description = job_info['description']
        job_street = job_info['street']
        job_city = job_info['city']
        job_zip = job_info['zipcode']
        job_address = str(job_street) + ', ' + CITIES[job_city] + ', Puerto Rico, ' + str(job_zip)
        job_price = job_info['price']

        styles = getSampleStyleSheet()
        pdf_file_name = 'Contract_' + str(job_id) + '.pdf'
        c = canvas.Canvas(pdf_file_name, pagesize=letter)
        width, height = letter

        c.setFont('Helvetica', 10, leading=None)
        c.drawRightString(width - 0.5 * inch, height - 0.25 * inch, 'Contract Automatically Generated - '
                          + str(date.today()))

        #image = 'NewLogo.png'
        #c.drawImage(image, 230, 630, width=None, height=None)

        c.setFont('Helvetica', 12, leading=None)
        c.drawCentredString(width * 0.5, 600, 'Client-Student Contract Agreement for: ')
        c.setFont('Helvetica-BoldOblique', 15, leading=None)
        c.drawCentredString(width * 0.5, 580, job_title.upper())

        c.setFont('Helvetica', 13, leading=None)
        c.drawString(inch, 535, 'Client: ' + client_name)
        c.drawString(inch, 518, 'Student: ' + student_name)

        c.setFont('Helvetica-Bold', 14, leading=None)
        c.drawString(width * 0.5 - 0.5 * inch, 490, 'Job Details')

        c.setFont('Helvetica', 13, leading=None)
        style = ParagraphStyle(name='Description', parent=styles['BodyText'], fontName='Helvetica', fontSize=13,
                               leading=15)
        description = Paragraph('Description: ' + job_description, style, bulletText=None)
        description.wrap(width - 2 * inch, 200)
        description.drawOn(c, inch, 300)
        c.drawString(inch, 270, 'Location: ' + job_address)
        c.drawString(inch, 250, 'Price: ' + job_price)

        text = 'This document uses the following terminology: the Student is defined as the party that will complete ' \
               'the job that has been listed, while the Client is the person that posts the job and pays the student.'

        clause = Paragraph(text, style, bulletText=None)
        clause.wrap(width - 2 * inch, 50)
        clause.drawOn(c, inch, 185)

        text1 = '1. Payment – The client must pay the agreed price, detailed above, upon satisfactory completion ' \
                'of the job by the student. '
        clause1 = Paragraph(text1, style, bulletText=None)
        clause1.wrap(width - 2 * inch, 50)
        clause1.drawOn(c, inch, 135)

        text2 = '2. Schedule – The student will complete the job in accordance with the agreed upon schedule.'
        clause2 = Paragraph(text2, style, bulletText=None)
        clause2.wrap(width - 2 * inch, 50)
        clause2.drawOn(c, inch, 85)

        c.showPage()

        text3 = '3. Entire Agreement - This document reflects the entire agreement between the Parties and reflects ' \
                'a complete understanding of the Parties with respect to the subject matter. This Contract ' \
                'supersedes all prior written and oral representations. The Contract may not be amended, altered, ' \
                'or supplemented except in writing signed by both Parties. '
        clause3 = Paragraph(text3, style, bulletText=None)
        clause3.wrap(width - 2 * inch, 100)
        clause3.drawOn(c, inch, 665)

        text4 = '4. Legal and Binding Contract - This Contract is legal and binding between the Parties as stated ' \
                'above. This Contract may be entered into and is legal and binding in Puerto Rico, the United ' \
                'States, and its other territories. The Parties each represent that they have the authority to enter ' \
                'into this Contract.'
        clause4 = Paragraph(text4, style, bulletText=None)
        clause4.wrap(width - 2 * inch, 100)
        clause4.drawOn(c, inch, 580)

        text5 = '5. Severability - If any provision of this Contract shall be held to be invalid or unenforceable ' \
                'for any reason, the remaining provisions shall continue to be valid and enforceable. If the ' \
                'Court finds that any provision of this Contract is invalid or unenforceable, but that by limiting ' \
                'such provision it would become valid and enforceable, then such provision shall be deemed to be ' \
                'written, construed, and enforced as so limited. '
        clause5 = Paragraph(text5, style, bulletText=None)
        clause5.wrap(width - 2 * inch, 100)
        clause5.drawOn(c, inch, 465)

        text6 = '6. Applicable Law - This Contract shall be governed and construed in accordance with the laws of the' \
                ' state where the Property is located, without giving effect to any conflicts of law’s provisions.'
        clause6 = Paragraph(text6, style, bulletText=None)
        clause6.wrap(width - 2 * inch, 100)
        clause6.drawOn(c, inch, 400)

        text7 = '7. Termination – Both parties can choose to terminate the contract; continued contract ' \
                'terminations without job completions will be faced with disciplinary action from the QWERTY Dev ' \
                'Solutions Admin team.'
        clause7 = Paragraph(text7, style, bulletText=None)
        clause7.wrap(width - 2 * inch, 100)
        clause7.drawOn(c, inch, 335)

        text8 = 'PaRapido and the QWERTY Dev Solutions Team is not responsible for the general payment process ' \
                'between both Parties. In case of a breach of contract by either Party – namely, failure of payment ' \
                'by the client or failure of job execution by the student – and the dispute that arises cannot ' \
                'be resolved, then both Parties must resort to appropriate legal action. '
        clause8 = Paragraph(text8, style, bulletText=None)
        clause8.wrap(width - 2 * inch, 100)
        clause8.drawOn(c, inch, 240)

        text9 = 'The page for the corresponding job contains a two-way certification process, allowing each Party to ' \
                'acknowledge and agree to the contract. BY CERTIFYING THIS STEP ON THE AFOREMENTIONED PAGE, BOTH ' \
                'PARTIES ACKNOWLEDGE HAVING READ AND UNDERSTOOD THIS CONTRACT AND THAT BOTH PARTIES ARE SATISFIED ' \
                'WITH THE TERMS AND CONDITIONS CONTAINED IN THIS CONTRACT. BOTH PARTIES ARE ENTITLED TO A COPY ' \
                'OF THIS CONTRACT.'
        clause9 = Paragraph(text9, style, bulletText=None)
        clause9.wrap(width - 2 * inch, 100)
        clause9.drawOn(c, inch, 120)

        c.setFont('Helvetica-Bold', 16, leading=None)
        c.drawCentredString(width * 0.5, 80, 'QWERTY Dev Solutions')
        c.setFont('Helvetica', 12, leading=None)
        c.drawCentredString(width * 0.5, 60, 'Email: parapidopr@gmail.com')

        c.showPage()
        c.save()

    def get_pdf(self):
        return self.pdf
