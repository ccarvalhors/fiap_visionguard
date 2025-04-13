import base64
import cv2
import numpy as np
import os
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
import uuid
from io import BytesIO
from PIL import Image
import requests
from dotenv import load_dotenv
import threading
from tqdm import tqdm

load_dotenv()

# Flask setup
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["REPORT_FOLDER"] = "reports"
socketio = SocketIO(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)

# Estado de detecção
last_detected_state = False

def send_email_alarm_live(email_to, image_b64, timestamp, message):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    html_content = f"""
    <h3>🚨 Alarme detectado</h3>
    <p><strong>{message}</strong> em {timestamp}</p>
    """

    data = {
        "sender": {"name": "Vision Guard", "email": os.getenv("EMAIL_FROM")},
        "to": [{"email": email_to}],
        "subject": "Alarme ao vivo - Vision Guard",
        "htmlContent": html_content,
        "attachment": [{
            "name": "alarme.jpg",
            "content": image_b64
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    print("[INFO] Alarme ao vivo enviado por e-mail:", response.status_code, response.text)

def send_email_with_pdf(email_to, report_path, original_filename):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    with open(report_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode()

    data = {
        "sender": {"name": "Vision Guard", "email": os.getenv("EMAIL_FROM")},
        "to": [{"email": email_to}],
        "subject": f"📄 Relatório Vision Guard - {original_filename}",
        "htmlContent": f"<p>Seu relatório chegou! Veja em anexo.</p>",
        "attachment": [{
            "name": f"relatorio_{original_filename}.pdf",
            "content": encoded_pdf
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    print("[INFO] Relatório enviado por e-mail:", response.status_code, response.text)

def detect_faces(frame):
    import face_recognition
    face_locations = face_recognition.face_locations(frame)
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    return frame, len(face_locations) > 0

def format_time(ms):
    seconds = ms / 1000.0
    return datetime.fromtimestamp(seconds, timezone.utc).strftime('%H:%M:%S')

def generate_pdf_report(alarms, output_folder, video_filename):
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

def process_frame(image_data, email_to):
    global last_detected_state

    try:
        print("[INFO] Processando frame ao vivo...")

        frame_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        _, detected = detect_faces(frame)
        if detected:
            print("[INFO] Face detectada...")        

        # Verifica transição de estado
        if detected and not last_detected_state:            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _, jpeg_image = cv2.imencode(".jpg", frame)
            base64_image = base64.b64encode(jpeg_image).decode("utf-8")
            print("[INFO] Novo alarme...")
            emit("alarm", {
                "image": f"data:image/jpeg;base64,{base64_image}",
                "message": "Face detectada",
                "timestamp": timestamp
            })
            send_email_alarm_live(email_to, base64_image, timestamp, "Face detectada")

        last_detected_state = detected        

    except Exception as e:
        print("[ERRO] Ao processar frame:", e)

def process_video(email_to, filepath, filename):
    cap = cv2.VideoCapture(filepath)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    alarms = []
    last_detected = False

    print(f"[INFO] Processando vídeo: {filename}")
    with tqdm(total=total_frames, desc="Processando vídeo") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame, detected = detect_faces(frame)
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            if detected and not last_detected:
                alarms.append({
                    "time": format_time(timestamp_ms),
                    "message": "Face detectada no vídeo",
                    "image": processed_frame.copy()
                })
            last_detected = detected
            pbar.update(1)

    cap.release()

    report_name = generate_pdf_report(alarms, app.config["REPORT_FOLDER"], filename)
    send_email_with_pdf(email_to, os.path.join(app.config["REPORT_FOLDER"], report_name), os.path.basename(filepath))

def start_video_processing(email_to, filepath, filename):
    thread = threading.Thread(
        target=process_video,
        args=(email_to, filepath, filename)
    )
    thread.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["video"]
    if not file:
        return "No file uploaded", 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    start_video_processing(request.form.get("email"), filepath, filename)

    return jsonify({
            "message": "Vídeo enviado com sucesso! Você receberá o relatório por e-mail assim que estiver pronto."
        })

@socketio.on("frame")
def frame(data):    
    process_frame(data["image"].split(",")[1], data["email"])

if __name__ == "__main__":
    socketio.run(app, debug=True)
