import base64
import cv2
import numpy as np
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import threading
from tqdm import tqdm
from deepface import DeepFace
from ultralytics import YOLO

from email_sender import send_email_alarm_live, send_email_with_pdf
from helpers import format_time
from report import generate_pdf_report

# Carrega configurações do arquivo .env e disponibiliza como variáveis de ambiente.
load_dotenv()

# Carregar o modelo YOLO treinado
knife_model = YOLO('models/knife/best.pt')

# Flask setup
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["REPORT_FOLDER"] = "reports"
socketio = SocketIO(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)

# Estado do alarme
alarm_triggered = False

def detect_faces(frame):
    try:
        # DeepFace retorna uma lista com as análises das faces encontradas
        detections = DeepFace.extract_faces(
            img_path=frame,
            detector_backend='opencv',  # você pode testar com 'retinaface', 'mediapipe', etc.
            enforce_detection=False,
            align=False
        )

        # Desenhar as caixas no frame
        for detection in detections:
            region = detection['facial_area']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return frame, len(detections) > 0

    except Exception as e:
        print("[ERRO] Erro ao detectar faces com DeepFace:", e)
        return frame, False

def emit_alarm(frame, email_to, message):
    """
    Emite um alarme quando um objeto cortante é detectado, enviando uma notificação por e-mail e transmitindo a imagem.

    Parâmetros:
    frame (ndarray): Imagem do frame capturado da câmera ou do vídeo onde o alarme foi detectado.
    email_to (str): Endereço de e-mail para o qual o alarme será enviado.
    message (str): Mensagem que descreve o tipo de alarme gerado (ex. "Objeto Cortante Detectado").

    Retorna:
    None
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _, jpeg_image = cv2.imencode(".jpg", frame)
    base64_image = base64.b64encode(jpeg_image).decode("utf-8")

    emit("alarm", {
        "image": f"data:image/jpeg;base64,{base64_image}",
        "message": message,
        "timestamp": timestamp
    })
    send_email_alarm_live(email_to, base64_image, timestamp, message)

def detect_knives(frame):
    """
    Detecta objetos cortantes (facas) em um frame de imagem e desenha retângulos ao redor dos objetos detectados.

    Parâmetros:
    frame (ndarray): Imagem ou vídeo onde a detecção de facas será realizada.

    Retorna:
    tuple:
        - frame (ndarray): O frame original com os retângulos desenhados ao redor das facas detectadas.
        - bool: True se uma faca foi detectada, caso contrário, False.
    """

    results = knife_model.predict(frame, conf=0.4, verbose=False)
    boxes = results[0].boxes
    
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        # Desenhar retângulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)        

    return frame, len(boxes) > 0

def process_frame(image_data, email_to):
    global alarm_triggered

    try:
        #print("[INFO] Processando frame ao vivo...")

        # Decodificar a imagem recebida
        frame_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)        

        # Detectar objetos cortantes
        _, knife_detected = detect_knives(frame)

        # Verifica se deve alarmar
        if knife_detected and not alarm_triggered:
            # Detectar faces
            _, face_detected = detect_faces(frame)

            if knife_detected and face_detected:
                print("[ALARM] Pessoa com objeto cortante detectada.")
                emit_alarm(frame, email_to, "Pessoa com objeto cortante detectada")                

            else:
                print("[ALARM] Objeto cortante detectado.")
                emit_alarm(frame, email_to, "Objeto cortante detectado")

            alarm_triggered = True

        elif not knife_detected:
            alarm_triggered = False

    except Exception as e:
        print("[ERRO] Ao processar frame:", e)

def process_video(email_to, filepath, filename):
    """
    Processa um frame de imagem recebido, detecta objetos cortantes e faces, e gera alarmes via e-mail.

    Parâmetros:
    image_data (str): Dados de imagem codificados em base64 recebidos do cliente.
    email_to (str): E-mail para o qual o alarme será enviado.

    Retorna:
    None

    A função processa o frame de imagem para detectar objetos cortantes e faces. Se um objeto cortante for
    detectado e uma face estiver presente na cena, um alarme de "Pessoa com objeto cortante detectada" é gerado.
    Caso contrário, um alarme de "Objeto cortante detectado" é gerado. O alarme é enviado por e-mail com a imagem.
    A função só gera um novo alarme quando um novo evento de detecção é detectado (alarm_triggered é verificado).
    """

    cap = cv2.VideoCapture(filepath)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    alarms = []
    
    # Flag para não repetir alarmes
    alarm_triggered = False    

    print(f"[INFO] Processando vídeo: {filename}")
    with tqdm(total=total_frames, desc="Processando vídeo") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = frame.copy()
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            time_str = format_time(timestamp_ms)

            # Detectar objetos cortantes
            processed_frame, knife_detected = detect_knives(processed_frame)

             # Verifica se deve alarmar
            if knife_detected and not alarm_triggered:
                # Detectar faces
                processed_frame, face_detected = detect_faces(processed_frame)

                if knife_detected and face_detected:                
                    alarms.append({
                        "time": time_str,
                        "message": "Pessoa com objeto cortante detectada",
                        "image": processed_frame.copy()
                    })
                else:
                    alarms.append({
                        "time": time_str,
                        "message": "Objeto cortante detectado",
                        "image": processed_frame.copy()
                    })
                
                alarm_triggered = True

            elif not knife_detected:
                alarm_triggered = False            
            
            pbar.update(1)

    cap.release()

    report_name = generate_pdf_report(alarms, app.config["REPORT_FOLDER"], filename)
    send_email_with_pdf(email_to, os.path.join(app.config["REPORT_FOLDER"], report_name), os.path.basename(filepath))

def start_video_processing(email_to, filepath, filename):
    """
    Inicia o processamento de um vídeo em um thread separado.

    Parâmetros:
    email_to (str): O endereço de e-mail para o qual o relatório será enviado ao final do processamento do vídeo.
    filepath (str): O caminho completo para o arquivo de vídeo a ser processado.
    filename (str): O nome do arquivo de vídeo.

    Retorna:
    None

    A função cria e inicia uma nova thread que chama a função `process_video` para processar o vídeo especificado.
    O processamento ocorre em segundo plano, permitindo que a aplicação continue responsiva enquanto o vídeo
    é processado. Ao final, um relatório é gerado e enviado por e-mail para o endereço fornecido.
    """

    thread = threading.Thread(
        target=process_video,
        args=(email_to, filepath, filename)
    )
    thread.start()

#--------------------------------------------------------------------------
# Rotas
#--------------------------------------------------------------------------

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

#--------------------------------------------------------------------------
# Eventos
#--------------------------------------------------------------------------
@socketio.on("frame")
def frame(data):    
    process_frame(data["image"].split(",")[1], data["email"])

@socketio.on("disarm_alarm")
def disarm_alarm(data):
    global alarm_triggered
    alarm_triggered = False

if __name__ == "__main__":
    socketio.run(app, debug=True)
