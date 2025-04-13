import cv2
import time

# Duração da gravação (em segundos)
duration = 5

# Inicializa a câmera (0 = câmera padrão)
cap = cv2.VideoCapture(0)

# Verifica se conseguiu acessar a câmera
if not cap.isOpened():
    print("Erro ao acessar a webcam.")
    exit()

# Configurações do vídeo
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20  # Frames por segundo

# Criar objeto de escrita de vídeo (.mp4)
out = cv2.VideoWriter(
    'output.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),  # Codec para MP4
    fps,
    (frame_width, frame_height)
)

print("Gravando por 5 segundos...")

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break

    out.write(frame)  # Grava o frame no arquivo
    cv2.imshow('Gravando...', frame)

    # Sai após o tempo ou se apertar 'q'
    if time.time() - start_time > duration or cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera os recursos
cap.release()
out.release()
cv2.destroyAllWindows()
print("Gravação finalizada. Vídeo salvo como 'output.mp4'")
