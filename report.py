from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
import uuid
import cv2
from io import BytesIO
from PIL import Image

def generate_pdf_report(alarms, output_folder, video_filename):
    """
    Gera um relatório em PDF contendo as informações dos alarmes detectados durante a análise do vídeo.

    Parâmetros:
    alarms (list): Lista de dicionários contendo os alarmes detectados, com informações como 
                   timestamp, tipo de alarme e imagem associada.
    output_folder (str): Caminho para a pasta onde o relatório em PDF será salvo.
    video_filename (str): Nome do arquivo de vídeo analisado, que será incluído no nome do relatório.

    Retorna:
    str: Caminho completo do arquivo PDF gerado.
    """

    # Gera nome do arquivo PDF com UUID
    unique_filename = f"relatorio_{uuid.uuid4().hex}.pdf"
    report_path = os.path.join(output_folder, unique_filename)

    # Data atual formatada
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Cria o canvas do PDF
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Título do relatório (somente na primeira página)
    c.setFont("Helvetica-Bold", 16)
    title = f"Relatório de Alarmes - {current_date} - {video_filename}"
    c.drawCentredString(width / 2, height - 50, title)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Total de alarmes detectados: {len(alarms)}")

    y_position = height - 120

    for alarm in alarms:
        # Converter imagem para RGB e salvar em buffer
        img_rgb = cv2.cvtColor(alarm["image"], cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        img_buffer = BytesIO()
        pil_img.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        # Inserir imagem no PDF
        image_reader = ImageReader(img_buffer)
        img_width = 3.5 * inch
        img_height = 2.5 * inch
        img_x = 50

        if y_position < 100:
            c.showPage()
            y_position = height - 80

        c.drawImage(image_reader, img_x, y_position - img_height, width=img_width, height=img_height, preserveAspectRatio=True)

        # Dados do alarme
        c.setFont("Helvetica", 11)
        c.drawString(img_x + img_width + 20, y_position - 30, f"⏰ Horário no vídeo: {alarm['time']}")
        c.drawString(img_x + img_width + 20, y_position - 50, f"📍 Mensagem: {alarm['message']}")

        y_position -= img_height + 60

    c.save()
    return unique_filename